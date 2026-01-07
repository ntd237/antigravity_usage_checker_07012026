"""
Cache Manager Module - Quản lý offline cache
"""

import json
from typing import Optional
from datetime import datetime, timedelta
from .utils import CACHE_FILE, CACHE_MAX_AGE_HOURS, ensure_cache_dir
from .api_client import QuotaData, QuotaModel


class CacheManager:
    """Manager để lưu và load cache"""
    
    def __init__(self):
        ensure_cache_dir()
    
    def save(self, quota_data: QuotaData):
        """
        Lưu quota data vào cache
        
        Args:
            quota_data: QuotaData object để save
        """
        try:
            cache_obj = {
                "timestamp": quota_data.timestamp,
                "models": [
                    {
                        "model_name": m.model_name,
                        "used": m.used,
                        "limit": m.limit,
                        "remaining": m.remaining,
                        "reset_time": m.reset_time,
                        "is_shared_pool": m.is_shared_pool,
                    }
                    for m in quota_data.models
                ]
            }
            
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_obj, f, indent=2)
                
        except Exception as e:
            # Silent fail - không critical nếu cache fail
            pass
    
    def load(self) -> Optional[QuotaData]:
        """
        Load quota data từ cache
        
        Returns:
            QuotaData nếu cache valid, None nếu không có hoặc expired
        """
        try:
            if not CACHE_FILE.exists():
                return None
            
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_obj = json.load(f)
            
            # Check cache age
            cache_timestamp = cache_obj.get("timestamp", 0)
            cache_age_hours = (datetime.now().timestamp() - cache_timestamp) / 3600
            
            if cache_age_hours > CACHE_MAX_AGE_HOURS:
                # Cache quá cũ
                return None
            
            # Parse models
            models = []
            for m in cache_obj.get("models", []):
                model = QuotaModel(
                    model_name=m["model_name"],
                    used=m["used"],
                    limit=m["limit"],
                    remaining=m["remaining"],
                    reset_time=m["reset_time"],
                    is_shared_pool=m.get("is_shared_pool", False)
                )
                models.append(model)
            
            return QuotaData(
                models=models,
                timestamp=cache_timestamp
            )
            
        except Exception as e:
            # Parse error hoặc file corrupt
            return None
    
    def get_cache_age(self) -> Optional[str]:
        """
        Get cache age string (e.g., "2 hours ago")
        
        Returns:
            Human-readable cache age hoặc None
        """
        try:
            if not CACHE_FILE.exists():
                return None
            
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_obj = json.load(f)
            
            cache_timestamp = cache_obj.get("timestamp", 0)
            cache_datetime = datetime.fromtimestamp(cache_timestamp)
            
            delta = datetime.now() - cache_datetime
            
            if delta.days > 0:
                return f"{delta.days} ngày trước"
            elif delta.seconds >= 3600:
                hours = delta.seconds // 3600
                return f"{hours} giờ trước"
            else:
                minutes = delta.seconds // 60
                return f"{minutes} phút trước"
                
        except:
            return None
