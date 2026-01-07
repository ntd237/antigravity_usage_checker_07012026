"""
Port Detector Module - Detect Antigravity server port và authentication info
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
        
        # Phương pháp 1: Dùng PowerShell để tìm language_server (chính xác nhất trên Windows)
        if sys.platform == 'win32':
            server_info = self._detect_with_powershell()
            if server_info and server_info.csrf_token:
                return server_info
        
        # Phương pháp 2: Tìm từ process names với psutil
        server_info = self._detect_from_process_name()
        if server_info:
            return server_info
        
        # Phương pháp 3: Scan ports trong range
        self._log("Không tìm thấy từ process name, scanning port range...")
        server_info = self._scan_port_range()
        if server_info:
            return server_info
        
        return None
    
    def _detect_with_powershell(self) -> Optional[ServerInfo]:
        """
        Dùng PowerShell để tìm language_server process (Windows only)
        Theo cách của tungcorn/antigravity-usage-checker
        """
        import subprocess
        import json
        
        try:
            # PowerShell command để tìm language_server với extension_server_port trong cmdline
            ps_cmd = '''
            Get-CimInstance Win32_Process | Where-Object { 
                $_.CommandLine -like "*extension_server_port*" -and $_.Name -like "*language_server*" 
            } | Select-Object -First 1 ProcessId, CommandLine | ConvertTo-Json -Compress
            '''
            
            self._log("Running PowerShell to find language_server...")
            result = subprocess.run(
                ['powershell', '-NoProfile', '-Command', ps_cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout.strip()
            if not output or output == 'null':
                self._log("PowerShell: language_server not found")
                return None
            
            # Parse JSON output
            data = json.loads(output)
            pid = data.get('ProcessId', 0)
            cmdline = data.get('CommandLine', '')
            
            self._log(f"PowerShell found process PID: {pid}")
            
            # Extract extension_server_port
            http_port_match = re.search(r'--extension_server_port\s+(\d+)', cmdline)
            http_port = int(http_port_match.group(1)) if http_port_match else 0
            
            # Extract csrf_token (có thể là --csrf_token hoặc variations)
            csrf_patterns = [
                r'--csrf_token\s+([a-zA-Z0-9_-]+)',
                r'--[a-z_]*csrf[a-z_]*\s+([a-zA-Z0-9_-]{20,})',
            ]
            
            csrf_token = ""
            for pattern in csrf_patterns:
                match = re.search(pattern, cmdline)
                if match:
                    csrf_token = match.group(1)
                    break
            
            if not http_port:
                self._log("PowerShell: Could not extract port")
                return None
            
            # Tìm API port bằng cách test các listening ports của process
            connect_port = self._find_api_port_for_pid(pid, csrf_token) or http_port
            
            self._log(f"PowerShell detected: connect={connect_port}, http={http_port}, csrf={'YES' if csrf_token else 'NO'}")
            
            return ServerInfo(
                port=connect_port,
                http_port=http_port,
                csrf_token=csrf_token,
                pid=pid
            )
            
        except Exception as e:
            self._log(f"PowerShell detection failed: {e}")
            return None
    
    def _find_api_port_for_pid(self, pid: int, csrf_token: str) -> Optional[int]:
        """Tìm port API cho một PID bằng cách test các listening ports"""
        import subprocess
        
        try:
            # Dùng netstat để lấy các port đang listen của process
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            ports = []
            pid_str = str(pid)
            for line in result.stdout.split('\n'):
                if 'LISTENING' in line and line.strip().endswith(pid_str):
                    # Extract port từ 127.0.0.1:PORT
                    match = re.search(r'127\.0\.0\.1:(\d+)', line)
                    if match:
                        ports.append(int(match.group(1)))
            
            self._log(f"Found {len(ports)} listening ports for PID {pid}: {ports}")
            
            # Test từng port để tìm API port
            for port in ports:
                if self._test_api_port(port, csrf_token):
                    return port
            
            return ports[0] if ports else None
            
        except Exception as e:
            self._log(f"Error finding API port: {e}")
            return None
    
    def _test_api_port(self, port: int, csrf_token: str) -> bool:
        """Test xem port có respond với API không"""
        import requests
        
        try:
            url = f"https://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/GetUserStatus"
            headers = {
                'Content-Type': 'application/json',
                'Connect-Protocol-Version': '1',
            }
            if csrf_token:
                headers['X-Codeium-Csrf-Token'] = csrf_token
            
            response = requests.post(url, json={}, headers=headers, timeout=2, verify=False)
            return response.status_code == 200
        except:
            return False
    
    def _detect_from_process_name(self) -> Optional[ServerInfo]:
        """Đetếct từ process names"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_name = proc.info['name'].lower()
                
                # Prioritize language_server process
                is_language_server = "language_server" in proc_name
                is_antigravity = any(
                    ag_name in proc_name 
                    for ag_name in ANTIGRAVITY_PROCESS_NAMES
                )
                
                if not (is_language_server or is_antigravity):
                    continue
                
                self._log(f"Tìm thấy process: {proc_name} (PID: {proc.info['pid']})")
                
                # Parse command line để extract port và CSRF
                cmdline = proc.info.get('cmdline', [])
                if not cmdline:
                    continue
                
                # Extract CSRF token first
                csrf_token = self._get_csrf_token(proc)
                
                # Extract ports
                port = self._extract_port_from_cmdline(cmdline)
                http_port = self._extract_http_port_from_cmdline(cmdline)
                
                if port:  # We must have at least the main port
                    self._log(f"Extracted port: {port}, http: {http_port or port}, csrf: {'YES' if csrf_token else 'NO'}")
                    
                    return ServerInfo(
                        port=port,
                        csrf_token=csrf_token,
                        pid=proc.info['pid'],
                        http_port=http_port or port
                    )
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return None
    
    def _extract_port_from_cmdline(self, cmdline: list) -> Optional[int]:
        """
        Extract connect port từ command line arguments
        Tìm --api_server_port hoặc tương tự
        """
        cmd_str = ' '.join(cmdline)
        
        # Patterns để tìm port (prioritize api_server_port for connect)
        patterns = [
            r'--api_server_port[=\s]+(\d+)',
            r'--port[=\s]+(\d+)',
            r'--connect-port[=\s]+(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, cmd_str)
            if match:
                port = int(match.group(1))
                if PORT_RANGE_START <= port <= PORT_RANGE_END:
                    return port
        
        return None
    
    def _extract_http_port_from_cmdline(self, cmdline: list) -> Optional[int]:
        """
        Extract HTTP fallback port (extension_server_port)
        """
        cmd_str = ' '.join(cmdline)
        
        # Tìm extension_server_port
        match = re.search(r'--extension_server_port[=\s]+(\d+)', cmd_str)
        if match:
            return int(match.group(1))
        
        return None
    
    def _get_csrf_token(self, proc: psutil.Process) -> str:
        """
        Lấy CSRF token từ process command line arguments
        
        Args:
            proc: psutil Process object
            
        Returns:
            CSRF token string hoặc empty string
        """
        try:
            cmdline = proc.info.get('cmdline', [])
            if not cmdline:
                return ""
            
            # Join cmdline thành string để parse
            cmd_str = ' '.join(cmdline)
            
            # Tìm --api_server_csrf_token flag
            # Format: --api_server_csrf_token=TOKEN hoặc --api_server_csrf_token TOKEN
            patterns = [
                r'--api_server_csrf_token[=\s]+([a-zA-Z0-9\-_]+)',
                r'--api-server-csrf-token[=\s]+([a-zA-Z0-9\-_]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, cmd_str)
                if match:
                    token = match.group(1).strip()
                    self._log(f"Found CSRF token: {token[:6]}...{token[-4:]}")
                    return token
            
            self._log("CSRF token not found in command line")
            return ""
            
        except Exception as e:
            self._log(f"Error extracting CSRF token: {e}")
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
