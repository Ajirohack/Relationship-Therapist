"""Vector Database Service for semantic search and embeddings"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
import hashlib
from datetime import datetime
import numpy as np

try:
    import qdrant_client
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
    qdrant_client = None

try:
    import pinecone
except ImportError:
    pinecone = None

try:
    import chromadb
except ImportError:
    chromadb = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

from config import settings, VectorDBType

logger = logging.getLogger(__name__)

@dataclass
class Document:
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    timestamp: Optional[datetime] = None

@dataclass
class SearchResult:
    document: Document
    score: float
    distance: float

class EmbeddingService:
    """Service for generating embeddings"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize embedding model"""
        try:
            if SentenceTransformer:
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"Initialized embedding model: {self.model_name}")
            else:
                logger.warning("SentenceTransformer not available, using fallback embeddings")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
    
    async def encode(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        if self.model:
            try:
                # Run in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                embeddings = await loop.run_in_executor(
                    None, 
                    lambda: self.model.encode(texts).tolist()
                )
                return embeddings
            except Exception as e:
                logger.error(f"Embedding generation failed: {e}")
        
        # Fallback: simple hash-based embeddings
        return [self._fallback_embedding(text) for text in texts]
    
    def _fallback_embedding(self, text: str, dim: int = 384) -> List[float]:
        """Generate simple hash-based embedding as fallback"""
        # Create deterministic embedding from text hash
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to float vector
        embedding = []
        for i in range(0, min(len(hash_bytes), dim // 8)):
            byte_val = hash_bytes[i]
            # Convert byte to 8 float values between -1 and 1
            for bit in range(8):
                if len(embedding) >= dim:
                    break
                bit_val = (byte_val >> bit) & 1
                embedding.append(2.0 * bit_val - 1.0)
        
        # Pad or truncate to desired dimension
        while len(embedding) < dim:
            embedding.append(0.0)
        
        return embedding[:dim]

class VectorDBInterface(ABC):
    """Abstract interface for vector databases"""
    
    @abstractmethod
    async def create_collection(self, collection_name: str, dimension: int) -> bool:
        pass
    
    @abstractmethod
    async def insert_documents(self, collection_name: str, documents: List[Document]) -> bool:
        pass
    
    @abstractmethod
    async def search(self, collection_name: str, query_vector: List[float], 
                   top_k: int = 10, filter_dict: Optional[Dict] = None) -> List[SearchResult]:
        pass
    
    @abstractmethod
    async def delete_documents(self, collection_name: str, document_ids: List[str]) -> bool:
        pass
    
    @abstractmethod
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        pass

class QdrantVectorDB(VectorDBInterface):
    """Qdrant vector database implementation"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Qdrant client"""
        try:
            if qdrant_client:
                self.client = qdrant_client.QdrantClient(
                    host=settings.qdrant_host,
                    port=settings.qdrant_port,
                    api_key=settings.qdrant_api_key
                )
                logger.info("Qdrant client initialized")
            else:
                logger.error("Qdrant client not available")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}")
    
    async def create_collection(self, collection_name: str, dimension: int) -> bool:
        """Create Qdrant collection"""
        if not self.client:
            return False
        
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=dimension, distance=Distance.COSINE)
            )
            logger.info(f"Created Qdrant collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create Qdrant collection: {e}")
            return False
    
    async def insert_documents(self, collection_name: str, documents: List[Document]) -> bool:
        """Insert documents into Qdrant"""
        if not self.client:
            return False
        
        try:
            points = []
            for doc in documents:
                if doc.embedding:
                    points.append(PointStruct(
                        id=doc.id,
                        vector=doc.embedding,
                        payload={
                            "content": doc.content,
                            "metadata": doc.metadata,
                            "timestamp": doc.timestamp.isoformat() if doc.timestamp else None
                        }
                    ))
            
            if points:
                self.client.upsert(
                    collection_name=collection_name,
                    points=points
                )
                logger.info(f"Inserted {len(points)} documents into Qdrant")
            return True
        except Exception as e:
            logger.error(f"Failed to insert documents into Qdrant: {e}")
            return False
    
    async def search(self, collection_name: str, query_vector: List[float], 
                   top_k: int = 10, filter_dict: Optional[Dict] = None) -> List[SearchResult]:
        """Search in Qdrant"""
        if not self.client:
            return []
        
        try:
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=filter_dict
            )
            
            results = []
            for hit in search_result:
                doc = Document(
                    id=str(hit.id),
                    content=hit.payload.get("content", ""),
                    metadata=hit.payload.get("metadata", {}),
                    timestamp=datetime.fromisoformat(hit.payload["timestamp"]) if hit.payload.get("timestamp") else None
                )
                results.append(SearchResult(
                    document=doc,
                    score=hit.score,
                    distance=1.0 - hit.score  # Convert similarity to distance
                ))
            
            return results
        except Exception as e:
            logger.error(f"Qdrant search failed: {e}")
            return []
    
    async def delete_documents(self, collection_name: str, document_ids: List[str]) -> bool:
        """Delete documents from Qdrant"""
        if not self.client:
            return False
        
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=document_ids
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete documents from Qdrant: {e}")
            return False
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get Qdrant collection info"""
        if not self.client:
            return {}
        
        try:
            info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count,
                "status": info.status,
                "config": info.config.dict() if hasattr(info.config, 'dict') else str(info.config)
            }
        except Exception as e:
            logger.error(f"Failed to get Qdrant collection info: {e}")
            return {}

class PineconeVectorDB(VectorDBInterface):
    """Pinecone vector database implementation"""
    
    def __init__(self):
        self.index = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Pinecone client"""
        try:
            if pinecone and settings.pinecone_api_key:
                pinecone.init(
                    api_key=settings.pinecone_api_key,
                    environment=settings.pinecone_environment
                )
                logger.info("Pinecone client initialized")
            else:
                logger.error("Pinecone client not available or API key missing")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone client: {e}")
    
    async def create_collection(self, collection_name: str, dimension: int) -> bool:
        """Create Pinecone index"""
        if not pinecone:
            return False
        
        try:
            if collection_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=collection_name,
                    dimension=dimension,
                    metric="cosine"
                )
            self.index = pinecone.Index(collection_name)
            logger.info(f"Created/connected to Pinecone index: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create Pinecone index: {e}")
            return False
    
    async def insert_documents(self, collection_name: str, documents: List[Document]) -> bool:
        """Insert documents into Pinecone"""
        if not self.index:
            await self.create_collection(collection_name, len(documents[0].embedding) if documents and documents[0].embedding else 384)
        
        try:
            vectors = []
            for doc in documents:
                if doc.embedding:
                    vectors.append((
                        doc.id,
                        doc.embedding,
                        {
                            "content": doc.content,
                            "metadata": json.dumps(doc.metadata),
                            "timestamp": doc.timestamp.isoformat() if doc.timestamp else None
                        }
                    ))
            
            if vectors:
                self.index.upsert(vectors)
                logger.info(f"Inserted {len(vectors)} documents into Pinecone")
            return True
        except Exception as e:
            logger.error(f"Failed to insert documents into Pinecone: {e}")
            return False
    
    async def search(self, collection_name: str, query_vector: List[float], 
                   top_k: int = 10, filter_dict: Optional[Dict] = None) -> List[SearchResult]:
        """Search in Pinecone"""
        if not self.index:
            return []
        
        try:
            search_result = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            results = []
            for match in search_result.matches:
                metadata = match.metadata or {}
                doc = Document(
                    id=match.id,
                    content=metadata.get("content", ""),
                    metadata=json.loads(metadata.get("metadata", "{}")),
                    timestamp=datetime.fromisoformat(metadata["timestamp"]) if metadata.get("timestamp") else None
                )
                results.append(SearchResult(
                    document=doc,
                    score=match.score,
                    distance=1.0 - match.score
                ))
            
            return results
        except Exception as e:
            logger.error(f"Pinecone search failed: {e}")
            return []
    
    async def delete_documents(self, collection_name: str, document_ids: List[str]) -> bool:
        """Delete documents from Pinecone"""
        if not self.index:
            return False
        
        try:
            self.index.delete(ids=document_ids)
            return True
        except Exception as e:
            logger.error(f"Failed to delete documents from Pinecone: {e}")
            return False
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get Pinecone index info"""
        if not self.index:
            return {}
        
        try:
            stats = self.index.describe_index_stats()
            return {
                "name": collection_name,
                "vectors_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }
        except Exception as e:
            logger.error(f"Failed to get Pinecone index info: {e}")
            return {}

class ChromaVectorDB(VectorDBInterface):
    """ChromaDB vector database implementation"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client"""
        try:
            if chromadb:
                self.client = chromadb.Client()
                logger.info("ChromaDB client initialized")
            else:
                logger.error("ChromaDB not available")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
    
    async def create_collection(self, collection_name: str, dimension: int) -> bool:
        """Create ChromaDB collection"""
        if not self.client:
            return False
        
        try:
            self.collection = self.client.get_or_create_collection(name=collection_name)
            logger.info(f"Created/connected to ChromaDB collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create ChromaDB collection: {e}")
            return False
    
    async def insert_documents(self, collection_name: str, documents: List[Document]) -> bool:
        """Insert documents into ChromaDB"""
        if not self.collection:
            await self.create_collection(collection_name, 384)
        
        try:
            ids = [doc.id for doc in documents]
            embeddings = [doc.embedding for doc in documents if doc.embedding]
            documents_text = [doc.content for doc in documents]
            metadatas = [{
                **doc.metadata,
                "timestamp": doc.timestamp.isoformat() if doc.timestamp else None
            } for doc in documents]
            
            if embeddings:
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=documents_text,
                    metadatas=metadatas
                )
                logger.info(f"Inserted {len(documents)} documents into ChromaDB")
            return True
        except Exception as e:
            logger.error(f"Failed to insert documents into ChromaDB: {e}")
            return False
    
    async def search(self, collection_name: str, query_vector: List[float], 
                   top_k: int = 10, filter_dict: Optional[Dict] = None) -> List[SearchResult]:
        """Search in ChromaDB"""
        if not self.collection:
            return []
        
        try:
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                where=filter_dict
            )
            
            search_results = []
            for i, doc_id in enumerate(results['ids'][0]):
                doc = Document(
                    id=doc_id,
                    content=results['documents'][0][i],
                    metadata=results['metadatas'][0][i],
                    timestamp=datetime.fromisoformat(results['metadatas'][0][i]['timestamp']) if results['metadatas'][0][i].get('timestamp') else None
                )
                search_results.append(SearchResult(
                    document=doc,
                    score=1.0 - results['distances'][0][i],  # Convert distance to similarity
                    distance=results['distances'][0][i]
                ))
            
            return search_results
        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            return []
    
    async def delete_documents(self, collection_name: str, document_ids: List[str]) -> bool:
        """Delete documents from ChromaDB"""
        if not self.collection:
            return False
        
        try:
            self.collection.delete(ids=document_ids)
            return True
        except Exception as e:
            logger.error(f"Failed to delete documents from ChromaDB: {e}")
            return False
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get ChromaDB collection info"""
        if not self.collection:
            return {}
        
        try:
            count = self.collection.count()
            return {
                "name": collection_name,
                "vectors_count": count,
                "type": "chromadb"
            }
        except Exception as e:
            logger.error(f"Failed to get ChromaDB collection info: {e}")
            return {}

class VectorDBService:
    """Main vector database service"""
    
    def __init__(self):
        self.db_type = settings.vector_db_type
        self.embedding_service = EmbeddingService()
        self.vector_db = self._initialize_vector_db()
    
    def _initialize_vector_db(self) -> Optional[VectorDBInterface]:
        """Initialize vector database based on configuration"""
        if self.db_type == VectorDBType.QDRANT:
            return QdrantVectorDB()
        elif self.db_type == VectorDBType.PINECONE:
            return PineconeVectorDB()
        elif self.db_type == VectorDBType.CHROMA:
            return ChromaVectorDB()
        else:
            logger.info("Vector database disabled")
            return None
    
    async def add_documents(self, collection_name: str, texts: List[str], 
                          metadatas: List[Dict[str, Any]], 
                          document_ids: Optional[List[str]] = None) -> bool:
        """Add documents to vector database"""
        if not self.vector_db:
            return False
        
        try:
            # Generate embeddings
            embeddings = await self.embedding_service.encode(texts)
            
            # Create document objects
            documents = []
            for i, (text, metadata, embedding) in enumerate(zip(texts, metadatas, embeddings)):
                doc_id = document_ids[i] if document_ids else f"doc_{i}_{hashlib.md5(text.encode()).hexdigest()[:8]}"
                documents.append(Document(
                    id=doc_id,
                    content=text,
                    metadata=metadata,
                    embedding=embedding,
                    timestamp=datetime.now()
                ))
            
            # Create collection if it doesn't exist
            await self.vector_db.create_collection(collection_name, len(embeddings[0]))
            
            # Insert documents
            return await self.vector_db.insert_documents(collection_name, documents)
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False
    
    async def search_similar(self, collection_name: str, query_text: str, 
                           top_k: int = 10, filter_dict: Optional[Dict] = None) -> List[SearchResult]:
        """Search for similar documents"""
        if not self.vector_db:
            return []
        
        try:
            # Generate query embedding
            query_embeddings = await self.embedding_service.encode([query_text])
            query_vector = query_embeddings[0]
            
            # Search in vector database
            return await self.vector_db.search(collection_name, query_vector, top_k, filter_dict)
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def delete_documents(self, collection_name: str, document_ids: List[str]) -> bool:
        """Delete documents from vector database"""
        if not self.vector_db:
            return False
        
        return await self.vector_db.delete_documents(collection_name, document_ids)
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get collection information"""
        if not self.vector_db:
            return {"error": "Vector database not available"}
        
        return await self.vector_db.get_collection_info(collection_name)
    
    def is_available(self) -> bool:
        """Check if vector database is available"""
        return self.vector_db is not None

# Global vector database service
vector_db_service = VectorDBService()