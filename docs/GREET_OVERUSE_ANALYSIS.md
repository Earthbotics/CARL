# Greet Skill Overuse Analysis

## Problem Identified
CARL is overusing the greet skill/concept during cognitive processing, which can lead to repetitive and inappropriate greeting behaviors.

## Root Causes

### 1. **Overly Broad Greeting Detection**
**Location**: `main.py` lines 2578-2581
```python
is_greeting_or_acknowledgment = (
    intent in ['acknowledge', 'greet', 'greeting'] or
    any(greeting_word in what for greeting_word in ['greeting', 'greet', 'hello', 'hi', 'hey'])
)
```
**Issue**: This detection is too broad and triggers on any mention of greeting-related words, even in contexts where greeting is not appropriate.

### 2. **Automatic Speech Act Classification**
**Location**: `main.py` lines 2592-2593
```python
# Additional override: if this is clearly a question or greeting, always treat as speech act
if intent == 'query' or is_greeting_or_acknowledgment:
    is_speech_act = True
```
**Issue**: Any content containing greeting words automatically becomes a speech act, forcing CARL to respond.

### 3. **Broad Skill Activation in Action System**
**Location**: `action_system.py` lines 505-506
```python
if 'greet' in action_lower or 'hello' in action_lower or 'hi' in action_lower:
    required_skills.append('greet')
```
**Issue**: Any action containing greeting words triggers the greet skill, regardless of context.

### 4. **Persistent Concept Creation**
**Location**: Test results show repeated creation of "greeting and inquiring about my well-being" concept
**Issue**: CARL keeps creating and referencing the same greeting concept, leading to repetitive behavior.

### 5. **Startup Greeting Loop**
**Location**: `main.py` lines 5774-5804
**Issue**: CARL has a startup greeting that may be triggering repeatedly during cognitive processing.

## Evidence from Test Results

1. **Repeated Concept Creation**: Multiple instances of "greeting and inquiring about my well-being"
2. **Persistent Skill Activation**: "skill:greet" appears multiple times
3. **Startup Greeting Triggers**: "🎭 CARL startup greeting" appears repeatedly
4. **Low Priority Skills**: "greet.json (Priority: 0.00)" - indicating the system recognizes it's not high priority but still activates it

## Proposed Fixes

### 1. **Context-Aware Greeting Detection**
- Add context checking before triggering greeting responses
- Implement cooldown periods for greeting behaviors
- Check if a greeting has already been exchanged recently

### 2. **Refined Speech Act Classification**
- Require stronger evidence before classifying as greeting speech act
- Add conversation state tracking to avoid repeated greetings
- Implement greeting fatigue detection

### 3. **Smart Skill Filtering**
- Add context validation before activating greet skill
- Implement skill usage tracking and limits
- Add conversation flow awareness

### 4. **Concept Usage Optimization**
- Prevent duplicate concept creation
- Implement concept usage limits
- Add concept relevance scoring

### 5. **Startup Greeting Control**
- Limit startup greeting frequency
- Add conversation state awareness
- Implement greeting appropriateness checks

## Implementation Priority

1. **High Priority**: Fix context-aware greeting detection
2. **High Priority**: Implement greeting cooldown system
3. **Medium Priority**: Add conversation state tracking
4. **Medium Priority**: Optimize concept creation
5. **Low Priority**: Refine startup greeting logic 