#!/usr/bin/env python3
"""
Knowledge Base Module
Handles document storage, retrieval, and knowledge management for the AI therapist
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json
import os
from pathlib import Path
import hashlib
from dataclasses import dataclass, asdict
from enum import Enum
import pickle

# Heavy ML dependencies not available in minimal setup
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from sentence_transformers import SentenceTransformer
# import faiss

# Heavy text processing dependencies not available in minimal setup
# from textblob import TextBlob
# import spacy
# from transformers import pipeline

logger = logging.getLogger(__name__)

class DocumentType(Enum):
    GUIDANCE = "guidance"
    INSTRUCTION = "instruction"
    CONTEXT = "context"
    METRICS = "metrics"
    ANALYSIS_PATTERN = "analysis_pattern"
    REPORT_TEMPLATE = "report_template"
    CASE_STUDY = "case_study"
    REFERENCE = "reference"

@dataclass
class KnowledgeDocument:
    document_id: str
    title: str
    content: str
    document_type: str
    tags: List[str]
    metadata: Dict[str, Any]
    embedding: Optional[List[float]]  # Changed from np.ndarray to List[float] for minimal setup
    created_at: datetime
    updated_at: datetime
    version: int
    source_file: Optional[str] = None
    checksum: Optional[str] = None

@dataclass
class SearchResult:
    document: KnowledgeDocument
    relevance_score: float
    matched_sections: List[str]
    context: Dict[str, Any]

class KnowledgeBase:
    def __init__(self, storage_path: str = "./knowledge_base"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Document storage
        self.documents: Dict[str, KnowledgeDocument] = {}
        
        # Vector database for semantic search
        self.embedding_model = None
        self.vector_index = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        
        # Document categories
        self.document_categories = {
            DocumentType.GUIDANCE.value: [],
            DocumentType.INSTRUCTION.value: [],
            DocumentType.CONTEXT.value: [],
            DocumentType.METRICS.value: [],
            DocumentType.ANALYSIS_PATTERN.value: [],
            DocumentType.REPORT_TEMPLATE.value: [],
            DocumentType.CASE_STUDY.value: [],
            DocumentType.REFERENCE.value: []
        }
        
        # NLP components
        self.nlp = None
        self.summarizer = None
        
        # Initialize components
        self._initialize_components()
        
        # Note: Knowledge base loading will be done when needed
        # asyncio.create_task(self._load_knowledge_base())
    
    def _initialize_components(self):
        """
        Initialize NLP components and models
        """
        try:
            # Initialize sentence transformer for embeddings
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize TF-IDF vectorizer
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Initialize spaCy for text processing
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found, using basic text processing")
            
            # Initialize summarizer
            try:
                self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            except Exception as e:
                logger.warning(f"Could not initialize summarizer: {str(e)}")
            
            logger.info("Knowledge base components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing knowledge base components: {str(e)}")
    
    async def _load_knowledge_base(self):
        """
        Load existing knowledge base from storage
        """
        try:
            # Load documents metadata
            metadata_file = self.storage_path / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                for doc_id, doc_data in metadata.items():
                    # Load document content
                    content_file = self.storage_path / f"{doc_id}.txt"
                    if content_file.exists():
                        with open(content_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Load embedding if exists
                        embedding_file = self.storage_path / f"{doc_id}.npy"
                        embedding = None
                        if embedding_file.exists():
                            embedding = np.load(embedding_file)
                        
                        # Create document object
                        document = KnowledgeDocument(
                            document_id=doc_id,
                            title=doc_data['title'],
                            content=content,
                            document_type=doc_data['document_type'],
                            tags=doc_data['tags'],
                            metadata=doc_data['metadata'],
                            embedding=embedding,
                            created_at=datetime.fromisoformat(doc_data['created_at']),
                            updated_at=datetime.fromisoformat(doc_data['updated_at']),
                            version=doc_data['version'],
                            source_file=doc_data.get('source_file'),
                            checksum=doc_data.get('checksum')
                        )
                        
                        self.documents[doc_id] = document
                        self.document_categories[document.document_type].append(doc_id)
            
            # Rebuild vector indices
            await self._rebuild_vector_indices()
            
            logger.info(f"Loaded {len(self.documents)} documents from knowledge base")
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")
    
    async def add_document(self, title: str, content: str, document_type: str,
                          tags: List[str] = None, metadata: Dict[str, Any] = None,
                          source_file: str = None) -> str:
        """
        Add a new document to the knowledge base
        """
        try:
            # Generate document ID
            doc_id = self._generate_document_id(title, content)
            
            # Check if document already exists
            if doc_id in self.documents:
                logger.warning(f"Document {doc_id} already exists, updating instead")
                return await self.update_document(doc_id, title, content, document_type, tags, metadata)
            
            # Generate embedding
            embedding = await self._generate_embedding(content)
            
            # Calculate checksum
            checksum = hashlib.md5(content.encode()).hexdigest()
            
            # Create document
            document = KnowledgeDocument(
                document_id=doc_id,
                title=title,
                content=content,
                document_type=document_type,
                tags=tags or [],
                metadata=metadata or {},
                embedding=embedding,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                version=1,
                source_file=source_file,
                checksum=checksum
            )
            
            # Store document
            self.documents[doc_id] = document
            self.document_categories[document_type].append(doc_id)
            
            # Save to storage
            await self._save_document(document)
            
            # Update vector indices
            await self._update_vector_indices()
            
            logger.info(f"Added document {doc_id} to knowledge base")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            raise
    
    async def update_document(self, doc_id: str, title: str = None, content: str = None,
                            document_type: str = None, tags: List[str] = None,
                            metadata: Dict[str, Any] = None) -> bool:
        """
        Update an existing document
        """
        try:
            if doc_id not in self.documents:
                raise ValueError(f"Document {doc_id} not found")
            
            document = self.documents[doc_id]
            
            # Update fields if provided
            if title is not None:
                document.title = title
            if content is not None:
                document.content = content
                document.embedding = await self._generate_embedding(content)
                document.checksum = hashlib.md5(content.encode()).hexdigest()
            if document_type is not None:
                # Remove from old category
                if doc_id in self.document_categories[document.document_type]:
                    self.document_categories[document.document_type].remove(doc_id)
                # Add to new category
                document.document_type = document_type
                self.document_categories[document_type].append(doc_id)
            if tags is not None:
                document.tags = tags
            if metadata is not None:
                document.metadata.update(metadata)
            
            document.updated_at = datetime.now()
            document.version += 1
            
            # Save to storage
            await self._save_document(document)
            
            # Update vector indices
            await self._update_vector_indices()
            
            logger.info(f"Updated document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            return False
    
    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the knowledge base
        """
        try:
            if doc_id not in self.documents:
                return False
            
            document = self.documents[doc_id]
            
            # Remove from category
            if doc_id in self.document_categories[document.document_type]:
                self.document_categories[document.document_type].remove(doc_id)
            
            # Remove from storage
            content_file = self.storage_path / f"{doc_id}.txt"
            embedding_file = self.storage_path / f"{doc_id}.npy"
            
            if content_file.exists():
                content_file.unlink()
            if embedding_file.exists():
                embedding_file.unlink()
            
            # Remove from memory
            del self.documents[doc_id]
            
            # Update metadata file
            await self._save_metadata()
            
            # Update vector indices
            await self._update_vector_indices()
            
            logger.info(f"Deleted document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False
    
    async def search(self, query: str, document_types: List[str] = None,
                    tags: List[str] = None, limit: int = 10,
                    min_relevance: float = 0.1) -> List[SearchResult]:
        """
        Search for relevant documents
        """
        try:
            # Filter documents by type and tags
            candidate_docs = self._filter_documents(document_types, tags)
            
            if not candidate_docs:
                return []
            
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Calculate semantic similarity
            semantic_results = await self._semantic_search(query_embedding, candidate_docs, limit * 2)
            
            # Calculate keyword similarity
            keyword_results = await self._keyword_search(query, candidate_docs, limit * 2)
            
            # Combine and rank results
            combined_results = self._combine_search_results(semantic_results, keyword_results)
            
            # Filter by minimum relevance and limit
            filtered_results = [
                result for result in combined_results
                if result.relevance_score >= min_relevance
            ][:limit]
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []
    
    async def get_context_for_analysis(self, analysis_type: str, 
                                     conversation_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get relevant context documents for conversation analysis
        """
        try:
            context = {
                'guidance_documents': [],
                'analysis_patterns': [],
                'metrics': [],
                'instructions': []
            }
            
            # Search for relevant guidance documents
            guidance_query = f"relationship analysis {analysis_type} guidance"
            guidance_results = await self.search(
                query=guidance_query,
                document_types=[DocumentType.GUIDANCE.value],
                limit=5
            )
            context['guidance_documents'] = [asdict(result) for result in guidance_results]
            
            # Search for analysis patterns
            pattern_query = f"{analysis_type} analysis pattern methodology"
            pattern_results = await self.search(
                query=pattern_query,
                document_types=[DocumentType.ANALYSIS_PATTERN.value],
                limit=3
            )
            context['analysis_patterns'] = [asdict(result) for result in pattern_results]
            
            # Get metrics documents
            metrics_results = await self.search(
                query=f"{analysis_type} metrics evaluation",
                document_types=[DocumentType.METRICS.value],
                limit=3
            )
            context['metrics'] = [asdict(result) for result in metrics_results]
            
            # Get instruction documents
            instruction_results = await self.search(
                query=f"therapist instructions {analysis_type}",
                document_types=[DocumentType.INSTRUCTION.value],
                limit=3
            )
            context['instructions'] = [asdict(result) for result in instruction_results]
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting analysis context: {str(e)}")
            return {}
    
    async def get_report_template(self, report_type: str) -> Optional[str]:
        """
        Get a report template for generating analysis reports
        """
        try:
            template_results = await self.search(
                query=f"{report_type} report template",
                document_types=[DocumentType.REPORT_TEMPLATE.value],
                limit=1
            )
            
            if template_results:
                return template_results[0].document.content
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting report template: {str(e)}")
            return None
    
    async def get_similar_cases(self, conversation_summary: str, limit: int = 5) -> List[SearchResult]:
        """
        Find similar case studies for reference
        """
        try:
            case_results = await self.search(
                query=conversation_summary,
                document_types=[DocumentType.CASE_STUDY.value],
                limit=limit
            )
            
            return case_results
            
        except Exception as e:
            logger.error(f"Error finding similar cases: {str(e)}")
            return []
    
    def _generate_document_id(self, title: str, content: str) -> str:
        """
        Generate a unique document ID
        """
        combined = f"{title}_{content[:100]}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text
        """
        try:
            if self.embedding_model:
                embedding = self.embedding_model.encode(text)
                return embedding
            else:
                # Fallback to simple word count vector
                return np.random.rand(384)  # Dummy embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return np.random.rand(384)
    
    def _filter_documents(self, document_types: List[str] = None, 
                         tags: List[str] = None) -> List[str]:
        """
        Filter documents by type and tags
        """
        candidate_docs = []
        
        # Filter by document type
        if document_types:
            for doc_type in document_types:
                if doc_type in self.document_categories:
                    candidate_docs.extend(self.document_categories[doc_type])
        else:
            candidate_docs = list(self.documents.keys())
        
        # Filter by tags
        if tags:
            filtered_docs = []
            for doc_id in candidate_docs:
                document = self.documents[doc_id]
                if any(tag in document.tags for tag in tags):
                    filtered_docs.append(doc_id)
            candidate_docs = filtered_docs
        
        return candidate_docs
    
    async def _semantic_search(self, query_embedding: List[float], 
                             candidate_docs: List[str], limit: int) -> List[SearchResult]:
        """
        Perform semantic search using embeddings
        """
        results = []
        
        for doc_id in candidate_docs:
            document = self.documents[doc_id]
            if document.embedding is not None:
                # Calculate cosine similarity
                similarity = cosine_similarity(
                    query_embedding.reshape(1, -1),
                    document.embedding.reshape(1, -1)
                )[0][0]
                
                results.append(SearchResult(
                    document=document,
                    relevance_score=similarity,
                    matched_sections=[],
                    context={'search_type': 'semantic'}
                ))
        
        # Sort by relevance and limit
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]
    
    async def _keyword_search(self, query: str, candidate_docs: List[str], 
                            limit: int) -> List[SearchResult]:
        """
        Perform keyword-based search using TF-IDF
        """
        results = []
        
        try:
            # Prepare documents for TF-IDF
            doc_contents = []
            doc_ids = []
            
            for doc_id in candidate_docs:
                document = self.documents[doc_id]
                doc_contents.append(document.content)
                doc_ids.append(doc_id)
            
            if not doc_contents:
                return results
            
            # Fit TF-IDF vectorizer
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(doc_contents + [query])
            
            # Calculate similarity with query (last item)
            query_vector = tfidf_matrix[-1]
            doc_vectors = tfidf_matrix[:-1]
            
            similarities = cosine_similarity(query_vector, doc_vectors).flatten()
            
            # Create results
            for i, similarity in enumerate(similarities):
                if similarity > 0:
                    doc_id = doc_ids[i]
                    document = self.documents[doc_id]
                    
                    # Find matched sections (simplified)
                    matched_sections = self._find_matched_sections(query, document.content)
                    
                    results.append(SearchResult(
                        document=document,
                        relevance_score=similarity,
                        matched_sections=matched_sections,
                        context={'search_type': 'keyword'}
                    ))
            
            # Sort by relevance and limit
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error in keyword search: {str(e)}")
            return results
    
    def _find_matched_sections(self, query: str, content: str, max_sections: int = 3) -> List[str]:
        """
        Find sections of content that match the query
        """
        query_words = set(query.lower().split())
        sentences = content.split('.')
        
        matched_sections = []
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            if query_words & sentence_words:  # If there's any overlap
                matched_sections.append(sentence.strip())
                if len(matched_sections) >= max_sections:
                    break
        
        return matched_sections
    
    def _combine_search_results(self, semantic_results: List[SearchResult],
                              keyword_results: List[SearchResult]) -> List[SearchResult]:
        """
        Combine and rank semantic and keyword search results
        """
        # Create a dictionary to combine results by document ID
        combined = {}
        
        # Add semantic results
        for result in semantic_results:
            doc_id = result.document.document_id
            combined[doc_id] = result
            combined[doc_id].context['semantic_score'] = result.relevance_score
        
        # Add keyword results
        for result in keyword_results:
            doc_id = result.document.document_id
            if doc_id in combined:
                # Combine scores (weighted average)
                semantic_score = combined[doc_id].context.get('semantic_score', 0)
                keyword_score = result.relevance_score
                combined_score = (semantic_score * 0.6) + (keyword_score * 0.4)
                combined[doc_id].relevance_score = combined_score
                combined[doc_id].context['keyword_score'] = keyword_score
                combined[doc_id].matched_sections.extend(result.matched_sections)
            else:
                combined[doc_id] = result
                combined[doc_id].context['keyword_score'] = result.relevance_score
        
        # Convert back to list and sort
        results = list(combined.values())
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results
    
    async def _save_document(self, document: KnowledgeDocument):
        """
        Save document to storage
        """
        try:
            # Save content
            content_file = self.storage_path / f"{document.document_id}.txt"
            with open(content_file, 'w', encoding='utf-8') as f:
                f.write(document.content)
            
            # Save embedding
            if document.embedding is not None:
                embedding_file = self.storage_path / f"{document.document_id}.npy"
                np.save(embedding_file, document.embedding)
            
            # Update metadata
            await self._save_metadata()
            
        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            raise
    
    async def _save_metadata(self):
        """
        Save documents metadata to file
        """
        try:
            metadata = {}
            for doc_id, document in self.documents.items():
                metadata[doc_id] = {
                    'title': document.title,
                    'document_type': document.document_type,
                    'tags': document.tags,
                    'metadata': document.metadata,
                    'created_at': document.created_at.isoformat(),
                    'updated_at': document.updated_at.isoformat(),
                    'version': document.version,
                    'source_file': document.source_file,
                    'checksum': document.checksum
                }
            
            metadata_file = self.storage_path / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving metadata: {str(e)}")
    
    async def _rebuild_vector_indices(self):
        """
        Rebuild vector indices for all documents
        """
        try:
            if not self.documents:
                return
            
            # Prepare documents for TF-IDF
            doc_contents = [doc.content for doc in self.documents.values()]
            
            if doc_contents:
                self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(doc_contents)
            
            logger.info("Vector indices rebuilt successfully")
            
        except Exception as e:
            logger.error(f"Error rebuilding vector indices: {str(e)}")
    
    async def _update_vector_indices(self):
        """
        Update vector indices after document changes
        """
        await self._rebuild_vector_indices()
    
    async def summarize_document(self, doc_id: str, max_length: int = 150) -> Optional[str]:
        """
        Generate a summary of a document
        """
        try:
            if doc_id not in self.documents:
                return None
            
            document = self.documents[doc_id]
            content = document.content
            
            if self.summarizer and len(content) > 200:
                # Use transformer-based summarization
                summary = self.summarizer(content, max_length=max_length, min_length=30, do_sample=False)
                return summary[0]['summary_text']
            else:
                # Fallback to simple truncation
                sentences = content.split('.')
                summary = '. '.join(sentences[:3]) + '.' if len(sentences) > 3 else content
                return summary[:max_length] + '...' if len(summary) > max_length else summary
                
        except Exception as e:
            logger.error(f"Error summarizing document: {str(e)}")
            return None
    
    def get_document_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base
        """
        stats = {
            'total_documents': len(self.documents),
            'documents_by_type': {},
            'total_content_length': 0,
            'average_content_length': 0,
            'most_recent_update': None,
            'oldest_document': None
        }
        
        if not self.documents:
            return stats
        
        # Calculate statistics
        content_lengths = []
        update_times = []
        
        for doc_type in DocumentType:
            stats['documents_by_type'][doc_type.value] = len(self.document_categories[doc_type.value])
        
        for document in self.documents.values():
            content_lengths.append(len(document.content))
            update_times.append(document.updated_at)
        
        stats['total_content_length'] = sum(content_lengths)
        stats['average_content_length'] = sum(content_lengths) / len(content_lengths)
        stats['most_recent_update'] = max(update_times).isoformat()
        stats['oldest_document'] = min(update_times).isoformat()
        
        return stats
    
    async def export_knowledge_base(self, export_path: str) -> bool:
        """
        Export the entire knowledge base to a file
        """
        try:
            export_data = {
                'metadata': {
                    'export_date': datetime.now().isoformat(),
                    'total_documents': len(self.documents),
                    'version': '1.0'
                },
                'documents': {}
            }
            
            for doc_id, document in self.documents.items():
                export_data['documents'][doc_id] = {
                    'title': document.title,
                    'content': document.content,
                    'document_type': document.document_type,
                    'tags': document.tags,
                    'metadata': document.metadata,
                    'created_at': document.created_at.isoformat(),
                    'updated_at': document.updated_at.isoformat(),
                    'version': document.version,
                    'source_file': document.source_file,
                    'checksum': document.checksum
                }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Knowledge base exported to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting knowledge base: {str(e)}")
            return False
    
    async def import_knowledge_base(self, import_path: str, merge: bool = True) -> bool:
        """
        Import knowledge base from a file
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if not merge:
                # Clear existing knowledge base
                self.documents.clear()
                for doc_type in self.document_categories:
                    self.document_categories[doc_type].clear()
            
            # Import documents
            imported_count = 0
            for doc_id, doc_data in import_data.get('documents', {}).items():
                if doc_id not in self.documents or not merge:
                    # Generate embedding for imported content
                    embedding = await self._generate_embedding(doc_data['content'])
                    
                    document = KnowledgeDocument(
                        document_id=doc_id,
                        title=doc_data['title'],
                        content=doc_data['content'],
                        document_type=doc_data['document_type'],
                        tags=doc_data['tags'],
                        metadata=doc_data['metadata'],
                        embedding=embedding,
                        created_at=datetime.fromisoformat(doc_data['created_at']),
                        updated_at=datetime.fromisoformat(doc_data['updated_at']),
                        version=doc_data['version'],
                        source_file=doc_data.get('source_file'),
                        checksum=doc_data.get('checksum')
                    )
                    
                    self.documents[doc_id] = document
                    self.document_categories[document.document_type].append(doc_id)
                    imported_count += 1
            
            # Save imported documents
            await self._save_metadata()
            for document in self.documents.values():
                await self._save_document(document)
            
            # Rebuild indices
            await self._rebuild_vector_indices()
            
            logger.info(f"Imported {imported_count} documents from {import_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing knowledge base: {str(e)}")
            return False