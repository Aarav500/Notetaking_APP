# AI Features User Guide

This guide provides detailed information on how to use the AI features in the Pansophy note-taking system.

## Table of Contents

- [Introduction](#introduction)
- [GPT-Powered Features](#gpt-powered-features)
  - [Text Summarization](#text-summarization)
  - [Key Points Extraction](#key-points-extraction)
  - [Question Generation](#question-generation)
  - [Mind Map Generation](#mind-map-generation)
- [Embedding-Based Features](#embedding-based-features)
  - [Semantic Search](#semantic-search)
  - [Auto-Linked Notes](#auto-linked-notes)
  - [Note to Quiz Conversion](#note-to-quiz-conversion)
- [Vision-Based Features](#vision-based-features)
  - [Image Flashcards](#image-flashcards)
  - [Image Mind Maps](#image-mind-maps)
  - [Math Formula Processing](#math-formula-processing)
- [AI UX Features](#ai-ux-features)
  - [Misconception Detector](#misconception-detector)
  - [Auto-Linked Notes](#auto-linked-notes-1)
  - [Discord Daily Agent](#discord-daily-agent)
- [Configuring AI Settings](#configuring-ai-settings)
  - [API Keys](#api-keys)
  - [Model Selection](#model-selection)
  - [Caching Settings](#caching-settings)

## Introduction

Pansophy leverages advanced AI technologies to enhance your note-taking and learning experience. These AI features include:

- **GPT Integration**: Uses OpenAI's GPT models or Azure OpenAI Service for text generation, summarization, and more
- **Embedding-Based Features**: Uses vector embeddings to find semantic relationships between notes
- **Vision-Based Features**: Processes images to extract information and create learning materials
- **AI UX Enhancements**: Provides intelligent user experience improvements

## GPT-Powered Features

### Text Summarization

Automatically generate concise summaries of your notes, articles, or any text content.

**How to use:**

1. Open a note or import content (text, PDF, webpage)
2. Click the "Summarize" button in the toolbar
3. Select the desired summary length (short, medium, long)
4. The AI will generate a summary that captures the main points

**Example:**

```
Original text: [Long paragraph about machine learning concepts...]
Summary: Machine learning is a subset of AI that uses algorithms to learn from data. The main types are supervised learning (using labeled data), unsupervised learning (finding patterns in unlabeled data), and reinforcement learning (learning through environment interaction).
```

### Key Points Extraction

Extract the most important points from your content.

**How to use:**

1. Open a note or import content
2. Click the "Extract Key Points" button
3. Adjust the number of key points to extract (default: 5)
4. The AI will identify and list the most important points

**Example:**

```
Key Points:
1. Machine learning algorithms learn from data without explicit programming
2. Supervised learning requires labeled training data
3. Unsupervised learning finds patterns in unlabeled data
4. Reinforcement learning uses rewards and penalties
5. Deep learning uses neural networks with multiple layers
```

### Question Generation

Generate study questions based on your notes.

**How to use:**

1. Open a note
2. Click the "Generate Questions" button
3. Select the question type (multiple choice, short answer, etc.)
4. Specify the number of questions
5. The AI will generate questions based on your content

**Example:**

```
Questions:
1. What are the three main types of machine learning?
   a) Supervised, unsupervised, and reinforcement learning
   b) Classification, regression, and clustering
   c) Neural networks, decision trees, and SVMs
   d) Batch learning, online learning, and transfer learning

2. What distinguishes supervised learning from unsupervised learning?
   [Short answer space]
```

### Mind Map Generation

Create visual mind maps from your notes.

**How to use:**

1. Open a note
2. Click the "Generate Mind Map" button
3. The AI will analyze your content and create a hierarchical mind map
4. You can edit the mind map manually after generation

**Example:**

```
mindmap
  root((Machine Learning))
    Types
      Supervised Learning
        Classification
        Regression
      Unsupervised Learning
        Clustering
        Dimensionality Reduction
      Reinforcement Learning
        Q-Learning
        Policy Gradient
    Applications
      Computer Vision
      Natural Language Processing
      Recommendation Systems
```

## Embedding-Based Features

### Semantic Search

Search your notes using natural language queries.

**How to use:**

1. Click the search icon in the top bar
2. Enter your query in natural language
3. The system will find semantically relevant notes, even if they don't contain the exact search terms
4. Results are ranked by relevance

**Example:**

```
Query: "How do neural networks learn?"
Results:
1. Deep Learning Fundamentals (92% match)
2. Backpropagation Algorithm (87% match)
3. Gradient Descent Optimization (79% match)
```

### Auto-Linked Notes

Automatically discover and link related notes.

**How to use:**

1. This feature works automatically in the background
2. When viewing a note, related notes appear in the sidebar
3. Click on a related note to open it
4. The relationship strength is indicated by a percentage

**Example:**

```
Current note: "Neural Networks Basics"
Related notes:
- Deep Learning Architectures (92% related)
- Activation Functions (85% related)
- Backpropagation Algorithm (82% related)
```

### Note to Quiz Conversion

Convert your notes into quizzes for active recall practice.

**How to use:**

1. Open a note
2. Click the "Create Quiz" button
3. Select the quiz type and number of questions
4. The AI will generate a quiz based on your note content
5. Take the quiz to test your knowledge

**Example:**

```
Note: [Content about neural networks]
Quiz:
1. What is the purpose of an activation function in a neural network?
2. How does backpropagation work?
3. What is the difference between a convolutional neural network and a recurrent neural network?
```

## Vision-Based Features

### Image Flashcards

Generate flashcards from images or diagrams.

**How to use:**

1. Import an image or take a screenshot
2. Click the "Create Flashcards from Image" button
3. The AI will analyze the image and generate question-answer pairs
4. Review and edit the flashcards if needed
5. Save to your flashcard collection

**Example:**

```
[Image of neural network architecture]
Question: What are the three main components shown in this neural network diagram?
Answer: Input layer, hidden layers, and output layer.
```

### Image Mind Maps

Create mind maps from diagrams or visual content.

**How to use:**

1. Import an image containing a diagram or structured information
2. Click the "Create Mind Map from Image" button
3. The AI will analyze the image and generate a mind map
4. Edit the mind map as needed

**Example:**

```
[Image of machine learning taxonomy]
[Generated mind map showing the hierarchy of machine learning algorithms]
```

### Math Formula Processing

Extract and process mathematical formulas from images.

**How to use:**

1. Import an image containing mathematical formulas
2. Click the "Extract Formulas" button
3. The AI will identify and extract the formulas in LaTeX format
4. You can edit the formulas and add explanations

**Example:**

```
[Image with formula E = mc²]
Extracted formula: E = mc^2
Explanation: Einstein's mass-energy equivalence formula, where E is energy, m is mass, and c is the speed of light.
```

## AI UX Features

### Misconception Detector

Identify potential misconceptions in your notes.

**How to use:**

1. This feature works automatically when you create or edit notes
2. Potential misconceptions are highlighted with a yellow underline
3. Hover over the highlighted text to see the explanation
4. Accept the suggestion or dismiss it

**Example:**

```
Note text: "Neural networks always require large amounts of data to train effectively."
Misconception alert: "This is not always true. Some neural networks can be effective with small datasets, especially when using transfer learning or data augmentation techniques."
```

### Auto-Linked Notes

(See [Auto-Linked Notes](#auto-linked-notes) in the Embedding-Based Features section)

### Discord Daily Agent

Receive daily learning prompts and micro-quizzes via Discord.

**How to use:**

1. Go to Settings > Integrations
2. Connect your Discord account
3. Configure the agent settings:
   - Study schedule
   - Topics to focus on
   - Quiz frequency
   - Reminder preferences
4. The agent will send you daily messages with:
   - Learning prompts
   - Micro-quizzes
   - Spaced repetition reminders
   - Study streak updates

**Example:**

```
[Discord message]
Good morning! Here's your daily micro-quiz on Neural Networks:

Q: What activation function is commonly used in the output layer for binary classification?
A) ReLU
B) Sigmoid
C) Tanh
D) Softmax

Reply with your answer to check!
```

## Configuring AI Settings

### API Keys

Configure your API keys for OpenAI or Azure OpenAI Service.

**How to set up:**

1. Go to Settings > AI Configuration
2. Enter your API keys:
   - OpenAI API Key
   - Azure OpenAI API Key (if using Azure)
   - Azure OpenAI Endpoint (if using Azure)
3. Test the connection
4. Save your settings

**Note:** Your API keys are stored securely and are only used for API calls from your application.

### Model Selection

Choose which AI models to use for different features.

**How to configure:**

1. Go to Settings > AI Configuration > Models
2. For each feature, select the preferred model:
   - Text generation: GPT-4, GPT-3.5-Turbo, etc.
   - Embeddings: text-embedding-3-small, text-embedding-3-large, etc.
   - Image processing: GPT-4 Vision, etc.
3. You can also select local models if available
4. Save your settings

### Caching Settings

Configure how AI-generated content is cached to reduce API calls and improve performance.

**How to configure:**

1. Go to Settings > AI Configuration > Caching
2. Configure the following settings:
   - Cache location (local or cloud)
   - Cache size limit
   - Cache expiration time
   - Content types to cache (summaries, flashcards, etc.)
3. You can clear the cache manually if needed
4. Save your settings

**Note:** Caching reduces API usage and costs while improving response times for repeated operations.