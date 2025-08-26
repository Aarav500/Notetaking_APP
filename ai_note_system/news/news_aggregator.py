"""
Domain-Specific News Aggregator module for AI Note System.
Provides functionality to monitor sources and generate interpretive summaries.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import uuid

# Setup logging
logger = logging.getLogger("ai_note_system.news.news_aggregator")

class NewsAggregator:
    """
    News Aggregator class for monitoring domain-specific news sources.
    Aggregates content from journals, ArXiv, tech policies, GitHub, and newsletters.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the News Aggregator.
        
        Args:
            config (Dict[str, Any], optional): Configuration dictionary
        """
        self.config = config or {}
        
        # Configure default sources
        self.default_sources = {
            "arxiv": True,
            "journals": True,
            "tech_policies": True,
            "github": True,
            "newsletters": True,
            "blogs": True
        }
        
        # Configure source settings
        self.source_settings = self.config.get("source_settings", {
            "arxiv": {
                "categories": ["cs.AI", "cs.LG", "cs.CV", "cs.CL"],
                "max_results": 10,
                "days_back": 7
            },
            "journals": {
                "names": ["Nature", "Science", "CACM"],
                "max_results": 5,
                "days_back": 30
            },
            "tech_policies": {
                "regions": ["US", "EU", "Global"],
                "max_results": 5,
                "days_back": 30
            },
            "github": {
                "languages": ["Python", "JavaScript", "TypeScript"],
                "max_results": 10,
                "days_back": 7
            },
            "newsletters": {
                "names": ["ImportAI", "The Batch", "ML Research Roundup"],
                "max_results": 5,
                "days_back": 14
            },
            "blogs": {
                "urls": ["https://openai.com/blog", "https://ai.googleblog.com/"],
                "max_results": 5,
                "days_back": 14
            }
        })
        
        logger.debug("Initialized NewsAggregator")
    
    def create_feed(self, 
                   topic: str,
                   sources: Optional[List[str]] = None,
                   keywords: Optional[List[str]] = None,
                   max_results_per_source: int = 10,
                   update_frequency: str = "daily",
                   user_interests: Optional[List[str]] = None,
                   output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new news feed for a specific topic.
        
        Args:
            topic (str): The topic to monitor (e.g., "Reinforcement Learning")
            sources (List[str], optional): List of sources to monitor
            keywords (List[str], optional): List of keywords to filter by
            max_results_per_source (int): Maximum results per source
            update_frequency (str): Update frequency ("hourly", "daily", "weekly")
            user_interests (List[str], optional): User interests for personalization
            output_dir (str, optional): Directory to save the feed
            
        Returns:
            Dict[str, Any]: Created feed
        """
        logger.info(f"Creating news feed for topic: {topic}")
        
        # Set default sources if not provided
        if sources is None:
            sources = [source for source, enabled in self.default_sources.items() if enabled]
        
        # Generate feed ID
        feed_id = str(uuid.uuid4())
        
        # Create feed
        feed = {
            "id": feed_id,
            "topic": topic,
            "sources": sources,
            "keywords": keywords or [],
            "max_results_per_source": max_results_per_source,
            "update_frequency": update_frequency,
            "user_interests": user_interests or [],
            "created_at": datetime.now().isoformat(),
            "last_updated": None,
            "next_update": self._calculate_next_update(update_frequency),
            "items": []
        }
        
        # Save feed if output directory is provided
        if output_dir:
            self._save_feed(feed, output_dir)
        
        logger.info(f"Feed created for topic: {topic}")
        return feed
    
    def update_feed(self, 
                   feed: Dict[str, Any],
                   force_update: bool = False,
                   output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a news feed with the latest content.
        
        Args:
            feed (Dict[str, Any]): The feed to update
            force_update (bool): Whether to force an update regardless of schedule
            output_dir (str, optional): Directory to save the updated feed
            
        Returns:
            Dict[str, Any]: Updated feed
        """
        feed_id = feed.get("id", "unknown")
        topic = feed.get("topic", "unknown")
        logger.info(f"Updating feed {feed_id} for topic: {topic}")
        
        # Check if update is needed
        next_update = feed.get("next_update")
        if not force_update and next_update and datetime.now().isoformat() < next_update:
            logger.info(f"Feed {feed_id} does not need an update yet")
            return feed
        
        # Get feed parameters
        sources = feed.get("sources", [])
        keywords = feed.get("keywords", [])
        max_results = feed.get("max_results_per_source", 10)
        user_interests = feed.get("user_interests", [])
        
        # Fetch new items from each source
        new_items = []
        
        for source in sources:
            source_items = self._fetch_from_source(
                source=source,
                topic=topic,
                keywords=keywords,
                max_results=max_results
            )
            new_items.extend(source_items)
        
        # Filter and sort items
        filtered_items = self._filter_items(new_items, keywords)
        sorted_items = self._sort_items(filtered_items, user_interests)
        
        # Generate interpretive summaries
        items_with_summaries = self._generate_interpretive_summaries(
            sorted_items,
            topic=topic,
            user_interests=user_interests
        )
        
        # Update feed
        updated_feed = feed.copy()
        updated_feed["items"] = items_with_summaries
        updated_feed["last_updated"] = datetime.now().isoformat()
        updated_feed["next_update"] = self._calculate_next_update(feed.get("update_frequency", "daily"))
        
        # Save feed if output directory is provided
        if output_dir:
            self._save_feed(updated_feed, output_dir)
        
        logger.info(f"Feed {feed_id} updated with {len(items_with_summaries)} items")
        return updated_feed
    
    def get_feed_summary(self, feed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of the feed.
        
        Args:
            feed (Dict[str, Any]): The feed to summarize
            
        Returns:
            Dict[str, Any]: Feed summary
        """
        feed_id = feed.get("id", "unknown")
        topic = feed.get("topic", "unknown")
        logger.info(f"Generating summary for feed {feed_id}")
        
        # Get feed items
        items = feed.get("items", [])
        
        if not items:
            logger.warning(f"Feed {feed_id} has no items")
            return {
                "feed_id": feed_id,
                "topic": topic,
                "num_items": 0,
                "summary": "No items in feed",
                "top_items": [],
                "categories": {}
            }
        
        # Group items by category
        categories = {}
        for item in items:
            category = item.get("category", "uncategorized")
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Get top items (highest relevance score)
        top_items = sorted(items, key=lambda x: x.get("relevance_score", 0), reverse=True)[:5]
        
        # Generate overall summary
        summary = self._generate_feed_summary(items, topic)
        
        return {
            "feed_id": feed_id,
            "topic": topic,
            "num_items": len(items),
            "summary": summary,
            "top_items": top_items,
            "categories": {
                category: len(items) for category, items in categories.items()
            }
        }
    
    def _calculate_next_update(self, update_frequency: str) -> str:
        """
        Calculate the next update time based on the update frequency.
        
        Args:
            update_frequency (str): Update frequency ("hourly", "daily", "weekly")
            
        Returns:
            str: Next update time in ISO format
        """
        now = datetime.now()
        
        if update_frequency == "hourly":
            next_update = now + timedelta(hours=1)
        elif update_frequency == "weekly":
            next_update = now + timedelta(days=7)
        else:  # daily is default
            next_update = now + timedelta(days=1)
        
        return next_update.isoformat()
    
    def _fetch_from_source(self, 
                         source: str,
                         topic: str,
                         keywords: List[str],
                         max_results: int) -> List[Dict[str, Any]]:
        """
        Fetch items from a specific source.
        
        Args:
            source (str): Source to fetch from
            topic (str): Topic to filter by
            keywords (List[str]): Keywords to filter by
            max_results (int): Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: List of items
        """
        logger.debug(f"Fetching from source: {source}")
        
        # Get source settings
        source_settings = self.source_settings.get(source, {})
        days_back = source_settings.get("days_back", 7)
        
        # This is a simplified implementation
        # In a real implementation, you would use APIs or web scraping
        
        # Mock data for demonstration
        if source == "arxiv":
            return self._mock_arxiv_items(topic, keywords, max_results, days_back)
        elif source == "journals":
            return self._mock_journal_items(topic, keywords, max_results, days_back)
        elif source == "tech_policies":
            return self._mock_policy_items(topic, keywords, max_results, days_back)
        elif source == "github":
            return self._mock_github_items(topic, keywords, max_results, days_back)
        elif source == "newsletters":
            return self._mock_newsletter_items(topic, keywords, max_results, days_back)
        elif source == "blogs":
            return self._mock_blog_items(topic, keywords, max_results, days_back)
        else:
            logger.warning(f"Unknown source: {source}")
            return []
    
    def _mock_arxiv_items(self, 
                        topic: str,
                        keywords: List[str],
                        max_results: int,
                        days_back: int) -> List[Dict[str, Any]]:
        """
        Generate mock ArXiv items.
        
        Args:
            topic (str): Topic to filter by
            keywords (List[str]): Keywords to filter by
            max_results (int): Maximum number of results
            days_back (int): Number of days to look back
            
        Returns:
            List[Dict[str, Any]]: List of ArXiv items
        """
        # This is a simplified implementation
        # In a real implementation, you would use the ArXiv API
        
        items = []
        
        # Generate mock items
        for i in range(max_results):
            # Generate a date within the last days_back days
            days_ago = i % days_back
            date = (datetime.now() - timedelta(days=days_ago)).isoformat()
            
            item = {
                "id": f"arxiv_{i}",
                "title": f"ArXiv Paper on {topic} - {i+1}",
                "authors": ["Author A", "Author B"],
                "abstract": f"This paper presents a novel approach to {topic} that addresses the challenges of {', '.join(keywords[:2])}.",
                "url": f"https://arxiv.org/abs/{2023+i}.{i+1:05d}",
                "published_date": date,
                "source": "arxiv",
                "category": "research",
                "keywords": keywords[:2] + [topic],
                "raw_content": f"Full text of the paper on {topic}...",
                "metadata": {
                    "arxiv_category": "cs.AI",
                    "comments": f"{5+i} pages, {2+i} figures"
                }
            }
            
            items.append(item)
        
        return items
    
    def _mock_journal_items(self, 
                          topic: str,
                          keywords: List[str],
                          max_results: int,
                          days_back: int) -> List[Dict[str, Any]]:
        """
        Generate mock journal items.
        
        Args:
            topic (str): Topic to filter by
            keywords (List[str]): Keywords to filter by
            max_results (int): Maximum number of results
            days_back (int): Number of days to look back
            
        Returns:
            List[Dict[str, Any]]: List of journal items
        """
        journals = ["Nature", "Science", "CACM"]
        items = []
        
        for i in range(max_results):
            journal = journals[i % len(journals)]
            days_ago = i % days_back
            date = (datetime.now() - timedelta(days=days_ago)).isoformat()
            
            item = {
                "id": f"journal_{i}",
                "title": f"{journal} Article on {topic} - {i+1}",
                "authors": ["Researcher A", "Researcher B"],
                "abstract": f"This article in {journal} explores the implications of {topic} for {', '.join(keywords[:2])}.",
                "url": f"https://example.com/{journal.lower()}/{2023+i}/{i+1}",
                "published_date": date,
                "source": "journals",
                "category": "research",
                "keywords": keywords[:2] + [topic],
                "raw_content": f"Full text of the article on {topic}...",
                "metadata": {
                    "journal": journal,
                    "volume": f"{100+i}",
                    "issue": f"{i+1}"
                }
            }
            
            items.append(item)
        
        return items
    
    def _mock_policy_items(self, 
                         topic: str,
                         keywords: List[str],
                         max_results: int,
                         days_back: int) -> List[Dict[str, Any]]:
        """
        Generate mock policy items.
        
        Args:
            topic (str): Topic to filter by
            keywords (List[str]): Keywords to filter by
            max_results (int): Maximum number of results
            days_back (int): Number of days to look back
            
        Returns:
            List[Dict[str, Any]]: List of policy items
        """
        regions = ["US", "EU", "Global"]
        items = []
        
        for i in range(max_results):
            region = regions[i % len(regions)]
            days_ago = i % days_back
            date = (datetime.now() - timedelta(days=days_ago)).isoformat()
            
            item = {
                "id": f"policy_{i}",
                "title": f"{region} Policy Update on {topic} - {i+1}",
                "authors": ["Policy Maker A", "Agency B"],
                "abstract": f"This policy update from {region} addresses regulations for {topic} with focus on {', '.join(keywords[:2])}.",
                "url": f"https://example.com/policy/{region.lower()}/{2023+i}/{i+1}",
                "published_date": date,
                "source": "tech_policies",
                "category": "policy",
                "keywords": keywords[:2] + [topic],
                "raw_content": f"Full text of the policy update on {topic}...",
                "metadata": {
                    "region": region,
                    "policy_type": "Regulation",
                    "effective_date": (datetime.now() + timedelta(days=30)).isoformat()
                }
            }
            
            items.append(item)
        
        return items
    
    def _mock_github_items(self, 
                         topic: str,
                         keywords: List[str],
                         max_results: int,
                         days_back: int) -> List[Dict[str, Any]]:
        """
        Generate mock GitHub items.
        
        Args:
            topic (str): Topic to filter by
            keywords (List[str]): Keywords to filter by
            max_results (int): Maximum number of results
            days_back (int): Number of days to look back
            
        Returns:
            List[Dict[str, Any]]: List of GitHub items
        """
        languages = ["Python", "JavaScript", "TypeScript"]
        items = []
        
        for i in range(max_results):
            language = languages[i % len(languages)]
            days_ago = i % days_back
            date = (datetime.now() - timedelta(days=days_ago)).isoformat()
            
            item = {
                "id": f"github_{i}",
                "title": f"GitHub Project on {topic} - {i+1}",
                "authors": [f"Developer{i+1}"],
                "abstract": f"This GitHub project implements {topic} using {language} with features for {', '.join(keywords[:2])}.",
                "url": f"https://github.com/user{i+1}/{topic.lower().replace(' ', '-')}-{i+1}",
                "published_date": date,
                "source": "github",
                "category": "code",
                "keywords": keywords[:2] + [topic, language],
                "raw_content": f"README of the GitHub project on {topic}...",
                "metadata": {
                    "language": language,
                    "stars": 100 + i * 10,
                    "forks": 20 + i * 5
                }
            }
            
            items.append(item)
        
        return items
    
    def _mock_newsletter_items(self, 
                             topic: str,
                             keywords: List[str],
                             max_results: int,
                             days_back: int) -> List[Dict[str, Any]]:
        """
        Generate mock newsletter items.
        
        Args:
            topic (str): Topic to filter by
            keywords (List[str]): Keywords to filter by
            max_results (int): Maximum number of results
            days_back (int): Number of days to look back
            
        Returns:
            List[Dict[str, Any]]: List of newsletter items
        """
        newsletters = ["ImportAI", "The Batch", "ML Research Roundup"]
        items = []
        
        for i in range(max_results):
            newsletter = newsletters[i % len(newsletters)]
            days_ago = i % days_back
            date = (datetime.now() - timedelta(days=days_ago)).isoformat()
            
            item = {
                "id": f"newsletter_{i}",
                "title": f"{newsletter} Issue on {topic} - {i+1}",
                "authors": [f"Editor{i+1}"],
                "abstract": f"This issue of {newsletter} covers recent developments in {topic} including {', '.join(keywords[:2])}.",
                "url": f"https://example.com/{newsletter.lower()}/{2023+i}/{i+1}",
                "published_date": date,
                "source": "newsletters",
                "category": "newsletter",
                "keywords": keywords[:2] + [topic],
                "raw_content": f"Full text of the newsletter issue on {topic}...",
                "metadata": {
                    "newsletter": newsletter,
                    "issue": f"#{100+i}"
                }
            }
            
            items.append(item)
        
        return items
    
    def _mock_blog_items(self, 
                       topic: str,
                       keywords: List[str],
                       max_results: int,
                       days_back: int) -> List[Dict[str, Any]]:
        """
        Generate mock blog items.
        
        Args:
            topic (str): Topic to filter by
            keywords (List[str]): Keywords to filter by
            max_results (int): Maximum number of results
            days_back (int): Number of days to look back
            
        Returns:
            List[Dict[str, Any]]: List of blog items
        """
        blogs = ["OpenAI Blog", "Google AI Blog", "Facebook AI Blog"]
        items = []
        
        for i in range(max_results):
            blog = blogs[i % len(blogs)]
            days_ago = i % days_back
            date = (datetime.now() - timedelta(days=days_ago)).isoformat()
            
            item = {
                "id": f"blog_{i}",
                "title": f"{blog} Post on {topic} - {i+1}",
                "authors": [f"Blogger{i+1}"],
                "abstract": f"This blog post on {blog} discusses advances in {topic} related to {', '.join(keywords[:2])}.",
                "url": f"https://example.com/{blog.lower().replace(' ', '')}/{2023+i}/{i+1}",
                "published_date": date,
                "source": "blogs",
                "category": "blog",
                "keywords": keywords[:2] + [topic],
                "raw_content": f"Full text of the blog post on {topic}...",
                "metadata": {
                    "blog": blog,
                    "reading_time": f"{5+i} min"
                }
            }
            
            items.append(item)
        
        return items
    
    def _filter_items(self, 
                    items: List[Dict[str, Any]],
                    keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Filter items based on keywords.
        
        Args:
            items (List[Dict[str, Any]]): List of items to filter
            keywords (List[str]): Keywords to filter by
            
        Returns:
            List[Dict[str, Any]]: Filtered items
        """
        if not keywords:
            return items
        
        filtered_items = []
        
        for item in items:
            # Check if any keyword is in the title, abstract, or keywords
            title = item.get("title", "").lower()
            abstract = item.get("abstract", "").lower()
            item_keywords = [k.lower() for k in item.get("keywords", [])]
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if (keyword_lower in title or 
                    keyword_lower in abstract or 
                    keyword_lower in item_keywords):
                    filtered_items.append(item)
                    break
        
        return filtered_items
    
    def _sort_items(self, 
                  items: List[Dict[str, Any]],
                  user_interests: List[str]) -> List[Dict[str, Any]]:
        """
        Sort items based on relevance to user interests.
        
        Args:
            items (List[Dict[str, Any]]): List of items to sort
            user_interests (List[str]): User interests
            
        Returns:
            List[Dict[str, Any]]: Sorted items
        """
        # If no user interests, sort by date (newest first)
        if not user_interests:
            return sorted(items, key=lambda x: x.get("published_date", ""), reverse=True)
        
        # Calculate relevance score for each item
        for item in items:
            relevance_score = self._calculate_relevance_score(item, user_interests)
            item["relevance_score"] = relevance_score
        
        # Sort by relevance score (highest first)
        return sorted(items, key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    def _calculate_relevance_score(self, 
                                 item: Dict[str, Any],
                                 user_interests: List[str]) -> float:
        """
        Calculate relevance score for an item based on user interests.
        
        Args:
            item (Dict[str, Any]): Item to calculate score for
            user_interests (List[str]): User interests
            
        Returns:
            float: Relevance score
        """
        # This is a simplified implementation
        # In a real implementation, you would use more sophisticated techniques
        
        score = 0.0
        
        # Check title, abstract, and keywords for user interests
        title = item.get("title", "").lower()
        abstract = item.get("abstract", "").lower()
        keywords = [k.lower() for k in item.get("keywords", [])]
        
        for interest in user_interests:
            interest_lower = interest.lower()
            
            # Title match (highest weight)
            if interest_lower in title:
                score += 3.0
            
            # Abstract match (medium weight)
            if interest_lower in abstract:
                score += 2.0
            
            # Keyword match (lowest weight)
            if interest_lower in keywords:
                score += 1.0
        
        # Normalize score
        max_possible_score = 6.0 * len(user_interests)  # 6.0 = 3.0 + 2.0 + 1.0
        if max_possible_score > 0:
            score = score / max_possible_score
        
        return score
    
    def _generate_interpretive_summaries(self, 
                                       items: List[Dict[str, Any]],
                                       topic: str,
                                       user_interests: List[str]) -> List[Dict[str, Any]]:
        """
        Generate interpretive summaries for items.
        
        Args:
            items (List[Dict[str, Any]]): List of items to summarize
            topic (str): Topic of the feed
            user_interests (List[str]): User interests
            
        Returns:
            List[Dict[str, Any]]: Items with summaries
        """
        logger.debug(f"Generating interpretive summaries for {len(items)} items")
        
        # This is a simplified implementation
        # In a real implementation, you would use LLMs or other summarization techniques
        
        items_with_summaries = []
        
        for item in items:
            # Generate interpretive summary
            interpretive_summary = self._generate_interpretive_summary(item, topic, user_interests)
            
            # Add summary to item
            item_with_summary = item.copy()
            item_with_summary["interpretive_summary"] = interpretive_summary
            
            items_with_summaries.append(item_with_summary)
        
        return items_with_summaries
    
    def _generate_interpretive_summary(self, 
                                     item: Dict[str, Any],
                                     topic: str,
                                     user_interests: List[str]) -> Dict[str, Any]:
        """
        Generate an interpretive summary for an item.
        
        Args:
            item (Dict[str, Any]): Item to summarize
            topic (str): Topic of the feed
            user_interests (List[str]): User interests
            
        Returns:
            Dict[str, Any]: Interpretive summary
        """
        # This is a simplified implementation
        # In a real implementation, you would use LLMs or other summarization techniques
        
        title = item.get("title", "")
        abstract = item.get("abstract", "")
        source = item.get("source", "")
        category = item.get("category", "")
        
        # Generate summary text
        summary_text = f"This {category} from {source} discusses {topic}. {abstract}"
        
        # Generate implications for learning/projects
        implications = f"This could be relevant for your learning in {topic}"
        if user_interests:
            implications += f", particularly for your interests in {', '.join(user_interests[:2])}"
        implications += "."
        
        # Generate contrasting viewpoints
        contrasting_viewpoints = f"While this {category} presents one perspective on {topic}, alternative viewpoints might emphasize different aspects or approaches."
        
        # Generate long-term significance
        long_term_significance = f"This development in {topic} could have long-term implications for the field, potentially influencing future research and applications."
        
        # Generate hype assessment
        hype_assessment = "Based on the content, this appears to be a substantive development rather than mere hype, though further validation would be beneficial."
        
        return {
            "summary": summary_text,
            "implications": implications,
            "contrasting_viewpoints": contrasting_viewpoints,
            "long_term_significance": long_term_significance,
            "hype_assessment": hype_assessment
        }
    
    def _generate_feed_summary(self, 
                             items: List[Dict[str, Any]],
                             topic: str) -> str:
        """
        Generate an overall summary for the feed.
        
        Args:
            items (List[Dict[str, Any]]): List of items in the feed
            topic (str): Topic of the feed
            
        Returns:
            str: Feed summary
        """
        # This is a simplified implementation
        # In a real implementation, you would use LLMs or other summarization techniques
        
        num_items = len(items)
        sources = set(item.get("source", "") for item in items)
        categories = set(item.get("category", "") for item in items)
        
        summary = f"This feed contains {num_items} items on {topic} from {len(sources)} sources, "
        summary += f"covering {len(categories)} categories. "
        
        if num_items > 0:
            # Get the most recent item
            most_recent = max(items, key=lambda x: x.get("published_date", ""))
            most_recent_date = most_recent.get("published_date", "")
            
            if most_recent_date:
                try:
                    date_obj = datetime.fromisoformat(most_recent_date)
                    summary += f"The most recent item was published on {date_obj.strftime('%Y-%m-%d')}. "
                except ValueError:
                    pass
        
        summary += f"Key sources include {', '.join(list(sources)[:3])}. "
        summary += f"The feed covers {', '.join(list(categories)[:3])} content."
        
        return summary
    
    def _save_feed(self, feed: Dict[str, Any], output_dir: str) -> None:
        """
        Save the feed to a file.
        
        Args:
            feed (Dict[str, Any]): Feed to save
            output_dir (str): Output directory
        """
        # Create output directory if needed
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        feed_id = feed.get("id", "unknown")
        topic = feed.get("topic", "feed")
        safe_topic = "".join(c if c.isalnum() or c in " .-" else "_" for c in topic)
        safe_topic = safe_topic.strip().replace(" ", "_")
        
        filename = f"{safe_topic}_{feed_id}.json"
        file_path = os.path.join(output_dir, filename)
        
        # Save feed to file
        with open(file_path, "w") as f:
            json.dump(feed, f, indent=2)
        
        logger.info(f"Feed saved to {file_path}")

# Command-line interface
def main():
    """
    Command-line interface for the News Aggregator.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Domain-Specific News Aggregator")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create feed command
    create_parser = subparsers.add_parser("create", help="Create a new feed")
    create_parser.add_argument("--topic", required=True, help="Topic to monitor")
    create_parser.add_argument("--sources", nargs="+", help="Sources to monitor")
    create_parser.add_argument("--keywords", nargs="+", help="Keywords to filter by")
    create_parser.add_argument("--max-results", type=int, default=10, help="Maximum results per source")
    create_parser.add_argument("--frequency", default="daily", choices=["hourly", "daily", "weekly"], help="Update frequency")
    create_parser.add_argument("--interests", nargs="+", help="User interests for personalization")
    create_parser.add_argument("--output", default="feeds", help="Output directory")
    
    # Update feed command
    update_parser = subparsers.add_parser("update", help="Update a feed")
    update_parser.add_argument("--feed", required=True, help="Path to feed JSON file")
    update_parser.add_argument("--force", action="store_true", help="Force update regardless of schedule")
    update_parser.add_argument("--output", default="feeds", help="Output directory")
    
    # List feeds command
    list_parser = subparsers.add_parser("list", help="List feeds in a directory")
    list_parser.add_argument("--dir", default="feeds", help="Directory containing feeds")
    
    # View feed command
    view_parser = subparsers.add_parser("view", help="View a feed")
    view_parser.add_argument("--feed", required=True, help="Path to feed JSON file")
    view_parser.add_argument("--summary", action="store_true", help="Show summary only")
    
    args = parser.parse_args()
    
    try:
        # Create aggregator
        aggregator = NewsAggregator()
        
        if args.command == "create":
            # Create feed
            feed = aggregator.create_feed(
                topic=args.topic,
                sources=args.sources,
                keywords=args.keywords,
                max_results_per_source=args.max_results,
                update_frequency=args.frequency,
                user_interests=args.interests,
                output_dir=args.output
            )
            
            # Update feed to get initial items
            feed = aggregator.update_feed(feed, force_update=True, output_dir=args.output)
            
            print(f"Feed created for topic: {args.topic}")
            print(f"Feed ID: {feed.get('id')}")
            print(f"Items: {len(feed.get('items', []))}")
            print(f"Saved to: {args.output}")
        
        elif args.command == "update":
            # Load feed
            with open(args.feed, "r") as f:
                feed = json.load(f)
            
            # Update feed
            updated_feed = aggregator.update_feed(
                feed=feed,
                force_update=args.force,
                output_dir=args.output
            )
            
            print(f"Feed updated: {updated_feed.get('topic')}")
            print(f"Items: {len(updated_feed.get('items', []))}")
            print(f"Last updated: {updated_feed.get('last_updated')}")
            print(f"Next update: {updated_feed.get('next_update')}")
        
        elif args.command == "list":
            # List feeds in directory
            feed_files = glob.glob(os.path.join(args.dir, "*.json"))
            
            if not feed_files:
                print(f"No feeds found in {args.dir}")
                return 0
            
            print(f"Feeds in {args.dir}:")
            for feed_file in feed_files:
                try:
                    with open(feed_file, "r") as f:
                        feed = json.load(f)
                    
                    print(f"  {os.path.basename(feed_file)}")
                    print(f"    Topic: {feed.get('topic')}")
                    print(f"    Items: {len(feed.get('items', []))}")
                    print(f"    Last updated: {feed.get('last_updated')}")
                    print()
                except Exception as e:
                    print(f"  Error loading {feed_file}: {str(e)}")
        
        elif args.command == "view":
            # Load feed
            with open(args.feed, "r") as f:
                feed = json.load(f)
            
            if args.summary:
                # Show summary
                summary = aggregator.get_feed_summary(feed)
                
                print(f"Feed Summary: {summary.get('topic')}")
                print(f"Items: {summary.get('num_items')}")
                print(f"Summary: {summary.get('summary')}")
                print("\nCategories:")
                for category, count in summary.get("categories", {}).items():
                    print(f"  {category}: {count} items")
                
                print("\nTop Items:")
                for i, item in enumerate(summary.get("top_items", []), 1):
                    print(f"  {i}. {item.get('title')}")
                    print(f"     Source: {item.get('source')}")
                    print(f"     URL: {item.get('url')}")
                    print(f"     Relevance: {item.get('relevance_score', 0):.2f}")
                    print()
            else:
                # Show full feed
                print(f"Feed: {feed.get('topic')}")
                print(f"ID: {feed.get('id')}")
                print(f"Sources: {', '.join(feed.get('sources', []))}")
                print(f"Keywords: {', '.join(feed.get('keywords', []))}")
                print(f"User Interests: {', '.join(feed.get('user_interests', []))}")
                print(f"Last Updated: {feed.get('last_updated')}")
                print(f"Next Update: {feed.get('next_update')}")
                print(f"Items: {len(feed.get('items', []))}")
                
                print("\nItems:")
                for i, item in enumerate(feed.get("items", []), 1):
                    print(f"  {i}. {item.get('title')}")
                    print(f"     Source: {item.get('source')}")
                    print(f"     Category: {item.get('category')}")
                    print(f"     Published: {item.get('published_date')}")
                    print(f"     URL: {item.get('url')}")
                    
                    if "interpretive_summary" in item:
                        summary = item.get("interpretive_summary", {})
                        print(f"     Summary: {summary.get('summary', '')[:100]}...")
                        print(f"     Implications: {summary.get('implications', '')[:100]}...")
                    
                    print()
        
        else:
            parser.print_help()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()