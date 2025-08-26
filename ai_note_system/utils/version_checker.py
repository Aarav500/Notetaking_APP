"""
Version checker module for AI Note System.
Provides utilities for checking package versions and compatibility.
"""

import logging
import importlib.metadata
import re
from typing import Dict, List, Optional, Tuple, Union

# Create a logger for this module
logger = logging.getLogger("ai_note_system.utils.version_checker")

# Define version requirements for critical dependencies
VERSION_REQUIREMENTS = {
    # Core dependencies
    "pyyaml": ">=6.0",
    "python-dotenv": ">=1.0.0",
    "requests": ">=2.28.0",
    "sqlalchemy": ">=2.0.0",
    
    # API clients
    "openai": ">=1.0.0",
    "notion-client": ">=2.0.0",
    
    # PDF processing
    "PyMuPDF": ">=1.20.0",
    
    # YouTube processing
    "yt-dlp": ">=2023.3.4",
    "youtube-transcript-api": ">=0.6.0",
    
    # Embeddings
    "sentence-transformers": ">=2.2.2",
    
    # Web & API
    "fastapi": ">=0.95.0",
    "uvicorn": ">=0.22.0",
}

def parse_version_requirement(requirement: str) -> Tuple[str, str, str]:
    """
    Parse a version requirement string into operator and version.
    
    Args:
        requirement (str): Version requirement string (e.g., ">=1.0.0")
        
    Returns:
        Tuple[str, str, str]: Tuple of (package_name, operator, version)
    """
    match = re.match(r'^([a-zA-Z0-9_-]+)\s*([<>=!~]+)\s*([0-9.]+)$', requirement)
    if match:
        return match.groups()
    
    # If no operator is specified, assume "=="
    match = re.match(r'^([a-zA-Z0-9_-]+)\s*([0-9.]+)$', requirement)
    if match:
        package_name, version = match.groups()
        return package_name, "==", version
    
    # If only package name is specified, assume any version is acceptable
    if re.match(r'^[a-zA-Z0-9_-]+$', requirement):
        return requirement, "", ""
    
    logger.warning(f"Could not parse version requirement: {requirement}")
    return "", "", ""

def compare_versions(version1: str, operator: str, version2: str) -> bool:
    """
    Compare two version strings using the specified operator.
    
    Args:
        version1 (str): First version string
        operator (str): Comparison operator (==, !=, >, >=, <, <=)
        version2 (str): Second version string
        
    Returns:
        bool: True if the comparison is satisfied, False otherwise
    """
    # Convert version strings to tuples of integers
    v1_parts = [int(x) for x in version1.split('.')]
    v2_parts = [int(x) for x in version2.split('.')]
    
    # Pad with zeros to make the tuples the same length
    max_length = max(len(v1_parts), len(v2_parts))
    v1_parts.extend([0] * (max_length - len(v1_parts)))
    v2_parts.extend([0] * (max_length - len(v2_parts)))
    
    # Compare the tuples
    if operator == "==":
        return v1_parts == v2_parts
    elif operator == "!=":
        return v1_parts != v2_parts
    elif operator == ">":
        return v1_parts > v2_parts
    elif operator == ">=":
        return v1_parts >= v2_parts
    elif operator == "<":
        return v1_parts < v2_parts
    elif operator == "<=":
        return v1_parts <= v2_parts
    else:
        logger.warning(f"Unknown operator: {operator}")
        return False

def get_installed_version(package_name: str) -> Optional[str]:
    """
    Get the installed version of a package.
    
    Args:
        package_name (str): Name of the package
        
    Returns:
        Optional[str]: Installed version if the package is installed, None otherwise
    """
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None

def check_package_version(package_name: str, requirement: str) -> Tuple[bool, Optional[str], str]:
    """
    Check if the installed version of a package meets the requirement.
    
    Args:
        package_name (str): Name of the package
        requirement (str): Version requirement string (e.g., ">=1.0.0")
        
    Returns:
        Tuple[bool, Optional[str], str]: Tuple of (is_compatible, installed_version, message)
    """
    installed_version = get_installed_version(package_name)
    
    if installed_version is None:
        return False, None, f"Package {package_name} is not installed"
    
    # If no requirement is specified, any version is acceptable
    if not requirement:
        return True, installed_version, f"Package {package_name} is installed (version {installed_version})"
    
    # Parse the requirement
    _, operator, required_version = parse_version_requirement(requirement)
    
    # If no operator or required version is specified, any version is acceptable
    if not operator or not required_version:
        return True, installed_version, f"Package {package_name} is installed (version {installed_version})"
    
    # Compare the versions
    is_compatible = compare_versions(installed_version, operator, required_version)
    
    if is_compatible:
        return True, installed_version, f"Package {package_name} {installed_version} meets requirement {operator} {required_version}"
    else:
        return False, installed_version, f"Package {package_name} {installed_version} does not meet requirement {operator} {required_version}"

def check_dependencies(dependencies: Dict[str, str] = None) -> Dict[str, Dict[str, Union[bool, str, None]]]:
    """
    Check if the installed versions of dependencies meet the requirements.
    
    Args:
        dependencies (Dict[str, str], optional): Dictionary of package names and version requirements.
            If None, uses the predefined VERSION_REQUIREMENTS.
            
    Returns:
        Dict[str, Dict[str, Union[bool, str, None]]]: Dictionary of package names and check results
    """
    if dependencies is None:
        dependencies = VERSION_REQUIREMENTS
    
    results = {}
    
    for package_name, requirement in dependencies.items():
        is_compatible, installed_version, message = check_package_version(package_name, requirement)
        
        results[package_name] = {
            "is_compatible": is_compatible,
            "installed_version": installed_version,
            "required_version": requirement,
            "message": message
        }
    
    return results

def log_dependency_check_results(results: Dict[str, Dict[str, Union[bool, str, None]]]) -> None:
    """
    Log the results of a dependency check.
    
    Args:
        results (Dict[str, Dict[str, Union[bool, str, None]]]): Results from check_dependencies
    """
    logger.info("Dependency check results:")
    
    for package_name, result in results.items():
        if result["is_compatible"]:
            logger.info(f"  ✓ {result['message']}")
        else:
            if result["installed_version"] is None:
                logger.warning(f"  ✗ {result['message']}")
            else:
                logger.error(f"  ✗ {result['message']}")

def get_incompatible_dependencies(results: Dict[str, Dict[str, Union[bool, str, None]]]) -> Dict[str, Dict[str, Union[bool, str, None]]]:
    """
    Get a dictionary of incompatible dependencies from check results.
    
    Args:
        results (Dict[str, Dict[str, Union[bool, str, None]]]): Results from check_dependencies
        
    Returns:
        Dict[str, Dict[str, Union[bool, str, None]]]: Dictionary of incompatible dependencies
    """
    return {
        package_name: result
        for package_name, result in results.items()
        if not result["is_compatible"]
    }

def format_dependency_check_message(results: Dict[str, Dict[str, Union[bool, str, None]]]) -> str:
    """
    Format a human-readable message from dependency check results.
    
    Args:
        results (Dict[str, Dict[str, Union[bool, str, None]]]): Results from check_dependencies
        
    Returns:
        str: Formatted message
    """
    incompatible = get_incompatible_dependencies(results)
    
    if not incompatible:
        return "All dependencies are compatible."
    
    message = "The following dependencies are incompatible:\n"
    
    for package_name, result in incompatible.items():
        if result["installed_version"] is None:
            message += f"  - {package_name}: Not installed (required: {result['required_version']})\n"
        else:
            message += f"  - {package_name}: Installed version {result['installed_version']} does not meet requirement {result['required_version']}\n"
    
    message += "\nPlease install the required versions of these dependencies."
    
    return message