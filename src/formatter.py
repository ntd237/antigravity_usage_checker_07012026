"""
Formatter Module - Format và display quota data với colors & progress bars

Author: ntd237
"""

from colorama import Fore, Back, Style, init
from .api_client import QuotaData, QuotaModel
from .utils import format_time_remaining

# Initialize colorama cho cross-platform color support
init(autoreset=True)


class QuotaFormatter:
    """Formatter để display quota data đẹp mắt"""
    
    def __init__(self):
        # Unicode characters cho progress bar
        self.filled_char = "█"
        self.empty_char = "░"
        self.bar_length = 10
    
    def format_and_print(self, quota_data: QuotaData, from_cache: bool = False, cache_age: str = None):
        """
        Format và print quota data
        
        Args:
            quota_data: QuotaData object
            from_cache: Có phải từ cache không
            cache_age: Cache age string nếu from_cache
        """
        print()
        print(f"{Fore.CYAN}🚀 Antigravity Usage Monitor{Style.RESET_ALL}")
        
        if from_cache and cache_age:
            print(f"{Fore.YELLOW}⚠️  Using cached data from {cache_age}{Style.RESET_ALL}")
        
        # Separator
        separator = "─" * 70
        print(separator)
        
        # Header
        print(f"{'Model':<25} {'Used':<6} {'Limit':<6} {'Left':<6} {'Progress':<12} {'Reset'}")
        print(separator)
        
        # Print từng model
        for model in quota_data.models:
            self._print_model_row(model)
        
        print(separator)
        
        # Total
        self._print_total(quota_data)
        
        print(separator)
        print()
    
    def _print_model_row(self, model: QuotaModel):
        """Print một row cho model"""
        # Truncate model name nếu quá dài
        display_name = model.model_name[:23] if len(model.model_name) > 23 else model.model_name
        
        # Progress bar
        progress_bar = self._create_progress_bar(model.percentage_used)
        
        # Color dựa vào % remaining
        remaining_pct = 100 - model.percentage_used
        color = self._get_color_for_percentage(remaining_pct)
        
        # Reset time
        reset_str = format_time_remaining(model.reset_time)
        
        # Format row
        print(
            f"{display_name:<25} "
            f"{color}{model.used:>4}{Style.RESET_ALL}   "
            f"{model.limit:>4}   "
            f"{color}{model.remaining:>4}{Style.RESET_ALL}   "
            f"{color}{progress_bar}{Style.RESET_ALL} {color}{model.percentage_used:>2}%{Style.RESET_ALL} "
            f"{reset_str}"
        )
    
    def _create_progress_bar(self, percentage: int) -> str:
        """
        Tạo unicode progress bar
        
        Args:
            percentage: % đã sử dụng (0-100)
            
        Returns:
            Progress bar string
        """
        filled_length = int(self.bar_length * percentage / 100)
        empty_length = self.bar_length - filled_length
        
        bar = self.filled_char * filled_length + self.empty_char * empty_length
        return bar
    
    def _get_color_for_percentage(self, remaining_pct: int) -> str:
        """
        Lấy color code dựa vào % remaining
        
        Args:
            remaining_pct: % còn lại (0-100)
            
        Returns:
            Colorama color code
        """
        if remaining_pct > 50:
            return Fore.GREEN
        elif remaining_pct > 20:
            return Fore.YELLOW
        else:
            return Fore.RED
    
    def _print_total(self, quota_data: QuotaData):
        """Print total row"""
        total_remaining_pct = 0
        if quota_data.total_limit > 0:
            total_remaining_pct = int((quota_data.total_limit - quota_data.total_used) / quota_data.total_limit * 100)
        
        color = self._get_color_for_percentage(total_remaining_pct)
        
        print(
            f"{Fore.CYAN}📊 Total:{Style.RESET_ALL} "
            f"{color}{quota_data.total_used}/{quota_data.total_limit} used "
            f"({total_remaining_pct}% remaining){Style.RESET_ALL}"
        )
