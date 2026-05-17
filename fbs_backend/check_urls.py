import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()
from django.urls import get_resolver

def print_urls(patterns, prefix=''):
    for pattern in patterns:
        if hasattr(pattern, 'url_patterns'):
            print_urls(pattern.url_patterns, prefix + str(pattern.pattern))
        else:
            print(f"{prefix}{str(pattern.pattern)} -> {pattern.callback.__name__ if hasattr(pattern.callback, '__name__') else pattern.callback}")

print_urls(get_resolver().url_patterns)
