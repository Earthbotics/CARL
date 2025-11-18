# Eye Expression and Head Movement System

## Overview

CARL now has an enhanced eye expression and head movement system that coordinates RGB eye animations with body movements to create more human-like behavior. This system includes:

1. **Eye RGB Expressions**: 12 different eye states for emotional and directional expressions
2. **Head Movement Skills**: New `head_no` and `head_yes` skills for non-verbal communication
3. **Coordinated Behavior**: Automatic coordination between eye expressions and body movements
4. **Emotional Integration**: Eye expressions that reflect CARL's current emotional state

## Eye RGB Expressions

### Available Eye States

CARL's eyes can display the following RGB expressions:

| Expression | Description | Use Case |
|------------|-------------|----------|
| `eyes_closed` | Eyes closed | Sleep, head shake (no), thinking |
| `eyes_down` | Looking down | Looking at objects, shame, submission |
| `eyes_left` | Looking left | Following movement, curiosity |
| `eyes_open` | Default open state | Normal interaction, head nod (yes) |
| `eyes_right` | Looking right | Following movement, curiosity |
| `eyes_up` | Looking up | Looking at sky, thinking, wonder |
| `eyes_anger` | Angry expression | Anger, frustration, aggression |
| `eyes_surprise` | Surprised expression | Surprise, shock, amazement |
| `eyes_fear` | Fearful expression | Fear, anxiety, worry |
| `eyes_disgust` | Disgusted expression | Disgust, aversion, dislike |
| `eyes_sad` | Sad expression | Sadness, grief, disappointment |
| `eyes_joy` | Happy expression | Joy, happiness, contentment |

### Emotional Mapping

The system automatically maps emotional states to appropriate eye expressions:

```python
emotion_to_eye = {
    'joy': 'eyes_joy',
    'happiness': 'eyes_joy', 
    'happy': 'eyes_joy',
    'anger': 'eyes_anger',
    'angry': 'eyes_anger',
    'fear': 'eyes_fear',
    'afraid': 'eyes_fear',
    'surprise': 'eyes_surprise',
    'surprised': 'eyes_surprise',
    'disgust': 'eyes_disgust',
    'disgusted': 'eyes_disgust',
    'sadness': 'eyes_sad',
    'sad': 'eyes_sad',
    'default': 'eyes_open',
    'neutral': 'eyes_open'
}
```

## Head Movement Skills

### New Skills Added

Two new head movement skills have been implemented:

#### `head_no` Skill
- **Purpose**: Non-verbal expression of disagreement, refusal, or negative response
- **Eye Coordination**: Automatically closes eyes during head shake
- **Execution**: `ControlCommand("Script Collection", "ScriptStartWait", "head_no")`
- **Completion Time**: 2.0 seconds

#### `head_yes` Skill  
- **Purpose**: Non-verbal expression of agreement, acceptance, or positive response
- **Eye Coordination**: Keeps eyes open during head nod
- **Execution**: `ControlCommand("Script Collection", "ScriptStartWait", "head_yes")`
- **Completion Time**: 2.0 seconds

### Skill Files

Both skills have been created with appropriate concepts and motivators:

**`skills/head_no.json`**:
```json
{
    "Name": "head_no",
    "Concepts": ["disagreement", "refusal", "negative", "head", "movement"],
    "Motivators": ["disagree", "refuse", "deny", "express_negative"],
    "Techniques": ["EZRobot-cmd-head_no"],
    "IsUsedInNeeds": false,
    "AssociatedGoals": [],
    "AssociatedNeeds": []
}
```

**`skills/head_yes.json`**:
```json
{
    "Name": "head_yes", 
    "Concepts": ["agreement", "acceptance", "positive", "head", "movement"],
    "Motivators": ["agree", "accept", "confirm", "express_positive"],
    "Techniques": ["EZRobot-cmd-head_yes"],
    "IsUsedInNeeds": false,
    "AssociatedGoals": [],
    "AssociatedNeeds": []
}
```

## Movement-Eye Coordination

### Automatic Coordination

The system automatically coordinates eye expressions with body movements:

| Movement | Eye Expression | Rationale |
|----------|----------------|-----------|
| `look_down` | `eyes_down` | Natural eye direction for looking down |
| `look_up` | `eyes_up` | Natural eye direction for looking up |
| `look_left` | `eyes_left` | Natural eye direction for looking left |
| `look_right` | `eyes_right` | Natural eye direction for looking right |
| `head_no` | `eyes_closed` | Close eyes during head shake (natural behavior) |
| `head_yes` | `eyes_open` | Keep eyes open during head nod (natural behavior) |

### Implementation

The coordination is handled in the `coordinate_eye_with_movement()` method in `action_system.py`:

```python
def coordinate_eye_with_movement(self, movement: str, emotion: str = None):
    """Coordinate eye expressions with body movements for human-like behavior."""
    movement_to_eye = {
        "look_down": "eyes_down",
        "look_up": "eyes_up", 
        "look_left": "eyes_left",
        "look_right": "eyes_right",
        "head_no": "eyes_closed",  # Close eyes during head shake
        "head_yes": "eyes_open"    # Keep eyes open during head nod
    }
    
    # Determine eye expression
    if emotion:
        eye_expression = emotion  # Use emotional expression if provided
    elif movement in movement_to_eye:
        eye_expression = movement_to_eye[movement]  # Use movement-specific expression
    else:
        eye_expression = "eyes_open"  # Default to open eyes
    
    return self.set_eye_expression(eye_expression)
```

## Integration with Main Application

### Emotional State Updates

Eye expressions are automatically updated when CARL's emotional state changes:

```python
def _update_emotion_display(self, emotional_state):
    # ... existing emotion processing ...
    
    # Update emotion face display
    self.update_emotion_face(dominant_emotion)
    
    # Update eye expression based on emotional state
    self._update_eye_expression(dominant_emotion)
```

### Action Execution

When EZ-Robot commands are executed, eye coordination happens automatically:

```python
def _execute_ezrobot_command(self, command: str, skill_name: str) -> bool:
    # ... existing command mapping ...
    
    # Coordinate eye expression with movement
    self.coordinate_eye_with_movement(command)
    
    # Handle special cases for head movements
    if command == "head_no":
        result = self.ez_robot.send_head_no()
    elif command == "head_yes":
        result = self.ez_robot.send_head_yes()
    else:
        result = self.ez_robot.send_auto_position(skill_enum)
```

## EZ-Robot Implementation

### New Methods Added

**`ezrobot.py`** has been enhanced with new methods:

```python
def send_script_wait(self, command):
    """Send a script command with ScriptStartWait parameter."""
    
def send_eye_expression(self, eye_expression: EZRobotEyeExpressions):
    """Send an eye RGB expression command."""
    
def send_head_no(self):
    """Send head_no script command."""
    
def send_head_yes(self):
    """Send head_yes script command."""
    
def set_eye_expression(self, emotion: str):
    """Set eye expression based on emotional state."""
```

### New Enums

```python
class EZRobotEyeExpressions(Enum):
    """Eye RGB expressions for human-like behavior."""
    EYES_CLOSED = "eyes_closed"
    EYES_DOWN = "eyes_down"
    EYES_LEFT = "eyes_left"
    EYES_OPEN = "eyes_open"
    EYES_RIGHT = "eyes_right"
    EYES_UP = "eyes_up"
    EYES_ANGER = "eyes_anger"
    EYES_SURPRISE = "eyes_surprise"
    EYES_FEAR = "eyes_fear"
    EYES_DISGUST = "eyes_disgust"
    EYES_SAD = "eyes_sad"
    EYES_JOY = "eyes_joy"

class EZRobotSkills(Enum):
    # ... existing skills ...
    Head_No = "head_no"
    Head_Yes = "head_yes"
```

## Usage Examples

### Emotional Eye Expressions

When CARL experiences emotions, his eyes automatically reflect his state:

```python
# CARL feels happy
bot._update_eye_expression('joy')  # Sets eyes_joy

# CARL feels angry  
bot._update_eye_expression('anger')  # Sets eyes_anger

# CARL feels sad
bot._update_eye_expression('sadness')  # Sets eyes_sad
```

### Coordinated Movements

When CARL performs movements, his eyes coordinate naturally:

```python
# CARL looks down at something
action_system.coordinate_eye_with_movement('look_down')  # Sets eyes_down

# CARL shakes his head no
action_system.coordinate_eye_with_movement('head_no')  # Sets eyes_closed

# CARL nods his head yes
action_system.coordinate_eye_with_movement('head_yes')  # Sets eyes_open
```

### Combined Emotional and Movement Coordination

```python
# CARL is happy and looks up
action_system.coordinate_eye_with_movement('look_up', 'joy')  # Uses joy expression

# CARL is sad and shakes his head
action_system.coordinate_eye_with_movement('head_no', 'sadness')  # Uses sadness expression
```

## Benefits

1. **Enhanced Human-Like Behavior**: CARL's eye expressions and movements now coordinate naturally
2. **Emotional Expressiveness**: Eye expressions reflect CARL's emotional state in real-time
3. **Non-Verbal Communication**: Head movements provide clear yes/no responses
4. **Automatic Coordination**: No manual intervention required - system works automatically
5. **Consistent Behavior**: Eye expressions are consistent with movement types and emotions
6. **Improved User Experience**: More natural and engaging interaction with CARL

## Technical Details

### Default Eye State
- **Default**: `eyes_open` (single blue dot in center of each 3x3 LED display)
- **Fallback**: Used when no specific emotion or movement is detected

### RGB LED Display
- **Format**: 3x3 LED grid per eye
- **Colors**: RGB support for various expressions
- **Default Color**: Blue for `eyes_open` state

### Action Completion Tracking
- **head_no**: 2.0 seconds completion time
- **head_yes**: 2.0 seconds completion time
- **Eye expressions**: Immediate (no completion tracking needed)

### Error Handling
- Graceful fallback to `eyes_open` if expression fails
- Logging of all eye expression attempts
- Connection status checking before sending commands

## Future Enhancements

1. **Dynamic Eye Movement**: Random eye movements during idle states
2. **Blinking**: Periodic blinking for more natural behavior
3. **Eye Tracking**: Follow moving objects with eye movements
4. **Emotional Blending**: Smooth transitions between emotional expressions
5. **Context-Aware Expressions**: Eye expressions based on conversation context
6. **Learning Eye Patterns**: CARL learns preferred eye expressions for different situations

## Testing

The system has been tested with `test_eye_expression_system.py` which verifies:

- ✅ Emotional eye expression mapping
- ✅ Head movement coordination
- ✅ Movement-specific eye expressions
- ✅ Error handling and fallbacks
- ✅ Integration with action system

All tests pass successfully, confirming the system works as designed. 