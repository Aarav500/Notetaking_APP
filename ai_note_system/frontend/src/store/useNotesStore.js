import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Mock data for initial notes
const initialNotes = [
  { 
    id: 1, 
    title: 'Machine Learning Fundamentals', 
    content: `# Machine Learning Fundamentals

## Introduction to Machine Learning

Machine learning is a subset of artificial intelligence that focuses on developing systems that can learn from and make decisions based on data. Unlike traditional programming, where explicit instructions are provided, machine learning algorithms build models based on sample data to make predictions or decisions without being explicitly programmed to do so.

## Types of Machine Learning

### Supervised Learning

In supervised learning, the algorithm is trained on labeled data, meaning that each training example is paired with an output label. The goal is to learn a mapping from inputs to outputs.

Examples:
- Classification (predicting a label)
- Regression (predicting a continuous value)

### Unsupervised Learning

Unsupervised learning deals with unlabeled data. The algorithm tries to learn the inherent structure of the data without any explicit guidance.

Examples:
- Clustering
- Dimensionality reduction
- Association rule learning

### Reinforcement Learning

Reinforcement learning involves an agent that learns to make decisions by taking actions in an environment to maximize some notion of cumulative reward.`,
    excerpt: 'An overview of machine learning concepts including supervised and unsupervised learning, neural networks, and deep learning architectures.',
    category: 'AI', 
    date: '2025-07-28', 
    lastEdited: '2025-07-29T14:30:00',
    tags: ['ML', 'AI', 'Neural Networks'],
    starred: true
  },
  { 
    id: 2, 
    title: 'React Hooks Deep Dive', 
    content: `# React Hooks Deep Dive

## Introduction to React Hooks

React Hooks are functions that let you "hook into" React state and lifecycle features from function components. Hooks were introduced in React 16.8 as a way to use state and other React features without writing a class component.

## Basic Hooks

### useState

The useState hook lets you add state to functional components. It returns a stateful value and a function to update it.

\`\`\`jsx
import React, { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}
\`\`\`

### useEffect

The useEffect hook lets you perform side effects in function components. It serves the same purpose as componentDidMount, componentDidUpdate, and componentWillUnmount in React classes.

\`\`\`jsx
import React, { useState, useEffect } from 'react';

function Example() {
  const [count, setCount] = useState(0);

  // Similar to componentDidMount and componentDidUpdate:
  useEffect(() => {
    // Update the document title using the browser API
    document.title = \`You clicked \${count} times\`;
    
    // Optional cleanup function (similar to componentWillUnmount)
    return () => {
      document.title = 'React App';
    };
  }, [count]); // Only re-run the effect if count changes

  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}
\`\`\``,
    excerpt: 'Exploring React hooks including useState, useEffect, useContext, useReducer, and creating custom hooks for reusable logic.',
    category: 'Programming', 
    date: '2025-07-25', 
    lastEdited: '2025-07-26T10:15:00',
    tags: ['React', 'JavaScript', 'Hooks'],
    starred: false
  },
  { 
    id: 3, 
    title: 'Advanced Data Structures', 
    content: `# Advanced Data Structures

## Introduction

Data structures are a way of organizing and storing data so that it can be accessed and modified efficiently. Advanced data structures build upon basic ones to solve more complex problems or to provide better performance characteristics for specific operations.

## Trees

### Binary Search Tree (BST)

A binary search tree is a binary tree where each node has at most two children, and:
- All nodes in the left subtree have values less than the node's value
- All nodes in the right subtree have values greater than the node's value

This property makes searching efficient, with an average time complexity of O(log n).

### AVL Tree

An AVL tree is a self-balancing binary search tree where the heights of the two child subtrees of any node differ by at most one. If the difference becomes more than one, rebalancing is done to restore this property.

### Red-Black Tree

A red-black tree is another self-balancing binary search tree with the following properties:
1. Each node is either red or black
2. The root is black
3. All leaves (NIL) are black
4. If a node is red, then both its children are black
5. Every path from a node to any of its descendant NIL nodes contains the same number of black nodes

## Graphs

### Representation

Graphs can be represented using:
- Adjacency Matrix: A 2D array where matrix[i][j] = 1 if there is an edge from vertex i to vertex j
- Adjacency List: An array of lists, where each list contains the neighbors of the corresponding vertex

### Graph Traversal

- Depth-First Search (DFS): Explores as far as possible along each branch before backtracking
- Breadth-First Search (BFS): Explores all neighbors at the present depth before moving to nodes at the next depth level`,
    excerpt: 'Comprehensive notes on advanced data structures including trees, graphs, heaps, and their implementation and applications.',
    category: 'Computer Science', 
    date: '2025-07-22', 
    lastEdited: '2025-07-23T09:45:00',
    tags: ['Algorithms', 'Data Structures'],
    starred: false
  },
];

const useNotesStore = create(
  persist(
    (set, get) => ({
      notes: initialNotes,
      activeNoteId: null,
      
      // Getters
      getActiveNote: () => {
        const { notes, activeNoteId } = get();
        return notes.find(note => note.id === activeNoteId) || null;
      },
      
      getNoteById: (id) => {
        const { notes } = get();
        return notes.find(note => note.id === id) || null;
      },
      
      getFilteredNotes: (searchTerm = '', category = 'All', tags = []) => {
        const { notes } = get();
        return notes.filter(note => {
          // Filter by search term
          const matchesSearch = searchTerm === '' || 
            note.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
            note.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
            note.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
          
          // Filter by category
          const matchesCategory = category === 'All' || note.category === category;
          
          // Filter by tags
          const matchesTags = tags.length === 0 || 
            tags.every(tag => note.tags.includes(tag));
          
          return matchesSearch && matchesCategory && matchesTags;
        });
      },
      
      // Actions
      setActiveNote: (noteId) => set({ activeNoteId: noteId }),
      
      createNote: (noteData) => {
        const { notes } = get();
        const newNote = {
          id: Date.now(), // Simple ID generation
          date: new Date().toISOString().split('T')[0],
          lastEdited: new Date().toISOString(),
          starred: false,
          ...noteData
        };
        
        set({ notes: [newNote, ...notes], activeNoteId: newNote.id });
        return newNote;
      },
      
      updateNote: (id, updatedData) => {
        const { notes } = get();
        const updatedNotes = notes.map(note => 
          note.id === id 
            ? { 
                ...note, 
                ...updatedData, 
                lastEdited: new Date().toISOString() 
              } 
            : note
        );
        
        set({ notes: updatedNotes });
        return updatedNotes.find(note => note.id === id);
      },
      
      deleteNote: (id) => {
        const { notes, activeNoteId } = get();
        const updatedNotes = notes.filter(note => note.id !== id);
        
        // If the active note is being deleted, clear the active note
        const newActiveNoteId = activeNoteId === id ? null : activeNoteId;
        
        set({ 
          notes: updatedNotes,
          activeNoteId: newActiveNoteId
        });
      },
      
      toggleStarNote: (id) => {
        const { notes } = get();
        const note = notes.find(note => note.id === id);
        
        if (note) {
          const updatedNotes = notes.map(n => 
            n.id === id ? { ...n, starred: !n.starred } : n
          );
          
          set({ notes: updatedNotes });
          return !note.starred;
        }
        
        return false;
      },
      
      addTag: (noteId, tag) => {
        const { notes } = get();
        const note = notes.find(note => note.id === noteId);
        
        if (note && !note.tags.includes(tag)) {
          const updatedNotes = notes.map(n => 
            n.id === noteId 
              ? { 
                  ...n, 
                  tags: [...n.tags, tag],
                  lastEdited: new Date().toISOString()
                } 
              : n
          );
          
          set({ notes: updatedNotes });
        }
      },
      
      removeTag: (noteId, tag) => {
        const { notes } = get();
        const note = notes.find(note => note.id === noteId);
        
        if (note && note.tags.includes(tag)) {
          const updatedNotes = notes.map(n => 
            n.id === noteId 
              ? { 
                  ...n, 
                  tags: n.tags.filter(t => t !== tag),
                  lastEdited: new Date().toISOString()
                } 
              : n
          );
          
          set({ notes: updatedNotes });
        }
      },
      
      // Bulk operations
      bulkDeleteNotes: (ids) => {
        const { notes, activeNoteId } = get();
        const updatedNotes = notes.filter(note => !ids.includes(note.id));
        
        // If the active note is being deleted, clear the active note
        const newActiveNoteId = ids.includes(activeNoteId) ? null : activeNoteId;
        
        set({ 
          notes: updatedNotes,
          activeNoteId: newActiveNoteId
        });
      },
      
      bulkAddTag: (ids, tag) => {
        const { notes } = get();
        const updatedNotes = notes.map(note => 
          ids.includes(note.id) && !note.tags.includes(tag)
            ? { 
                ...note, 
                tags: [...note.tags, tag],
                lastEdited: new Date().toISOString()
              } 
            : note
        );
        
        set({ notes: updatedNotes });
      },
      
      bulkRemoveTag: (ids, tag) => {
        const { notes } = get();
        const updatedNotes = notes.map(note => 
          ids.includes(note.id) && note.tags.includes(tag)
            ? { 
                ...note, 
                tags: note.tags.filter(t => t !== tag),
                lastEdited: new Date().toISOString()
              } 
            : note
        );
        
        set({ notes: updatedNotes });
      },
      
      // Import/Export
      importNotes: (importedNotes) => {
        // Merge imported notes with existing notes, avoiding duplicates by ID
        const { notes } = get();
        const existingIds = new Set(notes.map(note => note.id));
        
        const newNotes = importedNotes.filter(note => !existingIds.has(note.id));
        const mergedNotes = [...notes, ...newNotes];
        
        set({ notes: mergedNotes });
        return newNotes.length; // Return number of imported notes
      },
      
      exportNotes: () => {
        // Return all notes for export
        return get().notes;
      },
      
      // Reset store (for testing or logout)
      resetStore: () => {
        set({ notes: [], activeNoteId: null });
      }
    }),
    {
      name: 'notes-storage', // Name for localStorage
      partialize: (state) => ({ notes: state.notes }), // Only persist notes array
    }
  )
);

export default useNotesStore;