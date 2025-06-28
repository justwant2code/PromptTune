"""
Simple in-memory cache for prompt optimization results
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from loguru import logger

class PromptCache:
    def __init__(self, ttl_minutes: int = 60):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def _generate_key(self, description: str, context: str, model: str) -> str:
        """Generate a cache key from prompt parameters"""
        content = f"{description}|{context}|{model}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, description: str, context: str, model: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired"""
        key = self._generate_key(description, context, model)
        
        if key not in self.cache:
            return None
        
        cached_item = self.cache[key]
        
        # Check if expired
        if datetime.now() - cached_item['timestamp'] > self.ttl:
            del self.cache[key]
            logger.info(f"Cache expired for key: {key[:8]}...")
            return None
        
        logger.info(f"Cache hit for key: {key[:8]}...")
        return cached_item['result']
    
    def set(self, description: str, context: str, model: str, result: Dict[str, Any]) -> None:
        """Cache a result"""
        key = self._generate_key(description, context, model)
        
        self.cache[key] = {
            'result': result,
            'timestamp': datetime.now()
        }
        
        logger.info(f"Cached result for key: {key[:8]}...")
        
        # Clean up old entries periodically
        self._cleanup()
    
    def _cleanup(self) -> None:
        """Remove expired entries"""
        if len(self.cache) < 100:  # Only cleanup when cache gets large
            return
        
        now = datetime.now()
        expired_keys = [
            key for key, item in self.cache.items()
            if now - item['timestamp'] > self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = datetime.now()
        active_entries = sum(
            1 for item in self.cache.values()
            if now - item['timestamp'] <= self.ttl
        )
        
        return {
            "total_entries": len(self.cache),
            "active_entries": active_entries,
            "expired_entries": len(self.cache) - active_entries,
            "ttl_minutes": self.ttl.total_seconds() / 60
        }

# Global cache instance
prompt_cache = PromptCache(ttl_minutes=30)  # 30 minute TTL
