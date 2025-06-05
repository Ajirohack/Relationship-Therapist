#!/usr/bin/env python3
"""
Data Processor Module
Handles various input formats: screenshots, text, PDF, audio, zipped files, folders
"""

import asyncio
import logging
import os
import zipfile
import tempfile
import io
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json
import base64
from pathlib import Path
import mimetypes
from dataclasses import dataclass
from enum import Enum

# Image processing
from PIL import Image

# PDF processing
from PyPDF2 import PdfReader

# Heavy dependencies not available in minimal setup
# import pytesseract, cv2, speech_recognition, pydub, librosa, numpy, fitz, chardet, textblob

logger = logging.getLogger(__name__)

@dataclass
class ProcessedData:
    content: str
    metadata: Dict[str, Any]
    source_type: str
    confidence: float
    timestamp: datetime
    file_path: Optional[str] = None

class DataProcessor:
    def __init__(self):
        self.supported_image_formats = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
        self.supported_audio_formats = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac'}
        self.supported_text_formats = {'.txt', '.md', '.csv', '.json', '.log'}
        self.supported_document_formats = {'.pdf', '.docx', '.doc'}
        
        # Note: Heavy dependencies not available in minimal setup
        # self.recognizer = sr.Recognizer()
        
        # Configure OCR (disabled in minimal setup)
        # self._configure_ocr()
    
    def _configure_ocr(self):
        """
        Configure OCR settings for better text extraction (disabled in minimal setup)
        """
        logger.warning("OCR dependencies not available in minimal setup")
    
    async def process_input(self, input_data: Union[str, bytes, Dict[str, Any]], 
                          input_type: str = "auto") -> List[ProcessedData]:
        """
        Main processing function that handles various input types
        """
        try:
            if input_type == "auto":
                input_type = self._detect_input_type(input_data)
            
            logger.info(f"Processing input of type: {input_type}")
            
            if input_type == "file_path":
                return await self._process_file_path(input_data)
            elif input_type == "folder_path":
                return await self._process_folder(input_data)
            elif input_type == "zip_file":
                return await self._process_zip_file(input_data)
            elif input_type == "base64_image":
                return await self._process_base64_image(input_data)
            elif input_type == "text":
                return await self._process_text(input_data)
            elif input_type == "json":
                return await self._process_json(input_data)
            else:
                raise ValueError(f"Unsupported input type: {input_type}")
                
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            raise
    
    def _detect_input_type(self, input_data: Union[str, bytes, Dict[str, Any]]) -> str:
        """
        Automatically detect the type of input data
        """
        if isinstance(input_data, dict):
            if 'conversations' in input_data or 'messages' in input_data:
                return "json"
            elif 'file_path' in input_data:
                return "file_path"
            elif 'base64' in input_data:
                return "base64_image"
        
        elif isinstance(input_data, str):
            if os.path.isfile(input_data):
                return "file_path"
            elif os.path.isdir(input_data):
                return "folder_path"
            elif input_data.endswith('.zip'):
                return "zip_file"
            elif input_data.startswith('data:image') or len(input_data) > 100:
                return "base64_image"
            else:
                return "text"
        
        elif isinstance(input_data, bytes):
            # Try to detect if it's an image or other binary data
            try:
                Image.open(io.BytesIO(input_data))
                return "image_bytes"
            except:
                return "binary_data"
        
        return "unknown"
    
    async def _process_file_path(self, file_path: str) -> List[ProcessedData]:
        """
        Process a single file based on its extension
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in self.supported_image_formats:
            return await self._process_image_file(file_path)
        elif file_ext in self.supported_audio_formats:
            return await self._process_audio_file(file_path)
        elif file_ext in self.supported_text_formats:
            return await self._process_text_file(file_path)
        elif file_ext == '.pdf':
            return await self._process_pdf_file(file_path)
        elif file_ext == '.zip':
            return await self._process_zip_file(file_path)
        else:
            # Try to process as text file
            try:
                return await self._process_text_file(file_path)
            except Exception as e:
                logger.warning(f"Could not process file {file_path}: {str(e)}")
                return []
    
    async def _process_folder(self, folder_path: str) -> List[ProcessedData]:
        """
        Process all supported files in a folder recursively
        """
        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"Directory not found: {folder_path}")
        
        all_processed_data = []
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    processed_data = await self._process_file_path(file_path)
                    all_processed_data.extend(processed_data)
                except Exception as e:
                    logger.warning(f"Failed to process file {file_path}: {str(e)}")
                    continue
        
        return all_processed_data
    
    async def _process_zip_file(self, zip_path: str) -> List[ProcessedData]:
        """
        Extract and process files from a ZIP archive
        """
        all_processed_data = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Process extracted files
                all_processed_data = await self._process_folder(temp_dir)
                
            except zipfile.BadZipFile:
                logger.error(f"Invalid ZIP file: {zip_path}")
                raise
        
        return all_processed_data
    
    async def _process_image_file(self, image_path: str) -> List[ProcessedData]:
        """
        Extract text from image using OCR (minimal setup - OCR not available)
        """
        try:
            # Extract metadata only since OCR is not available
            metadata = self._extract_image_metadata(image_path)
            
            # Return placeholder content since OCR dependencies are not available
            extracted_text = f"[Image content - OCR not available in minimal setup. File: {os.path.basename(image_path)}]"
            
            return [ProcessedData(
                content=extracted_text,
                metadata=metadata,
                source_type="image_placeholder",
                confidence=0.1,
                timestamp=datetime.now(),
                file_path=image_path
            )]
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            return []
    
    def _preprocess_image_for_ocr(self, image):
        """
        Preprocess image to improve OCR accuracy (disabled in minimal setup)
        """
        logger.warning("Image preprocessing not available - OCR dependencies missing")
        return None
    
    def _extract_image_metadata(self, image_path: str) -> Dict[str, Any]:
        """
        Extract metadata from image file
        """
        try:
            with Image.open(image_path) as img:
                metadata = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'filename': os.path.basename(image_path),
                    'file_size': os.path.getsize(image_path)
                }
                
                # Extract EXIF data if available
                if hasattr(img, '_getexif') and img._getexif():
                    exif_data = img._getexif()
                    if exif_data:
                        metadata['exif'] = {k: v for k, v in exif_data.items() if isinstance(v, (str, int, float))}
                
                return metadata
        except Exception as e:
            logger.warning(f"Could not extract image metadata: {str(e)}")
            return {'filename': os.path.basename(image_path)}
    
    async def _process_audio_file(self, audio_path: str) -> List[ProcessedData]:
        """
        Convert audio to text using speech recognition (minimal setup - not available)
        """
        try:
            # Extract basic metadata only since speech recognition is not available
            metadata = {
                'filename': os.path.basename(audio_path),
                'file_size': os.path.getsize(audio_path)
            }
            
            # Return placeholder content since speech recognition dependencies are not available
            text = f"[Audio content - Speech recognition not available in minimal setup. File: {os.path.basename(audio_path)}]"
            
            return [ProcessedData(
                content=text,
                metadata=metadata,
                source_type="audio_placeholder",
                confidence=0.1,
                timestamp=datetime.now(),
                file_path=audio_path
            )]
            
        except Exception as e:
            logger.error(f"Error processing audio {audio_path}: {str(e)}")
            return []
    
    async def _convert_to_wav(self, audio_path: str) -> str:
        """
        Convert audio file to WAV format for speech recognition (disabled in minimal setup)
        """
        logger.warning("Audio conversion not available - audio processing dependencies missing")
        return audio_path
    
    def _extract_audio_metadata(self, audio_path: str) -> Dict[str, Any]:
        """
        Extract metadata from audio file (minimal setup - limited metadata)
        """
        try:
            # Basic file metadata only since audio processing libraries are not available
            metadata = {
                'filename': os.path.basename(audio_path),
                'file_size': os.path.getsize(audio_path)
            }
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Could not extract audio metadata: {str(e)}")
            return {'filename': os.path.basename(audio_path)}
    
    async def _process_text_file(self, text_path: str) -> List[ProcessedData]:
        """
        Process text files
        """
        try:
            # Try to detect encoding (chardet not available in minimal setup)
            encoding = 'utf-8'
            encoding_confidence = 1.0
            
            try:
                # Try UTF-8 first
                with open(text_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Fallback to latin-1 if UTF-8 fails
                try:
                    with open(text_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                    encoding = 'latin-1'
                    encoding_confidence = 0.8
                except Exception:
                    # Last resort - read as binary and decode with errors='ignore'
                    with open(text_path, 'rb') as f:
                        raw_data = f.read()
                    content = raw_data.decode('utf-8', errors='ignore')
                    encoding = 'utf-8-with-errors'
                    encoding_confidence = 0.5
            
            # Extract metadata
            metadata = {
                'encoding': encoding,
                'encoding_confidence': encoding_confidence,
                'filename': os.path.basename(text_path),
                'file_size': os.path.getsize(text_path),
                'line_count': content.count('\n') + 1,
                'word_count': len(content.split())
            }
            
            return [ProcessedData(
                content=content,
                metadata=metadata,
                source_type="text_file",
                confidence=1.0,
                timestamp=datetime.now(),
                file_path=text_path
            )]
            
        except Exception as e:
            logger.error(f"Error processing text file {text_path}: {str(e)}")
            return []
    
    async def _process_pdf_file(self, pdf_path: str) -> List[ProcessedData]:
        """
        Extract text from PDF files
        """
        try:
            extracted_texts = []
            extraction_method = 'PyPDF2'
            
            # Use PyPDF2 (PyMuPDF/fitz not available in minimal setup)
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PdfReader(file)
                    full_text = ""
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        text = page.extract_text()
                        full_text += f"\n--- Page {page_num + 1} ---\n{text}"
                    
                    if full_text.strip():
                        extracted_texts.append(full_text)
                        
            except Exception as e:
                logger.error(f"PyPDF2 extraction failed: {str(e)}")
                return []
            
            # Extract metadata
            metadata = {
                'filename': os.path.basename(pdf_path),
                'file_size': os.path.getsize(pdf_path),
                'extraction_method': extraction_method
            }
            
            if not extracted_texts:
                logger.warning(f"No text extracted from PDF: {pdf_path}")
                return []
            
            return [ProcessedData(
                content=text,
                metadata=metadata,
                source_type="pdf_extraction",
                confidence=0.9,
                timestamp=datetime.now(),
                file_path=pdf_path
            ) for text in extracted_texts]
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            return []
    
    async def _process_base64_image(self, base64_data: str) -> List[ProcessedData]:
        """
        Process base64 encoded image
        """
        try:
            # Decode base64 data
            if base64_data.startswith('data:image'):
                # Remove data URL prefix
                base64_data = base64_data.split(',')[1]
            
            image_data = base64.b64decode(base64_data)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_file.write(image_data)
                temp_path = temp_file.name
            
            try:
                # Process the temporary image file
                result = await self._process_image_file(temp_path)
                
                # Update metadata to indicate base64 source
                for item in result:
                    item.metadata['source'] = 'base64_image'
                    item.file_path = None
                
                return result
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception as e:
            logger.error(f"Error processing base64 image: {str(e)}")
            return []
    
    async def _process_text(self, text_content: str) -> List[ProcessedData]:
        """
        Process plain text content
        """
        try:
            # Basic text analysis (TextBlob not available in minimal setup)
            sentences = text_content.split('.') if text_content else []
            
            metadata = {
                'word_count': len(text_content.split()),
                'character_count': len(text_content),
                'sentence_count': len([s for s in sentences if s.strip()]),
                'language': 'unknown'  # Language detection not available in minimal setup
            }
            
            return [ProcessedData(
                content=text_content,
                metadata=metadata,
                source_type="plain_text",
                confidence=1.0,
                timestamp=datetime.now()
            )]
            
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            return []
    
    async def _process_json(self, json_data: Union[str, Dict[str, Any]]) -> List[ProcessedData]:
        """
        Process JSON conversation data
        """
        try:
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
            
            processed_items = []
            
            # Handle different JSON structures
            if 'conversations' in data:
                conversations = data['conversations']
            elif 'messages' in data:
                conversations = data['messages']
            elif isinstance(data, list):
                conversations = data
            else:
                # Single conversation object
                conversations = [data]
            
            for i, conv in enumerate(conversations):
                # Extract text content
                text_content = ""
                if isinstance(conv, dict):
                    text_content = conv.get('text', conv.get('message', conv.get('content', '')))
                elif isinstance(conv, str):
                    text_content = conv
                
                if text_content:
                    metadata = {
                        'conversation_index': i,
                        'original_data': conv if isinstance(conv, dict) else {'text': conv},
                        'timestamp': conv.get('timestamp') if isinstance(conv, dict) else None,
                        'sender': conv.get('sender') if isinstance(conv, dict) else None,
                        'platform': conv.get('platform') if isinstance(conv, dict) else None
                    }
                    
                    processed_items.append(ProcessedData(
                        content=text_content,
                        metadata=metadata,
                        source_type="json_conversation",
                        confidence=1.0,
                        timestamp=datetime.now()
                    ))
            
            return processed_items
            
        except Exception as e:
            logger.error(f"Error processing JSON: {str(e)}")
            return []
    
    async def extract_conversations_from_processed_data(self, processed_data: List[ProcessedData]) -> List[Dict[str, Any]]:
        """
        Convert processed data into conversation format for analysis
        """
        conversations = []
        
        for data in processed_data:
            # Parse conversation from different sources
            if data.source_type == "json_conversation":
                # Already in conversation format
                conv_data = data.metadata.get('original_data', {})
                conv_data['text'] = data.content
                conversations.append(conv_data)
                
            else:
                # Extract conversations from text content
                extracted_convs = await self._extract_conversations_from_text(data.content, data.metadata)
                conversations.extend(extracted_convs)
        
        return conversations
    
    async def _extract_conversations_from_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract individual conversations from text content
        """
        conversations = []
        
        # Try to identify conversation patterns
        lines = text.split('\n')
        current_conversation = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for conversation indicators
            if self._is_conversation_line(line):
                if current_conversation:
                    conversations.append({
                        'text': current_conversation.strip(),
                        'timestamp': datetime.now().isoformat(),
                        'sender': 'unknown',
                        'source_metadata': metadata
                    })
                    current_conversation = ""
                
                current_conversation = line
            else:
                current_conversation += " " + line
        
        # Add the last conversation
        if current_conversation:
            conversations.append({
                'text': current_conversation.strip(),
                'timestamp': datetime.now().isoformat(),
                'sender': 'unknown',
                'source_metadata': metadata
            })
        
        # If no conversation patterns found, treat entire text as one conversation
        if not conversations and text.strip():
            conversations.append({
                'text': text.strip(),
                'timestamp': datetime.now().isoformat(),
                'sender': 'unknown',
                'source_metadata': metadata
            })
        
        return conversations
    
    def _is_conversation_line(self, line: str) -> bool:
        """
        Determine if a line represents the start of a conversation
        """
        # Common conversation indicators
        conversation_indicators = [
            r'^\d{1,2}[:/]\d{1,2}',  # Time stamps
            r'^\[\d{1,2}:\d{1,2}',   # [Time] format
            r'^\w+:',                # Name: format
            r'^You:',                # You: format
            r'^Me:',                 # Me: format
            r'^\d{4}-\d{2}-\d{2}',   # Date format
        ]
        
        import re
        for pattern in conversation_indicators:
            if re.match(pattern, line):
                return True
        
        return False
    
    async def process_batch(self, batch_inputs: List[Dict[str, Any]]) -> Dict[str, List[ProcessedData]]:
        """
        Process multiple inputs in batch
        """
        results = {}
        
        for i, input_item in enumerate(batch_inputs):
            try:
                input_data = input_item.get('data')
                input_type = input_item.get('type', 'auto')
                input_id = input_item.get('id', f'batch_item_{i}')
                
                processed_data = await self.process_input(input_data, input_type)
                results[input_id] = processed_data
                
            except Exception as e:
                logger.error(f"Error processing batch item {i}: {str(e)}")
                results[f'batch_item_{i}'] = []
        
        return results
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """
        Return list of supported file formats
        """
        return {
            'images': list(self.supported_image_formats),
            'audio': list(self.supported_audio_formats),
            'text': list(self.supported_text_formats),
            'documents': list(self.supported_document_formats),
            'archives': ['.zip'],
            'other': ['folders', 'base64_images', 'json_data']
        }
    
    async def validate_input(self, input_data: Union[str, bytes, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate input data before processing
        """
        validation_result = {
            'valid': True,
            'input_type': 'unknown',
            'estimated_size': 0,
            'warnings': [],
            'errors': []
        }
        
        try:
            # Detect input type
            input_type = self._detect_input_type(input_data)
            validation_result['input_type'] = input_type
            
            # Validate based on type
            if input_type == "file_path":
                if not os.path.exists(input_data):
                    validation_result['errors'].append(f"File not found: {input_data}")
                    validation_result['valid'] = False
                else:
                    file_size = os.path.getsize(input_data)
                    validation_result['estimated_size'] = file_size
                    
                    # Check file size limits
                    if file_size > 100 * 1024 * 1024:  # 100MB
                        validation_result['warnings'].append("Large file detected, processing may take time")
            
            elif input_type == "folder_path":
                if not os.path.isdir(input_data):
                    validation_result['errors'].append(f"Directory not found: {input_data}")
                    validation_result['valid'] = False
                else:
                    # Estimate folder size
                    total_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                                   for dirpath, dirnames, filenames in os.walk(input_data)
                                   for filename in filenames)
                    validation_result['estimated_size'] = total_size
            
            elif input_type == "base64_image":
                try:
                    if input_data.startswith('data:image'):
                        base64_data = input_data.split(',')[1]
                    else:
                        base64_data = input_data
                    
                    decoded_size = len(base64.b64decode(base64_data))
                    validation_result['estimated_size'] = decoded_size
                except Exception as e:
                    validation_result['errors'].append(f"Invalid base64 image data: {str(e)}")
                    validation_result['valid'] = False
            
        except Exception as e:
            validation_result['errors'].append(f"Validation error: {str(e)}")
            validation_result['valid'] = False
        
        return validation_result