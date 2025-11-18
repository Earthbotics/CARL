# CARL Memory Explorer

## Overview

The Memory Explorer is a comprehensive GUI tool that allows users to browse, search, and analyze CARL's memories stored in the `memories` folder. It provides an intuitive interface for exploring the cognitive agent's past experiences and emotional responses.

## Features

### 1. Memory List View
- **Chronological Display**: Memories are displayed in chronological order by default
- **Quick Summary**: Each memory shows timestamp, dominant emotion, and a brief summary
- **Sorting Options**: 
  - Chronological (oldest first)
  - Reverse chronological (newest first)
  - Emotional intensity (highest first)
  - Alphabetical (by summary)

### 2. Filtering and Search
- **Emotion Filter**: Filter memories by dominant emotion (joy, surprise, sadness, fear, anger, disgust)
- **Text Search**: Search through memory content, WHAT field, and WHO field
- **Real-time Updates**: Results update as you type or change filters

### 3. Detailed Memory View
When you select a memory from the list, the right panel shows comprehensive details:

#### Context Information
- **5W+H Analysis**: Who, What, When, Where, Why, How
- **Intent**: The detected intent of the interaction (query, inform, command, etc.)
- **Expected Response**: What response was expected

#### Emotional State
- **Emotion Intensities**: Detailed breakdown of all emotions and their intensities
- **Dominant Emotion**: The most prominent emotion during the interaction

#### Carl's Thoughts
- **Automatic Thoughts**: Carl's internal thought process
- **Proposed Actions**: What actions Carl considered taking
- **Emotional Context**: How emotions influenced the response
- **MBTI Function Phases**: How Carl's personality functions processed the information

#### Associated Concepts
- **Nouns, Verbs, People, Subjects**: All concepts mentioned or related to the memory
- **Needs and Goals**: How the interaction affected Carl's needs and goals

### 4. Export Functionality
- **Export Selected Memory**: Save any selected memory as a text file
- **Formatted Output**: Exported files include all memory details in a readable format
- **Timestamp Naming**: Files are named with the memory timestamp for easy identification

### 5. Memory Statistics
The Memory Statistics feature provides comprehensive analytics:

#### Basic Statistics
- **Total Memories**: Count of all stored memories
- **Date Range**: Earliest and latest memory timestamps
- **File Sizes**: Min, max, and average file sizes

#### Emotional Analysis
- **Emotion Frequency**: How often each emotion appears
- **Emotional Intensity**: Min, max, and average emotional intensity across all memories
- **Average Intensity per Emotion**: Statistical breakdown by emotion type

#### Content Analysis
- **Intent Distribution**: Percentage breakdown of different interaction intents
- **Top Concepts**: Most frequently mentioned concepts (nouns)
- **Top Verbs**: Most frequently used action words
- **People Mentioned**: List of people referenced in memories

## How to Use

### Opening the Memory Explorer
1. Start the CARL application (`python main.py`)
2. Click the "Explore Memories" button in the control panel
3. A new window will open with the Memory Explorer interface

### Browsing Memories
1. **View List**: The left panel shows all memories in chronological order
2. **Select Memory**: Click on any memory to view its details in the right panel
3. **Sort Memories**: Use the "Sort by" dropdown to change the order
4. **Filter Memories**: Use the "Filter by emotion" dropdown to show only specific emotions
5. **Search Memories**: Type in the search box to find specific content

### Using Advanced Features
1. **Refresh**: Click "Refresh Memories" to reload the memory list
2. **Export**: Select a memory and click "Export Selected" to save it as a text file
3. **Statistics**: Click "Memory Stats" to view comprehensive memory analytics

### Understanding Memory Data
Each memory contains rich information about:
- **Perception**: What CARL perceived from the interaction
- **Analysis**: How CARL interpreted the meaning
- **Emotional Response**: How CARL felt about the interaction
- **Cognitive Processing**: How CARL's personality functions processed the information
- **Proposed Actions**: What CARL considered doing in response

## File Format

Memories are stored as JSON files in the `memories` folder with the naming convention:
```
YYYYMMDD_HHMMSS_event.json
```

Example: `20250624_135043_event.json`

## Technical Details

### Memory Structure
Each memory file contains:
```json
{
  "WHAT": "Description of what happened",
  "WHEN": "When it occurred",
  "WHERE": "Where it occurred",
  "WHY": "Why it happened",
  "HOW": "How it happened",
  "intent": "Detected intent",
  "emotions": {
    "joy": 0.0,
    "surprise": 0.0,
    "sadness": 0.0,
    "fear": 0.0,
    "anger": 0.0,
    "disgust": 0.0
  },
  "carl_thought": {
    "automatic_thought": "Carl's internal thoughts",
    "proposed_action": {
      "type": "action_type",
      "content": "action_description"
    },
    "emotional_context": {
      "emotion": "dominant_emotion",
      "memory_reference": "related_memory"
    }
  }
}
```

### Performance Considerations
- The Memory Explorer loads all memory files into memory for fast searching and sorting
- Large numbers of memories may slow down the interface
- Consider archiving old memories if performance becomes an issue

## Troubleshooting

### Common Issues
1. **No memories found**: Ensure the `memories` folder exists and contains `*_event.json` files
2. **Memory not loading**: Check that memory files are valid JSON format
3. **Export fails**: Ensure you have write permissions in the current directory

### Error Messages
- "No memories directory found": The `memories` folder doesn't exist
- "No memory files found": No `*_event.json` files in the memories folder
- "Error loading memory details": Memory file is corrupted or invalid JSON

## Future Enhancements

Potential improvements for future versions:
- **Memory Visualization**: Charts and graphs for emotional trends
- **Memory Clustering**: Group similar memories together
- **Advanced Search**: Search by date range, emotion intensity, etc.
- **Memory Editing**: Ability to modify or annotate memories
- **Memory Backup**: Export all memories as a single archive
- **Memory Import**: Import memories from other sources 