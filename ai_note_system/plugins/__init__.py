"""
Plugin system for AI Note System.
Provides a framework for extending the system with custom plugins.
"""

import os
import sys
import logging
import importlib
import inspect
from typing import Dict, Any, List, Optional, Type, Callable, Union
from abc import ABC, abstractmethod

# Setup logging
logger = logging.getLogger("ai_note_system.plugins")