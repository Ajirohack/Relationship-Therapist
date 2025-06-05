"""Redis Cache Service for improved performance and session management"""

import asyncio
import json
import logging
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import pickle
import hashlib

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

from config import settings

logger = logging.getLogger(__name__)

class CacheService:
    """Redis-based caching service with fallback to in-memory cache"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}  # Fallback in-memory cache
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection"""
        if not redis or not settings.redis_enabled:
            logger.info("Redis disabled or not available, using in-memory cache")
            return
        
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                db=settings.redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            logger.info("Redis client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            self.redis_client = None
    
    async def ping(self) -> bool:
        """Test Redis connection"""
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    def _generate_key(self, key: str, prefix: str = "") -> str:
        """Generate cache key with optional prefix"""
        if prefix:
            return f"{settings.redis_key_prefix}:{prefix}:{key}"
        return f"{settings.redis_key_prefix}:{key}"
    
    async def get(self, key: str, prefix: str = "") -> Optional[Any]:
        """Get value from cache"""
        cache_key = self._generate_key(key, prefix)
        
        try:
            if self.redis_client:
                value = await self.redis_client.get(cache_key)
                if value is not None:
                    self.cache_stats["hits"] += 1
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        # Try pickle for complex objects
                        try:
                            return pickle.loads(value.encode('latin-1'))
                        except:
                            return value
                else:
                    self.cache_stats["misses"] += 1
                    return None
            else:
                # Fallback to memory cache
                if cache_key in self.memory_cache:
                    entry = self.memory_cache[cache_key]
                    if entry["expires_at"] is None or datetime.now() < entry["expires_at"]:
                        self.cache_stats["hits"] += 1
                        return entry["value"]
                    else:
                        del self.memory_cache[cache_key]
                
                self.cache_stats["misses"] += 1
                return None
                
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.cache_stats["misses"] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, prefix: str = "") -> bool:
        """Set value in cache with optional TTL (seconds)"""
        cache_key = self._generate_key(key, prefix)
        
        try:
            if self.redis_client:
                # Serialize value
                try:
                    serialized_value = json.dumps(value)
                except (TypeError, ValueError):
                    # Use pickle for complex objects
                    serialized_value = pickle.dumps(value).decode('latin-1')
                
                if ttl:
                    await self.redis_client.setex(cache_key, ttl, serialized_value)
                else:
                    await self.redis_client.set(cache_key, serialized_value)
                
                self.cache_stats["sets"] += 1
                return True
            else:
                # Fallback to memory cache
                expires_at = datetime.now() + timedelta(seconds=ttl) if ttl else None
                self.memory_cache[cache_key] = {
                    "value": value,
                    "expires_at": expires_at
                }
                self.cache_stats["sets"] += 1
                return True
                
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str, prefix: str = "") -> bool:
        """Delete value from cache"""
        cache_key = self._generate_key(key, prefix)
        
        try:
            if self.redis_client:
                result = await self.redis_client.delete(cache_key)
                self.cache_stats["deletes"] += 1
                return result > 0
            else:
                # Fallback to memory cache
                if cache_key in self.memory_cache:
                    del self.memory_cache[cache_key]
                    self.cache_stats["deletes"] += 1
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def exists(self, key: str, prefix: str = "") -> bool:
        """Check if key exists in cache"""
        cache_key = self._generate_key(key, prefix)
        
        try:
            if self.redis_client:
                return await self.redis_client.exists(cache_key) > 0
            else:
                if cache_key in self.memory_cache:
                    entry = self.memory_cache[cache_key]
                    if entry["expires_at"] is None or datetime.now() < entry["expires_at"]:
                        return True
                    else:
                        del self.memory_cache[cache_key]
                return False
                
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1, prefix: str = "") -> Optional[int]:
        """Increment a numeric value in cache"""
        cache_key = self._generate_key(key, prefix)
        
        try:
            if self.redis_client:
                return await self.redis_client.incrby(cache_key, amount)
            else:
                # Fallback to memory cache
                current_value = await self.get(key, prefix) or 0
                new_value = int(current_value) + amount
                await self.set(key, new_value, prefix=prefix)
                return new_value
                
        except Exception as e:
            logger.error(f"Cache increment error: {e}")
            return None
    
    async def expire(self, key: str, ttl: int, prefix: str = "") -> bool:
        """Set expiration time for a key"""
        cache_key = self._generate_key(key, prefix)
        
        try:
            if self.redis_client:
                return await self.redis_client.expire(cache_key, ttl)
            else:
                # Update expiration in memory cache
                if cache_key in self.memory_cache:
                    self.memory_cache[cache_key]["expires_at"] = datetime.now() + timedelta(seconds=ttl)
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Cache expire error: {e}")
            return False
    
    async def clear_prefix(self, prefix: str) -> int:
        """Clear all keys with given prefix"""
        try:
            if self.redis_client:
                pattern = self._generate_key("*", prefix)
                keys = await self.redis_client.keys(pattern)
                if keys:
                    return await self.redis_client.delete(*keys)
                return 0
            else:
                # Clear from memory cache
                prefix_pattern = self._generate_key("", prefix)
                keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(prefix_pattern)]
                for key in keys_to_delete:
                    del self.memory_cache[key]
                return len(keys_to_delete)
                
        except Exception as e:
            logger.error(f"Cache clear prefix error: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = self.cache_stats.copy()
        stats["backend"] = "redis" if self.redis_client else "memory"
        stats["hit_rate"] = stats["hits"] / (stats["hits"] + stats["misses"]) if (stats["hits"] + stats["misses"]) > 0 else 0
        
        if self.redis_client:
            try:
                info = await self.redis_client.info()
                stats["redis_info"] = {
                    "used_memory": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                    "total_commands_processed": info.get("total_commands_processed")
                }
            except Exception as e:
                logger.error(f"Failed to get Redis info: {e}")
        else:
            stats["memory_cache_size"] = len(self.memory_cache)
        
        return stats

class SessionCache:
    """Session-specific caching functionality"""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        self.session_prefix = "session"
    
    async def set_session_data(self, session_id: str, data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Store session data"""
        return await self.cache.set(session_id, data, ttl, self.session_prefix)
    
    async def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data"""
        return await self.cache.get(session_id, self.session_prefix)
    
    async def update_session_data(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update specific fields in session data"""
        current_data = await self.get_session_data(session_id) or {}
        current_data.update(updates)
        return await self.set_session_data(session_id, current_data)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session data"""
        return await self.cache.delete(session_id, self.session_prefix)
    
    async def extend_session(self, session_id: str, ttl: int = 3600) -> bool:
        """Extend session expiration"""
        return await self.cache.expire(session_id, ttl, self.session_prefix)

class ConversationCache:
    """Conversation-specific caching functionality"""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        self.conversation_prefix = "conversation"
        self.analysis_prefix = "analysis"
    
    async def cache_conversation_analysis(self, conversation_id: str, analysis: Dict[str, Any], ttl: int = 7200) -> bool:
        """Cache conversation analysis results"""
        key = f"{conversation_id}_analysis"
        return await self.cache.set(key, analysis, ttl, self.analysis_prefix)
    
    async def get_conversation_analysis(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached conversation analysis"""
        key = f"{conversation_id}_analysis"
        return await self.cache.get(key, self.analysis_prefix)
    
    async def cache_conversation_summary(self, conversation_id: str, summary: str, ttl: int = 86400) -> bool:
        """Cache conversation summary"""
        key = f"{conversation_id}_summary"
        return await self.cache.set(key, summary, ttl, self.conversation_prefix)
    
    async def get_conversation_summary(self, conversation_id: str) -> Optional[str]:
        """Retrieve cached conversation summary"""
        key = f"{conversation_id}_summary"
        return await self.cache.get(key, self.conversation_prefix)
    
    async def cache_user_conversations(self, user_id: str, conversations: List[Dict], ttl: int = 3600) -> bool:
        """Cache user's conversation list"""
        key = f"user_{user_id}_conversations"
        return await self.cache.set(key, conversations, ttl, self.conversation_prefix)
    
    async def get_user_conversations(self, user_id: str) -> Optional[List[Dict]]:
        """Retrieve cached user conversations"""
        key = f"user_{user_id}_conversations"
        return await self.cache.get(key, self.conversation_prefix)
    
    async def invalidate_user_cache(self, user_id: str) -> bool:
        """Invalidate all cached data for a user"""
        pattern = f"user_{user_id}_"
        # This is a simplified approach - in production, you'd want more sophisticated cache invalidation
        await self.cache.delete(f"user_{user_id}_conversations", self.conversation_prefix)
        await self.cache.delete(f"user_{user_id}_profile", "user")
        return True

class RateLimitCache:
    """Rate limiting functionality using cache"""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        self.rate_limit_prefix = "rate_limit"
    
    async def check_rate_limit(self, identifier: str, limit: int, window: int) -> Dict[str, Any]:
        """Check if identifier is within rate limit"""
        key = f"{identifier}_{window}"
        
        try:
            current_count = await self.cache.get(key, self.rate_limit_prefix) or 0
            
            if current_count >= limit:
                return {
                    "allowed": False,
                    "current_count": current_count,
                    "limit": limit,
                    "reset_time": window
                }
            
            # Increment counter
            new_count = await self.cache.increment(key, 1, self.rate_limit_prefix)
            
            # Set expiration if this is the first request
            if new_count == 1:
                await self.cache.expire(key, window, self.rate_limit_prefix)
            
            return {
                "allowed": True,
                "current_count": new_count,
                "limit": limit,
                "remaining": limit - new_count
            }
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # Allow request on error
            return {
                "allowed": True,
                "current_count": 0,
                "limit": limit,
                "error": str(e)
            }
    
    async def reset_rate_limit(self, identifier: str, window: int) -> bool:
        """Reset rate limit for identifier"""
        key = f"{identifier}_{window}"
        return await self.cache.delete(key, self.rate_limit_prefix)

class CacheManager:
    """Main cache manager that coordinates all cache services"""
    
    def __init__(self):
        self.cache_service = CacheService()
        self.session_cache = SessionCache(self.cache_service)
        self.conversation_cache = ConversationCache(self.cache_service)
        self.rate_limit_cache = RateLimitCache(self.cache_service)
    
    async def initialize(self) -> bool:
        """Initialize cache manager"""
        try:
            if self.cache_service.redis_client:
                is_connected = await self.cache_service.ping()
                if is_connected:
                    logger.info("Cache manager initialized with Redis")
                else:
                    logger.warning("Redis connection failed, using memory cache")
            else:
                logger.info("Cache manager initialized with memory cache")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize cache manager: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on cache system"""
        health = {
            "status": "healthy",
            "backend": "redis" if self.cache_service.redis_client else "memory",
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            if self.cache_service.redis_client:
                is_connected = await self.cache_service.ping()
                if not is_connected:
                    health["status"] = "unhealthy"
                    health["error"] = "Redis connection failed"
            
            # Get cache statistics
            stats = await self.cache_service.get_stats()
            health["stats"] = stats
            
        except Exception as e:
            health["status"] = "unhealthy"
            health["error"] = str(e)
        
        return health
    
    async def cleanup(self):
        """Cleanup cache resources"""
        try:
            if self.cache_service.redis_client:
                await self.cache_service.redis_client.close()
            logger.info("Cache manager cleanup completed")
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")

# Global cache manager instance
cache_manager = CacheManager()