from django.db.models import Sum
from .models import Candidate

STORAGE_LIMIT = 1024  * 1024  * 1024  

def check_storage_limit(user, new_file_size):
    """Check if user can upload a file of given size."""
    
    if not user.email.lower().endswith('@dspe.in'):
        return True, "", 0
    
    print(f"🔍 CHECK CALLED for user: {user.email}")
    print(f"📁 File size: {new_file_size} bytes ({new_file_size/1024:.2f} KB)")
    print(f"📊 Limit: {STORAGE_LIMIT} bytes ({STORAGE_LIMIT/1024:.2f} KB)")
    
    total_used = Candidate.objects.filter(
        uploaded_by=user
    ).aggregate(total_size=Sum('file_size'))['total_size'] or 0
    
    print(f"📊 Already used: {total_used} bytes ({total_used/1024:.2f} KB)")
    print(f"📊 Total would be: {total_used + new_file_size} bytes ({(total_used + new_file_size)/1024:.2f} KB)")

    if total_used + new_file_size > STORAGE_LIMIT:
        used_mb = total_used / (1024 * 1024)
        limit_mb = STORAGE_LIMIT / (1024 * 1024)
        file_mb = new_file_size / (1024 * 1024)
        
        message = (
            f'Storage limit exceeded! Your storage limit is 1 GB. If you need more storage, please contact info@jmsadvisory.in. '
            
        )
        print(f"❌ REJECTED: {message}")
        return False, message, total_used

    print("✅ ALLOWED!")
    return True, "", total_used


def get_storage_usage(user):
    """
    Get storage usage information for a user.
    
    Returns: dict with storage metrics or None if user doesn't have limit
    """
    # ✅ Only track storage for @dspe.in users
    if not user.email.lower().endswith('@dspe.in'):
        return None

    total_used = Candidate.objects.filter(
        uploaded_by=user
    ).aggregate(total_size=Sum('file_size'))['total_size'] or 0

    remaining = max(0, STORAGE_LIMIT - total_used)
    percentage = (total_used / STORAGE_LIMIT) * 100 if STORAGE_LIMIT > 0 else 0

    return {
        'used_bytes': total_used,
        'used_kb': total_used / 1024,
        'used_mb': total_used / (1024 * 1024),
        'used_gb': total_used / (1024 * 1024 * 1024),
        
        'limit_bytes': STORAGE_LIMIT,
        'limit_kb': STORAGE_LIMIT / 1024,
        'limit_mb': STORAGE_LIMIT / (1024 * 1024),
        'limit_gb': STORAGE_LIMIT / (1024 * 1024 * 1024),
        
        'remaining_bytes': remaining,
        'remaining_mb': remaining / (1024 * 1024),
        'percentage': percentage,
        'is_low': percentage > 80,  # True if usage > 80%
        'is_critical': percentage > 95,  # True if usage > 95%
    }


def format_bytes(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"