# CARL Memory System Architecture Documentation

## Overview

CARL's memory system is organized into a hierarchical structure with different types of memories stored in specific sub-folders. This document explains the architecture, triggers, and mechanisms that populate these memory sub-folders.

## Memory Directory Structure

```
memories/
├── imagined/           # Imagination-generated episodes
│   ├── images/        # Generated imagination images
│   ├── sessions/      # Imagination session data
│   └── *.json         # Individual imagined episodes
├── episodic/          # Episodic memories (currently empty)
├── semantic/          # Semantic memories (currently empty)
├── procedural/        # Procedural memories (currently empty)
├── working/           # Working memory (currently empty)
└── *_event.json       # Event memories (main memory files)
```

## Memory Types and Population Triggers

### 1. Event Memories (`*_event.json`)

**Location**: `memories/` (root directory)  
**Format**: `YYYYMMDD_HHMMSS_event.json`  
**Trigger**: Every user interaction processed through `process_input()`

#### Population Mechanism:
```python
# In main.py, process_input() method (line ~6076)
event_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_event.json"
event_path = os.path.join(self.memory_dir, event_filename)
with open(event_path, 'w') as f:
    json.dump(event_data, f, indent=4)
```

#### Trigger Events:
- **User Input Processing**: Every time CARL processes user input
- **Speech Acts**: When someone speaks to CARL
- **Actions**: When CARL executes actions
- **Cognitive Processing**: When CARL thinks or makes decisions

#### Content Structure:
```json
{
    "timestamp": "2025-08-20T20:16:10.123456",
    "WHO": "User",
    "WHAT": "User input text",
    "WHERE": "Joe's condo",
    "WHY": "Purpose of interaction",
    "HOW": "Method of interaction",
    "intent": "request|query|command|inform|share",
    "emotions": {"joy": 0.7, "surprise": 0.2, ...},
    "neucogar_emotional_state": {...},
    "carl_thought": {...},
    "nouns": [...],
    "verbs": [...],
    "people": [...],
    "subjects": [...]
}
```

### 2. Imagined Episodes (`memories/imagined/`)

**Location**: `memories/imagined/`  
**Format**: `imagined_YYYYMMDD_HHMMSS_XXXXXX.json`  
**Trigger**: Imagination system generates new episodes

#### Population Mechanism:
```python
# In imagination_system.py, _store_imagined_episode() method (line ~1076)
memory_file = os.path.join(self.imagined_episodes_dir, f"{episode.episode_id}.json")
with open(memory_file, 'w', encoding='utf-8') as f:
    json.dump(memory_data, f, indent=2, ensure_ascii=False)
```

#### Trigger Events:
- **Imagination Generation**: When CARL generates imaginative scenarios
- **Creative Processing**: When CARL creates new ideas or scenarios
- **Episode Creation**: When imagination system produces new episodes

#### Content Structure:
```json
{
    "id": "imagined_20250820_201805_67f8fd",
    "type": "imagined_episode",
    "timestamp": "2025-08-20T20:18:05.123456",
    "WHAT": "Imagined scenario: [scenario description]",
    "WHERE": "imagined_space",
    "WHY": "Purpose: [purpose]",
    "HOW": "Generated through imagination system",
    "WHO": "Carl (self)",
    "emotions": ["joy"],
    "neucogar_emotional_state": {...},
    "scene_graph": {...},
    "render_data": {...},
    "scores": {
        "coherence": 0.8,
        "plausibility": 0.7,
        "novelty": 0.6,
        "utility": 0.5,
        "vividness": 0.9,
        "affect_alignment": 0.7
    },
    "metadata": {...}
}
```

### 3. Short-Term Memory (STM)

**Location**: Stored in memory but displayed in GUI  
**Format**: In-memory list with file references  
**Trigger**: Every event processing

#### Population Mechanism:
```python
# In main.py, _add_event_to_stm() method (line ~13717)
self.memory.append(stm_entry)
if len(self.memory) > 7:
    removed = self.memory.pop(0)  # Remove oldest entry
```

#### Trigger Events:
- **Event Processing**: Every time an event is processed
- **Memory Addition**: When new events are added to STM
- **Memory Cleanup**: When STM exceeds 7 entries

## Memory Population Triggers in Code

### Primary Triggers:

1. **User Input Processing** (`process_input()` method):
   - Creates event files in `memories/`
   - Adds entries to Short-Term Memory
   - Triggers cognitive processing

2. **Imagination System** (`imagination_system.py`):
   - Creates imagined episodes in `memories/imagined/`
   - Generates images in `memories/imagined/images/`
   - Stores session data in `memories/imagined/sessions/`

3. **Action Execution** (various action methods):
   - Records action results in event files
   - Updates emotional states
   - Stores procedural learning

### Secondary Triggers:

4. **Cognitive Processing** (`_process_cognitive()` method):
   - Updates emotional states
   - Records thought processes
   - Stores decision-making data

5. **Memory Management** (`_save_short_term_memory()` method):
   - Persists STM to disk
   - Manages memory cleanup
   - Updates memory displays

## Memory File Naming Conventions

### Event Files:
- **Format**: `YYYYMMDD_HHMMSS_event.json`
- **Example**: `20250820_201610_event.json`
- **Generated**: Every user interaction

### Imagined Episodes:
- **Format**: `imagined_YYYYMMDD_HHMMSS_XXXXXX.json`
- **Example**: `imagined_20250820_201805_67f8fd.json`
- **Generated**: When imagination creates new episodes

### Images:
- **Format**: Generated by imagination system
- **Location**: `memories/imagined/images/`
- **Generated**: When imagination produces visual content

## Memory System Integration

### Cross-References:
- **Event Files** → **STM** → **GUI Display**
- **Imagined Episodes** → **Imagination GUI** → **Image Display**
- **All Memories** → **Concept System** → **Goal System**

### Data Flow:
1. **Input** → **Event Creation** → **STM Addition** → **Cognitive Processing**
2. **Imagination** → **Episode Creation** → **Image Generation** → **Memory Storage**
3. **Memory Retrieval** → **Concept Association** → **Decision Making**

## Current Status

### Populated Directories:
- ✅ `memories/` (root) - Contains event files
- ✅ `memories/imagined/` - Contains imagined episodes and images

### Empty Directories (Future Implementation):
- ⏳ `memories/episodic/` - For episodic memory consolidation
- ⏳ `memories/semantic/` - For semantic knowledge storage
- ⏳ `memories/procedural/` - For skill and procedure storage
- ⏳ `memories/working/` - For working memory operations

## Memory System Statistics

### Current Memory Count:
- **Total Event Files**: 12 (as of test results)
- **Total Imagined Episodes**: 6 (visible in imagined directory)
- **STM Capacity**: 7 entries (rolling window)

### Memory Types Distribution:
- **Request**: 4 (33.3%)
- **Share**: 3 (25.0%)
- **Query**: 2 (16.7%)
- **Command**: 2 (16.7%)
- **Inform**: 1 (8.3%)

## Future Enhancements

### Planned Memory Types:
1. **Episodic Memory**: Long-term storage of personal experiences
2. **Semantic Memory**: Factual knowledge and concepts
3. **Procedural Memory**: Skills and procedures
4. **Working Memory**: Active cognitive processing

### Integration Points:
- **Memory Consolidation**: Transfer from STM to long-term memory
- **Memory Retrieval**: Context-aware memory access
- **Memory Association**: Linking related memories
- **Memory Forgetting**: Selective memory cleanup

## Technical Implementation Notes

### File Operations:
- **Event Files**: Created synchronously during processing
- **Imagined Episodes**: Created asynchronously by imagination system
- **STM**: Maintained in memory with periodic persistence

### Error Handling:
- **File Creation**: Graceful handling of write failures
- **Memory Cleanup**: Automatic removal of missing files
- **Data Validation**: JSON structure validation

### Performance Considerations:
- **Memory Limits**: STM limited to 7 entries
- **File Size**: Average event file ~2.7KB
- **Processing Time**: Average execution ~0.145 seconds

This documentation provides a comprehensive overview of how CARL's memory system works and how the various sub-folders get populated through different triggers in the codebase.
