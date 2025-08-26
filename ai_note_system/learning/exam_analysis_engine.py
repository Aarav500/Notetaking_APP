"""
Exam Analysis Engine module for AI Note System.
Provides functionality to analyze exam results and identify areas for improvement.
"""

import os
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from collections import Counter, defaultdict

# Setup logging
logger = logging.getLogger("ai_note_system.learning.exam_analysis_engine")

class ExamAnalysisEngine:
    """
    Exam Analysis Engine class for analyzing exam results.
    Identifies areas of weakness, time management issues, and mistake patterns.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Exam Analysis Engine.
        
        Args:
            config (Dict[str, Any], optional): Configuration dictionary
        """
        self.config = config or {}
        self.mistake_categories = [
            "content_known_but_could_not_express",
            "misread_the_question",
            "conceptual_confusion",
            "calculation_mistake",
            "time_management",
            "incomplete_answer",
            "other"
        ]
        
        logger.debug("Initialized ExamAnalysisEngine")
    
    def analyze_exam(self, 
                    exam_data: Dict[str, Any], 
                    answers: List[Dict[str, Any]],
                    generate_visualizations: bool = True,
                    output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze exam results to identify areas for improvement.
        
        Args:
            exam_data (Dict[str, Any]): Exam metadata including topics, duration, etc.
            answers (List[Dict[str, Any]]): List of answers with timing and mistake data
            generate_visualizations (bool): Whether to generate visualization charts
            output_dir (str, optional): Directory to save visualizations
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        logger.info("Analyzing exam results")
        
        if not answers:
            logger.warning("No answers provided for analysis")
            return {"error": "No answers provided for analysis"}
        
        # Create output directory if needed
        if generate_visualizations and output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Perform various analyses
        topic_analysis = self._analyze_topics(exam_data, answers)
        time_analysis = self._analyze_time_management(exam_data, answers)
        mistake_analysis = self._analyze_mistake_patterns(answers)
        
        # Generate visualizations if requested
        visualization_paths = {}
        if generate_visualizations:
            visualization_paths = self._generate_visualizations(
                topic_analysis, 
                time_analysis, 
                mistake_analysis,
                output_dir
            )
        
        # Generate improvement recommendations
        recommendations = self._generate_recommendations(
            topic_analysis,
            time_analysis,
            mistake_analysis
        )
        
        # Compile final analysis
        analysis_result = {
            "exam_id": exam_data.get("id", "unknown"),
            "exam_title": exam_data.get("title", "Untitled Exam"),
            "date_analyzed": datetime.now().isoformat(),
            "total_questions": len(answers),
            "correct_answers": sum(1 for a in answers if a.get("is_correct", False)),
            "incorrect_answers": sum(1 for a in answers if not a.get("is_correct", False)),
            "overall_score": sum(1 for a in answers if a.get("is_correct", False)) / len(answers) if answers else 0,
            "topic_analysis": topic_analysis,
            "time_analysis": time_analysis,
            "mistake_analysis": mistake_analysis,
            "recommendations": recommendations,
            "visualization_paths": visualization_paths
        }
        
        logger.info(f"Exam analysis completed for {exam_data.get('title', 'Untitled Exam')}")
        return analysis_result
    
    def _analyze_topics(self, exam_data: Dict[str, Any], answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze performance by topic.
        
        Args:
            exam_data (Dict[str, Any]): Exam metadata
            answers (List[Dict[str, Any]]): List of answers
            
        Returns:
            Dict[str, Any]: Topic analysis results
        """
        logger.debug("Analyzing performance by topic")
        
        # Extract topics from exam data
        topics = exam_data.get("topics", {})
        if not topics:
            # Try to extract topics from questions
            topics = self._extract_topics_from_questions(exam_data, answers)
        
        # Initialize topic statistics
        topic_stats = {}
        for topic_id, topic_name in topics.items():
            topic_stats[topic_id] = {
                "name": topic_name,
                "total_questions": 0,
                "correct_answers": 0,
                "incorrect_answers": 0,
                "score": 0.0,
                "avg_time_seconds": 0.0,
                "common_mistakes": []
            }
        
        # Process answers
        for answer in answers:
            question_topics = answer.get("topics", [])
            time_spent = answer.get("time_spent_seconds", 0)
            is_correct = answer.get("is_correct", False)
            mistake_type = answer.get("mistake_type", "other") if not is_correct else None
            
            for topic_id in question_topics:
                if topic_id in topic_stats:
                    # Update topic statistics
                    topic_stats[topic_id]["total_questions"] += 1
                    
                    if is_correct:
                        topic_stats[topic_id]["correct_answers"] += 1
                    else:
                        topic_stats[topic_id]["incorrect_answers"] += 1
                        if mistake_type:
                            topic_stats[topic_id]["common_mistakes"].append(mistake_type)
                    
                    # Update average time
                    current_avg = topic_stats[topic_id]["avg_time_seconds"]
                    current_count = topic_stats[topic_id]["total_questions"]
                    topic_stats[topic_id]["avg_time_seconds"] = (
                        (current_avg * (current_count - 1) + time_spent) / current_count
                    )
        
        # Calculate scores and finalize statistics
        for topic_id, stats in topic_stats.items():
            if stats["total_questions"] > 0:
                stats["score"] = stats["correct_answers"] / stats["total_questions"]
            
            # Find most common mistakes
            if stats["common_mistakes"]:
                mistake_counter = Counter(stats["common_mistakes"])
                stats["common_mistakes"] = [
                    {"type": mistake_type, "count": count}
                    for mistake_type, count in mistake_counter.most_common(3)
                ]
            else:
                stats["common_mistakes"] = []
        
        # Identify weakest and strongest topics
        if topic_stats:
            sorted_topics = sorted(topic_stats.items(), key=lambda x: x[1]["score"])
            weakest_topics = [topic_id for topic_id, _ in sorted_topics[:3]]
            strongest_topics = [topic_id for topic_id, _ in sorted_topics[-3:]]
        else:
            weakest_topics = []
            strongest_topics = []
        
        return {
            "topic_stats": topic_stats,
            "weakest_topics": weakest_topics,
            "strongest_topics": strongest_topics
        }
    
    def _extract_topics_from_questions(self, exam_data: Dict[str, Any], answers: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Extract topics from questions if not provided in exam data.
        
        Args:
            exam_data (Dict[str, Any]): Exam metadata
            answers (List[Dict[str, Any]]): List of answers
            
        Returns:
            Dict[str, str]: Dictionary of topic IDs to topic names
        """
        topics = {}
        
        # Try to get questions from exam data
        questions = exam_data.get("questions", [])
        
        # If no questions in exam data, try to get from answers
        if not questions:
            question_ids = [a.get("question_id") for a in answers if "question_id" in a]
            questions = [
                exam_data.get("questions_by_id", {}).get(qid, {})
                for qid in question_ids
            ]
        
        # Extract topics from questions
        for question in questions:
            question_topics = question.get("topics", [])
            for topic in question_topics:
                if isinstance(topic, dict):
                    topic_id = topic.get("id")
                    topic_name = topic.get("name")
                    if topic_id and topic_name:
                        topics[topic_id] = topic_name
                elif isinstance(topic, str):
                    # If topic is just a string, use it as both ID and name
                    topics[topic] = topic
        
        return topics
    
    def _analyze_time_management(self, exam_data: Dict[str, Any], answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze time management during the exam.
        
        Args:
            exam_data (Dict[str, Any]): Exam metadata
            answers (List[Dict[str, Any]]): List of answers
            
        Returns:
            Dict[str, Any]: Time management analysis results
        """
        logger.debug("Analyzing time management")
        
        # Extract timing data
        times_per_question = [a.get("time_spent_seconds", 0) for a in answers]
        
        if not times_per_question:
            return {"error": "No timing data available"}
        
        # Calculate statistics
        avg_time = sum(times_per_question) / len(times_per_question) if times_per_question else 0
        median_time = sorted(times_per_question)[len(times_per_question) // 2] if times_per_question else 0
        max_time = max(times_per_question) if times_per_question else 0
        min_time = min(times_per_question) if times_per_question else 0
        
        # Identify questions that took too long
        time_threshold = avg_time * 1.5  # 50% longer than average
        long_questions = [
            {
                "question_id": a.get("question_id", f"Q{i+1}"),
                "time_spent_seconds": a.get("time_spent_seconds", 0),
                "is_correct": a.get("is_correct", False)
            }
            for i, a in enumerate(answers)
            if a.get("time_spent_seconds", 0) > time_threshold
        ]
        
        # Identify questions that were rushed
        rush_threshold = avg_time * 0.5  # 50% shorter than average
        rushed_questions = [
            {
                "question_id": a.get("question_id", f"Q{i+1}"),
                "time_spent_seconds": a.get("time_spent_seconds", 0),
                "is_correct": a.get("is_correct", False)
            }
            for i, a in enumerate(answers)
            if a.get("time_spent_seconds", 0) < rush_threshold
        ]
        
        # Analyze time distribution
        time_distribution = self._calculate_time_distribution(times_per_question)
        
        # Analyze time vs. correctness
        time_vs_correctness = self._analyze_time_vs_correctness(answers)
        
        # Check if exam was completed in time
        total_time_spent = sum(times_per_question)
        exam_duration = exam_data.get("duration_minutes", 0) * 60  # Convert to seconds
        time_pressure = None
        
        if exam_duration > 0:
            time_pressure = {
                "total_time_spent_seconds": total_time_spent,
                "exam_duration_seconds": exam_duration,
                "time_utilization_percentage": (total_time_spent / exam_duration) * 100,
                "completed_in_time": total_time_spent <= exam_duration,
                "time_remaining_seconds": max(0, exam_duration - total_time_spent)
            }
        
        return {
            "average_time_per_question_seconds": avg_time,
            "median_time_per_question_seconds": median_time,
            "max_time_per_question_seconds": max_time,
            "min_time_per_question_seconds": min_time,
            "long_questions": long_questions,
            "rushed_questions": rushed_questions,
            "time_distribution": time_distribution,
            "time_vs_correctness": time_vs_correctness,
            "time_pressure": time_pressure
        }
    
    def _calculate_time_distribution(self, times_per_question: List[float]) -> Dict[str, Any]:
        """
        Calculate the distribution of time spent on questions.
        
        Args:
            times_per_question (List[float]): List of times spent on each question
            
        Returns:
            Dict[str, Any]: Time distribution statistics
        """
        if not times_per_question:
            return {}
        
        # Calculate percentiles
        percentiles = {
            "10th": np.percentile(times_per_question, 10),
            "25th": np.percentile(times_per_question, 25),
            "50th": np.percentile(times_per_question, 50),
            "75th": np.percentile(times_per_question, 75),
            "90th": np.percentile(times_per_question, 90)
        }
        
        # Create time bins
        max_time = max(times_per_question)
        bin_size = max_time / 10 if max_time > 0 else 1
        bins = [int(i * bin_size) for i in range(11)]  # 0 to max_time in 10 steps
        
        # Count questions in each bin
        hist, _ = np.histogram(times_per_question, bins=bins)
        
        # Create histogram data
        histogram = [
            {
                "bin_start": bins[i],
                "bin_end": bins[i+1],
                "count": int(hist[i])
            }
            for i in range(len(hist))
        ]
        
        return {
            "percentiles": percentiles,
            "histogram": histogram
        }
    
    def _analyze_time_vs_correctness(self, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the relationship between time spent and correctness.
        
        Args:
            answers (List[Dict[str, Any]]): List of answers
            
        Returns:
            Dict[str, Any]: Analysis of time vs. correctness
        """
        # Separate times for correct and incorrect answers
        correct_times = [a.get("time_spent_seconds", 0) for a in answers if a.get("is_correct", False)]
        incorrect_times = [a.get("time_spent_seconds", 0) for a in answers if not a.get("is_correct", False)]
        
        # Calculate statistics
        avg_correct_time = sum(correct_times) / len(correct_times) if correct_times else 0
        avg_incorrect_time = sum(incorrect_times) / len(incorrect_times) if incorrect_times else 0
        
        # Determine if there's a correlation between time and correctness
        time_correlation = None
        if correct_times and incorrect_times:
            if avg_correct_time > avg_incorrect_time * 1.2:
                time_correlation = "more_time_better_results"
            elif avg_incorrect_time > avg_correct_time * 1.2:
                time_correlation = "more_time_worse_results"
            else:
                time_correlation = "no_strong_correlation"
        
        return {
            "average_time_correct_seconds": avg_correct_time,
            "average_time_incorrect_seconds": avg_incorrect_time,
            "time_correlation": time_correlation
        }
    
    def _analyze_mistake_patterns(self, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze patterns in mistakes made during the exam.
        
        Args:
            answers (List[Dict[str, Any]]): List of answers
            
        Returns:
            Dict[str, Any]: Mistake pattern analysis
        """
        logger.debug("Analyzing mistake patterns")
        
        # Count mistakes by type
        mistake_counts = Counter()
        for answer in answers:
            if not answer.get("is_correct", False):
                mistake_type = answer.get("mistake_type", "other")
                mistake_counts[mistake_type] += 1
        
        # Calculate percentages
        total_mistakes = sum(mistake_counts.values())
        mistake_percentages = {
            mistake_type: (count / total_mistakes * 100) if total_mistakes > 0 else 0
            for mistake_type, count in mistake_counts.items()
        }
        
        # Identify most common mistake types
        common_mistakes = [
            {"type": mistake_type, "count": count, "percentage": mistake_percentages[mistake_type]}
            for mistake_type, count in mistake_counts.most_common()
        ]
        
        # Analyze mistakes by topic
        mistakes_by_topic = defaultdict(Counter)
        for answer in answers:
            if not answer.get("is_correct", False):
                mistake_type = answer.get("mistake_type", "other")
                for topic in answer.get("topics", []):
                    mistakes_by_topic[topic][mistake_type] += 1
        
        # Convert to serializable format
        mistakes_by_topic_serializable = {
            topic: [{"type": m_type, "count": count} 
                   for m_type, count in counter.most_common(3)]
            for topic, counter in mistakes_by_topic.items()
        }
        
        return {
            "total_mistakes": total_mistakes,
            "mistake_counts": dict(mistake_counts),
            "mistake_percentages": mistake_percentages,
            "common_mistakes": common_mistakes,
            "mistakes_by_topic": mistakes_by_topic_serializable
        }
    
    def _generate_visualizations(self, 
                               topic_analysis: Dict[str, Any],
                               time_analysis: Dict[str, Any],
                               mistake_analysis: Dict[str, Any],
                               output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Generate visualization charts for the analysis.
        
        Args:
            topic_analysis (Dict[str, Any]): Topic analysis results
            time_analysis (Dict[str, Any]): Time analysis results
            mistake_analysis (Dict[str, Any]): Mistake analysis results
            output_dir (str, optional): Directory to save visualizations
            
        Returns:
            Dict[str, str]: Paths to generated visualizations
        """
        logger.debug("Generating visualizations")
        
        visualization_paths = {}
        
        try:
            # Create output directory if needed
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            else:
                output_dir = "."
            
            # Generate topic performance chart
            topic_chart_path = os.path.join(output_dir, "topic_performance.png")
            self._generate_topic_chart(topic_analysis, topic_chart_path)
            visualization_paths["topic_performance"] = topic_chart_path
            
            # Generate time distribution chart
            time_chart_path = os.path.join(output_dir, "time_distribution.png")
            self._generate_time_chart(time_analysis, time_chart_path)
            visualization_paths["time_distribution"] = time_chart_path
            
            # Generate mistake pattern chart
            mistake_chart_path = os.path.join(output_dir, "mistake_patterns.png")
            self._generate_mistake_chart(mistake_analysis, mistake_chart_path)
            visualization_paths["mistake_patterns"] = mistake_chart_path
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")
        
        return visualization_paths
    
    def _generate_topic_chart(self, topic_analysis: Dict[str, Any], output_path: str) -> None:
        """
        Generate a chart showing performance by topic.
        
        Args:
            topic_analysis (Dict[str, Any]): Topic analysis results
            output_path (str): Path to save the chart
        """
        try:
            topic_stats = topic_analysis.get("topic_stats", {})
            if not topic_stats:
                logger.warning("No topic data available for chart")
                return
            
            # Extract data for chart
            topics = []
            scores = []
            
            for topic_id, stats in topic_stats.items():
                if stats["total_questions"] > 0:
                    topics.append(stats["name"])
                    scores.append(stats["score"] * 100)  # Convert to percentage
            
            if not topics:
                logger.warning("No topics with questions for chart")
                return
            
            # Create chart
            plt.figure(figsize=(10, 6))
            bars = plt.bar(topics, scores, color='skyblue')
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}%', ha='center', va='bottom')
            
            plt.xlabel('Topics')
            plt.ylabel('Score (%)')
            plt.title('Performance by Topic')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.ylim(0, 105)  # Set y-axis limit to 0-105%
            
            # Save chart
            plt.savefig(output_path)
            plt.close()
            
            logger.debug(f"Topic performance chart saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error generating topic chart: {str(e)}")
    
    def _generate_time_chart(self, time_analysis: Dict[str, Any], output_path: str) -> None:
        """
        Generate a chart showing time distribution.
        
        Args:
            time_analysis (Dict[str, Any]): Time analysis results
            output_path (str): Path to save the chart
        """
        try:
            time_distribution = time_analysis.get("time_distribution", {})
            histogram = time_distribution.get("histogram", [])
            
            if not histogram:
                logger.warning("No time distribution data available for chart")
                return
            
            # Extract data for chart
            bin_labels = [f"{h['bin_start']}-{h['bin_end']}" for h in histogram]
            counts = [h["count"] for h in histogram]
            
            # Create chart
            plt.figure(figsize=(10, 6))
            plt.bar(bin_labels, counts, color='lightgreen')
            plt.xlabel('Time Range (seconds)')
            plt.ylabel('Number of Questions')
            plt.title('Time Distribution')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Save chart
            plt.savefig(output_path)
            plt.close()
            
            logger.debug(f"Time distribution chart saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error generating time chart: {str(e)}")
    
    def _generate_mistake_chart(self, mistake_analysis: Dict[str, Any], output_path: str) -> None:
        """
        Generate a chart showing mistake patterns.
        
        Args:
            mistake_analysis (Dict[str, Any]): Mistake analysis results
            output_path (str): Path to save the chart
        """
        try:
            mistake_counts = mistake_analysis.get("mistake_counts", {})
            
            if not mistake_counts:
                logger.warning("No mistake data available for chart")
                return
            
            # Extract data for chart
            mistake_types = list(mistake_counts.keys())
            counts = list(mistake_counts.values())
            
            # Create readable labels
            readable_labels = [t.replace('_', ' ').title() for t in mistake_types]
            
            # Create chart
            plt.figure(figsize=(10, 6))
            bars = plt.bar(readable_labels, counts, color='salmon')
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        str(int(height)), ha='center', va='bottom')
            
            plt.xlabel('Mistake Type')
            plt.ylabel('Count')
            plt.title('Mistake Patterns')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Save chart
            plt.savefig(output_path)
            plt.close()
            
            logger.debug(f"Mistake patterns chart saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error generating mistake chart: {str(e)}")
    
    def _generate_recommendations(self,
                                topic_analysis: Dict[str, Any],
                                time_analysis: Dict[str, Any],
                                mistake_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate personalized recommendations based on the analysis.
        
        Args:
            topic_analysis (Dict[str, Any]): Topic analysis results
            time_analysis (Dict[str, Any]): Time analysis results
            mistake_analysis (Dict[str, Any]): Mistake analysis results
            
        Returns:
            List[Dict[str, Any]]: List of recommendations
        """
        logger.debug("Generating recommendations")
        
        recommendations = []
        
        # Topic-based recommendations
        topic_stats = topic_analysis.get("topic_stats", {})
        weakest_topics = topic_analysis.get("weakest_topics", [])
        
        for topic_id in weakest_topics:
            if topic_id in topic_stats:
                topic_name = topic_stats[topic_id]["name"]
                score = topic_stats[topic_id]["score"] * 100  # Convert to percentage
                
                recommendations.append({
                    "category": "topic",
                    "topic_id": topic_id,
                    "topic_name": topic_name,
                    "recommendation": f"Focus on improving your understanding of {topic_name}. Your current score is {score:.1f}%.",
                    "priority": "high" if score < 50 else "medium"
                })
        
        # Time management recommendations
        time_vs_correctness = time_analysis.get("time_vs_correctness", {})
        time_correlation = time_vs_correctness.get("time_correlation")
        
        if time_correlation == "more_time_better_results":
            recommendations.append({
                "category": "time_management",
                "recommendation": "You perform better when you spend more time on questions. Consider allocating more time for difficult questions.",
                "priority": "medium"
            })
        elif time_correlation == "more_time_worse_results":
            recommendations.append({
                "category": "time_management",
                "recommendation": "Spending more time on questions doesn't improve your results. Focus on understanding the question quickly and moving on if stuck.",
                "priority": "medium"
            })
        
        # Check for rushed questions
        rushed_questions = time_analysis.get("rushed_questions", [])
        if rushed_questions:
            incorrect_rushed = sum(1 for q in rushed_questions if not q.get("is_correct", False))
            if incorrect_rushed > len(rushed_questions) / 2:
                recommendations.append({
                    "category": "time_management",
                    "recommendation": f"You rushed through {len(rushed_questions)} questions and got {incorrect_rushed} wrong. Take more time to read and understand questions.",
                    "priority": "high" if incorrect_rushed > 3 else "medium"
                })
        
        # Mistake pattern recommendations
        common_mistakes = mistake_analysis.get("common_mistakes", [])
        
        for mistake in common_mistakes[:3]:  # Top 3 mistakes
            mistake_type = mistake["type"]
            count = mistake["count"]
            
            if mistake_type == "content_known_but_could_not_express":
                recommendations.append({
                    "category": "mistake_pattern",
                    "mistake_type": mistake_type,
                    "recommendation": f"You knew the content but struggled to express it clearly in {count} questions. Practice writing clear, structured answers.",
                    "priority": "high" if count > 3 else "medium"
                })
            elif mistake_type == "misread_the_question":
                recommendations.append({
                    "category": "mistake_pattern",
                    "mistake_type": mistake_type,
                    "recommendation": f"You misread {count} questions. Slow down and carefully read each question, underlining key words.",
                    "priority": "high" if count > 3 else "medium"
                })
            elif mistake_type == "conceptual_confusion":
                recommendations.append({
                    "category": "mistake_pattern",
                    "mistake_type": mistake_type,
                    "recommendation": f"You had conceptual confusion in {count} questions. Review fundamental concepts and create concept maps to clarify relationships.",
                    "priority": "high" if count > 3 else "medium"
                })
            elif mistake_type == "calculation_mistake":
                recommendations.append({
                    "category": "mistake_pattern",
                    "mistake_type": mistake_type,
                    "recommendation": f"You made calculation errors in {count} questions. Practice step-by-step problem solving and double-check your work.",
                    "priority": "high" if count > 3 else "medium"
                })
        
        return recommendations

# Command-line interface
def main():
    """
    Command-line interface for the Exam Analysis Engine.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Exam Analysis Engine")
    parser.add_argument("--exam-data", required=True, help="Path to exam data JSON file")
    parser.add_argument("--answers", required=True, help="Path to answers JSON file")
    parser.add_argument("--output", default="analysis_results.json", help="Path to output JSON file")
    parser.add_argument("--visualizations", action="store_true", help="Generate visualization charts")
    parser.add_argument("--viz-dir", default="visualizations", help="Directory to save visualizations")
    
    args = parser.parse_args()
    
    try:
        # Load exam data
        with open(args.exam_data, 'r') as f:
            exam_data = json.load(f)
        
        # Load answers
        with open(args.answers, 'r') as f:
            answers = json.load(f)
        
        # Create analyzer
        analyzer = ExamAnalysisEngine()
        
        # Analyze exam
        analysis_result = analyzer.analyze_exam(
            exam_data=exam_data,
            answers=answers,
            generate_visualizations=args.visualizations,
            output_dir=args.viz_dir if args.visualizations else None
        )
        
        # Save analysis results
        with open(args.output, 'w') as f:
            json.dump(analysis_result, f, indent=2)
        
        print(f"Analysis completed and saved to {args.output}")
        
        if args.visualizations:
            print(f"Visualizations saved to {args.viz_dir}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()