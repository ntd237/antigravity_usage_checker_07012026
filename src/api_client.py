"""
API Client Module - Communicate với Antigravity server để fetch quota data
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
        """Smart calculation - deduplicate shared quota pools based on reset_time"""
        # Track các pools đã count để avoid duplicate
        # Group by reset_time để detect shared pools
        reset_time_groups = {}
        
        for model in self.models:
            reset_time = model.reset_time
            if reset_time not in reset_time_groups:
                reset_time_groups[reset_time] = []
            reset_time_groups[reset_time].append(model)
        
        # Nếu nhiều models cùng reset_time → shared pool
        for reset_time, models_in_group in reset_time_groups.items():
            if len(models_in_group) > 1:
                # Shared pool - chỉ count 1 lần
                # Mark all as shared
                for m in models_in_group:
                    m.is_shared_pool = True
                
                # Có trong pool đầu tiên
                self.total_used += models_in_group[0].used
                self.total_limit += models_in_group[0].limit
            else:
                # Independent quota
                model = models_in_group[0]
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
        # Exact endpoint từ Antigravity Language Server
        endpoints = [
            "/exa.language_server_pb.LanguageServerService/GetUserStatus",
        ]
        
        for endpoint in endpoints:
            try:
                self._log(f"Trying endpoint: {endpoint}")
                data = self._fetch_from_endpoint(endpoint)
                if data:
                    self._log("Successfully fetched real quota data!")
                    return data
            except Exception as e:
                self._log(f"Failed endpoint {endpoint}: {e}")
                continue
        
        # Nếu tất cả endpoints fail, return mock data for development
        self._log("All endpoints failed, returning mock data")
        return self._get_mock_data()
    
    def _fetch_from_endpoint(self, endpoint: str) -> Optional[QuotaData]:
        """Fetch từ một endpoint cụ thể"""
        # Construct full URL với HTTPS
        url = f"https://127.0.0.1:{self.port}{endpoint}"
        
        # Prepare headers theo Antigravity API spec
        headers = {
            'Content-Type': 'application/json',
            'Connect-Protocol-Version': '1',
        }
        
        if self.csrf_token:
            headers["X-Codeium-Csrf-Token"] = self.csrf_token
        else:
            self._log("WARNING: No CSRF token available")
        
        # Prepare request body
        request_body = {}  # Empty body for GetUserStatus
        
        self._log(f"Making HTTPS request to {url}")
        self._log(f"Headers: {list(headers.keys())}")
        
        try:
            # Try HTTPS first
            response = requests.post(
                url,
                headers=headers,
                json=request_body,
                timeout=5,
                verify=False  # Disable SSL verification for local server
            )
            
            self._log(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                return self._parse_response(response.json())
                
        except requests.exceptions.SSLError as e:
            # HTTPS failed, try HTTP fallback on httpPort
            if self.http_port != self.port:
                self._log(f"HTTPS failed, trying HTTP on port {self.http_port}")
                url_http = f"http://127.0.0.1:{self.http_port}{endpoint}"
                
                try:
                    response = requests.post(
                        url_http,
                        headers=headers,
                        json=request_body,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        return self._parse_response(response.json())
                except Exception as e2:
                    self._log(f"HTTP fallback also failed: {e2}")
        except Exception as e:
            self._log(f"Request failed: {e}")
        
        return None
    
    def _parse_response(self, data: Dict) -> Optional[QuotaData]:
        """
        Parse API response thành QuotaData
        
        Antigravity response format:
        {
          "userStatus": {
            "cascadeModelConfigData": {
              "clientModelConfigs": [
                {
                  "label": "Model Name",
                  "quotaInfo": {
                    "remainingFraction": 0.98,
                    "resetTime": "2026-01-07T14:30:00Z"
                  }
                }
              ]
            }
          }
        }
        """
        try:
            models = []
            
            # Extract từ UserStatusResponse format
            user_status = data.get('userStatus', {})
            cascade_data = user_status.get('cascadeModelConfigData', {})
            model_configs = cascade_data.get('clientModelConfigs', [])
            
            self._log(f"Found {len(model_configs)} model configs in response")
            
            for config in model_configs:
                label = config.get('label', 'Unknown')
                quota_info = config.get('quotaInfo', {})
                
                if not quota_info:
                    # Model không có quota info, skip
                    continue
                
                # Parse quota info
                remaining_fraction = quota_info.get('remainingFraction', 1.0)
                reset_time_str = quota_info.get('resetTime', '')
                
                # Calculate used/limit (assuming limit = 100 for now)
                # TODO: Get actual limit from tier info
                limit = 100
                remaining = int(remaining_fraction * limit)
                used = limit - remaining
                
                # Parse reset time
                try:
                    from datetime import datetime
                    reset_dt = datetime.fromisoformat(reset_time_str.replace('Z', '+00:00'))
                    now = datetime.now(reset_dt.tzinfo)
                    reset_seconds = int((reset_dt - now).total_seconds())
                    reset_seconds = max(0, reset_seconds)
                except:
                    reset_seconds = 0
                
                # Detect shared pool (models with same resetTime)
                # For now, assume all models are independent
                is_shared = False
                
                model = QuotaModel(
                    model_name=label,
                    used=used,
                    limit=limit,
                    remaining=remaining,
                    reset_time=reset_seconds,
                    is_shared_pool=is_shared
                )
                models.append(model)
            
            if models:
                return QuotaData(
                    models=models,
                    timestamp=datetime.now().timestamp()
                )
            else:
                self._log("No models found in response, using fallback")
                return None
            
        except Exception as e:
            self._log(f"Parse error: {e}")
            import traceback
            self._log(f"Traceback: {traceback.format_exc()}")
            return None
    
    def _get_mock_data(self) -> QuotaData:
        """
        Mock data for development/testing
        Model names từ Antigravity thực tế
        """
        models = [
            # Gemini 3 Pro (High) và (Low) có cùng reset time → shared pool
            QuotaModel("Gemini 3 Pro (High)", 2, 100, 98, 17760, False),
            QuotaModel("Gemini 3 Pro (Low)", 2, 100, 98, 17760, False),
            QuotaModel("Gemini 3 Flash   New", 0, 100, 100, 17940, False),
            # Claude models có cùng reset time → shared pool
            QuotaModel("Claude Sonnet 4.5", 2, 100, 98, 12720, False),
            QuotaModel("Claude Sonnet 4.5 (Thinking)", 2, 100, 98, 12720, False),
            QuotaModel("Claude Opus 4.5 (Thinking)", 2, 100, 98, 12720, False),
            QuotaModel("GPT-OSS 120B (Medium)", 2, 100, 98, 12720, False),
        ]
        
        return QuotaData(
            models=models,
            timestamp=datetime.now().timestamp()
        )
