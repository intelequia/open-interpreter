"""
Proxy configuration utilities for handling HTTP/HTTPS proxies in downloads and API calls.
"""

import os
from typing import Dict, Optional


def get_proxy_config() -> Dict[str, str]:
    """
    Get proxy configuration from environment variables.
    
    Supports standard proxy environment variables:
    - http_proxy / HTTP_PROXY
    - https_proxy / HTTPS_PROXY
    - all_proxy / ALL_PROXY
    
    Returns:
        Dictionary with 'http' and 'https' keys for use with requests library.
        Returns empty dict if no proxies are configured.
    """
    proxies = {}
    
    # Check for http proxy (case-insensitive)
    http_proxy = os.getenv('http_proxy') or os.getenv('HTTP_PROXY')
    if http_proxy:
        proxies['http'] = http_proxy
    
    # Check for https proxy (case-insensitive)
    https_proxy = os.getenv('https_proxy') or os.getenv('HTTPS_PROXY')
    if https_proxy:
        proxies['https'] = https_proxy
    
    # Fallback to all_proxy if specific proxies not set
    all_proxy = os.getenv('all_proxy') or os.getenv('ALL_PROXY')
    if all_proxy:
        if not proxies.get('http'):
            proxies['http'] = all_proxy
        if not proxies.get('https'):
            proxies['https'] = all_proxy
    
    return proxies if proxies else {}


def get_wget_proxy_args() -> list:
    """
    Get wget command-line arguments for proxy configuration.
    
    Returns:
        List of command-line arguments to pass to wget.
        Returns empty list if no proxies are configured.
    """
    args = []
    
    http_proxy = os.getenv('http_proxy') or os.getenv('HTTP_PROXY')
    if http_proxy:
        args.extend(['-e', f'http_proxy={http_proxy}'])
    
    https_proxy = os.getenv('https_proxy') or os.getenv('HTTPS_PROXY')
    if https_proxy:
        args.extend(['-e', f'https_proxy={https_proxy}'])
    
    return args
