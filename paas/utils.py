import frappe
from functools import wraps

# Try to import from rokct, otherwise use fallback
try:
    from rokct.rokct.utils.subscription_checker import check_subscription_feature as rokct_check_feature
    from rokct.rokct.tenant.api import get_subscription_details as rokct_get_details
    HAS_ROKCT = True
except ImportError:
    HAS_ROKCT = False

def check_subscription_feature(feature_module):
    """
    Decorator to check if a feature is enabled in the subscription.
    If rokct is installed, it delegates to rokct's checker.
    If not, it allows the feature (standalone mode).
    """
    if HAS_ROKCT:
        return rokct_check_feature(feature_module)
    
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # In standalone mode, we assume all features are enabled
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def get_subscription_details():
    """
    Retrieves subscription details.
    If rokct is installed, delegates to rokct.
    If not, returns a default 'Active' subscription with all modules.
    """
    if HAS_ROKCT:
        return rokct_get_details()
    
    # Default fallback for standalone PaaS
    return {
        "status": "Active",
        "plan": "Standalone",
        "modules": ["all"], 
        "subscription_cache_duration": 86400
    }
