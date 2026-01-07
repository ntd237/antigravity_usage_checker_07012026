"""
CLI Module - Command line interface entry point
"""

import sys
import argparse
from colorama import Fore, Style

from .port_detector import PortDetector
from .api_client import APIClient
from .formatter import QuotaFormatter
from .cache_manager import CacheManager


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Antigravity Usage Checker - Kiểm tra quota AI models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agcheck              Kiểm tra quota (default)
  agcheck --verbose    Hiển thị debug logs
  agcheck --no-cache   Không sử dụng cache
  
Author: ntd237 (ntd237.work@gmail.com)
GitHub: https://github.com/ntd237/antigravity_usage_checker_07012026
        """
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Hiển thị debug logs chi tiết'
    )
    
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Không sử dụng cached data, luôn fetch từ server'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='agcheck 1.0.0'
    )
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()
    
    # Initialize components
    detector = PortDetector(verbose=args.verbose)
    cache_mgr = CacheManager()
    formatter = QuotaFormatter()
    
    quota_data = None
    from_cache = False
    cache_age = None
    
    # Step 1: Scan cho Antigravity server
    print(f"{Fore.CYAN}🔍 Scanning for Antigravity server...{Style.RESET_ALL}")
    
    server_info = detector.detect()
    
    if server_info:
        print(f"{Fore.GREEN}✅ Found server on port {server_info.port} (PID: {server_info.pid}){Style.RESET_ALL}")
        
        # Step 2: Fetch quota data
        print(f"{Fore.CYAN}📡 Fetching quota data...{Style.RESET_ALL}")
        
        client = APIClient(
            port=server_info.port,
            csrf_token=server_info.csrf_token,
            http_port=server_info.http_port,
            verbose=args.verbose
        )
        
        quota_data = client.fetch_quota()
        
        # Save to cache (nếu fetch thành công)
        if quota_data and not args.no_cache:
            cache_mgr.save(quota_data)
    
    else:
        print(f"{Fore.YELLOW}⚠️  Server not found{Style.RESET_ALL}")
        
        # Try load từ cache nếu không có --no-cache
        if not args.no_cache:
            print(f"{Fore.CYAN}💾 Trying to load from cache...{Style.RESET_ALL}")
            quota_data = cache_mgr.load()
            
            if quota_data:
                from_cache = True
                cache_age = cache_mgr.get_cache_age()
            else:
                print(f"{Fore.RED}❌ No valid cache found{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Cannot proceed without server (--no-cache flag is set){Style.RESET_ALL}")
    
    # Step 3: Display results
    if quota_data:
        formatter.format_and_print(quota_data, from_cache, cache_age)
        return 0
    else:
        print()
        print(f"{Fore.RED}❌ Không thể lấy quota data{Style.RESET_ALL}")
        print()
        print("Vui lòng:")
        print("  1. Đảm bảo Antigravity IDE đang chạy")
        print("  2. Thử lại với --verbose để xem chi tiết")
        print()
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Cancelled by user{Style.RESET_ALL}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        sys.exit(1)
