from django.core.cache import cache
import hashlib
import json

def get_cache_key(context, prompt_type):
    """
    Generate a cache key based on the context and prompt type.
    
    Args:
        context (str): The context string used in the prompt
        prompt_type (str): Type of prompt (e.g., 'feedback', 'recommendation')
    
    Returns:
        str: A unique cache key
    """
    context_hash = hashlib.md5(context.encode()).hexdigest()
    return f"openai_response:{prompt_type}:{context_hash}"

def get_cached_response(context, prompt_type, cache_timeout=3600):  # 1 hour default timeout
    """
    Get a cached OpenAI response or return None if not found.
    
    Args:
        context (str): The context string used in the prompt
        prompt_type (str): Type of prompt
        cache_timeout (int): Cache timeout in seconds
        
    Returns:
        str or None: The cached response if found, None otherwise
    """
    cache_key = get_cache_key(context, prompt_type)
    return cache.get(cache_key)

def cache_response(context, prompt_type, response, timeout=3600):
    """
    Cache an OpenAI response.
    
    Args:
        context (str): The context string used in the prompt
        prompt_type (str): Type of prompt
        response (str): The response to cache
        timeout (int): Cache timeout in seconds
    """
    cache_key = get_cache_key(context, prompt_type)
    cache.set(cache_key, response, timeout)