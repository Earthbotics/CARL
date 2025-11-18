# NEUCOGAR Emotional Engine Implementation

## Overview

The NEUCOGAR (Neurotransmitter-based Emotional Cognitive Architecture) emotional engine has been successfully implemented inside CARL based on the Lövheim Cube of Emotion (Lövheim, 2012). This system maps emotional states using three key neurotransmitters:

- **Dopamine (DA)** — reward/motivation
- **Serotonin (5-HT)** — mood/stability/confidence  
- **Noradrenaline (NE)** — arousal/alertness

## Implementation Details

### Core Components

#### 1. NeuroCoordinates Class
```python
@dataclass
class NeuroCoordinates:
    dopamine: float      # DA: reward/motivation (-1.0 to +1.0)
    serotonin: float     # 5-HT: mood/stability/confidence (-1.0 to +1.0)
    noradrenaline: float # NE: arousal/alertness (-1.0 to +1.0)
```

**Features:**
- Automatic value clamping to valid range (-1.0 to +1.0)
- Euclidean distance calculation between coordinates
- Dictionary conversion for JSON serialization

#### 2. EmotionalState Class
```python
@dataclass
class EmotionalState:
    primary: str
    sub_emotion: str
    detail: str
    neuro_coordinates: NeuroCoordinates
    intensity: float
    timestamp: datetime
```

**Features:**
- Complete emotional state representation
- JSON serialization support
- Timestamp tracking for session logging

#### 3. NEUCOGAREmotionalEngine Class

The main engine class that implements the Lövheim Cube of Emotion.

### Lövheim Cube Mapping

The system represents a 3D cube space with each axis ranging from -1.0 to +1.0, mapping core emotions to specific coordinates:

| Emotion | Dopamine (DA) | Serotonin (5-HT) | Noradrenaline (NE) | Description |
|---------|---------------|------------------|-------------------|-------------|
| **Anger** | 0.8 (High) | -0.6 (Low) | 0.9 (High) | High motivation, low confidence, high alertness |
| **Sadness** | -0.7 (Low) | 0.8 (High) | -0.5 (Low) | Low motivation, high confidence, low alertness |
| **Fear** | -0.6 (Low) | -0.7 (Low) | 0.8 (High) | Low motivation, low confidence, high alertness |
| **Joy** | 0.9 (High) | 0.8 (High) | 0.3 (Moderate) | High motivation, high confidence, moderate alertness |
| **Surprise** | 0.4 (Moderate) | 0.3 (Moderate) | 0.9 (High) | Moderate motivation, moderate confidence, high alertness |
| **Disgust** | -0.5 (Low) | 0.7 (High) | 0.6 (High) | Low motivation, high confidence, high alertness |

### Sub-Emotions with Depth Mapping

Each sub-emotion maps to a parent emotion with a depth factor (0.0 = surface level, 1.0 = deep/internal):

**Surface Level (0.0-0.4):**
- annoyed, irritated, pleased, startled, worried, nervous

**Moderate Depth (0.4-0.7):**
- frustrated, anxious, delighted, amazed, scared, disturbed

**Deep/Internal (0.7-1.0):**
- enraged, terrified, elated, shocked, heartbroken, revolted

### Emotional Triggers

The system includes comprehensive trigger mappings:

**Positive Triggers:**
- praise, success, laughter, music, dance, exercise, learning, creativity, connection, achievement

**Negative Triggers:**
- criticism, failure, rejection, conflict, stress, loneliness, boredom, uncertainty, overwhelm, disappointment

**Neutral/Contextual Triggers:**
- surprise, change, challenge, discovery, reflection, rest

## Integration with CARL

### 1. Main Application Integration

The NEUCOGAR engine is integrated into `main.py`:

```python
# Import the engine
from neucogar_emotional_engine import NEUCOGAREmotionalEngine

# Initialize in PersonalityBotApp
self.neucogar_engine = NEUCOGAREmotionalEngine()
```

### 2. Emotional Processing Integration

The engine is integrated into the existing emotional processing pipeline:

```python
def _process_emotional_response(self, event):
    # Determine trigger input for NEUCOGAR engine
    trigger_input = self._determine_emotional_trigger(event, context)
    
    # Update NEUCOGAR emotional state
    neucogar_state = self.neucogar_engine.update_emotion_state(trigger_input)
    
    # Log the NEUCOGAR emotional state
    self.log("\n🧠 NEUCOGAR Emotional State:")
    self.log(f"Primary: {neucogar_state['primary']}")
    self.log(f"Sub-emotion: {neucogar_state['sub_emotion']}")
    self.log(f"Detail: {neucogar_state['detail']}")
    self.log(f"Intensity: {neucogar_state['intensity']:.3f}")
```

### 3. API Functions

#### get_current_emotion()
Returns the current emotional state:
```python
{
    "primary": "joy",
    "sub_emotion": "elated", 
    "detail": "deeply elated and motivated, confident",
    "neuro_coordinates": {
        "dopamine": 0.9,
        "serotonin": 0.8,
        "noradrenaline": 0.3
    },
    "intensity": 0.75,
    "timestamp": "2024-01-15T10:30:00"
}
```

#### update_emotion_state(trigger_input)
Updates emotional state based on external input:
```python
# Example usage
state = engine.update_emotion_state("praise")
state = engine.update_emotion_state("You did a great job!")
```

### 4. Session Logging and Reporting

The system automatically logs all emotional transitions and generates comprehensive reports when the bot is stopped.

#### Session Log Features:
- Automatic logging of all emotional state transitions
- Timestamp tracking for each transition
- Neurotransmitter value recording
- Session duration and statistics

#### Report Generation:
When the "stop bot" button is pressed, the system generates a comprehensive report including:

- **Session Information**: Duration, total transitions, transitions per minute
- **Emotion Frequency Histogram**: Count and percentage of each emotion
- **Sub-Emotion Frequency Histogram**: Count and percentage of each sub-emotion
- **Neurotransmitter Averages**: Average DA, 5-HT, and NE levels
- **Peak Emotional States**: Most intense DA, 5-HT, and NE moments
- **Most Common Emotion Pair**: Primary/sub-emotion combination
- **Emotional Trajectory Summary**: Narrative description of emotional flow

#### Export Functionality:
```python
# Export session data to JSON file
export_path = engine.export_session_data("session_report.json")
```

## Testing and Validation

### Test Suite

A comprehensive test suite (`test_neucogar_emotional_engine.py`) validates:

1. **NeuroCoordinates Class**: Value clamping, distance calculation, serialization
2. **EmotionalState Class**: State creation, serialization
3. **Lövheim Cube Mapping**: Verification of emotion-to-neurotransmitter mappings
4. **Engine Functionality**: Trigger processing, state transitions, session logging
5. **Report Generation**: Session statistics, export functionality
6. **Reset Functionality**: Session reset and state restoration

### Test Results

All tests pass successfully, confirming:
- ✅ Proper neurotransmitter coordinate mapping
- ✅ Accurate emotional state transitions
- ✅ Correct session logging and reporting
- ✅ Valid JSON export functionality
- ✅ Proper integration with CARL's emotional processing

## Usage Examples

### Basic Usage

```python
# Initialize the engine
engine = NEUCOGAREmotionalEngine()

# Get current emotion
current = engine.get_current_emotion()
print(f"Current emotion: {current['primary']}/{current['sub_emotion']}")

# Update emotion with trigger
state = engine.update_emotion_state("praise")
print(f"New emotion: {state['primary']} - {state['detail']}")

# Generate session report
report = engine.generate_emotion_report()
print(f"Session had {report['session_info']['total_transitions']} transitions")
```

### Integration with CARL

```python
# In CARL's emotional processing
def process_user_input(self, user_input):
    # Determine emotional trigger from user input
    trigger = self._analyze_input_for_emotional_trigger(user_input)
    
    # Update NEUCOGAR emotional state
    emotional_state = self.neucogar_engine.update_emotion_state(trigger)
    
    # Use emotional state for decision making
    if emotional_state['primary'] == 'joy' and emotional_state['intensity'] > 0.7:
        # High joy intensity - respond with enthusiasm
        return self._generate_enthusiastic_response()
    elif emotional_state['primary'] == 'fear' and emotional_state['intensity'] > 0.6:
        # High fear intensity - respond with reassurance
        return self._generate_reassuring_response()
```

## Scientific Basis

### Lövheim Cube of Emotion (2012)

The implementation is based on the research by Lövheim (2012) which proposes that emotional states can be mapped to three-dimensional space defined by the relative levels of three key neurotransmitters:

1. **Dopamine (DA)**: Associated with reward, motivation, and approach behavior
2. **Serotonin (5-HT)**: Associated with mood regulation, confidence, and social behavior
3. **Noradrenaline (NE)**: Associated with arousal, alertness, and stress response

### Neurotransmitter Dynamics

The system implements realistic neurotransmitter dynamics:

- **Natural Decay**: Neurotransmitter levels naturally decay over time
- **Differential Decay Rates**: Different neurotransmitters decay at different rates
- **Trigger Effects**: External stimuli cause immediate changes in neurotransmitter levels
- **State Resolution**: Current emotional state is determined by proximity to core emotion coordinates

## Future Enhancements

### Potential Improvements

1. **Learning Mechanisms**: Adaptive trigger sensitivity based on experience
2. **Personality Integration**: Individual differences in neurotransmitter baseline levels
3. **Temporal Dynamics**: More sophisticated decay and recovery patterns
4. **Context Awareness**: Environmental and situational factors affecting emotional responses
5. **Cross-Modal Integration**: Integration with visual, auditory, and other sensory inputs

### Research Applications

The NEUCOGAR engine provides a foundation for:
- Computational modeling of emotional processes
- Human-robot interaction research
- Affective computing applications
- Psychological research on emotional dynamics

## Conclusion

The NEUCOGAR emotional engine successfully implements the Lövheim Cube of Emotion within CARL, providing a scientifically-grounded, computationally-tractable model of emotional states. The system offers:

- **Scientific Accuracy**: Based on established neurobiological research
- **Computational Efficiency**: Real-time emotional state processing
- **Comprehensive Logging**: Detailed session tracking and reporting
- **Seamless Integration**: Works alongside CARL's existing emotional systems
- **Extensibility**: Framework for future emotional intelligence enhancements

This implementation represents a significant advancement in CARL's emotional intelligence capabilities, providing a more nuanced and scientifically-based approach to emotional state modeling and management. 