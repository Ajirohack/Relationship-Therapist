"""Admin Service Module

Provides administrative functionality for the Relationship Therapist System.
Includes user management, system monitoring, analytics, and maintenance operations.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import os
from pathlib import Path

from database import DatabaseManager
from cache_service import CacheManager
from vector_db import VectorDBService
from auth import User
from database import Conversation
from conversation_analyzer import AnalysisResult as Analysis

logger = logging.getLogger(__name__)

class AdminService:
    """Service class for administrative operations"""
    
    def __init__(self, db_manager: DatabaseManager, cache_manager: CacheManager, vector_db: VectorDBService):
        self.db = db_manager
        self.cache = cache_manager
        self.vector_db = vector_db
        
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            # User statistics
            total_users = await self.db.count_users()
            active_users = await self.db.count_active_users()
            new_users_today = await self.db.count_new_users_today()
            
            # Session statistics
            total_sessions = await self.db.count_sessions()
            active_sessions = await self.db.count_active_sessions()
            completed_sessions = await self.db.count_completed_sessions()
            
            # Analysis statistics
            total_analyses = await self.db.count_analyses()
            analyses_today = await self.db.count_analyses_today()
            avg_analysis_rating = await self.db.get_average_analysis_rating()
            
            # System health
            db_health = await self.db.health_check()
            cache_health = await self.cache.health_check()
            vector_db_health = await self.vector_db.health_check()
            
            # Storage statistics
            storage_stats = await self.get_storage_stats()
            
            return {
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "new_today": new_users_today,
                    "growth_rate": await self.calculate_user_growth_rate()
                },
                "sessions": {
                    "total": total_sessions,
                    "active": active_sessions,
                    "completed": completed_sessions,
                    "completion_rate": (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
                },
                "analyses": {
                    "total": total_analyses,
                    "today": analyses_today,
                    "avg_rating": avg_analysis_rating or 0
                },
                "system_health": {
                    "database": db_health,
                    "cache": cache_health,
                    "vector_db": vector_db_health,
                    "overall": all([db_health, cache_health, vector_db_health])
                },
                "storage": storage_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            raise
    
    async def get_user_analytics(self, period: str = "7d") -> Dict[str, Any]:
        """Get user activity analytics"""
        try:
            end_date = datetime.utcnow()
            
            if period == "7d":
                start_date = end_date - timedelta(days=7)
                interval = "day"
            elif period == "30d":
                start_date = end_date - timedelta(days=30)
                interval = "day"
            elif period == "90d":
                start_date = end_date - timedelta(days=90)
                interval = "week"
            else:
                start_date = end_date - timedelta(days=7)
                interval = "day"
            
            # Get user activity data
            activity_data = await self.db.get_user_activity_data(start_date, end_date, interval)
            
            # Get user registration data
            registration_data = await self.db.get_user_registration_data(start_date, end_date, interval)
            
            # Get session data
            session_data = await self.db.get_session_data(start_date, end_date, interval)
            
            return {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "user_activity": activity_data,
                "user_registrations": registration_data,
                "session_activity": session_data
            }
        except Exception as e:
            logger.error(f"Failed to get user analytics: {e}")
            raise
    
    async def get_analysis_metrics(self) -> Dict[str, Any]:
        """Get analysis performance metrics"""
        try:
            # Trust score distribution
            trust_scores = await self.db.get_trust_score_distribution()
            
            # Communication metrics
            comm_metrics = await self.db.get_communication_metrics()
            
            # Analysis completion times
            completion_times = await self.db.get_analysis_completion_times()
            
            # Popular analysis types
            analysis_types = await self.db.get_popular_analysis_types()
            
            return {
                "trust_score_distribution": trust_scores,
                "communication_metrics": comm_metrics,
                "completion_times": completion_times,
                "popular_types": analysis_types,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get analysis metrics: {e}")
            raise
    
    async def get_users_list(self, skip: int = 0, limit: int = 100, search: str = None, role: str = None) -> Dict[str, Any]:
        """Get paginated list of users with optional filtering"""
        try:
            users = await self.db.get_users_with_filters(skip=skip, limit=limit, search=search, role=role)
            total_count = await self.db.count_users_with_filters(search=search, role=role)
            
            # Enhance user data with additional info
            enhanced_users = []
            for user in users:
                user_stats = await self.db.get_user_stats(user.id)
                enhanced_user = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "stats": user_stats
                }
                enhanced_users.append(enhanced_user)
            
            return {
                "users": enhanced_users,
                "total": total_count,
                "skip": skip,
                "limit": limit,
                "has_more": (skip + limit) < total_count
            }
        except Exception as e:
            logger.error(f"Failed to get users list: {e}")
            raise
    
    async def get_sessions_list(self, skip: int = 0, limit: int = 100, status: str = None, user_id: str = None) -> Dict[str, Any]:
        """Get paginated list of sessions with optional filtering"""
        try:
            sessions = await self.db.get_sessions_with_filters(skip=skip, limit=limit, status=status, user_id=user_id)
            total_count = await self.db.count_sessions_with_filters(status=status, user_id=user_id)
            
            # Enhance session data
            enhanced_sessions = []
            for session in sessions:
                session_stats = await self.db.get_session_stats(session.id)
                enhanced_session = {
                    "id": session.id,
                    "title": session.title,
                    "user_id": session.user_id,
                    "status": session.status,
                    "created_at": session.created_at.isoformat() if session.created_at else None,
                    "updated_at": session.updated_at.isoformat() if session.updated_at else None,
                    "stats": session_stats
                }
                enhanced_sessions.append(enhanced_session)
            
            return {
                "sessions": enhanced_sessions,
                "total": total_count,
                "skip": skip,
                "limit": limit,
                "has_more": (skip + limit) < total_count
            }
        except Exception as e:
            logger.error(f"Failed to get sessions list: {e}")
            raise
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user information"""
        try:
            # Validate update data
            allowed_fields = ['username', 'email', 'role', 'is_active', 'full_name']
            filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
            
            if not filtered_data:
                raise ValueError("No valid fields to update")
            
            # Update user
            updated_user = await self.db.update_user(user_id, filtered_data)
            
            # Clear user cache
            await self.cache.delete(f"user:{user_id}")
            
            # Log the update
            await self.log_admin_action("user_update", {
                "user_id": user_id,
                "updated_fields": list(filtered_data.keys()),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "id": updated_user.id,
                "username": updated_user.username,
                "email": updated_user.email,
                "role": updated_user.role,
                "is_active": updated_user.is_active,
                "updated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            raise
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user and all associated data"""
        try:
            # Get user info before deletion for logging
            user = await self.db.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Delete user data in order
            await self.db.delete_user_analyses(user_id)
            await self.db.delete_user_sessions(user_id)
            await self.db.delete_user_conversations(user_id)
            await self.db.delete_user(user_id)
            
            # Clear caches
            await self.cache.delete(f"user:{user_id}")
            await self.cache.delete_pattern(f"user:{user_id}:*")
            
            # Log the deletion
            await self.log_admin_action("user_delete", {
                "user_id": user_id,
                "username": user.username,
                "email": user.email,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise
    
    async def create_system_backup(self) -> str:
        """Create a system backup"""
        try:
            backup_id = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            backup_path = Path(f"backups/{backup_id}")
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup database
            db_backup_path = await self.db.create_backup(str(backup_path / "database.sql"))
            
            # Backup vector database
            vector_backup_path = await self.vector_db.create_backup(str(backup_path / "vectors"))
            
            # Create backup manifest
            manifest = {
                "backup_id": backup_id,
                "created_at": datetime.utcnow().isoformat(),
                "components": {
                    "database": db_backup_path,
                    "vector_db": vector_backup_path
                },
                "size": await self.calculate_backup_size(backup_path)
            }
            
            with open(backup_path / "manifest.json", "w") as f:
                json.dump(manifest, f, indent=2)
            
            # Log the backup
            await self.log_admin_action("system_backup", {
                "backup_id": backup_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return backup_id
        except Exception as e:
            logger.error(f"Failed to create system backup: {e}")
            raise
    
    async def clear_system_cache(self) -> bool:
        """Clear all system caches"""
        try:
            await self.cache.clear_all()
            
            # Log the action
            await self.log_admin_action("cache_clear", {
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return True
        except Exception as e:
            logger.error(f"Failed to clear system cache: {e}")
            raise
    
    async def get_system_logs(self, level: str = "INFO", limit: int = 100) -> List[Dict[str, Any]]:
        """Get system logs"""
        try:
            # This would typically read from log files or a logging database
            # For now, return mock data
            logs = [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": "INFO",
                    "message": "System health check completed",
                    "module": "health_monitor"
                },
                {
                    "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                    "level": "INFO",
                    "message": "User authentication successful",
                    "module": "auth_service"
                },
                {
                    "timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat(),
                    "level": "WARNING",
                    "message": "High memory usage detected",
                    "module": "system_monitor"
                }
            ]
            
            return logs[:limit]
        except Exception as e:
            logger.error(f"Failed to get system logs: {e}")
            raise
    
    async def export_user_data(self, user_id: str) -> str:
        """Export all data for a specific user"""
        try:
            user = await self.db.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Get all user data
            conversations = await self.db.get_user_conversations(user_id)
            analyses = await self.db.get_user_analyses(user_id)
            sessions = await self.db.get_user_sessions(user_id)
            
            # Create export data
            export_data = {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                },
                "conversations": [conv.to_dict() for conv in conversations],
                "analyses": [analysis.to_dict() for analysis in analyses],
                "sessions": [session.to_dict() for session in sessions],
                "exported_at": datetime.utcnow().isoformat()
            }
            
            # Save to file
            export_path = Path(f"exports/user_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json")
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, "w") as f:
                json.dump(export_data, f, indent=2)
            
            return str(export_path)
        except Exception as e:
            logger.error(f"Failed to export user data for {user_id}: {e}")
            raise
    
    async def calculate_user_growth_rate(self) -> float:
        """Calculate user growth rate"""
        try:
            # Get user counts for the last two periods
            end_date = datetime.utcnow()
            mid_date = end_date - timedelta(days=30)
            start_date = end_date - timedelta(days=60)
            
            current_period_users = await self.db.count_users_in_period(mid_date, end_date)
            previous_period_users = await self.db.count_users_in_period(start_date, mid_date)
            
            if previous_period_users == 0:
                return 0.0
            
            growth_rate = ((current_period_users - previous_period_users) / previous_period_users) * 100
            return round(growth_rate, 2)
        except Exception as e:
            logger.error(f"Failed to calculate user growth rate: {e}")
            return 0.0
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage usage statistics"""
        try:
            # Calculate database size
            db_size = await self.db.get_database_size()
            
            # Calculate vector database size
            vector_db_size = await self.vector_db.get_storage_size()
            
            # Calculate file storage size
            file_storage_size = self.calculate_directory_size("uploads")
            
            # Calculate backup storage size
            backup_storage_size = self.calculate_directory_size("backups")
            
            total_size = db_size + vector_db_size + file_storage_size + backup_storage_size
            
            return {
                "database": self.format_bytes(db_size),
                "vector_database": self.format_bytes(vector_db_size),
                "file_storage": self.format_bytes(file_storage_size),
                "backup_storage": self.format_bytes(backup_storage_size),
                "total": self.format_bytes(total_size),
                "raw_bytes": {
                    "database": db_size,
                    "vector_database": vector_db_size,
                    "file_storage": file_storage_size,
                    "backup_storage": backup_storage_size,
                    "total": total_size
                }
            }
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {}
    
    def calculate_directory_size(self, directory: str) -> int:
        """Calculate total size of a directory"""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            return total_size
        except Exception:
            return 0
    
    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    async def calculate_backup_size(self, backup_path: Path) -> int:
        """Calculate size of a backup directory"""
        return self.calculate_directory_size(str(backup_path))
    
    async def log_admin_action(self, action: str, details: Dict[str, Any]):
        """Log administrative actions"""
        try:
            log_entry = {
                "action": action,
                "details": details,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store in database or log file
            await self.db.log_admin_action(log_entry)
            
            # Also log to application logger
            logger.info(f"Admin action: {action}", extra=details)
        except Exception as e:
            logger.error(f"Failed to log admin action: {e}")