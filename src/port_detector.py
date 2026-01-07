"""
Port Detector Module - Detect Antigravity server port và authentication info

Author: ntd237
"""

import psutil
import re
import sys
from typing import Optional, Tuple
from .utils import PORT_RANGE_START, PORT_RANGE_END, ANTIGRAVITY_PROCESS_NAMES


class ServerInfo:
    """Class chứa thông tin server"""
    def __init__(self, port: int, csrf_token: str = "", pid: int = 0, http_port: int = 0):
        self.port = port
        self.csrf_token = csrf_token
        self.pid = pid
        self.http_port = http_port or port


class PortDetector:
    """Detector để tìm Antigravity server port"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def _log(self, message: str):
        """Log message nếu verbose mode"""
        if self.verbose:
            print(f"[DEBUG] {message}")
    
    def detect(self) -> Optional[ServerInfo]:
        """
        Detect Antigravity server port và authentication info
        
        Returns:
            ServerInfo nếu tìm thấy, None nếu không
        """
        self._log("Bắt đầu scan processes...")
        
        # Phương pháp 1: Tìm từ process names
        server_info = self._detect_from_process_name()
        if server_info:
            return server_info
        
        # Phương pháp 2: Scan ports trong range
        self._log("Không tìm thấy từ process name, scanning port range...")
        server_info = self._scan_port_range()
        if server_info:
            return server_info
        
        return None
    
    def _detect_from_process_name(self) -> Optional[ServerInfo]:
        """Detect từ process names"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_name = proc.info['name'].lower()
                
                # Check xem có phải Antigravity process không
                is_antigravity = any(
                    ag_name in proc_name 
                    for ag_name in ANTIGRAVITY_PROCESS_NAMES
                )
                
                if not is_antigravity:
                    continue
                
                self._log(f"Tìm thấy process: {proc_name} (PID: {proc.info['pid']})")
                
                # Parse command line để extract port
                cmdline = proc.info.get('cmdline', [])
                if not cmdline:
                    continue
                
                port = self._extract_port_from_cmdline(cmdline)
                if port:
                    self._log(f"Extracted port: {port}")
                    
                    # Try to get CSRF token (simplified - có thể cần adjust)
                    csrf_token = self._get_csrf_token(proc)
                    
                    return ServerInfo(
                        port=port,
                        csrf_token=csrf_token,
                        pid=proc.info['pid']
                    )
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return None
    
    def _extract_port_from_cmdline(self, cmdline: list) -> Optional[int]:
        """
        Extract port từ command line arguments
        
        Args:
            cmdline: List of command line arguments
            
        Returns:
            Port number nếu tìm thấy, None nếu không
        """
        # Join cmdline thành string để parse
        cmd_str = ' '.join(cmdline)
        
        # Pattern để tìm port (các dạng thường gặp:  --port=XXXX, --port XXXX, :XXXX)
        patterns = [
            r'--port[=\s]+(\d+)',
            r'--connect-port[=\s]+(\d+)',
            r':(\d{5})',  # 5-digit port number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, cmd_str)
            if match:
                port = int(match.group(1))
                if PORT_RANGE_START <= port <= PORT_RANGE_END:
                    return port
        
        return None
    
    def _get_csrf_token(self, proc: psutil.Process) -> str:
        """
        Lấy CSRF token từ process (simplified implementation)
        
        Args:
            proc: psutil Process object
            
        Returns:
            CSRF token string hoặc empty string
        """
        # TODO: Implementation phức tạp hơn có thể cần đọc từ env vars
        # hoặc config files. Tạm thời return empty string.
        # Extension VSCode thường lấy từ localStorage hoặc secret storage.
        return ""
    
    def _scan_port_range(self) -> Optional[ServerInfo]:
        """
        Scan port range để tìm server đang listen
        (Fallback method - chậm hơn)
        """
        import socket
        
        self._log(f"Scanning port range {PORT_RANGE_START}-{PORT_RANGE_END}...")
        
        # Lấy danh sách ports đang được sử dụng
        connections = psutil.net_connections(kind='inet')
        listening_ports = set()
        
        for conn in connections:
            if conn.status == 'LISTEN' and conn.laddr:
                port = conn.laddr.port
                if PORT_RANGE_START <= port <= PORT_RANGE_END:
                    listening_ports.add(port)
        
        self._log(f"Tìm thấy {len(listening_ports)} ports đang listen trong range")
        
        # Test từng port
        for port in sorted(listening_ports):
            if self._test_port_is_antigravity(port):
                self._log(f"Port {port} có vẻ là Antigravity server")
                return ServerInfo(port=port)
        
        return None
    
    def _test_port_is_antigravity(self, port: int) -> bool:
        """
        Test xem port có phải là Antigravity server không
        (Simplified - chỉ check xem có connectable không)
        """
        import socket
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except:
            return False
