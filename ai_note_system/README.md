# AI Note System (Pansophy)

A comprehensive AI-powered note-taking and knowledge management system that processes various inputs, extracts key information, generates visualizations, and creates active recall materials.

## 🚀 Features

> **Oracle Cloud Deployment**: For instructions on deploying this application to Oracle Cloud Infrastructure, see [ORACLE_CLOUD_DEPLOYMENT.md](ORACLE_CLOUD_DEPLOYMENT.md)

- **Multiple Input Types**: Process text, PDFs, images, voice recordings (with Whisper and SpeechRecognition engines), and YouTube videos
- **AI-Powered Processing**: Extract summaries, key points, and glossary terms
- **AI-Powered Visualization Generation**: Create flowcharts, mind maps, timelines, knowledge graphs, 3D tree graphs, and word clouds using LLM-enhanced algorithms
- **Active Recall**: Generate questions, MCQs, fill-in-the-blanks, and more
- **Spaced Repetition**: Track learning progress with SM-2 algorithm
- **Notion Integration**: Sync notes with structured Notion pages
- **Export Options**: Export to Markdown, PDF, and Anki
- **Auto-Linking**: Automatically link related topics across your knowledge hierarchy
- **Database Support**: Store and manage all your notes and related data efficiently
  - **SQLite**: Default lightweight database for local development
  - **Oracle ATP/MySQL HeatWave**: Enterprise-grade database for cloud deployment
- **ML Enhancements**: Content gap filling, mastery estimation, and adaptive quizzes
- **Learning Agents**: Personalized learning assistants to guide your study
- **Automated Research Agent**: Research topics from multiple sources (Wikipedia, ArXiv, Semantic Scholar, YouTube, GitHub, web) and generate structured knowledge packs
- **YouTube Video Processing**: Download transcripts, segment by timestamps, and generate structured notes with timestamp references
- **Mathematical Formula Processing**: Detect, extract, and OCR math formulas from images, link formulas to explanations, and generate practice problems
- **Image-Based Flashcards**: Extract images from PDFs, slides, and videos; generate Q&A pairs using GPT-4 Vision
- **Speech Generation**: Convert notes to speech using various TTS engines (gTTS, pyttsx3, Azure)
- **Reminder System**: Schedule reminders for study sessions with notifications via email, desktop, Slack, and Discord
- **Plugin System**: Extend functionality with custom plugins
- **Multilingual Processing**: Process and generate content in multiple languages
- **Image Extraction and Processing**: Extract and analyze images from various sources
- **Study Planning**: Generate personalized study plans based on content and learning goals
- **Misconception Detection**: Identify and flag potential misconceptions in notes
- **Semantic Search & Q&A Agent**: Ask questions in natural language across all notes, imported papers, videos, and research packs using embedding + RAG
- **Automatic Topic Clustering & Hierarchical Organization**: Auto-cluster related notes using embeddings and generate hierarchical topic trees
- **Auto-Updating Research Feeds**: Monitor ArXiv, YouTube channels, and blogs for new content based on specified interests
- **Knowledge Decay & Refresh Suggestions**: Track knowledge decay using time-based decay curves and recommend when to review topics
- **Code & Notebook Generator**: Generate runnable Jupyter notebooks with explanations from theoretical notes
- **Project & Lab Practice Generator**: Generate mini-project ideas and practice lab tasks based on study notes
- **Cognitive Bias & Logical Fallacy Detector**: Detect logical inconsistencies, overgeneralizations, and cognitive biases in notes
- **Browser Extension Integration**: Highlight text on any webpage to auto-summarize and add to notes
- **Analytics & Mastery Dashboard**: Track time spent per topic, active vs passive learning ratio, and visualize mastery heatmaps
- **Privacy-Preserving Cloud Sync**: End-to-end encrypted sync between devices while maintaining data ownership
- **Visual Diagram Extraction**: Extract flowcharts, graphs, and architecture diagrams from slides or PDFs and convert to editable formats
- **Conversational Tutoring Mode**: Chat-based tutoring on your own notes with corrections and quizzing
- **Experiment Tracking Integration**: Extract model configs, results, and metrics for ML experiments
- **Event-based Reminder Integration**: Generate personalized revision plans before exams or project deadlines
- **Plugin Marketplace**: Enable community-developed plugins for extended functionality
- **Dynamic Knowledge Graph with Reasoning**: Add logical reasoning paths between concepts, highlight dependencies and prerequisites, and enable querying for concept relationships
- **Citation & Source Tracking**: Track where each note or fact came from and auto-generate citations in APA/MLA/IEEE formats for essays and projects
- **Curriculum Generation Mode**: Generate personalized learning paths, resource recommendations, and milestones based on specified learning goals and timeframes
- **Collaboration Mode**: Share knowledge packs with classmates or team members, enable collaborative annotation with comment threads, and track changes
- **Simulated Exam/Test Generator**: Generate timed tests from your notes with multiple-choice, short answer, diagram labeling, and coding exercises, and track scores to improve weak areas
- **Personal Research Summaries**: Monitor specified ArXiv categories and generate personalized summaries with contextual relevance to your notes and possible connections to your projects
- **Emotion & Motivation Tracking**: Track learning performance versus motivation with lightweight mood tagging and generate personalized study strategies based on motivation cycles
- **Zero-Shot Flashcard Generation**: Generate flashcards from unstructured data like screenshots or tweets using LLM and vision models for robust Q&A generation
- **Podcast & Audiobook Processing**: Ingest podcasts and audiobooks by transcribing, summarizing, and generating flashcards and structured notes
- **Personal Knowledge Reasoning Chat**: Generate coherent, personalized explanations using your personal notes and knowledge graph, not just simple retrieval
- **Auto-Correction & Note Refinement**: Run periodic quality checks to flag unclear explanations, identify missing diagrams or examples, and suggest rephrasing for clarity
- **Learning Style Adaptation**: Track user performance to adapt outputs to individual learning styles, prioritizing visual content or text-based learning based on recall effectiveness
- **Multimodal Reasoning Tasks**: Generate connections and explanations from multiple input types (diagrams, research papers, questions) for advanced learning
- **Learning Agent with Accountability Mode**: Create a Telegram/Discord/Slack bot that checks in daily, sends personalized micro-quizzes, and generates quick voice notes for on-the-go learning
- **Content Difficulty Estimator**: Estimate the difficulty level of imported content and organize notes as "Beginner," "Intermediate," or "Advanced" with auto-generated learning paths
- **Time-Sensitive Knowledge Highlighting**: Flag outdated notes in fast-evolving fields like GenAI and ML, and suggest updated papers or videos for these topics
- **AI-Powered Mindset & Habits Coach**: Track daily consistency streaks, focus session quality, and energy/mood patterns; suggest habit tweaks and provide encouragement nudges
- **AI Debugging & Thought Process Tracer**: Guide step-by-step debugging of code, predict potential bug causes, suggest debugging strategies, and identify misconceptions in reasoning
- **Multi-Agent Cooperative Project Planning**: Deploy specialized agents (Roadmapper, Resource Scout, Test Builder, Debugging) that coordinate to generate comprehensive project execution plans with checks and balances
- **Distraction Tracking & Intervention**: Detect app/window switching, inactivity spikes, and distraction patterns; provide soft interventions and weekly distraction pattern reports for improvement
- **Auto-Microlearning Generator**: Automatically create 2-5 minute micro-lessons with key explanations, quick questions, and related diagrams; package for Telegram/Discord/Slack bots for learning during micro-breaks
- **Real-World Application Context Generator**: Generate real-world use cases, industry applications, and historical context for any concept to help connect theory to practical relevance
- **Stress & Cognitive Load Monitor**: Track cognitive fatigue and stress levels using webcam micro-expression detection, keyboard usage patterns, and self-reporting; adjust study recommendations based on cognitive state
- **Interactive Visual Glossary**: Create clickable, interactive term maps showing definitions, related diagrams, example problems, and references to where terms appear in your notes and knowledge graph
- **Voice-Based Conversational Agent**: Enable hands-free learning with voice-based Q&A, flashcard drills, and semantic memory of previous conversations
- **Automatic Essay & Report Draft Generator**: Generate structured essay drafts with proper citations in various formats (APA, MLA, IEEE, etc.), create summary tables, and refine drafts based on feedback
- **Integrated Whiteboard Reasoning**: Create collaborative canvases for mind maps and diagrams with AI auto-labeling and conversion to structured notes
- **Automated Ethics & Bias Analyzer**: Scan ML projects and notes for potential biases, overgeneralized statements, and ethical risks; provide actionable suggestions for improvement
- **Community Knowledge Sharing Layer**: Share anonymized insights, flashcards, and mind maps with others; upvote high-quality resources and build collective learning packs
- **Long-Term Career & Research Path Advisor**: Map potential career paths with layered plans (short/mid/long-term) and suggest mentors, communities, and internships based on interests
- **Custom Dataset Curation Assistant**: Automatically fetch, clean, and summarize open datasets in your field with licensing information and preprocessing code
- **Learning Impact Predictor**: Predict mastery time for concepts, calculate forgetting probability without review, and assess exam readiness based on topic mastery

### 📚 Advanced PDF Reading and Retention

- **In-App Smart Reading View**: Read PDFs directly in the app with adjustable fonts, themes, and margins; add annotations, highlights, and comments; navigate using auto-extracted headings and structure
- **Auto-Active Recall Layer**: Get prompted with micro-questions about recently read sections; generate flashcards using GPT-Vision and LLM summarization; build mind maps of highlighted concepts automatically
- **Long-Term Memory Mode**: Auto-generate summary sheets (5, 15, and 30 min versions), core mind maps, flashcard decks, and timelines of key concepts; track knowledge decay with spaced repetition; receive contextual reminders about previously read books
- **Quick Recall Mode**: Refresh book content with 15-minute interactive re-immersion sessions including key concepts, examples, and quizzes; access structured summaries, personal notes, and highlights
- **Concept Linking Across Books**: Connect overlapping concepts across different books; build a personal knowledge graph showing interconnections; understand how concepts relate to each other

### 💻 Coding Theory-Practice Bridge

- **AI-Powered Coding Competency Map**: Categorize coding skills as critical manual, AI-assisted, or theory-only; analyze notes to generate a personalized competency map; assign relevance scores to skills based on learning goals
- **Theory-to-Practice Converter**: Generate practical coding tasks from theoretical concepts; create interactive Jupyter notebooks for practicing skills; focus on real-world applications of theoretical knowledge
- **Simulation Mode for Practical Problem Solving**: Create realistic debugging exercises and system design challenges; provide guided assistance only when needed to foster independent problem-solving
- **AI Collaboration Awareness Trainer**: Track which tasks are completed manually vs. with AI assistance; calculate a balance score to ensure healthy skill development; provide insights into AI usage patterns
- **Self-Assessment Module**: Assess coding skills based on competency map; identify strengths and areas for improvement; generate personalized learning plans with specific next steps

## 🌟 Advanced Features

### Exam-Focused Learning with Environment Control & Analysis

- **Exam Mode Launcher**: Create a distraction-free environment by closing applications, blocking websites, and enforcing focus periods with configurable break policies
- **Exam Analysis Engine**: Analyze test results to identify areas of weakness, time management issues, and mistake patterns (content known but couldn't express, misread questions, conceptual confusion, calculation mistakes)
- **Exam Research Mode**: Automatically fetch past papers, examiner reports, commonly tested subtopics, and tips for expressing knowledge clearly

### Goal-Based Realistic Roadmap Generator

- **Learning Requirements Research**: Automatically research learning requirements for specific goals based on standard curricula and resources
- **Realistic Effort Estimation**: Estimate required effort based on content complexity and user skill level
- **Adaptive Planning**: Generate date-specific plans with buffer time for revision and unexpected events
- **Dependency Management**: Organize learning requirements based on prerequisites and dependencies
- **Calendar Integration**: Export study plans to calendar applications (iCal format)

### Domain-Specific News Aggregator with Interpretive Summaries

- **Multi-Source Monitoring**: Monitor journals, ArXiv, tech policies, GitHub, newsletters, and blogs for domain-specific content
- **Personalized Relevance Scoring**: Calculate relevance scores based on user interests for content prioritization
- **Interpretive Summaries**: Generate summaries with implications for learning/projects, contrasting viewpoints, long-term significance, and hype assessment
- **Automatic Linking**: Connect news items to existing notes and knowledge graphs
- **Customizable Feeds**: Create and manage multiple feeds for different topics and interests

### Adaptive Revision Engine with Memory Models

- **Spaced Repetition with Knowledge Decay**: Track knowledge decay using personalized decay curves and automatically adjust review frequency
- **Adaptive Review Scheduling**: Increase review frequency for topics you forget faster, based on performance data
- **Memory Model Integration**: Use cognitive science-based memory models to optimize retention
- **Roadmap Integration**: Seamlessly integrate revision schedules with your goal roadmap
- **Performance Analytics**: Track retention rates across different knowledge domains and identify optimal review patterns

### Deep Project Integrator

- **Project Breakdown**: Break down project ideas into manageable modules and components
- **Knowledge Mapping**: Map your existing notes to required skills and identify knowledge gaps
- **Learning Checkpoints**: Generate specific learning milestones and micro-projects to build mastery
- **Progress Tracking**: Track project progress alongside study plans with integrated dashboards
- **Resource Recommendation**: Suggest resources and learning materials specific to project requirements

### Simulation Mode (Practical Learning Layer)

- **Mini-Case Generator**: Create domain-specific case studies and practical scenarios
- **Simulation Exercises**: Generate realistic problem-solving scenarios (e.g., debugging exercises, system design challenges)
- **Real-World Data Interpretation**: Practice interpreting and analyzing real-world data and examples
- **Theory-Practice Connection**: Bridge theoretical knowledge with practical application through guided exercises
- **Scenario Difficulty Scaling**: Adjust complexity of simulations based on current mastery level

### Focused Expression Trainer

- **Expression Analysis**: Analyze written answers for coherence, structure, depth, and completeness
- **Key Point Detection**: Identify missing key points and concepts in your written responses
- **Constructive Feedback**: Provide specific, actionable feedback to improve expression
- **Model Answer Generation**: Generate exemplar answers for comparison and learning
- **Expression Improvement Tracking**: Monitor improvement in expressive capability over time with metrics and visualizations

### Automated Curriculum Comparator

- **Standard Curriculum Analysis**: Compare your learning roadmap with top educational institutions (MIT, Stanford, etc.)
- **Industry Certification Alignment**: Align your learning with industry certification paths and requirements
- **Gap Identification**: Identify missing topics and concepts in your current learning plan
- **Content Recommendation**: Suggest additional content to align with best-in-class standards
- **Customized Alignment**: Tailor comparisons to your specific field and career goals

## 🪐 Architecture

The system is built with a modular architecture that allows for easy extension and customization:

1. **Input Pipelines**: Handle various input types (text, PDF, images, voice)
2. **Processing Pipelines**: Extract information and generate learning materials
3. **Visualization Generators**: Create visual representations of knowledge
4. **Output Pipelines**: Export and sync notes to various formats
5. **Utility & Infrastructure**: Configuration, logging, and database management

## 📋 Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`
- OpenAI API key (or local LLM alternatives)
- Notion API token (optional, for Notion integration)

## 🚀 Getting Started

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure API keys in `config/config.yaml`

### Database Setup

#### SQLite (Default for Local Development)

Before using the system locally, you can initialize the SQLite database:

```bash
# Navigate to the data directory
cd ai_note_system/data

# Run the database initialization script
python init_db.py
```

This will create the `pansophy.db` file with all necessary tables for storing notes, tags, keypoints, glossary terms, questions, and relationships between notes.

#### Oracle ATP or MySQL HeatWave (For Cloud Deployment)

For production deployment on Oracle Cloud, the system supports Oracle ATP or Oracle MySQL HeatWave:

1. Create an Oracle ATP or MySQL HeatWave instance in Oracle Cloud
2. Configure the database connection in `config/config.yaml`:
   ```yaml
   database:
     type: oracle  # or mysql_heatwave
     connection_string: your_connection_string
     username: your_username
     password: your_password
   ```
3. Initialize the Oracle database schema:
   ```bash
   # Initialize Oracle database schema
   python init_oracle_db.py
   ```

The Oracle schema includes tables for users, notes, flashcards, and files, with appropriate relationships between them. The schema is designed for scalability and performance in cloud environments.

### Usage

The system provides a command-line interface with several commands:

#### Process Input

```bash
# Process text input
python main.py process --input "Your text here" --type text --summarize --keypoints --questions

# Process a PDF file
python main.py process --input path/to/file.pdf --type pdf --summarize --keypoints

# Process an image with text
python main.py process --input path/to/image.jpg --type image --summarize

# Record and process speech
python main.py process --type speech --summarize

# Process a YouTube video
python main.py process --input "https://www.youtube.com/watch?v=VIDEO_ID" --type youtube --summarize --keypoints --questions

# Process a YouTube video with advanced options
python main.py process --input "https://www.youtube.com/watch?v=VIDEO_ID" --type youtube --segment-method fixed --segment-size 60 --export-markdown
```

#### YouTube Video Processing

The system can process YouTube videos by downloading transcripts, segmenting them by timestamps, and generating structured notes with timestamp references.

```bash
# Basic YouTube video processing
python main.py process --input "https://www.youtube.com/watch?v=VIDEO_ID" --type youtube

# Specify segmentation method (fixed, topic, or smart)
python main.py process --input "https://www.youtube.com/watch?v=VIDEO_ID" --type youtube --segment-method topic

# Specify segment size in seconds (for fixed segmentation)
python main.py process --input "https://www.youtube.com/watch?v=VIDEO_ID" --type youtube --segment-method fixed --segment-size 60

# Specify transcript language
python main.py process --input "https://www.youtube.com/watch?v=VIDEO_ID" --type youtube --language en

# Export to Markdown with timestamp references
python main.py process --input "https://www.youtube.com/watch?v=VIDEO_ID" --type youtube --export-markdown --output path/to/output.md

# Process with specific LLM model
python main.py process --input "https://www.youtube.com/watch?v=VIDEO_ID" --type youtube --model gpt-3.5-turbo
```

You can also use the YouTube processing functionality programmatically:

```python
from ai_note_system.inputs.youtube_input import process_youtube_video

# Process a YouTube video
result = process_youtube_video(
    youtube_url="https://www.youtube.com/watch?v=VIDEO_ID",
    segment_method="fixed",
    segment_size=60,
    generate_summary=True,
    generate_keypoints=True,
    generate_questions=True,
    export_markdown=True,
    markdown_path="path/to/output.md"
)

# Access the processed data
segments = result.get("processed_segments", [])
for segment in segments:
    print(f"Segment: {segment['timestamp']}")
    print(f"Summary: {segment.get('summary', '')}")
    print(f"Key Points: {segment.get('keypoints', [])}")
```

#### Export Notes

```bash
# Export a note to Markdown
python main.py export --id note_id --format markdown --output path/to/output.md

# Export a note to PDF
python main.py export --id note_id --format pdf --output path/to/output.pdf

# Export a note to Anki
python main.py export --id note_id --format anki --output path/to/output.apkg
```

#### Search Notes

```bash
# Search for notes
python main.py search "query" --tags tag1 tag2 --limit 10
```

#### Review Notes

```bash
# Review a specific note
python main.py review --id note_id

# Review all due notes
python main.py review --due
```

#### View or Edit Configuration

```bash
# View configuration
python main.py config --view

# Edit configuration
python main.py config --edit KEY VALUE
```

#### Semantic Search & Q&A

Ask questions in natural language across all your notes, imported papers, videos, and research packs:

```bash
# Ask a question based on your notes
python main.py pansophy_ask "Explain CNN vs Transformer differences."

# Filter by tags
python main.py pansophy_ask "Give me examples of the chain rule in backpropagation." --tags math neural_networks

# Limit the number of relevant notes to retrieve
python main.py pansophy_ask "What are the key components of a transformer architecture?" --limit 10

# Set similarity threshold
python main.py pansophy_ask "How does BERT work?" --threshold 0.8

# Specify LLM model
python main.py pansophy_ask "Explain the attention mechanism." --model gpt-4

# Don't include source information in the answer
python main.py pansophy_ask "What is transfer learning?" --no-sources
```

#### Automatic Topic Clustering

Automatically cluster related notes and generate hierarchical topic trees:

```bash
# Auto-cluster all notes
python main.py cluster_topics

# Specify clustering algorithm
python main.py cluster_topics --algorithm hdbscan

# Set number of clusters (for KMeans)
python main.py cluster_topics --algorithm kmeans --num-clusters 10

# Filter by tags
python main.py cluster_topics --tags machine_learning deep_learning

# Generate visualization of topic hierarchy
python main.py cluster_topics --visualize mindmap

# Export topic hierarchy
python main.py cluster_topics --export hierarchy.json
```

#### Auto-Updating Research Feeds

Monitor sources for new content based on your interests:

```bash
# Add a new feed
python main.py feeds add --topic "Reinforcement Learning" --sources arxiv youtube

# List all feeds
python main.py feeds list

# Update all feeds
python main.py feeds update

# Update specific feed
python main.py feeds update --id feed_id

# Set update schedule
python main.py feeds schedule --id feed_id --interval daily

# View feed content
python main.py feeds view --id feed_id

# Delete feed
python main.py feeds delete --id feed_id
```

#### Knowledge Decay & Refresh

Track knowledge decay and get refresh suggestions:

```bash
# View knowledge decay metrics
python main.py decay_metrics

# Get refresh suggestions
python main.py refresh_suggestions

# Get refresh suggestions for specific topic
python main.py refresh_suggestions --topic "Neural Networks"

# Set decay curve parameters
python main.py decay_settings --half-life 30 --threshold 0.7
```

#### Code & Notebook Generator

Generate runnable code and Jupyter notebooks from your notes:

```bash
# Generate a notebook from notes
python main.py generate_notebook --notes note_id1 note_id2 --output notebook.ipynb

# Specify programming language
python main.py generate_notebook --notes note_id --language python

# Generate with specific framework
python main.py generate_notebook --notes note_id --framework pytorch

# Generate code snippet
python main.py generate_code --notes note_id --language python --output code.py
```

#### Project & Lab Practice Generator

Generate project ideas and practice tasks based on your notes:

```bash
# Generate project ideas
python main.py generate_projects --topic "Computer Vision"

# Specify difficulty level
python main.py generate_projects --topic "NLP" --difficulty intermediate

# Generate lab practice tasks
python main.py generate_labs --topic "Machine Learning" --count 5

# Generate with time constraints
python main.py generate_projects --topic "Deep Learning" --time-hours 10
```

#### Cognitive Bias & Logical Fallacy Detector

Detect logical inconsistencies and cognitive biases in your notes:

```bash
# Check note for biases
python main.py detect_biases --id note_id

# Check multiple notes
python main.py detect_biases --ids note_id1 note_id2

# Check notes with specific tag
python main.py detect_biases --tags philosophy ethics

# Get explanations for detected biases
python main.py detect_biases --id note_id --explain
```

#### Browser Extension Integration

Manage the browser extension for capturing web content:

```bash
# Install browser extension
python main.py extension install --browser chrome

# Configure extension settings
python main.py extension config --api-key YOUR_API_KEY

# View extension status
python main.py extension status

# List captured content
python main.py extension list_captures
```

#### Analytics & Mastery Dashboard

View analytics and mastery metrics:

```bash
# Generate analytics dashboard
python main.py analytics dashboard

# View time spent per topic
python main.py analytics time_spent

# View mastery heatmap
python main.py analytics mastery_heatmap

# Export analytics data
python main.py analytics export --format csv --output analytics.csv

# View learning progress over time
python main.py analytics progress --period 30d
```

#### Privacy-Preserving Cloud Sync

Sync your notes between devices with end-to-end encryption:

```bash
# Set up cloud sync
python main.py cloud_sync setup

# Add a device
python main.py cloud_sync add_device --name "My Laptop"

# Sync notes
python main.py cloud_sync sync

# List synced devices
python main.py cloud_sync devices

# Remove device
python main.py cloud_sync remove_device --name "Old Phone"

# View sync status
python main.py cloud_sync status
```

#### Visual Diagram Extraction

Extract and convert diagrams from PDFs and images:

```bash
# Extract diagrams from PDF
python main.py extract_diagrams --input document.pdf

# Extract diagrams from image
python main.py extract_diagrams --input image.jpg

# Convert to editable format
python main.py extract_diagrams --input document.pdf --format mermaid

# Extract and save diagrams
python main.py extract_diagrams --input document.pdf --output diagrams/

# Generate flashcards from diagrams
python main.py extract_diagrams --input document.pdf --generate-flashcards
```

#### Conversational Tutoring Mode

Chat with a tutor based on your notes:

```bash
# Start tutoring session
python main.py tutor start --topic "Machine Learning"

# Start tutoring with specific notes
python main.py tutor start --notes note_id1 note_id2

# Start quiz mode
python main.py tutor quiz --topic "Neural Networks"

# Review misconceptions
python main.py tutor review_misconceptions

# Get explanation on specific concept
python main.py tutor explain "Backpropagation"
```

#### Experiment Tracking Integration

Track and visualize machine learning experiments:

```bash
# Track experiment
python main.py track_experiment --config config.json --results results.json

# List experiments
python main.py list_experiments

# View experiment details
python main.py view_experiment --id experiment_id

# Compare experiments
python main.py compare_experiments --ids experiment_id1 experiment_id2

# Visualize experiment results
python main.py visualize_experiment --id experiment_id --metric accuracy
```

#### Event-based Reminder Integration

Set up event-based reminders and revision plans:

```bash
# Add calendar event
python main.py calendar add --title "ML Exam" --date "2025-08-15"

# Generate revision plan for event
python main.py calendar revision_plan --event "ML Exam"

# List upcoming events
python main.py calendar list

# Set reminder for event
python main.py calendar set_reminder --event "ML Exam" --days-before 7

# View revision plan
python main.py calendar view_plan --event "ML Exam"
```

#### Plugin Marketplace

Discover, install, and manage plugins:

```bash
# List available plugins
python main.py plugins marketplace list

# Search for plugins
python main.py plugins marketplace search "anki"

# Install plugin
python main.py plugins marketplace install "anki_sync"

# Update plugin
python main.py plugins marketplace update "anki_sync"

# Remove plugin
python main.py plugins marketplace remove "anki_sync"

# View plugin details
python main.py plugins marketplace info "anki_sync"
```

#### Dynamic Knowledge Graph with Reasoning

Create and query knowledge graphs with logical reasoning paths:

```bash
# Generate a dynamic knowledge graph with reasoning paths
python main.py dynamic_graph --topic "Machine Learning" --include-reasoning

# Query the knowledge graph for concept relationships
python main.py dynamic_graph query "What are the prerequisites for understanding CNN backpropagation?"

# Highlight dependencies between concepts
python main.py dynamic_graph dependencies --concept "Transformer Architecture"

# Visualize causal relationships
python main.py dynamic_graph causal --concepts "Gradient Descent" "Learning Rate"

# Export the dynamic knowledge graph with reasoning
python main.py dynamic_graph export --format html --output reasoning_graph.html
```

#### Citation & Source Tracking

Track sources and generate citations:

```bash
# Add source information to a note
python main.py add_source --note-id note_id --source "YouTube: Stanford CS231n Lecture 5" --url "https://www.youtube.com/watch?v=example"

# Add source with additional metadata
python main.py add_source --note-id note_id --source "Research Paper" --authors "Smith, J., Jones, K." --year 2023 --title "Advances in Deep Learning"

# Generate citations for a note
python main.py generate_citations --note-id note_id --format apa

# Generate citations in multiple formats
python main.py generate_citations --note-id note_id --format apa,mla,ieee --output citations.txt

# View all sources for a note
python main.py view_sources --note-id note_id

# Search notes by source
python main.py search_by_source --source "arXiv"
```

#### Curriculum Generation Mode

Generate personalized learning paths:

```bash
# Generate a learning path for a specific goal
python main.py generate_curriculum --goal "Learn Computer Vision deeply" --timeframe "3 months"

# Generate with specific prior knowledge
python main.py generate_curriculum --goal "Master NLP" --timeframe "6 months" --prior-knowledge "Python,Basic ML"

# Include specific resource types
python main.py generate_curriculum --goal "Learn Reinforcement Learning" --resource-types "videos,papers,books,projects"

# Generate with milestones
python main.py generate_curriculum --goal "Deep Learning for Healthcare" --with-milestones

# Export curriculum to file
python main.py generate_curriculum --goal "Quantum Computing Basics" --export curriculum.md

# Generate with active recall checkpoints
python main.py generate_curriculum --goal "Full Stack Development" --with-active-recall
```

#### Collaboration Mode

Share and collaborate on knowledge:

```bash
# Share a knowledge pack
python main.py share --notes note_id1,note_id2 --with user@example.com

# Create a collaborative workspace
python main.py collaboration create --name "Study Group" --description "ML Study Group"

# Invite users to a workspace
python main.py collaboration invite --workspace "Study Group" --users user1@example.com,user2@example.com

# Add a comment to a note
python main.py add_comment --note-id note_id --text "This explanation could be clearer"

# View comments on a note
python main.py view_comments --note-id note_id

# Track changes to a note
python main.py track_changes --note-id note_id

# Merge changes from collaborators
python main.py merge_changes --note-id note_id --from user@example.com
```

#### Simulated Exam/Test Generator

Generate and take tests from your notes:

```bash
# Generate a test from notes
python main.py generate_test --notes note_id1,note_id2 --duration 60

# Generate test with specific question types
python main.py generate_test --topic "Neural Networks" --question-types mcq,short_answer,coding

# Take a timed test
python main.py take_test --test-id test_id --timed

# Generate test focusing on weak areas
python main.py generate_test --adaptive --focus-weak-areas

# Export test to file
python main.py generate_test --topic "Statistics" --export test.pdf

# Review test results and analytics
python main.py review_test --test-id test_id --with-analytics
```

#### Personal Research Summaries

Monitor and summarize research papers:

```bash
# Set up ArXiv monitoring
python main.py research_monitor setup --categories cs.AI,cs.LG,cs.CV

# Get personalized summaries of new papers
python main.py research_monitor summarize

# Get summaries with relevance to your notes
python main.py research_monitor summarize --with-relevance

# View paper connections to your projects
python main.py research_monitor connections --project-id project_id

# Export research summaries
python main.py research_monitor export --format markdown --output research_summaries.md

# Filter papers by relevance score
python main.py research_monitor filter --min-relevance 0.7
```

#### Emotion & Motivation Tracking

Track motivation and learning performance:

```bash
# Log current motivation level
python main.py track_motivation --level 7 --notes "Feeling productive today"

# View motivation history
python main.py view_motivation --period 30d

# Generate motivation insights
python main.py motivation_insights

# Correlate motivation with learning performance
python main.py motivation_correlate --with-performance

# Get personalized study strategy
python main.py study_strategy --based-on-motivation

# Export motivation data
python main.py export_motivation --format csv --output motivation_data.csv
```

#### Zero-Shot Flashcard Generation

Generate flashcards from unstructured data:

```bash
# Generate flashcards from an image
python main.py zero_shot_flashcards --input image.jpg

# Generate from a screenshot
python main.py zero_shot_flashcards --input screenshot.png --type screenshot

# Generate from a tweet or social media post
python main.py zero_shot_flashcards --input tweet.txt --type social_media

# Specify number of flashcards to generate
python main.py zero_shot_flashcards --input random_notes.txt --count 10

# Export generated flashcards
python main.py zero_shot_flashcards --input lecture_slide.jpg --export anki
```

#### Podcast & Audiobook Processing

Process audio content:

```bash
# Process a podcast episode
python main.py process_audio --input podcast.mp3 --type podcast

# Process an audiobook
python main.py process_audio --input audiobook.mp3 --type audiobook

# Transcribe audio only
python main.py process_audio --input audio.mp3 --transcribe-only

# Generate summary and notes
python main.py process_audio --input podcast.mp3 --summarize --generate-notes

# Generate flashcards from audio
python main.py process_audio --input lecture.mp3 --generate-flashcards

# Export processed audio content
python main.py process_audio --input interview.mp3 --export markdown --output interview_notes.md
```

#### Personal Knowledge Reasoning Chat

Chat with your knowledge base:

```bash
# Start a reasoning chat session
python main.py knowledge_chat

# Ask a specific question
python main.py knowledge_chat --question "Explain CNN vs RNN from my notes"

# Chat with specific context
python main.py knowledge_chat --context "Neural Networks" --question "Why is attention better than recurrence?"

# Export chat history
python main.py knowledge_chat --export chat_history.md

# Enable deep reasoning mode
python main.py knowledge_chat --deep-reasoning

# Use specific notes as context
python main.py knowledge_chat --notes note_id1,note_id2 --question "Compare these approaches"
```

#### Auto-Correction & Note Refinement

Improve note quality:

```bash
# Run quality check on a note
python main.py quality_check --note-id note_id

# Check for unclear explanations
python main.py quality_check --note-id note_id --check-clarity

# Identify missing diagrams or examples
python main.py quality_check --note-id note_id --check-completeness

# Suggest rephrasing for clarity
python main.py quality_check --note-id note_id --suggest-rephrasing

# Run periodic quality checks on all notes
python main.py quality_check --periodic

# Apply suggested improvements automatically
python main.py quality_check --note-id note_id --auto-apply
```

#### Learning Style Adaptation

Adapt content to your learning style:

```bash
# Analyze your learning style
python main.py learning_style analyze

# Generate content adapted to your style
python main.py generate_adapted --note-id note_id

# Convert text notes to visual format
python main.py adapt_format --note-id note_id --to visual

# Convert visual content to text format
python main.py adapt_format --note-id note_id --to textual

# View learning style analytics
python main.py learning_style analytics

# Update learning style preferences manually
python main.py learning_style update --preference visual
```

#### Multimodal Reasoning Tasks

Work with multiple input types:

```bash
# Process multiple inputs together
python main.py multimodal_reasoning --diagram diagram.jpg --paper paper.pdf --question "How does this relate to X?"

# Generate connections between inputs
python main.py multimodal_reasoning --inputs input1.jpg,input2.pdf --generate-connections

# Create explanations from multiple sources
python main.py multimodal_reasoning --inputs input1.jpg,input2.pdf --generate-explanation

# Generate Q&A from multimodal inputs
python main.py multimodal_reasoning --inputs input1.jpg,input2.pdf --generate-qa

# Export multimodal reasoning results
python main.py multimodal_reasoning --inputs input1.jpg,input2.pdf --export results.md
```

#### Learning Agent with Accountability Mode

Set up an accountability bot:

```bash
# Set up accountability agent
python main.py accountability setup --platform telegram --username @your_username

# Configure daily check-ins
python main.py accountability schedule --time "09:00" --days mon,tue,wed,thu,fri

# Configure micro-quizzes
python main.py accountability quizzes --frequency daily --topics "Current Study Topics"

# Generate voice notes for on-the-go learning
python main.py accountability voice_notes --topic "Machine Learning" --duration 5min

# View accountability statistics
python main.py accountability stats --period 30d

# Adjust accountability settings
python main.py accountability settings --strictness medium
```

#### Content Difficulty Estimator

Estimate and organize content by difficulty:

```bash
# Estimate difficulty of content
python main.py estimate_difficulty --input document.pdf

# Organize notes by difficulty
python main.py organize_by_difficulty

# Generate learning path based on difficulty
python main.py difficulty_learning_path --start beginner --target advanced

# View difficulty distribution of notes
python main.py difficulty_analytics

# Manually set difficulty level
python main.py set_difficulty --note-id note_id --level intermediate

# Filter notes by difficulty
python main.py filter_notes --difficulty beginner
```

#### Time-Sensitive Knowledge Highlighting

Manage knowledge freshness:

```bash
# Flag outdated notes
python main.py knowledge_freshness --check-outdated

# Suggest updates for outdated content
python main.py knowledge_freshness --suggest-updates --topic "GenAI"

# Set knowledge half-life for topics
python main.py knowledge_freshness --set-half-life --topic "ML" --months 6

# View knowledge freshness report
python main.py knowledge_freshness --report

# Update outdated notes automatically
python main.py knowledge_freshness --auto-update --topic "Transformers"

# Export freshness analytics
python main.py knowledge_freshness --export-analytics freshness.csv
```

#### AI-Powered Mindset & Habits Coach

Track and improve learning habits:

```bash
# Log your current mood and energy levels
python main.py mindset log_mood --energy 4 --motivation 3 --focus 4 --notes "Feeling productive today"

# View your mood history
python main.py mindset view_moods --period 30d

# Update a consistency streak
python main.py mindset update_streak --type daily_study

# View your consistency streaks
python main.py mindset view_streaks

# Get a personalized habit suggestion
python main.py mindset suggest_habit

# Record focus session quality
python main.py mindset record_focus --session-id 123 --quality 0.8 --distractions 3

# Adjust your learning roadmap based on consistency patterns
python main.py mindset adjust_roadmap --roadmap-id roadmap_123

# Start the mindset coach scheduler for periodic checks
python main.py mindset start_scheduler
```

#### AI Debugging & Thought Process Tracer

Debug code and trace thought processes:

```bash
# Create a debugging session with a buggy code snippet
python main.py debug create --language python --file buggy_code.py

# Add a debugging step
python main.py debug add_step --session-id 123 --action "Examined the function logic" --observation "The function doesn't check for empty input" --hypothesis "Division by zero error"

# Generate test cases for a debugging session
python main.py debug generate_tests --session-id 123 --count 5

# Run test cases
python main.py debug run_tests --session-id 123

# Predict potential bug causes
python main.py debug predict_causes --session-id 123

# Suggest debugging strategies
python main.py debug suggest_strategies --session-id 123

# Analyze a thought process about code
python main.py debug analyze_thought --code-file code.py --explanation "explanation.txt"

# Complete a debugging session
python main.py debug complete --session-id 123
```

#### Voice-Based Conversational Agent

Enable hands-free learning:

```bash
# Start a voice conversation
python main.py voice start_conversation --title "Learning Session"

# Ask a question using voice input
python main.py voice ask --use-voice-input

# Ask a question using text input but get voice output
python main.py voice ask --question "Explain neural networks" --use-voice-output

# Continue an existing conversation
python main.py voice ask --conversation-id 123 --question "How does backpropagation work?"

# Start a flashcard drill session
python main.py voice flashcards --topic "Machine Learning" --count 5

# Search conversation history
python main.py voice search --query "neural networks"

# Set voice settings
python main.py voice set_voice --engine gtts --voice en-us --rate 1.0
```

#### Automatic Essay & Report Draft Generator

Generate structured essays and reports:

```bash
# Generate an essay draft on a topic
python main.py essay generate --topic "Impact of AI on Education" --word-count 1500

# Generate an essay using specific notes
python main.py essay generate --notes note_id1,note_id2 --citation-style apa

# Include a summary table
python main.py essay generate --topic "Climate Change" --include-summary-table

# Refine an essay draft based on feedback
python main.py essay refine --essay-id 123 --feedback "feedback.txt"

# Format citations in a specific style
python main.py essay format_citations --essay-id 123 --style mla

# Get user's essay drafts
python main.py essay list --limit 10
```

#### Integrated Whiteboard Reasoning

Create and manage interactive whiteboards:

```bash
# Create a new whiteboard
python main.py whiteboard create --title "Machine Learning Concepts" --description "Visual map of ML concepts"

# Add a text element to the whiteboard
python main.py whiteboard add_element --id 123 --type text --position "100,100" --content "Neural Networks"

# Add an image element
python main.py whiteboard add_element --id 123 --type image --position "300,100" --file image.jpg

# Add a link between elements
python main.py whiteboard add_link --id 123 --from-element 1 --to-element 2 --type "related"

# Auto-label elements using AI
python main.py whiteboard auto_label --id 123

# Convert whiteboard to structured notes
python main.py whiteboard convert_to_notes --id 123 --format markdown

# Export whiteboard as image
python main.py whiteboard export --id 123 --format png --output whiteboard.png
```

#### Automated Ethics & Bias Analyzer

Scan for biases and ethical issues:

```bash
# Analyze a note for biases
python main.py ethics analyze_note --note-id 123

# Analyze a note from a file
python main.py ethics analyze_note --file note.txt

# Analyze an ML project
python main.py ethics analyze_project --file project.py --description "Customer churn prediction model"

# Get suggestions for improvement
python main.py ethics get_suggestions --analysis-id 123

# Generate a bias report
python main.py ethics generate_report --note-id 123 --output report.md

# Check for ethical risks in algorithm design
python main.py ethics check_algorithm --file algorithm.py
```

#### Community Knowledge Sharing Layer

Share and collaborate on knowledge:

```bash
# Share content with the community
python main.py community share --type note --note-id 123 --anonymous --permission public

# Create a learning pack
python main.py community create_pack --name "Machine Learning Fundamentals" --description "Essential ML concepts" --topic "machine_learning" --level beginner

# Add content to a learning pack
python main.py community add_to_pack --pack-id 123 --content-ids 456,789

# Upvote shared content
python main.py community upvote --content-id 123

# Search for shared content
python main.py community search --query "neural networks" --type note

# View popular learning packs
python main.py community popular_packs --topic "machine_learning" --limit 10
```

#### Long-Term Career & Research Path Advisor

Plan your career and research path:

```bash
# Create a career goal
python main.py career create_goal --title "Become a Machine Learning Engineer" --description "Work as an ML engineer at a tech company" --field "machine_learning"

# Generate career paths
python main.py career generate_paths --goal-id 123

# Generate a layered plan
python main.py career generate_plan --path-id 123 --timeframe short,mid,long

# Identify required skills
python main.py career identify_skills --path-id 123

# Suggest mentors and communities
python main.py career suggest_mentors --path-id 123

# Update career progress
python main.py career update_progress --goal-id 123 --milestone-id 456 --status completed
```

#### Custom Dataset Curation Assistant

Fetch and analyze datasets:

```bash
# Search for datasets
python main.py datasets search --query "facial recognition" --attributes "detailed labels"

# Fetch a dataset
python main.py datasets fetch --source kaggle --dataset-id "dataset_name" --output datasets/

# Analyze a dataset
python main.py datasets analyze --file dataset.csv

# Generate preprocessing code
python main.py datasets generate_preprocessing --file dataset.csv --tasks "normalization,missing_values,encoding"

# Get dataset summary
python main.py datasets summarize --file dataset.csv --output summary.md

# Get licensing information
python main.py datasets licensing --dataset-id "dataset_name"
```

#### Learning Impact Predictor

Predict learning outcomes:

```bash
# Predict mastery time for a topic
python main.py impact predict_mastery --topic "Neural Networks" --content "topic_content.txt"

# Calculate forgetting probability
python main.py impact forgetting_probability --prediction-id 123 --days 7

# Update performance data
python main.py impact update_performance --prediction-id 123 --activity-type "quiz" --score 0.8 --time-minutes 30

# Assess exam readiness
python main.py impact assess_exam --name "Machine Learning Exam" --topics "Neural Networks:0.4,Decision Trees:0.3,SVMs:0.3" --date "2025-08-15"

# View learning predictions
python main.py impact view_predictions --topic "Neural Networks"

# Generate a learning impact report
python main.py impact generate_report --user-id 123 --output report.md
```

#### Research a Topic

The system can automatically research a topic from various sources, extract key information, and generate structured knowledge materials.

```bash
# Basic topic research (uses all available sources)
python main.py research "Computer Vision"

# Specify sources to use
python main.py research "Machine Learning" --sources wikipedia arxiv youtube

# Limit the number of results per source
python main.py research "Quantum Computing" --max-results 5

# Specify output directory
python main.py research "Natural Language Processing" --output-dir path/to/research

# Generate visualizations from research results
python main.py research "Reinforcement Learning" --visualize knowledge_graph

# Generate flashcards from research results
python main.py research "Deep Learning" --generate-flashcards

# Generate summary of research results
python main.py research "Artificial Intelligence" --generate-summary

# Print verbose output
python main.py research "Neural Networks" --verbose
```

The research command will:
1. Disambiguate the topic if needed (e.g., "CV" could mean "Computer Vision" or "Curriculum Vitae")
2. Crawl multiple sources for relevant content
3. Download and parse the content
4. Extract key information and organize it
5. Generate visualizations and learning materials if requested
6. Save all research materials to a structured directory

## 📁 Project Structure

```
ai_note_system/
│
├── main.py                   # CLI entry point
├── requirements.txt
├── README.md
├── test_system.py            # Database testing script
├── test_youtube.py           # YouTube processing testing script
│
├── agents/                   # Learning agents
│   ├── learning_agent.py     # Personalized learning assistant
│   ├── quiz_agent.py         # Quiz generation and management
│   ├── research_agent.py     # Automated research assistant
│   ├── tutor_agent.py        # Conversational tutoring mode
│   ├── accountability_agent.py # Accountability and habit tracking
│   └── voice_agent.py        # Voice-based conversational agent
│
├── analytics/                # Analytics & mastery dashboard
│   ├── dashboard_generator.py # Generates analytics dashboards
│   ├── data_collector.py     # Collects usage and learning data
│   └── visualization_components.py # Analytics visualization components
│
├── api/                      # API interfaces
│   ├── embedding_interface.py # Interface for embedding models
│   └── llm_interface.py      # Interface for language models
│
├── browser_extension/        # Browser extension integration
│   ├── api_endpoints.py      # API endpoints for extension communication
│   ├── chrome/               # Chrome extension files
│   └── firefox/              # Firefox extension files
│
├── config/
│   └── config.yaml           # API keys, Notion DB IDs, flags
│
├── data/
│   ├── raw/                  # Raw PDFs, images
│   ├── processed/            # Processed text
│   ├── research/             # Research results
│   ├── feeds/                # Auto-updating research feeds
│   ├── init_db.py            # Database initialization script
│   └── pansophy.db           # SQLite database
│
├── database/
│   └── db_manager.py         # SQLite database management
│
├── embeddings/
│   └── embedder.py           # Embeddings for linking & search
│
├── inputs/
│   ├── text_input.py         # Handles raw text input
│   ├── pdf_input.py          # PDF → text extraction
│   ├── ocr_input.py          # OCR on images
│   ├── speech_input.py       # Voice → text
│   ├── youtube_input.py      # YouTube video processing
│   ├── diagram_extractor.py  # Visual diagram extraction
│   ├── feed_monitor.py       # Auto-updating research feeds
│   └── crawlers/             # Web crawlers for research
│       ├── base_crawler.py   # Base crawler interface
│       └── wikipedia_crawler.py # Wikipedia crawler
│
├── outputs/
│   ├── notion_uploader.py    # Handles Notion API sync
│   ├── export_markdown.py    # Export notes as Markdown
│   ├── export_pdf.py         # Export notes as PDF
│   ├── export_anki.py        # Export as Anki deck
│   ├── spaced_repetition.py  # Handles spaced repetition metadata
│   ├── refresh_suggestions.py # Knowledge decay & refresh suggestions
│   ├── cloud_sync.py         # Privacy-preserving cloud sync
│   └── reminder_manager.py   # Reminder system with calendar integration
│
├── plugins/
│   ├── plugin_base.py        # Base plugin class
│   ├── plugin_manager.py     # Plugin management
│   ├── marketplace/          # Plugin marketplace
│   │   ├── discovery.py      # Plugin discovery
│   │   └── installer.py      # Plugin installer
│   └── builtin/              # Built-in plugins
│       └── wordcloud_plugin.py # Word cloud generation
│
├── processing/
│   ├── summarizer.py         # Summarizes input using LLMs
│   ├── keypoints_extractor.py# Extracts key points & glossary
│   ├── active_recall_gen.py  # Generates Q&A, MCQs, fill-in
│   ├── topic_linker.py       # Auto-linking related topics
│   ├── misconception_checker.py # Detects misunderstandings
│   ├── simplifier.py         # ELI5 simplification
│   ├── retrieval_qa.py       # Semantic search & Q&A
│   ├── topic_clustering.py   # Automatic topic clustering
│   ├── code_generator.py     # Code & notebook generator
│   ├── practice_generator.py # Project & lab practice generator
│   ├── bias_detector.py      # Cognitive bias & logical fallacy detector
│   ├── essay_generator.py    # Automatic essay & report draft generator
│   ├── ethics_analyzer.py    # Automated ethics & bias analyzer
│   └── ml_enhancements/      # Machine learning enhancements
│       ├── content_gap_filler.py # Identifies and fills content gaps
│       ├── mastery_estimator.py  # Estimates learning mastery
│       └── quiz_adaptive_trainer.py # Adaptive quiz generation
│
├── tracking/
│   ├── study_tracker.py      # Tracks study progress
│   ├── experiment_tracker.py # Experiment tracking integration
│   ├── mindset_coach.py      # AI-Powered mindset and habits coach
│   └── motivation_tracker.py # Emotion and motivation tracking
│
├── utils/
│   ├── logger.py             # Central logging
│   ├── config_loader.py      # Loads YAML configs
│   └── helpers.py            # Misc utilities
│
├── visualization/
│   ├── flowchart_gen.py      # Generates Mermaid or Graphviz diagrams
│   ├── mindmap_gen.py        # Generates mind maps
│   ├── timeline_gen.py       # Generates timelines
│   ├── treegraph_gen.py      # Generates 3D tree graphs
│   ├── knowledge_graph_gen.py # Generates knowledge graphs
│   └── whiteboard.py         # Integrated whiteboard reasoning & note mapping
│
├── learning/
│   ├── adaptive_revision_engine.py # Adaptive revision with memory models
│   ├── code_debugger.py      # AI debugging & thought process tracer
│   ├── career_advisor.py     # Long-term career & research path advisor
│   ├── dataset_assistant.py  # Custom dataset curation & analysis assistant
│   ├── impact_predictor.py   # Learning impact predictor
│   ├── goal_roadmap.py       # Goal-based realistic roadmap generator
│   ├── deep_project_integrator.py # Deep project integrator
│   ├── simulation_mode.py    # Simulation mode for practical learning
│   ├── focused_expression_trainer.py # Focused expression trainer
│   └── curriculum_comparator.py # Automated curriculum comparator
│
├── collaboration/
│   ├── collaboration_manager.py # Manages collaborative workspaces
│   └── community_sharing.py  # Community knowledge sharing layer
│
└── tests/
    ├── test_summarizer.py
    ├── test_keypoints_extractor.py
    └── ...
```

## 🧪 Testing

You can verify that the system is working correctly by running the test script:

```bash
# Run the database test script
python test_system.py
```

This script tests the database functionality by:
1. Verifying the database structure
2. Inserting a test note
3. Adding tags and keypoints
4. Retrieving the stored data

For more comprehensive testing, you can run individual module tests in the `tests` directory.

## 🧠 AI/ML Features

The system includes several AI/ML features to enhance learning:

- **Learning Progress Tracking**: Track mastery scores and identify weak areas
- **Misconception Detection**: Automatically flag potential misconceptions
- **Content Gap Filling**: Identify missing subtopics in your notes
- **Adaptive Quiz Generation**: Generate quizzes focusing on weak areas
- **Summarization Quality Reinforcement**: Compare multiple model outputs
- **Visualization Auto-Generation**: Automatically generate visualizations from text
- **Personalized Learning Agent**: Create a personal AI tutor

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.