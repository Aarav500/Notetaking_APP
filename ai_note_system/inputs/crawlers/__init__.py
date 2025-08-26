"""
Crawlers package for AI Note System.
Contains crawler implementations for various sources.
"""

from .base_crawler import BaseCrawler
from .wikipedia_crawler import WikipediaCrawler

__all__ = [
    'BaseCrawler',
    'WikipediaCrawler',
]