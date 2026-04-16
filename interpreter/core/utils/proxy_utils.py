"""
Proxy configuration utilities for handling HTTP/HTTPS proxies in downloads and API calls.
"""

import os
from typing import Dict, Optional
from urllib.parse import urlparse


def _should_bypass_proxy(url: str) -> bool:
    """
    Check if a URL should bypass the proxy based on NO_PROXY setting.
    
    Args:
        url: The URL to check
        
    Returns:
        True if the URL should bypass proxy, False otherwise
    """
    no_proxy = os.getenv('no_proxy') or os.getenv('NO_PROXY')
    if not no_proxy:
        return False
    
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or parsed.netloc
        
        # Split NO_PROXY by comma and process each pattern
        for pattern in no_proxy.split(','):
            pattern = pattern.strip()
            if not pattern:
                continue
            
            # Handle wildcard patterns
            if pattern.startswith('*.'):
                # Domain suffix match: *.example.com matches subdomain.example.com
                domain_suffix = pattern[2:]  # Remove '*.'
                if hostname.endswith(domain_suffix) or hostname == domain_suffix[2:]:
                    return True
            elif pattern.startswith('.'):
                # Domain suffix match: .example.com matches example.com and *.example.com
                if hostname.endswith(pattern) or hostname == pattern[1:]:
                    return True
            else:
                # Exact match (including localhost, IP addresses, etc.)
                if hostname == pattern or hostname.startswith(pattern):
                    return True
    except Exception:
        pass
    
    return False


def get_proxy_config() -> Dict[str, str]:
    """
    Get proxy configuration from environment variables.
    
    Supports standard proxy environment variables:
    - http_proxy / HTTP_PROXY
    - https_proxy / HTTPS_PROXY
    - all_proxy / ALL_PROXY
    - no_proxy / NO_PROXY (for bypassing proxy for specific hosts)
    
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
    
    # Add no_proxy if configured
    no_proxy = os.getenv('no_proxy') or os.getenv('NO_PROXY')
    if no_proxy:
        args.extend(['-e', f'no_proxy={no_proxy}'])
    
    return args
