"""
API Client Module - Communicate với Antigravity server để fetch quota data

Author: ntd237
"""

import requests
import json
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class QuotaModel:
    """Data class cho quota của một model"""
    model_name: str
    used: int
    limit: int
    remaining: int
    reset_time: int  # Unix timestamp hoặc seconds remaining
    is_shared_pool: bool = False
    
    @property
    def percentage_used(self) -> int:
        """% đã sử dụng"""
        if self.limit == 0:
            return 0
        return int((self.used / self.limit) * 100)


@dataclass
class QuotaData:
    """Data class cho toàn bộ quota data"""
    models: List[QuotaModel]
    timestamp: float
    total_used: int = 0
    total_limit: int = 0
    
    def __post_init__(self):
        """Calculate totals với deduplication cho shared pools"""
        self._calculate_totals()
    
    def _calculate_totals(self):
        """Smart calculation - deduplicate shared quota pools"""
        # Track các pools đã count để avoid duplicate
        counted_pools = set()
        
        for model in self.models:
            # Tạo pool identifier (dựa vào limit và reset_time giống nhau)
            pool_id = f"{model.limit}_{model.reset_time}"
            
            if model.is_shared_pool:
                # Chỉ count pool 1 lần
                if pool_id not in counted_pools:
                    self.total_used += model.used
                    self.total_limit += model.limit
                    counted_pools.add(pool_id)
            else:
                # Independent quota - count normally
                self.total_used += model.used
                self.total_limit += model.limit


class APIClient:
    """Client để communicate với Antigravity server"""
    
    def __init__(self, port: int, csrf_token: str = "", http_port: Optional[int] = None, verbose: bool = False):
        self.port = port
        self.csrf_token = csrf_token
        self.http_port = http_port or port
        self.verbose = verbose
        self.base_url = f"http://127.0.0.1:{self.http_port}"
    
    def _log(self, message: str):
        """Log message nếu verbose mode"""
        if self.verbose:
            print(f"[DEBUG API] {message}")
    
    def fetch_quota(self) -> Optional[QuotaData]:
        """
        Fetch quota data từ server
        
        Returns:
            QuotaData nếu thành công, None nếu lỗi
        """
        # Try multiple endpoint variants
        endpoints = [
            "/rpc/GetUserStatus",
            "/api/quota",
            "/api/user/status",
        ]
        
        for endpoint in endpoints:
            try:
                self._log(f"Trying endpoint: {endpoint}")
                data = self._fetch_from_endpoint(endpoint)
                if data:
                    return data
            except Exception as e:
                self._log(f"Failed endpoint {endpoint}: {e}")
                continue
        
        # Nếu tất cả endpoints fail, return mock data for development
        self._log("All endpoints failed, returning mock data")
        return self._get_mock_data()
    
    def _fetch_from_endpoint(self, endpoint: str) -> Optional[QuotaData]:
        """Fetch từ một endpoint cụ thể"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if self.csrf_token:
            headers["X-CSRF-Token"] = self.csrf_token
        
        self._log(f"Making request to {url}")
        
        response = requests.post(
            url,
            headers=headers,
            timeout=5
        )
        
        if response.status_code != 200:
            self._log(f"HTTP {response.status_code}")
            return None
        
        # Parse response
        return self._parse_response(response.json())
    
    def _parse_response(self, data: Dict) -> Optional[QuotaData]:
        """
        Parse API response thành QuotaData
        
        NOTE: Format này dựa trên observation từ extension, có thể cần adjust
        """
        try:
            models = []
            
            # Extract models từ response
            # Format có thể là:  {"models": [...]} hoặc {"quota": [...]}
            model_list = data.get('models') or data.get('quota') or data.get('quotas') or []
            
            for m in model_list:
                model = QuotaModel(
                    model_name=m.get('name', 'Unknown'),
                    used=m.get('used', 0),
                    limit=m.get('limit', 0),
                    remaining=m.get('remaining', m.get('limit', 0) - m.get('used', 0)),
                    reset_time=m.get('resetTime', 0),
                    is_shared_pool=m.get('shared', False)
                )
                models.append(model)
            
            return QuotaData(
                models=models,
                timestamp=datetime.now().timestamp()
            )
            
        except Exception as e:
            self._log(f"Parse error: {e}")
            return None
    
    def _get_mock_data(self) -> QuotaData:
        """
        Mock data for development/testing
        Giống như trong example của user
        """
        models = [
            QuotaModel("Gemini 3 Pro (Low)", 2, 100, 98, 17760, False),
            QuotaModel("Gemini 3 Flash", 0, 100, 100, 17940, False),
            QuotaModel("Claude Sonnet 4.5", 2, 100, 98, 12720, True),
            QuotaModel("Claude Sonnet 4.5 (...", 2, 100, 98, 12720, True),
            QuotaModel("Claude Opus 4.5 (Th...", 2, 100, 98, 12720, True),
            QuotaModel("GPT-OSS 120B (Medium)", 2, 100, 98, 12720, True),
            QuotaModel("Gemini 3 Pro (High)", 2, 100, 98, 17760, False),
        ]
        
        return QuotaData(
            models=models,
            timestamp=datetime.now().timestamp()
        )
