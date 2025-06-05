#!/usr/bin/env python3
"""
MCP Server Module
Handles Model Context Protocol connectivity for the relationship therapist system
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime
import json
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from pathlib import Path

# MCP Protocol - commented out for minimal setup
# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client
# from mcp.types import (
#     CallToolRequest, CallToolResult,
#     ListToolsRequest, ListToolsResult,
#     GetPromptRequest, GetPromptResult,
#     ListPromptsRequest, ListPromptsResult,
#     Tool, Prompt, TextContent, ImageContent
# )

# Placeholder classes for MCP types when not available
class Tool:
    def __init__(self, name, description, inputSchema):
        self.name = name
        self.description = description
        self.inputSchema = inputSchema

class Prompt:
    def __init__(self, name, description, arguments):
        self.name = name
        self.description = description
        self.arguments = arguments

class TextContent:
    def __init__(self, type, text):
        self.type = type
        self.text = text

class CallToolResult:
    def __init__(self, content, isError=False):
        self.content = content
        self.isError = isError

class GetPromptResult:
    def __init__(self, description, messages):
        self.description = description
        self.messages = messages

class ListToolsResult:
    def __init__(self, tools):
        self.tools = tools

class ListPromptsResult:
    def __init__(self, prompts):
        self.prompts = prompts

class ClientSession:
    def __init__(self):
        pass

class CallToolRequest:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class GetPromptRequest:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class ListToolsRequest:
    def __init__(self):
        pass

class ListPromptsRequest:
    def __init__(self):
        pass

# FastAPI and WebSocket
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class MCPMessageType(Enum):
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    PROMPT_REQUEST = "prompt_request"
    PROMPT_RESPONSE = "prompt_response"
    STATUS_UPDATE = "status_update"
    ERROR = "error"

@dataclass
class MCPMessage:
    message_id: str
    message_type: str
    timestamp: datetime
    data: Dict[str, Any]
    session_id: Optional[str] = None
    user_id: Optional[str] = None

@dataclass
class MCPSession:
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    websocket: Optional[WebSocket]
    client_session: Optional[ClientSession]
    active_tools: List[str]
    context: Dict[str, Any]

class MCPServer:
    def __init__(self, conversation_analyzer=None, data_processor=None, 
                 real_time_monitor=None, knowledge_base=None, ai_therapist=None):
        self.conversation_analyzer = conversation_analyzer
        self.data_processor = data_processor
        self.real_time_monitor = real_time_monitor
        self.knowledge_base = knowledge_base
        self.ai_therapist = ai_therapist
        
        # MCP Sessions
        self.sessions: Dict[str, MCPSession] = {}
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Available tools and prompts
        self.available_tools = self._initialize_tools()
        self.available_prompts = self._initialize_prompts()
        
        # Message handlers
        self.message_handlers = {
            MCPMessageType.TOOL_CALL.value: self._handle_tool_call,
            MCPMessageType.PROMPT_REQUEST.value: self._handle_prompt_request,
            MCPMessageType.STATUS_UPDATE.value: self._handle_status_update
        }
        
        logger.info("MCP Server initialized")
    
    def _initialize_tools(self) -> List[Tool]:
        """
        Initialize available MCP tools
        """
        tools = [
            Tool(
                name="analyze_conversation",
                description="Analyze conversation history and provide insights",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "conversation_data": {
                            "type": "string",
                            "description": "Conversation data to analyze"
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["comprehensive", "emotional", "communication_style", "compatibility", "relationship_stage"],
                            "description": "Type of analysis to perform"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User ID for context"
                        }
                    },
                    "required": ["conversation_data", "analysis_type"]
                }
            ),
            Tool(
                name="process_conversation_file",
                description="Process uploaded conversation files (images, audio, text, PDF, etc.)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_data": {
                            "type": "string",
                            "description": "Base64 encoded file data or file path"
                        },
                        "file_type": {
                            "type": "string",
                            "enum": ["image", "audio", "text", "pdf", "zip", "folder"],
                            "description": "Type of file to process"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User ID for context"
                        }
                    },
                    "required": ["file_data", "file_type"]
                }
            ),
            Tool(
                name="get_real_time_recommendation",
                description="Get real-time recommendations for ongoing conversations",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "current_message": {
                            "type": "string",
                            "description": "Current message in the conversation"
                        },
                        "conversation_context": {
                            "type": "object",
                            "description": "Context of the ongoing conversation"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User ID for personalized recommendations"
                        }
                    },
                    "required": ["current_message", "user_id"]
                }
            ),
            Tool(
                name="start_monitoring_session",
                description="Start monitoring a social media platform for real-time conversation analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "enum": ["whatsapp", "telegram", "discord", "instagram", "facebook", "twitter"],
                            "description": "Social media platform to monitor"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User ID for the monitoring session"
                        },
                        "monitoring_config": {
                            "type": "object",
                            "description": "Configuration for monitoring session"
                        }
                    },
                    "required": ["platform", "user_id"]
                }
            ),
            Tool(
                name="search_knowledge_base",
                description="Search the knowledge base for relevant guidance and context",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for knowledge base"
                        },
                        "document_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Types of documents to search"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return"
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="generate_analysis_report",
                description="Generate a comprehensive analysis report",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID for the report"
                        },
                        "report_type": {
                            "type": "string",
                            "enum": ["relationship_health", "communication_patterns", "compatibility_analysis", "progress_report"],
                            "description": "Type of report to generate"
                        },
                        "time_period": {
                            "type": "string",
                            "description": "Time period for the report (e.g., 'last_week', 'last_month')"
                        }
                    },
                    "required": ["user_id", "report_type"]
                }
            ),
            Tool(
                name="update_user_profile",
                description="Update user profile and preferences",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID to update"
                        },
                        "profile_data": {
                            "type": "object",
                            "description": "Profile data to update"
                        }
                    },
                    "required": ["user_id", "profile_data"]
                }
            ),
            Tool(
                name="add_knowledge_document",
                description="Add a new document to the knowledge base",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Document title"
                        },
                        "content": {
                            "type": "string",
                            "description": "Document content"
                        },
                        "document_type": {
                            "type": "string",
                            "enum": ["guidance", "instruction", "context", "metrics", "analysis_pattern", "report_template", "case_study", "reference"],
                            "description": "Type of document"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Document tags"
                        }
                    },
                    "required": ["title", "content", "document_type"]
                }
            )
        ]
        
        return tools
    
    def _initialize_prompts(self) -> List[Prompt]:
        """
        Initialize available MCP prompts
        """
        prompts = [
            Prompt(
                name="relationship_analysis_prompt",
                description="Prompt for analyzing relationship dynamics",
                arguments=[
                    {
                        "name": "conversation_data",
                        "description": "The conversation data to analyze",
                        "required": True
                    },
                    {
                        "name": "analysis_focus",
                        "description": "Specific aspect to focus on in the analysis",
                        "required": False
                    }
                ]
            ),
            Prompt(
                name="real_time_recommendation_prompt",
                description="Prompt for generating real-time conversation recommendations",
                arguments=[
                    {
                        "name": "current_context",
                        "description": "Current conversation context",
                        "required": True
                    },
                    {
                        "name": "user_profile",
                        "description": "User profile and preferences",
                        "required": False
                    }
                ]
            ),
            Prompt(
                name="communication_coaching_prompt",
                description="Prompt for providing communication coaching advice",
                arguments=[
                    {
                        "name": "communication_issue",
                        "description": "Specific communication issue to address",
                        "required": True
                    },
                    {
                        "name": "relationship_stage",
                        "description": "Current stage of the relationship",
                        "required": False
                    }
                ]
            ),
            Prompt(
                name="conflict_resolution_prompt",
                description="Prompt for conflict resolution guidance",
                arguments=[
                    {
                        "name": "conflict_description",
                        "description": "Description of the conflict situation",
                        "required": True
                    },
                    {
                        "name": "parties_involved",
                        "description": "Information about parties involved",
                        "required": False
                    }
                ]
            )
        ]
        
        return prompts
    
    async def create_session(self, user_id: str, websocket: WebSocket = None) -> str:
        """
        Create a new MCP session
        """
        try:
            session_id = str(uuid.uuid4())
            
            session = MCPSession(
                session_id=session_id,
                user_id=user_id,
                created_at=datetime.now(),
                last_activity=datetime.now(),
                websocket=websocket,
                client_session=None,
                active_tools=[],
                context={}
            )
            
            self.sessions[session_id] = session
            
            if websocket:
                self.active_connections[session_id] = websocket
            
            logger.info(f"Created MCP session {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating MCP session: {str(e)}")
            raise
    
    async def close_session(self, session_id: str):
        """
        Close an MCP session
        """
        try:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                
                # Close client session if exists
                if session.client_session:
                    await session.client_session.close()
                
                # Remove from active connections
                if session_id in self.active_connections:
                    del self.active_connections[session_id]
                
                # Remove session
                del self.sessions[session_id]
                
                logger.info(f"Closed MCP session {session_id}")
            
        except Exception as e:
            logger.error(f"Error closing MCP session: {str(e)}")
    
    async def handle_websocket_connection(self, websocket: WebSocket, user_id: str):
        """
        Handle WebSocket connection for MCP communication
        """
        session_id = None
        try:
            await websocket.accept()
            session_id = await self.create_session(user_id, websocket)
            
            # Send initial connection message
            await self.send_message(session_id, {
                "type": "connection_established",
                "session_id": session_id,
                "available_tools": [tool.name for tool in self.available_tools],
                "available_prompts": [prompt.name for prompt in self.available_prompts]
            })
            
            # Listen for messages
            while True:
                try:
                    data = await websocket.receive_text()
                    message_data = json.loads(data)
                    
                    # Process message
                    await self.process_message(session_id, message_data)
                    
                except WebSocketDisconnect:
                    logger.info(f"WebSocket disconnected for session {session_id}")
                    break
                except json.JSONDecodeError:
                    await self.send_error(session_id, "Invalid JSON format")
                except Exception as e:
                    logger.error(f"Error processing WebSocket message: {str(e)}")
                    await self.send_error(session_id, f"Error processing message: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error in WebSocket connection: {str(e)}")
        
        finally:
            if session_id:
                await self.close_session(session_id)
    
    async def process_message(self, session_id: str, message_data: Dict[str, Any]):
        """
        Process incoming MCP message
        """
        try:
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            session.last_activity = datetime.now()
            
            # Create MCP message
            message = MCPMessage(
                message_id=message_data.get('message_id', str(uuid.uuid4())),
                message_type=message_data.get('type', 'unknown'),
                timestamp=datetime.now(),
                data=message_data,
                session_id=session_id,
                user_id=session.user_id
            )
            
            # Route message to appropriate handler
            if message.message_type in self.message_handlers:
                await self.message_handlers[message.message_type](session, message)
            else:
                await self.send_error(session_id, f"Unknown message type: {message.message_type}")
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.send_error(session_id, f"Error processing message: {str(e)}")
    
    async def _handle_tool_call(self, session: MCPSession, message: MCPMessage):
        """
        Handle tool call requests
        """
        try:
            tool_name = message.data.get('tool_name')
            tool_args = message.data.get('arguments', {})
            
            if not tool_name:
                await self.send_error(session.session_id, "Tool name is required")
                return
            
            # Execute tool
            result = await self.execute_tool(tool_name, tool_args, session)
            
            # Send result back
            await self.send_message(session.session_id, {
                "type": "tool_result",
                "message_id": message.message_id,
                "tool_name": tool_name,
                "result": result
            })
        
        except Exception as e:
            logger.error(f"Error handling tool call: {str(e)}")
            await self.send_error(session.session_id, f"Tool execution error: {str(e)}")
    
    async def _handle_prompt_request(self, session: MCPSession, message: MCPMessage):
        """
        Handle prompt requests
        """
        try:
            prompt_name = message.data.get('prompt_name')
            prompt_args = message.data.get('arguments', {})
            
            if not prompt_name:
                await self.send_error(session.session_id, "Prompt name is required")
                return
            
            # Generate prompt
            prompt_content = await self.generate_prompt(prompt_name, prompt_args, session)
            
            # Send prompt back
            await self.send_message(session.session_id, {
                "type": "prompt_response",
                "message_id": message.message_id,
                "prompt_name": prompt_name,
                "content": prompt_content
            })
        
        except Exception as e:
            logger.error(f"Error handling prompt request: {str(e)}")
            await self.send_error(session.session_id, f"Prompt generation error: {str(e)}")
    
    async def _handle_status_update(self, session: MCPSession, message: MCPMessage):
        """
        Handle status update messages
        """
        try:
            status_data = message.data.get('status', {})
            
            # Update session context
            session.context.update(status_data)
            
            # Acknowledge status update
            await self.send_message(session.session_id, {
                "type": "status_acknowledged",
                "message_id": message.message_id
            })
        
        except Exception as e:
            logger.error(f"Error handling status update: {str(e)}")
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any], 
                          session: MCPSession) -> Dict[str, Any]:
        """
        Execute a specific tool
        """
        try:
            if tool_name == "analyze_conversation":
                return await self._execute_analyze_conversation(arguments, session)
            elif tool_name == "process_conversation_file":
                return await self._execute_process_conversation_file(arguments, session)
            elif tool_name == "get_real_time_recommendation":
                return await self._execute_get_real_time_recommendation(arguments, session)
            elif tool_name == "start_monitoring_session":
                return await self._execute_start_monitoring_session(arguments, session)
            elif tool_name == "search_knowledge_base":
                return await self._execute_search_knowledge_base(arguments, session)
            elif tool_name == "generate_analysis_report":
                return await self._execute_generate_analysis_report(arguments, session)
            elif tool_name == "update_user_profile":
                return await self._execute_update_user_profile(arguments, session)
            elif tool_name == "add_knowledge_document":
                return await self._execute_add_knowledge_document(arguments, session)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {"error": str(e), "success": False}
    
    async def _execute_analyze_conversation(self, arguments: Dict[str, Any], 
                                          session: MCPSession) -> Dict[str, Any]:
        """
        Execute conversation analysis tool
        """
        try:
            conversation_data = arguments.get('conversation_data')
            analysis_type = arguments.get('analysis_type', 'comprehensive')
            user_id = arguments.get('user_id', session.user_id)
            
            if not self.conversation_analyzer:
                return {"error": "Conversation analyzer not available", "success": False}
            
            # Perform analysis
            if analysis_type == "comprehensive":
                result = await self.conversation_analyzer.analyze_comprehensive(conversation_data, user_id)
            elif analysis_type == "emotional":
                result = await self.conversation_analyzer.analyze_emotional_intelligence(conversation_data)
            elif analysis_type == "communication_style":
                result = await self.conversation_analyzer.analyze_communication_style(conversation_data)
            elif analysis_type == "compatibility":
                result = await self.conversation_analyzer.analyze_compatibility(conversation_data)
            elif analysis_type == "relationship_stage":
                result = await self.conversation_analyzer.analyze_relationship_stage(conversation_data)
            else:
                return {"error": f"Unknown analysis type: {analysis_type}", "success": False}
            
            return {"result": asdict(result), "success": True}
        
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _execute_process_conversation_file(self, arguments: Dict[str, Any], 
                                               session: MCPSession) -> Dict[str, Any]:
        """
        Execute file processing tool
        """
        try:
            file_data = arguments.get('file_data')
            file_type = arguments.get('file_type')
            user_id = arguments.get('user_id', session.user_id)
            
            if not self.data_processor:
                return {"error": "Data processor not available", "success": False}
            
            # Process file
            result = await self.data_processor.process_input(file_data, file_type)
            
            return {"result": result, "success": True}
        
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _execute_get_real_time_recommendation(self, arguments: Dict[str, Any], 
                                                  session: MCPSession) -> Dict[str, Any]:
        """
        Execute real-time recommendation tool
        """
        try:
            current_message = arguments.get('current_message')
            conversation_context = arguments.get('conversation_context', {})
            user_id = arguments.get('user_id', session.user_id)
            
            if not self.real_time_monitor:
                return {"error": "Real-time monitor not available", "success": False}
            
            # Generate recommendation
            recommendation = await self.real_time_monitor.generate_recommendation(
                current_message, conversation_context, user_id
            )
            
            return {"result": asdict(recommendation), "success": True}
        
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _execute_start_monitoring_session(self, arguments: Dict[str, Any], 
                                              session: MCPSession) -> Dict[str, Any]:
        """
        Execute monitoring session start tool
        """
        try:
            platform = arguments.get('platform')
            user_id = arguments.get('user_id', session.user_id)
            monitoring_config = arguments.get('monitoring_config', {})
            
            if not self.real_time_monitor:
                return {"error": "Real-time monitor not available", "success": False}
            
            # Start monitoring session
            monitoring_session_id = await self.real_time_monitor.start_monitoring_session(
                user_id, platform, monitoring_config
            )
            
            # Add to session context
            session.context['monitoring_session_id'] = monitoring_session_id
            
            return {"result": {"monitoring_session_id": monitoring_session_id}, "success": True}
        
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _execute_search_knowledge_base(self, arguments: Dict[str, Any], 
                                           session: MCPSession) -> Dict[str, Any]:
        """
        Execute knowledge base search tool
        """
        try:
            query = arguments.get('query')
            document_types = arguments.get('document_types')
            limit = arguments.get('limit', 10)
            
            if not self.knowledge_base:
                return {"error": "Knowledge base not available", "success": False}
            
            # Search knowledge base
            results = await self.knowledge_base.search(
                query=query,
                document_types=document_types,
                limit=limit
            )
            
            # Convert results to dict format
            search_results = [asdict(result) for result in results]
            
            return {"result": search_results, "success": True}
        
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _execute_generate_analysis_report(self, arguments: Dict[str, Any], 
                                              session: MCPSession) -> Dict[str, Any]:
        """
        Execute analysis report generation tool
        """
        try:
            user_id = arguments.get('user_id', session.user_id)
            report_type = arguments.get('report_type')
            time_period = arguments.get('time_period', 'last_week')
            
            if not self.ai_therapist:
                return {"error": "AI therapist not available", "success": False}
            
            # Generate report
            report = await self.ai_therapist.generate_analysis_report(
                user_id, report_type, time_period
            )
            
            return {"result": report, "success": True}
        
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _execute_update_user_profile(self, arguments: Dict[str, Any], 
                                         session: MCPSession) -> Dict[str, Any]:
        """
        Execute user profile update tool
        """
        try:
            user_id = arguments.get('user_id', session.user_id)
            profile_data = arguments.get('profile_data')
            
            # Update user profile (implement based on your user management system)
            # This is a placeholder implementation
            session.context['user_profile'] = profile_data
            
            return {"result": {"updated": True}, "success": True}
        
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _execute_add_knowledge_document(self, arguments: Dict[str, Any], 
                                            session: MCPSession) -> Dict[str, Any]:
        """
        Execute knowledge document addition tool
        """
        try:
            title = arguments.get('title')
            content = arguments.get('content')
            document_type = arguments.get('document_type')
            tags = arguments.get('tags', [])
            
            if not self.knowledge_base:
                return {"error": "Knowledge base not available", "success": False}
            
            # Add document to knowledge base
            doc_id = await self.knowledge_base.add_document(
                title=title,
                content=content,
                document_type=document_type,
                tags=tags
            )
            
            return {"result": {"document_id": doc_id}, "success": True}
        
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def generate_prompt(self, prompt_name: str, arguments: Dict[str, Any], 
                            session: MCPSession) -> str:
        """
        Generate a prompt based on the prompt name and arguments
        """
        try:
            if prompt_name == "relationship_analysis_prompt":
                return await self._generate_relationship_analysis_prompt(arguments, session)
            elif prompt_name == "real_time_recommendation_prompt":
                return await self._generate_real_time_recommendation_prompt(arguments, session)
            elif prompt_name == "communication_coaching_prompt":
                return await self._generate_communication_coaching_prompt(arguments, session)
            elif prompt_name == "conflict_resolution_prompt":
                return await self._generate_conflict_resolution_prompt(arguments, session)
            else:
                raise ValueError(f"Unknown prompt: {prompt_name}")
        
        except Exception as e:
            logger.error(f"Error generating prompt {prompt_name}: {str(e)}")
            return f"Error generating prompt: {str(e)}"
    
    async def _generate_relationship_analysis_prompt(self, arguments: Dict[str, Any], 
                                                   session: MCPSession) -> str:
        """
        Generate relationship analysis prompt
        """
        conversation_data = arguments.get('conversation_data', '')
        analysis_focus = arguments.get('analysis_focus', 'general relationship dynamics')
        
        prompt = f"""
As a professional relationship therapist, analyze the following conversation data with a focus on {analysis_focus}.

Conversation Data:
{conversation_data}

Please provide a comprehensive analysis including:
1. Communication patterns and styles
2. Emotional dynamics and intelligence
3. Relationship health indicators
4. Areas for improvement
5. Specific recommendations for better communication

Base your analysis on established psychological principles and relationship therapy best practices.
"""
        
        return prompt
    
    async def _generate_real_time_recommendation_prompt(self, arguments: Dict[str, Any], 
                                                      session: MCPSession) -> str:
        """
        Generate real-time recommendation prompt
        """
        current_context = arguments.get('current_context', '')
        user_profile = arguments.get('user_profile', {})
        
        prompt = f"""
As a relationship coach, provide real-time advice for the following conversation context.

Current Context:
{current_context}

User Profile:
{json.dumps(user_profile, indent=2)}

Provide specific, actionable recommendations for:
1. How to respond to the current message
2. Tone and approach to use
3. What to avoid saying
4. Long-term relationship building strategies

Keep recommendations practical and immediately applicable.
"""
        
        return prompt
    
    async def _generate_communication_coaching_prompt(self, arguments: Dict[str, Any], 
                                                    session: MCPSession) -> str:
        """
        Generate communication coaching prompt
        """
        communication_issue = arguments.get('communication_issue', '')
        relationship_stage = arguments.get('relationship_stage', 'unknown')
        
        prompt = f"""
As a communication coach specializing in relationships, address the following communication issue.

Communication Issue:
{communication_issue}

Relationship Stage: {relationship_stage}

Provide coaching advice including:
1. Root cause analysis of the communication issue
2. Specific techniques to improve communication
3. Scripts or examples of better ways to communicate
4. Exercises to practice better communication
5. Warning signs to watch for

Tailor your advice to the current relationship stage and be specific and actionable.
"""
        
        return prompt
    
    async def _generate_conflict_resolution_prompt(self, arguments: Dict[str, Any], 
                                                 session: MCPSession) -> str:
        """
        Generate conflict resolution prompt
        """
        conflict_description = arguments.get('conflict_description', '')
        parties_involved = arguments.get('parties_involved', {})
        
        prompt = f"""
As a conflict resolution specialist, help resolve the following relationship conflict.

Conflict Description:
{conflict_description}

Parties Involved:
{json.dumps(parties_involved, indent=2)}

Provide conflict resolution guidance including:
1. Analysis of the underlying issues
2. Step-by-step resolution process
3. Communication strategies for each party
4. Compromise solutions
5. Prevention strategies for future conflicts

Focus on win-win solutions and maintaining relationship health.
"""
        
        return prompt
    
    async def send_message(self, session_id: str, message_data: Dict[str, Any]):
        """
        Send a message to a specific session
        """
        try:
            if session_id in self.active_connections:
                websocket = self.active_connections[session_id]
                await websocket.send_text(json.dumps(message_data))
            else:
                logger.warning(f"No active connection for session {session_id}")
        
        except Exception as e:
            logger.error(f"Error sending message to session {session_id}: {str(e)}")
    
    async def send_error(self, session_id: str, error_message: str):
        """
        Send an error message to a specific session
        """
        await self.send_message(session_id, {
            "type": "error",
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        })
    
    async def broadcast_message(self, message_data: Dict[str, Any], user_id: str = None):
        """
        Broadcast a message to all active sessions or sessions for a specific user
        """
        try:
            target_sessions = []
            
            if user_id:
                # Send to specific user's sessions
                target_sessions = [
                    session_id for session_id, session in self.sessions.items()
                    if session.user_id == user_id
                ]
            else:
                # Send to all sessions
                target_sessions = list(self.active_connections.keys())
            
            for session_id in target_sessions:
                await self.send_message(session_id, message_data)
        
        except Exception as e:
            logger.error(f"Error broadcasting message: {str(e)}")
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific session
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            return {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "active_tools": session.active_tools,
                "context": session.context
            }
        return None
    
    def get_server_stats(self) -> Dict[str, Any]:
        """
        Get server statistics
        """
        return {
            "active_sessions": len(self.sessions),
            "active_connections": len(self.active_connections),
            "available_tools": len(self.available_tools),
            "available_prompts": len(self.available_prompts),
            "uptime": datetime.now().isoformat()
        }
    
    async def list_tools(self) -> ListToolsResult:
        """
        List available tools for MCP protocol
        """
        return ListToolsResult(tools=self.available_tools)
    
    async def list_prompts(self) -> ListPromptsResult:
        """
        List available prompts for MCP protocol
        """
        return ListPromptsResult(prompts=self.available_prompts)
    
    async def call_tool(self, request: CallToolRequest, session_id: str) -> CallToolResult:
        """
        Handle MCP tool call request
        """
        try:
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            result = await self.execute_tool(request.params.name, request.params.arguments, session)
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )
                ]
            )
        
        except Exception as e:
            logger.error(f"Error in MCP tool call: {str(e)}")
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps({"error": str(e), "success": False}, indent=2)
                    )
                ],
                isError=True
            )
    
    async def get_prompt(self, request: GetPromptRequest, session_id: str) -> GetPromptResult:
        """
        Handle MCP prompt request
        """
        try:
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            prompt_content = await self.generate_prompt(
                request.params.name, 
                request.params.arguments or {}, 
                session
            )
            
            return GetPromptResult(
                description=f"Generated prompt for {request.params.name}",
                messages=[
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": prompt_content
                        }
                    }
                ]
            )
        
        except Exception as e:
            logger.error(f"Error in MCP prompt request: {str(e)}")
            return GetPromptResult(
                description=f"Error generating prompt: {str(e)}",
                messages=[
                    {
                        "role": "assistant",
                        "content": {
                            "type": "text",
                            "text": f"Error: {str(e)}"
                        }
                    }
                ]
            )