# 🧠 CARL Memory Retrieval System Documentation

## Overview

CARL's Memory Retrieval System implements human-like memory retrieval processes that replicate the four main types of memory retrieval observed in humans:

1. **Recall** - Retrieving information without external cues (most effortful)
2. **Recognition** - Identifying information when presented with cues (easier than recall)
3. **Recollection** - Reconstructing memories with partial information (piecing together fragments)
4. **Relearning** - Relearning information that was previously known (easiest, indicates some forgetting)

## Key Features

### 🎯 **Personality-Based Retrieval Preferences**
- **INTP**: Deep, systematic recall with high decision thresholds
- **ISFP**: Recognition-based retrieval with moderate search depth
- **INFP**: Recollection-focused with deep search patterns
- **Other Types**: Default to recall with moderate parameters

### 🧠 **Cognitive Load Simulation**
- Tracks retrieval attempts and cognitive fatigue
- Adjusts retrieval probability based on cognitive load
- Simulates realistic human memory limitations

### 📊 **Memory Consolidation Factors**
- **Recency Effect**: More recent memories are easier to retrieve
- **Frequency Effect**: Frequently accessed memories are more accessible
- **Importance Effect**: Important memories have higher retrieval probability
- **Emotional Intensity**: Emotionally significant memories are prioritized

## System Architecture

### Core Components

#### 1. **MemoryRetrievalSystem Class**
```python
class MemoryRetrievalSystem:
    def __init__(self, personality_type: str = "INTP")
    def retrieve_memory(self, query: str, context: Dict, cognitive_ticks: int) -> Dict
    def _determine_retrieval_strategy(self, query: str, context: Dict, cognitive_ticks: int) -> Dict
    def _process_recall(self, query: str, context: Dict, cognitive_ticks: int) -> Dict
    def _process_recognition(self, query: str, context: Dict, cognitive_ticks: int) -> Dict
    def _process_recollection(self, query: str, context: Dict, cognitive_ticks: int) -> Dict
    def _process_relearning(self, query: str, context: Dict, cognitive_ticks: int) -> Dict
```

#### 2. **Integration with CARL's Cognitive Loop**
- **Judgment Phase**: Memory retrieval is triggered during judgment processing
- **Context Building**: Uses current emotional state, location, and recent events
- **Cognitive Ticks**: Determines search depth based on personality and situation
- **Response Integration**: Memory retrieval results are integrated into speech responses

## Memory Retrieval Processes

### 1. **Recall Process**
**Purpose**: Retrieve information without external cues (most effortful)

**Characteristics**:
- Requires deep cognitive effort
- Systematic search through memory stores
- Higher cognitive load penalty
- INTPs excel at this process

**Algorithm**:
```python
def _process_recall(self, query: str, context: Dict, cognitive_ticks: int) -> Dict:
    # Calculate recall probability based on cognitive effort
    recall_probability = min(0.3 + (cognitive_ticks * 0.15), 0.9)
    
    # Apply cognitive load penalty
    recall_probability *= (1.0 - self.cognitive_load * 0.3)
    
    # Determine search scope based on personality
    if self.personality_type == "INTP":
        search_scope = min(len(memories), 50)  # Deep search
        search_pattern = "systematic"
    else:
        search_scope = min(len(memories), 20)  # Standard search
        search_pattern = "selective"
```

### 2. **Recognition Process**
**Purpose**: Identify information when presented with cues

**Characteristics**:
- Easier than recall
- Requires external cues
- Higher confidence levels
- ISFPs prefer this method

**Algorithm**:
```python
def _process_recognition(self, query: str, context: Dict, cognitive_ticks: int) -> Dict:
    # Extract recognition cues from query and context
    recognition_cues = self._extract_recognition_cues(query, context)
    
    # Find memories that match recognition cues
    for memory in memories:
        match_score = self._calculate_recognition_match(memory, recognition_cues)
        if match_score > 0.3:  # Recognition threshold
            matching_memories.append((memory, match_score))
    
    # Recognition is generally more confident than recall
    confidence = min(0.8 + (best_score * 0.2), 0.95)
```

### 3. **Recollection Process**
**Purpose**: Reconstruct memories with partial information

**Characteristics**:
- Involves piecing together fragments
- Moderate confidence levels
- INFPs excel at this process
- Used for complex memory reconstruction

**Algorithm**:
```python
def _process_recollection(self, query: str, context: Dict, cognitive_ticks: int) -> Dict:
    # Extract memory fragments from query and context
    memory_fragments = self._extract_memory_fragments(query, context)
    
    # Find memories that contain these fragments
    for memory in memories:
        fragment_score = self._calculate_fragment_match(memory, memory_fragments)
        if fragment_score > 0.2:  # Fragment matching threshold
            fragment_matches.append((memory, fragment_score))
    
    # Reconstruct memory from best matches
    reconstructed_memory = self._reconstruct_memory(fragment_matches, context)
```

### 4. **Relearning Process**
**Purpose**: Relearn information that was previously known

**Characteristics**:
- Easiest retrieval process
- Indicates some forgetting occurred
- Very high confidence levels
- "Oh yes, I remember now!" experience

**Algorithm**:
```python
def _process_relearning(self, query: str, context: Dict, cognitive_ticks: int) -> Dict:
    # Find memories that might need relearning (older, less accessed)
    for memory in memories:
        relearning_score = self._calculate_relearning_score(memory)
        if relearning_score > 0.4:  # Relearning threshold
            relearning_candidates.append((memory, relearning_score))
    
    # Relearning is very confident
    confidence = min(0.9 + (relearning_score * 0.1), 0.98)
```

## Personality-Based Behavior

### INTP Personality
```python
"INTP": {
    "preferred_method": "recall",           # Internal recall
    "search_depth": "deep",                 # Thorough search
    "decision_threshold": 0.7,              # High threshold for decisions
    "openness_to_alternatives": 0.9,        # Very open to alternatives
    "cognitive_ticks_for_search": 3,        # More ticks for thorough search
    "randomness_factor": 0.3                # Some randomness in search
}
```

**Behavioral Characteristics**:
- Prefers deep, systematic memory search
- High decision thresholds (overthinking)
- Very open to alternative interpretations
- More cognitive ticks for thorough analysis
- Can appear indecisive due to high standards

### ISFP Personality
```python
"ISFP": {
    "preferred_method": "recognition",      # Recognition-based
    "search_depth": "moderate",             # Moderate search
    "decision_threshold": 0.6,              # Moderate threshold
    "openness_to_alternatives": 0.7,        # Some openness
    "cognitive_ticks_for_search": 2,        # Standard ticks
    "randomness_factor": 0.2                # Low randomness
}
```

**Behavioral Characteristics**:
- Prefers recognition over recall
- Moderate search depth
- Balanced decision thresholds
- Practical approach to memory retrieval

### INFP Personality
```python
"INFP": {
    "preferred_method": "recollection",     # Recollection-focused
    "search_depth": "deep",                 # Deep search
    "decision_threshold": 0.6,              # Moderate threshold
    "openness_to_alternatives": 0.8,        # High openness
    "cognitive_ticks_for_search": 3,        # More ticks
    "randomness_factor": 0.4                # Higher randomness
}
```

**Behavioral Characteristics**:
- Prefers recollection and reconstruction
- Deep, introspective search patterns
- High openness to alternatives
- Creative memory reconstruction

## Integration with CARL's Cognitive Systems

### 1. **Judgment Phase Integration**
```python
# In main.py process_input method
if self._is_memory_request(user_input, event_data):
    self.log("\n=== Memory Retrieval Phase ===")
    memory_retrieval_result = self._process_memory_retrieval_request(
        user_input, event_data, judgment_result
    )
```

### 2. **Context Building**
```python
def _build_memory_retrieval_context(self, event_data: Dict, judgment_result: Dict) -> Dict:
    context = {
        "current_emotion": self.neucogar_engine.current_state.primary,
        "current_location": event_data.get('WHERE', ''),
        "recent_events": self.conversation_context[-5:],
        "emotional_state": {
            "primary": self.neucogar_engine.current_state.primary,
            "sub_emotion": self.neucogar_engine.current_state.sub_emotion,
            "intensity": self.neucogar_engine.current_state.intensity
        }
    }
    return context
```

### 3. **Cognitive Ticks Calculation**
```python
def _calculate_cognitive_ticks_for_memory_retrieval(self, judgment_result: Dict) -> int:
    base_ticks = 2
    
    # Add ticks based on personality type
    if personality_type == "INTP":
        base_ticks += 2  # INTPs think more deeply
    elif personality_type == "INFP":
        base_ticks += 1  # INFPs also think deeply
    
    # Add ticks based on judgment complexity
    if judgment_result.get('interaction_priority', 0) > 0.7:
        base_ticks += 1  # High priority interactions get more thinking time
    
    return min(base_ticks, 6)  # Cap at 6 ticks
```

### 4. **Response Integration**
```python
def _extract_speech_text(self, action: str, event_data: Dict) -> str:
    # Check if we have a memory retrieval result to use
    memory_retrieval_result = self.cognitive_state.get("memory_retrieval_result")
    if memory_retrieval_result and memory_retrieval_result.get('success'):
        formatted_memory = memory_retrieval_result.get('formatted_memory')
        if formatted_memory:
            return formatted_memory
```

## Memory Consolidation Factors

### 1. **Recency Effect**
```python
def _calculate_memory_recall_probability(self, memory: Dict, context: Dict) -> float:
    # Recency effect
    if "created" in memory:
        created_time = datetime.fromisoformat(memory["created"])
        age_hours = (datetime.now() - created_time).total_seconds() / 3600
        recency_factor = max(0.1, 1.0 - (age_hours / 168))  # Decay over a week
        probability += recency_factor * self.recency_weight
```

### 2. **Frequency Effect**
```python
# Frequency effect (access count)
if "access_count" in memory:
    frequency_factor = min(1.0, memory["access_count"] / 10.0)
    probability += frequency_factor * self.frequency_weight
```

### 3. **Importance Effect**
```python
# Importance effect
if "importance" in memory:
    importance_factor = memory["importance"] / 10.0
    probability += importance_factor * self.importance_weight
```

### 4. **Emotional Intensity Effect**
```python
# Emotional intensity effect
if "emotions" in memory and memory["emotions"]:
    max_emotion = max(memory["emotions"].values()) if memory["emotions"] else 0
    if max_emotion > self.emotional_intensity_threshold:
        probability += 0.2
```

## Usage Examples

### Example 1: Simple Memory Request
```python
# User: "share a memory"
# System: Uses recall process (INTP preference)
result = memory_retrieval_system.retrieve_memory(
    query="share a memory",
    context={"current_emotion": "joy", "current_location": "condo"},
    cognitive_ticks=3
)
# Response: "I remember: What happened: We danced together. Who was involved: You and me. When: recently. I recalled this through deep thinking."
```

### Example 2: Recognition-Based Request
```python
# User: "do you remember when we danced"
# System: Uses recognition process (cues: "danced")
result = memory_retrieval_system.retrieve_memory(
    query="do you remember when we danced",
    context={"current_emotion": "excitement"},
    cognitive_ticks=2
)
# Response: "I remember: What happened: We danced together. I recognized this when you mentioned it."
```

### Example 3: Deep Thinking Request
```python
# User: "think about your memories"
# System: Uses recollection process (deep thinking)
result = memory_retrieval_system.retrieve_memory(
    query="think about your memories",
    context={"current_emotion": "contemplation"},
    cognitive_ticks=5
)
# Response: "I remember: What happened: We had a conversation. I reconstructed this from memory fragments."
```

## Testing

### Running the Test Suite
```bash
python test_memory_retrieval_system.py
```

### Test Coverage
- ✅ Memory retrieval system functionality
- ✅ Personality-based behavior differences
- ✅ Memory file structure validation
- ✅ Retrieval statistics tracking
- ✅ Integration with CARL's cognitive systems

## Configuration

### Personality Settings
The memory retrieval system automatically configures based on the personality type set in `settings_current.ini`:

```ini
[personality]
type = INTP
```

### Memory Consolidation Weights
```python
self.recency_weight = 0.4      # How much recency affects retrieval
self.frequency_weight = 0.3    # How much frequency affects retrieval
self.importance_weight = 0.3   # How much importance affects retrieval
```

## Performance Considerations

### Memory Loading
- Working memory: Limited to 7 items (Miller's Law)
- Long-term memory: Loaded from JSON files in `memories/` directory
- Search scope: Limited based on personality type (20-50 memories)

### Cognitive Load Management
- Tracks retrieval attempts to prevent cognitive fatigue
- Adjusts retrieval probability based on recent activity
- Simulates realistic human memory limitations

### Response Time
- Memory retrieval adds minimal overhead to cognitive processing
- Results are cached in cognitive state for immediate access
- Integration with existing speech response system

## Future Enhancements

### Planned Features
1. **Memory Association Networks**: Build associative links between related memories
2. **Emotional Memory Filtering**: Filter memories based on emotional state
3. **Temporal Memory Organization**: Organize memories by time periods
4. **Memory Consolidation**: Automatic memory strengthening over time
5. **Forgetting Simulation**: Realistic memory decay and forgetting

### Research Integration
- **Spacing Effect**: Optimize memory retrieval timing
- **Context-Dependent Memory**: Improve retrieval based on environmental context
- **Memory Priming**: Use subtle cues to improve retrieval
- **False Memory Detection**: Identify and handle potentially inaccurate memories

## Conclusion

CARL's Memory Retrieval System provides a sophisticated, human-like approach to memory access that:

1. **Replicates Human Memory Processes**: Implements the four main retrieval types
2. **Adapts to Personality**: Different personalities use different retrieval strategies
3. **Simulates Cognitive Load**: Realistic limitations and fatigue
4. **Integrates Seamlessly**: Works within CARL's existing cognitive architecture
5. **Provides Rich Context**: Uses emotional state, location, and recent events

This system enhances CARL's ability to engage in natural, human-like conversations about past experiences while maintaining the personality-specific characteristics that make each interaction unique and authentic.
