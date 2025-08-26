"""
Exam Research Mode module for AI Note System.
Provides functionality to research exam-related resources and materials.
"""

import os
import json
import logging
import re
import time
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Setup logging
logger = logging.getLogger("ai_note_system.learning.exam_research_mode")

class ExamResearchMode:
    """
    Exam Research Mode class for fetching exam-related resources.
    Retrieves past papers, examiner reports, commonly tested topics, and expression tips.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Exam Research Mode.
        
        Args:
            config (Dict[str, Any], optional): Configuration dictionary
        """
        self.config = config or {}
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        
        # Configure search sources
        self.search_sources = self.config.get("search_sources", {
            "past_papers": True,
            "examiner_reports": True,
            "syllabus": True,
            "study_guides": True,
            "forums": True
        })
        
        # Configure resource limits
        self.resource_limits = self.config.get("resource_limits", {
            "max_papers": 10,
            "max_reports": 5,
            "max_guides": 5,
            "max_forum_threads": 3
        })
        
        logger.debug("Initialized ExamResearchMode")
    
    def research_exam(self, 
                     subject: str,
                     exam_board: Optional[str] = None,
                     level: Optional[str] = None,
                     year_range: Optional[List[int]] = None,
                     output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Research exam resources for a specific subject and exam board.
        
        Args:
            subject (str): The subject to research (e.g., "Mathematics", "Physics")
            exam_board (str, optional): The exam board (e.g., "AQA", "Edexcel", "Cambridge")
            level (str, optional): The level (e.g., "GCSE", "A-Level", "IB", "University")
            year_range (List[int], optional): Range of years to search for (e.g., [2018, 2023])
            output_dir (str, optional): Directory to save downloaded resources
            
        Returns:
            Dict[str, Any]: Research results
        """
        logger.info(f"Researching exam resources for {subject} ({exam_board or 'Any board'}, {level or 'Any level'})")
        
        # Create output directory if needed
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Initialize results
        results = {
            "subject": subject,
            "exam_board": exam_board,
            "level": level,
            "year_range": year_range,
            "timestamp": datetime.now().isoformat(),
            "past_papers": [],
            "examiner_reports": [],
            "common_topics": [],
            "expression_tips": [],
            "resources": []
        }
        
        # Search for past papers
        if self.search_sources.get("past_papers", True):
            past_papers = self._search_past_papers(subject, exam_board, level, year_range)
            results["past_papers"] = past_papers
            
            # Download past papers if output directory is provided
            if output_dir and past_papers:
                self._download_resources(past_papers, os.path.join(output_dir, "past_papers"))
        
        # Search for examiner reports
        if self.search_sources.get("examiner_reports", True):
            examiner_reports = self._search_examiner_reports(subject, exam_board, level, year_range)
            results["examiner_reports"] = examiner_reports
            
            # Download examiner reports if output directory is provided
            if output_dir and examiner_reports:
                self._download_resources(examiner_reports, os.path.join(output_dir, "examiner_reports"))
        
        # Extract common topics
        common_topics = self._extract_common_topics(subject, exam_board, level, results)
        results["common_topics"] = common_topics
        
        # Get expression tips
        expression_tips = self._get_expression_tips(subject, level)
        results["expression_tips"] = expression_tips
        
        # Find additional resources
        additional_resources = self._find_additional_resources(subject, exam_board, level)
        results["resources"] = additional_resources
        
        # Save results if output directory is provided
        if output_dir:
            results_path = os.path.join(output_dir, "research_results.json")
            with open(results_path, "w") as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Research results saved to {results_path}")
        
        logger.info(f"Exam research completed for {subject}")
        return results
    
    def _search_past_papers(self, 
                           subject: str,
                           exam_board: Optional[str] = None,
                           level: Optional[str] = None,
                           year_range: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Search for past papers.
        
        Args:
            subject (str): The subject
            exam_board (str, optional): The exam board
            level (str, optional): The level
            year_range (List[int], optional): Range of years to search for
            
        Returns:
            List[Dict[str, Any]]: List of past papers
        """
        logger.debug(f"Searching for past papers: {subject}, {exam_board}, {level}")
        
        papers = []
        max_papers = self.resource_limits.get("max_papers", 10)
        
        # Build search query
        query = f"{subject} past papers"
        if exam_board:
            query += f" {exam_board}"
        if level:
            query += f" {level}"
        
        # Search for papers using various sources
        try:
            # Search on exam board websites
            if exam_board:
                board_papers = self._search_exam_board_website(subject, exam_board, level, "past_papers")
                papers.extend(board_papers)
            
            # Search on general past paper repositories
            repo_papers = self._search_paper_repositories(subject, exam_board, level)
            papers.extend(repo_papers)
            
            # Filter by year range if provided
            if year_range and len(year_range) == 2:
                min_year, max_year = year_range
                papers = [p for p in papers if p.get("year") and min_year <= p.get("year") <= max_year]
            
            # Limit the number of papers
            papers = papers[:max_papers]
            
        except Exception as e:
            logger.error(f"Error searching for past papers: {str(e)}")
        
        logger.info(f"Found {len(papers)} past papers for {subject}")
        return papers
    
    def _search_examiner_reports(self, 
                               subject: str,
                               exam_board: Optional[str] = None,
                               level: Optional[str] = None,
                               year_range: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        """
        Search for examiner reports.
        
        Args:
            subject (str): The subject
            exam_board (str, optional): The exam board
            level (str, optional): The level
            year_range (List[int], optional): Range of years to search for
            
        Returns:
            List[Dict[str, Any]]: List of examiner reports
        """
        logger.debug(f"Searching for examiner reports: {subject}, {exam_board}, {level}")
        
        reports = []
        max_reports = self.resource_limits.get("max_reports", 5)
        
        # Build search query
        query = f"{subject} examiner report"
        if exam_board:
            query += f" {exam_board}"
        if level:
            query += f" {level}"
        
        # Search for reports using various sources
        try:
            # Search on exam board websites
            if exam_board:
                board_reports = self._search_exam_board_website(subject, exam_board, level, "examiner_reports")
                reports.extend(board_reports)
            
            # Filter by year range if provided
            if year_range and len(year_range) == 2:
                min_year, max_year = year_range
                reports = [r for r in reports if r.get("year") and min_year <= r.get("year") <= max_year]
            
            # Limit the number of reports
            reports = reports[:max_reports]
            
        except Exception as e:
            logger.error(f"Error searching for examiner reports: {str(e)}")
        
        logger.info(f"Found {len(reports)} examiner reports for {subject}")
        return reports
    
    def _search_exam_board_website(self, 
                                 subject: str,
                                 exam_board: str,
                                 level: Optional[str] = None,
                                 resource_type: str = "past_papers") -> List[Dict[str, Any]]:
        """
        Search for resources on exam board websites.
        
        Args:
            subject (str): The subject
            exam_board (str): The exam board
            level (str, optional): The level
            resource_type (str): Type of resource to search for
            
        Returns:
            List[Dict[str, Any]]: List of resources
        """
        resources = []
        
        # Map of exam boards to their websites
        board_websites = {
            "aqa": "https://www.aqa.org.uk",
            "edexcel": "https://qualifications.pearson.com",
            "ocr": "https://www.ocr.org.uk",
            "wjec": "https://www.wjec.co.uk",
            "cambridge": "https://www.cambridgeinternational.org",
            "ib": "https://www.ibo.org"
        }
        
        # Normalize exam board name
        exam_board_lower = exam_board.lower()
        
        # Check if we have a website for this exam board
        if exam_board_lower not in board_websites:
            logger.warning(f"No website information for exam board: {exam_board}")
            return resources
        
        # Get the website URL
        website_url = board_websites[exam_board_lower]
        
        # Implement board-specific search logic
        if exam_board_lower == "aqa":
            resources = self._search_aqa_website(website_url, subject, level, resource_type)
        elif exam_board_lower == "edexcel":
            resources = self._search_edexcel_website(website_url, subject, level, resource_type)
        elif exam_board_lower == "ocr":
            resources = self._search_ocr_website(website_url, subject, level, resource_type)
        else:
            # Generic search for other boards
            resources = self._search_generic_board_website(website_url, subject, level, resource_type)
        
        return resources
    
    def _search_aqa_website(self, 
                          website_url: str,
                          subject: str,
                          level: Optional[str] = None,
                          resource_type: str = "past_papers") -> List[Dict[str, Any]]:
        """
        Search for resources on the AQA website.
        
        Args:
            website_url (str): The website URL
            subject (str): The subject
            level (str, optional): The level
            resource_type (str): Type of resource to search for
            
        Returns:
            List[Dict[str, Any]]: List of resources
        """
        # This is a simplified implementation
        # In a real implementation, you would parse the AQA website structure
        
        # For demonstration purposes, return mock data
        if resource_type == "past_papers":
            return [
                {
                    "title": f"AQA {level} {subject} Paper 1 June 2022",
                    "url": f"{website_url}/example/paper1_2022.pdf",
                    "year": 2022,
                    "exam_board": "AQA",
                    "level": level,
                    "subject": subject,
                    "paper": "Paper 1",
                    "session": "June"
                },
                {
                    "title": f"AQA {level} {subject} Paper 2 June 2022",
                    "url": f"{website_url}/example/paper2_2022.pdf",
                    "year": 2022,
                    "exam_board": "AQA",
                    "level": level,
                    "subject": subject,
                    "paper": "Paper 2",
                    "session": "June"
                }
            ]
        elif resource_type == "examiner_reports":
            return [
                {
                    "title": f"AQA {level} {subject} Examiner Report June 2022",
                    "url": f"{website_url}/example/report_2022.pdf",
                    "year": 2022,
                    "exam_board": "AQA",
                    "level": level,
                    "subject": subject,
                    "session": "June"
                }
            ]
        else:
            return []
    
    def _search_edexcel_website(self, 
                              website_url: str,
                              subject: str,
                              level: Optional[str] = None,
                              resource_type: str = "past_papers") -> List[Dict[str, Any]]:
        """
        Search for resources on the Edexcel website.
        
        Args:
            website_url (str): The website URL
            subject (str): The subject
            level (str, optional): The level
            resource_type (str): Type of resource to search for
            
        Returns:
            List[Dict[str, Any]]: List of resources
        """
        # This is a simplified implementation
        # In a real implementation, you would parse the Edexcel website structure
        
        # For demonstration purposes, return mock data
        if resource_type == "past_papers":
            return [
                {
                    "title": f"Edexcel {level} {subject} Paper 1 June 2022",
                    "url": f"{website_url}/example/paper1_2022.pdf",
                    "year": 2022,
                    "exam_board": "Edexcel",
                    "level": level,
                    "subject": subject,
                    "paper": "Paper 1",
                    "session": "June"
                },
                {
                    "title": f"Edexcel {level} {subject} Paper 2 June 2022",
                    "url": f"{website_url}/example/paper2_2022.pdf",
                    "year": 2022,
                    "exam_board": "Edexcel",
                    "level": level,
                    "subject": subject,
                    "paper": "Paper 2",
                    "session": "June"
                }
            ]
        elif resource_type == "examiner_reports":
            return [
                {
                    "title": f"Edexcel {level} {subject} Examiner Report June 2022",
                    "url": f"{website_url}/example/report_2022.pdf",
                    "year": 2022,
                    "exam_board": "Edexcel",
                    "level": level,
                    "subject": subject,
                    "session": "June"
                }
            ]
        else:
            return []
    
    def _search_ocr_website(self, 
                          website_url: str,
                          subject: str,
                          level: Optional[str] = None,
                          resource_type: str = "past_papers") -> List[Dict[str, Any]]:
        """
        Search for resources on the OCR website.
        
        Args:
            website_url (str): The website URL
            subject (str): The subject
            level (str, optional): The level
            resource_type (str): Type of resource to search for
            
        Returns:
            List[Dict[str, Any]]: List of resources
        """
        # This is a simplified implementation
        # In a real implementation, you would parse the OCR website structure
        
        # For demonstration purposes, return mock data
        if resource_type == "past_papers":
            return [
                {
                    "title": f"OCR {level} {subject} Paper 1 June 2022",
                    "url": f"{website_url}/example/paper1_2022.pdf",
                    "year": 2022,
                    "exam_board": "OCR",
                    "level": level,
                    "subject": subject,
                    "paper": "Paper 1",
                    "session": "June"
                },
                {
                    "title": f"OCR {level} {subject} Paper 2 June 2022",
                    "url": f"{website_url}/example/paper2_2022.pdf",
                    "year": 2022,
                    "exam_board": "OCR",
                    "level": level,
                    "subject": subject,
                    "paper": "Paper 2",
                    "session": "June"
                }
            ]
        elif resource_type == "examiner_reports":
            return [
                {
                    "title": f"OCR {level} {subject} Examiner Report June 2022",
                    "url": f"{website_url}/example/report_2022.pdf",
                    "year": 2022,
                    "exam_board": "OCR",
                    "level": level,
                    "subject": subject,
                    "session": "June"
                }
            ]
        else:
            return []
    
    def _search_generic_board_website(self, 
                                    website_url: str,
                                    subject: str,
                                    level: Optional[str] = None,
                                    resource_type: str = "past_papers") -> List[Dict[str, Any]]:
        """
        Generic search for resources on exam board websites.
        
        Args:
            website_url (str): The website URL
            subject (str): The subject
            level (str, optional): The level
            resource_type (str): Type of resource to search for
            
        Returns:
            List[Dict[str, Any]]: List of resources
        """
        # This is a simplified implementation
        # In a real implementation, you would use a more sophisticated approach
        
        # For demonstration purposes, return empty list
        return []
    
    def _search_paper_repositories(self, 
                                 subject: str,
                                 exam_board: Optional[str] = None,
                                 level: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for papers in general repositories.
        
        Args:
            subject (str): The subject
            exam_board (str, optional): The exam board
            level (str, optional): The level
            
        Returns:
            List[Dict[str, Any]]: List of papers
        """
        # This is a simplified implementation
        # In a real implementation, you would search repositories like pastpapers.co, etc.
        
        # For demonstration purposes, return mock data
        return [
            {
                "title": f"{exam_board or 'General'} {level or 'All Levels'} {subject} Paper 1 June 2021",
                "url": "https://example.com/papers/paper1_2021.pdf",
                "year": 2021,
                "exam_board": exam_board or "Various",
                "level": level or "Various",
                "subject": subject,
                "paper": "Paper 1",
                "session": "June"
            },
            {
                "title": f"{exam_board or 'General'} {level or 'All Levels'} {subject} Paper 2 June 2021",
                "url": "https://example.com/papers/paper2_2021.pdf",
                "year": 2021,
                "exam_board": exam_board or "Various",
                "level": level or "Various",
                "subject": subject,
                "paper": "Paper 2",
                "session": "June"
            }
        ]
    
    def _extract_common_topics(self, 
                             subject: str,
                             exam_board: Optional[str] = None,
                             level: Optional[str] = None,
                             research_results: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Extract commonly tested topics from research results.
        
        Args:
            subject (str): The subject
            exam_board (str, optional): The exam board
            level (str, optional): The level
            research_results (Dict[str, Any], optional): Research results
            
        Returns:
            List[Dict[str, Any]]: List of common topics
        """
        logger.debug(f"Extracting common topics for {subject}")
        
        # This is a simplified implementation
        # In a real implementation, you would analyze past papers and examiner reports
        
        # For demonstration purposes, return mock data based on subject
        if subject.lower() == "mathematics":
            return [
                {
                    "topic": "Calculus",
                    "frequency": "Very High",
                    "subtopics": ["Differentiation", "Integration", "Applications"],
                    "typical_questions": ["Find the derivative of...", "Calculate the integral of..."],
                    "importance": "Essential"
                },
                {
                    "topic": "Algebra",
                    "frequency": "High",
                    "subtopics": ["Equations", "Functions", "Sequences"],
                    "typical_questions": ["Solve the equation...", "Find the domain of..."],
                    "importance": "Very Important"
                },
                {
                    "topic": "Statistics",
                    "frequency": "Medium",
                    "subtopics": ["Probability", "Distributions", "Hypothesis Testing"],
                    "typical_questions": ["Calculate the probability...", "Test the hypothesis..."],
                    "importance": "Important"
                }
            ]
        elif subject.lower() == "physics":
            return [
                {
                    "topic": "Mechanics",
                    "frequency": "Very High",
                    "subtopics": ["Kinematics", "Forces", "Energy"],
                    "typical_questions": ["Calculate the velocity...", "Find the force required..."],
                    "importance": "Essential"
                },
                {
                    "topic": "Electricity",
                    "frequency": "High",
                    "subtopics": ["Circuits", "Electromagnetism", "Fields"],
                    "typical_questions": ["Calculate the current...", "Explain how..."],
                    "importance": "Very Important"
                },
                {
                    "topic": "Waves",
                    "frequency": "Medium",
                    "subtopics": ["Properties", "Optics", "Sound"],
                    "typical_questions": ["Calculate the wavelength...", "Explain the phenomenon..."],
                    "importance": "Important"
                }
            ]
        else:
            # Generic topics for other subjects
            return [
                {
                    "topic": "Core Principles",
                    "frequency": "Very High",
                    "subtopics": ["Fundamental Concepts", "Key Theories", "Basic Applications"],
                    "typical_questions": ["Explain the concept of...", "Apply the theory to..."],
                    "importance": "Essential"
                },
                {
                    "topic": "Advanced Applications",
                    "frequency": "High",
                    "subtopics": ["Complex Problems", "Real-world Scenarios", "Case Studies"],
                    "typical_questions": ["Analyze the following scenario...", "Solve the problem..."],
                    "importance": "Very Important"
                },
                {
                    "topic": "Evaluation and Analysis",
                    "frequency": "Medium",
                    "subtopics": ["Critical Thinking", "Comparative Analysis", "Evaluation Techniques"],
                    "typical_questions": ["Evaluate the effectiveness...", "Compare and contrast..."],
                    "importance": "Important"
                }
            ]
    
    def _get_expression_tips(self, 
                           subject: str,
                           level: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get tips for expressing knowledge clearly in exams.
        
        Args:
            subject (str): The subject
            level (str, optional): The level
            
        Returns:
            List[Dict[str, Any]]: List of expression tips
        """
        logger.debug(f"Getting expression tips for {subject}")
        
        # This is a simplified implementation
        # In a real implementation, you would gather tips from various sources
        
        # Common tips for all subjects
        common_tips = [
            {
                "category": "Structure",
                "tip": "Use clear paragraphs with topic sentences",
                "example": "The causes of World War I can be categorized into several key factors. First, nationalism played a significant role...",
                "importance": "High"
            },
            {
                "category": "Terminology",
                "tip": "Use subject-specific terminology accurately",
                "example": "The mitochondria is the powerhouse of the cell, responsible for cellular respiration...",
                "importance": "Very High"
            },
            {
                "category": "Evidence",
                "tip": "Support claims with specific evidence",
                "example": "Shakespeare uses imagery of darkness throughout Macbeth, such as when Lady Macbeth says 'Come, thick night...'",
                "importance": "High"
            },
            {
                "category": "Clarity",
                "tip": "Use simple, clear language for complex ideas",
                "example": "Instead of 'The precipitation event occurred', write 'It rained'",
                "importance": "Medium"
            }
        ]
        
        # Subject-specific tips
        subject_tips = []
        
        if subject.lower() == "mathematics":
            subject_tips = [
                {
                    "category": "Working",
                    "tip": "Show all steps of your working clearly",
                    "example": "When solving an equation, write out each step on a new line",
                    "importance": "Very High"
                },
                {
                    "category": "Notation",
                    "tip": "Use correct mathematical notation",
                    "example": "Write integrals with the correct symbols and limits",
                    "importance": "High"
                }
            ]
        elif subject.lower() in ["english", "literature"]:
            subject_tips = [
                {
                    "category": "Analysis",
                    "tip": "Use the PEE/PEA structure (Point, Evidence, Explanation/Analysis)",
                    "example": "Point: Steinbeck presents Lennie as childlike. Evidence: 'Lennie dabbled his big paw in the water'. Analysis: The word 'dabbled' suggests playful, childish behavior, while 'paw' rather than 'hand' suggests animalistic qualities.",
                    "importance": "Very High"
                },
                {
                    "category": "Quotations",
                    "tip": "Embed short quotations within your sentences",
                    "example": "Fitzgerald describes Gatsby's smile as 'rare' and 'full of eternal reassurance'",
                    "importance": "High"
                }
            ]
        elif subject.lower() in ["history", "politics"]:
            subject_tips = [
                {
                    "category": "Argumentation",
                    "tip": "Develop a clear argument with a thesis statement",
                    "example": "While economic factors contributed to the French Revolution, it was ultimately the political grievances that triggered the uprising in 1789.",
                    "importance": "Very High"
                },
                {
                    "category": "Chronology",
                    "tip": "Demonstrate understanding of chronology and causation",
                    "example": "The Wall Street Crash of 1929 led to the Great Depression, which in turn contributed to Hitler's rise to power in 1933.",
                    "importance": "High"
                }
            ]
        
        # Combine common and subject-specific tips
        all_tips = common_tips + subject_tips
        
        return all_tips
    
    def _find_additional_resources(self, 
                                 subject: str,
                                 exam_board: Optional[str] = None,
                                 level: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find additional resources for exam preparation.
        
        Args:
            subject (str): The subject
            exam_board (str, optional): The exam board
            level (str, optional): The level
            
        Returns:
            List[Dict[str, Any]]: List of additional resources
        """
        logger.debug(f"Finding additional resources for {subject}")
        
        # This is a simplified implementation
        # In a real implementation, you would search for textbooks, websites, videos, etc.
        
        # For demonstration purposes, return mock data
        return [
            {
                "title": f"{subject} Study Guide",
                "type": "Book",
                "author": "John Smith",
                "url": "https://example.com/books/study_guide",
                "description": f"Comprehensive study guide for {level or 'all levels'} {subject}",
                "rating": 4.5,
                "relevance": "High"
            },
            {
                "title": f"{subject} Video Tutorials",
                "type": "Video Series",
                "author": "Education Channel",
                "url": "https://example.com/videos/tutorials",
                "description": f"Video tutorials covering all aspects of {subject}",
                "rating": 4.8,
                "relevance": "Very High"
            },
            {
                "title": f"{subject} Practice Questions",
                "type": "Website",
                "author": "ExamPractice",
                "url": "https://example.com/practice",
                "description": f"Thousands of practice questions for {subject} with detailed solutions",
                "rating": 4.2,
                "relevance": "High"
            }
        ]
    
    def _download_resources(self, 
                          resources: List[Dict[str, Any]],
                          output_dir: str) -> None:
        """
        Download resources to the specified directory.
        
        Args:
            resources (List[Dict[str, Any]]): List of resources to download
            output_dir (str): Directory to save downloaded resources
        """
        logger.debug(f"Downloading {len(resources)} resources to {output_dir}")
        
        # Create output directory if needed
        os.makedirs(output_dir, exist_ok=True)
        
        # Download each resource
        for resource in resources:
            url = resource.get("url")
            if not url:
                continue
            
            # Generate filename from title or URL
            title = resource.get("title", "")
            if title:
                # Create a safe filename from title
                filename = "".join(c if c.isalnum() or c in " .-" else "_" for c in title)
                filename = filename.strip().replace(" ", "_")
            else:
                # Extract filename from URL
                filename = os.path.basename(urllib.parse.urlparse(url).path)
            
            # Add extension if missing
            if not os.path.splitext(filename)[1]:
                filename += ".pdf"  # Default to PDF
            
            # Full path to save the file
            file_path = os.path.join(output_dir, filename)
            
            # Skip download for demonstration purposes
            logger.info(f"Would download {url} to {file_path}")
            
            # In a real implementation, you would download the file:
            # try:
            #     response = self.session.get(url, stream=True)
            #     response.raise_for_status()
            #     
            #     with open(file_path, 'wb') as f:
            #         for chunk in response.iter_content(chunk_size=8192):
            #             f.write(chunk)
            #     
            #     logger.info(f"Downloaded {url} to {file_path}")
            # except Exception as e:
            #     logger.error(f"Error downloading {url}: {str(e)}")

# Command-line interface
def main():
    """
    Command-line interface for the Exam Research Mode.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Exam Research Mode")
    parser.add_argument("--subject", required=True, help="Subject to research")
    parser.add_argument("--exam-board", help="Exam board (e.g., AQA, Edexcel)")
    parser.add_argument("--level", help="Level (e.g., GCSE, A-Level)")
    parser.add_argument("--years", help="Year range (e.g., 2018-2023)")
    parser.add_argument("--output", default="exam_research", help="Output directory")
    
    args = parser.parse_args()
    
    try:
        # Parse year range
        year_range = None
        if args.years:
            years = args.years.split("-")
            if len(years) == 2:
                try:
                    year_range = [int(years[0]), int(years[1])]
                except ValueError:
                    print(f"Invalid year range: {args.years}")
                    return 1
        
        # Create researcher
        researcher = ExamResearchMode()
        
        # Research exam
        results = researcher.research_exam(
            subject=args.subject,
            exam_board=args.exam_board,
            level=args.level,
            year_range=year_range,
            output_dir=args.output
        )
        
        # Print summary
        print(f"\nExam Research Summary for {args.subject}")
        print(f"{'=' * 40}")
        print(f"Found {len(results['past_papers'])} past papers")
        print(f"Found {len(results['examiner_reports'])} examiner reports")
        print(f"Identified {len(results['common_topics'])} commonly tested topics")
        print(f"Compiled {len(results['expression_tips'])} expression tips")
        print(f"Found {len(results['resources'])} additional resources")
        print(f"\nResults saved to {args.output}/research_results.json")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()