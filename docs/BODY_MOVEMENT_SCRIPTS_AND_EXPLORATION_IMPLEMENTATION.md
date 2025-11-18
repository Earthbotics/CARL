# Body Movement Scripts and Exploration Implementation

## Overview

This document describes the implementation of automatic body movement scripts based on NUECOGAR emotional levels and the integration of exploration movement commands with CARL's knowledge base.

## 1. Body Movement Scripts Implementation

### 1.1 New Script Collection Scripts

Five new body movement scripts have been added to the Script Collection in ARC:

#### Eye Expressions (RGB Animator Commands)
- **`eyes_joy`** - Executes with `reaction_amused`
- **`eyes_surprise`** - Executes with `reaction_amazed`, `reaction_ecstatic`
- **`eyes_sad`** - Executes with `reaction_terrified`, `reaction_irritated`

#### Body Movement Reactions
- **`reaction_amazed`** - Body reaction for surprise and wonder
- **`reaction_terrified`** - Body reaction for fear and anxiety
- **`reaction_ecstatic`** - Body reaction for extreme joy
- **`reaction_amused`** - Body reaction for light joy and amusement
- **`reaction_irritated`** - Body reaction for anger and frustration

### 1.2 NEUCOGAR Emotional Engine Integration

The body movement scripts are automatically executed based on CARL's NUECOGAR emotional state:

```python
def _initialize_body_movement_scripts(self) -> Dict[str, Dict[str, Any]]:
    """Initialize body movement scripts that automatically execute based on NUECOGAR levels."""
    return {
        "eyes_joy": {
            "type": "eye_expression",
            "command": "eyes_joy",
            "triggers": ["reaction_amused"],
            "emotions": ["joy", "happiness", "elated", "ecstatic", "pleased", "thrilled", "delighted"],
            "intensity_threshold": 0.4,
            "description": "Joyful eye expression for positive emotions"
        },
        # ... additional scripts
    }
```

### 1.3 Automatic Execution System

The system automatically executes body movements when:
1. **Emotion matches** - Current emotion is in the script's emotion list
2. **Intensity threshold met** - Emotional intensity exceeds the threshold
3. **Cooldown period passed** - Minimum 5 seconds between executions
4. **Coordination enabled** - Eye and body movements execute simultaneously

### 1.4 Coordinated Movement Execution

Eye expressions and body movements are coordinated to simulate realistic human behavior:

```python
async def execute_coordinated_movements(self, movements: List[Dict[str, Any]]) -> bool:
    """Execute coordinated eye and body movements simultaneously."""
    # Group movements by timing (simultaneous vs sequential)
    # Execute eye expressions and body movements together
    # Handle timing and synchronization
```

## 2. Exploration Movement Commands

### 2.1 HTTP Movement Commands

The following HTTP commands are available for exploration movements:

```
http://192.168.56.1/movement?direction=forward
http://192.168.56.1/movement?direction=reverse
http://192.168.56.1/movement?direction=left
http://192.168.56.1/movement?direction=right
http://192.168.56.1/movement?direction=stop
```

### 2.2 Knowledge Base Integration

The exploration commands are integrated with CARL's knowledge base through the walk skill:

```json
{
  "Name": "walk",
  "arc_http_commands": {
    "forward": "http://192.168.56.1/movement?direction=forward",
    "reverse": "http://192.168.56.1/movement?direction=reverse",
    "left": "http://192.168.56.1/movement?direction=left",
    "right": "http://192.168.56.1/movement?direction=right",
    "stop": "http://192.168.56.1/movement?direction=stop"
  },
  "exploration_triggers": ["explore", "move", "walk", "go", "travel", "navigate"],
  "need_satisfaction": {
    "exploration": 0.3
  }
}
```

### 2.3 Automatic Exploration System

CARL automatically decides when to explore based on:

1. **Exploration need level** - Tracks exploration need (0.0 to 1.0)
2. **Need threshold** - Triggers exploration when need > 0.7
3. **Cooldown period** - 30 seconds between exploration actions
4. **Random direction selection** - Chooses forward, left, or right

```python
def check_exploration_need(self) -> Optional[str]:
    """Check if exploration need should trigger movement."""
    if self.exploration_need_level < self.exploration_threshold:
        return None
    
    if current_time - self.last_exploration_action < self.exploration_cooldown:
        return None
    
    # Determine exploration direction based on current state
    directions = ["forward", "left", "right"]
    return random.choice(directions)
```

## 3. Integration with Main Application

### 3.1 Emotional Response Processing

Body movements are automatically triggered during emotional response processing:

```python
def _process_emotional_response(self, event):
    # Get current emotional state from NEUCOGAR engine
    emotional_state = self.neucogar_engine.get_current_emotion()
    
    # Execute automatic body movement scripts based on NUECOGAR levels
    self._execute_automatic_body_movements(primary_emotion, intensity)
```

### 3.2 Cognitive Processing Loop

Exploration movements are checked during the cognitive processing loop:

```python
def _cognitive_processing_loop(self):
    while self.cognitive_state["is_processing"]:
        # Check and execute exploration movements based on need level
        self._check_exploration_need()
        
        # Continue with other cognitive processing...
```

### 3.3 Action System Integration

The ActionSystem class handles both body movement scripts and exploration commands:

```python
class ActionSystem:
    def __init__(self):
        # Movement command system for exploration
        self.movement_commands = {
            "forward": "http://192.168.56.1/movement?direction=forward",
            "reverse": "http://192.168.56.1/movement?direction=reverse",
            "left": "http://192.168.56.1/movement?direction=left",
            "right": "http://192.168.56.1/movement?direction=right",
            "stop": "http://192.168.56.1/movement?direction=stop"
        }
        
        # Body movement script execution tracking
        self.last_body_movement_time = 0.0
        self.body_movement_cooldown = 5.0
        self.executed_body_movements = set()
```

## 4. Skill Files Created

### 4.1 Body Movement Reaction Skills

Five new skill files have been created:

1. **`skills/reaction_amazed.json`** - Amazed body reaction
2. **`skills/reaction_terrified.json`** - Terrified body reaction
3. **`skills/reaction_ecstatic.json`** - Ecstatic body reaction
4. **`skills/reaction_amused.json`** - Amused body reaction
5. **`skills/reaction_irritated.json`** - Irritated body reaction

Each skill includes:
- Emotional triggers and intensity thresholds
- ARC HTTP commands for execution
- Coordination settings for eye movements
- Learning system integration

### 4.2 Concept Integration

**`concepts/body_movement_reactions.json`** - Central concept file that:
- Links all body movement reaction skills
- Defines emotional mappings and thresholds
- Configures execution conditions
- Integrates with NEUCOGAR system

## 5. Usage Examples

### 5.1 Automatic Body Movement Execution

When CARL experiences emotions, body movements are automatically triggered:

```python
# CARL feels surprised (intensity 0.6)
# Automatically executes:
# - eyes_surprise (RGB Animator)
# - reaction_amazed (Script Collection)
# Both execute simultaneously
```

### 5.2 Exploration Movement Execution

When CARL's exploration need is high:

```python
# Exploration need level: 0.8 (above 0.7 threshold)
# Automatically executes:
# - HTTP request to ARC: http://192.168.56.1/movement?direction=forward
# - Updates exploration need level to 0.6
# - Waits 30 seconds before next exploration
```

### 5.3 Coordinated Movement Example

```python
# CARL feels ecstatic joy (intensity 0.8)
# Executes coordinated movements:
# 1. reaction_ecstatic (body movement)
# 2. eyes_surprise (eye expression)
# Both execute simultaneously for realistic behavior
```

## 6. Benefits

### 6.1 Enhanced Human-Like Behavior
- **Realistic emotional expressions** - Eye and body movements coordinate naturally
- **Automatic responses** - No manual intervention required
- **Intensity-based execution** - Movements scale with emotional intensity

### 6.2 Improved Exploration
- **Need-based movement** - CARL explores when it needs to
- **Autonomous decision making** - CARL decides when and where to move
- **Knowledge base integration** - Movement commands are part of CARL's skills

### 6.3 NUECOGAR Integration
- **Emotional state awareness** - Movements reflect current emotional state
- **Neurotransmitter-based timing** - Execution timing based on brain chemistry
- **Coordinated responses** - Multiple systems work together seamlessly

## 7. Configuration

### 7.1 Cooldown Settings
- **Body movement cooldown**: 5.0 seconds
- **Exploration cooldown**: 30.0 seconds
- **Emotional expression cooldown**: 2.0 seconds

### 7.2 Intensity Thresholds
- **eyes_joy**: 0.4
- **eyes_surprise**: 0.3
- **eyes_sad**: 0.3
- **reaction_amazed**: 0.5
- **reaction_terrified**: 0.6
- **reaction_ecstatic**: 0.7
- **reaction_amused**: 0.4
- **reaction_irritated**: 0.4

### 7.3 Exploration Settings
- **Exploration threshold**: 0.7
- **Need reduction per movement**: 0.2
- **Available directions**: ["forward", "left", "right"]

## 8. Future Enhancements

### 8.1 Planned Improvements
- **Context-aware exploration** - Consider environment and obstacles
- **Learning-based movement** - Improve movement patterns over time
- **Social movement coordination** - Coordinate with human presence
- **Emotional memory** - Remember and repeat successful movements

### 8.2 Potential Additions
- **More body movement scripts** - Additional emotional reactions
- **Complex movement sequences** - Multi-step movement patterns
- **Environmental interaction** - Movement based on objects and space
- **Predictive movement** - Anticipate and prepare for interactions

## 9. Role-Playing Emotional System

### 9.1 Overview

CARL now supports **role-playing emotional requests** through natural language, allowing users to ask CARL to "act amazed," "pretend to be scared," or "show me a surprised reaction." This system simulates how humans can act out emotions for entertainment, demonstration, or social interaction.

### 9.2 How It Works

The system detects role-playing requests in user input and maps them to appropriate emotional triggers:

```python
def detect_role_playing_request(self, text: str) -> Optional[str]:
    """Detect if text contains a role-playing emotional request."""
    # Maps phrases like "act amazed" to trigger "act_amazed"
    # Maps phrases like "pretend to be scared" to trigger "pretend_scared"
    # Maps phrases like "show me surprised" to trigger "show_surprised"
```

### 9.3 Supported Role-Playing Requests

#### Act Commands
- **"Act amazed"** → Triggers `act_amazed` → Executes `reaction_amazed` + `eyes_surprise`
- **"Act surprised"** → Triggers `act_surprised` → Executes `reaction_amazed` + `eyes_surprise`
- **"Act amused"** → Triggers `act_amused` → Executes `reaction_amused` + `eyes_joy`
- **"Act happy"** → Triggers `act_joyful` → Executes `reaction_amused` + `eyes_joy`
- **"Act ecstatic"** → Triggers `act_ecstatic` → Executes `reaction_ecstatic` + `eyes_surprise`
- **"Act terrified"** → Triggers `act_terrified` → Executes `reaction_terrified` + `eyes_sad`
- **"Act scared"** → Triggers `act_scared` → Executes `reaction_terrified` + `eyes_sad`
- **"Act irritated"** → Triggers `act_irritated` → Executes `reaction_irritated` + `eyes_sad`
- **"Act angry"** → Triggers `act_angry` → Executes `reaction_irritated` + `eyes_sad`
- **"Act sad"** → Triggers `act_sad` → Executes `reaction_terrified` + `eyes_sad`

#### Pretend Commands
- **"Pretend to be amazed"** → Triggers `pretend_amazed`
- **"Pretend to be surprised"** → Triggers `pretend_surprised`
- **"Pretend to be amused"** → Triggers `pretend_amused`
- **"Pretend to be happy"** → Triggers `pretend_joyful`
- **"Pretend to be ecstatic"** → Triggers `pretend_ecstatic`
- **"Pretend to be terrified"** → Triggers `pretend_terrified`
- **"Pretend to be scared"** → Triggers `pretend_scared`
- **"Pretend to be irritated"** → Triggers `pretend_irritated`
- **"Pretend to be angry"** → Triggers `pretend_angry`
- **"Pretend to be sad"** → Triggers `pretend_sad`

#### Show Commands
- **"Show me amazed"** → Triggers `show_amazed`
- **"Show me surprised"** → Triggers `show_surprised`
- **"Show me amused"** → Triggers `show_amused`
- **"Show me happy"** → Triggers `show_joyful`
- **"Show me ecstatic"** → Triggers `show_ecstatic`
- **"Show me terrified"** → Triggers `show_terrified`
- **"Show me scared"** → Triggers `show_scared`
- **"Show me irritated"** → Triggers `show_irritated`
- **"Show me angry"** → Triggers `show_angry`
- **"Show me sad"** → Triggers `show_sad`

#### Question Commands
- **"Can you act amazed?"** → Triggers `act_amazed`
- **"Could you pretend to be scared?"** → Triggers `pretend_scared`
- **"Would you show me surprised?"** → Triggers `show_surprised`

### 9.4 Neurotransmitter Effects

Role-playing triggers create realistic neurotransmitter changes:

```python
# Role-playing emotional triggers
"act_amazed": {"dopamine": 0.2, "serotonin": 0.1, "noradrenaline": 0.4},
"act_amused": {"dopamine": 0.3, "serotonin": 0.2, "noradrenaline": 0.1},
"act_terrified": {"dopamine": -0.1, "serotonin": -0.2, "noradrenaline": 0.5},
"act_irritated": {"dopamine": -0.1, "serotonin": -0.2, "noradrenaline": 0.3},
```

### 9.5 Usage Examples

#### Example 1: Acting Amazed
```
User: "Can you act amazed?"
CARL: 
1. Detects role-playing request: "act_amazed"
2. Updates neurotransmitters: DA+0.2, 5-HT+0.1, NE+0.4
3. Resolves emotional state: "surprise" with "amazed" sub-emotion
4. Executes coordinated movements:
   - reaction_amazed (body movement)
   - eyes_surprise (eye expression)
5. Logs: "🎭 Executing coordinated body movements: reaction_amazed for surprise (intensity: 0.65)"
```

#### Example 2: Pretending to be Scared
```
User: "Pretend to be scared"
CARL:
1. Detects role-playing request: "pretend_scared"
2. Updates neurotransmitters: DA-0.1, 5-HT-0.2, NE+0.4
3. Resolves emotional state: "fear" with "scared" sub-emotion
4. Executes coordinated movements:
   - reaction_terrified (body movement)
   - eyes_sad (eye expression)
5. Logs: "🎭 Executing coordinated body movements: reaction_terrified for fear (intensity: 0.58)"
```

#### Example 3: Showing Amusement
```
User: "Show me amused"
CARL:
1. Detects role-playing request: "show_amused"
2. Updates neurotransmitters: DA+0.3, 5-HT+0.2, NE+0.1
3. Resolves emotional state: "joy" with "amused" sub-emotion
4. Executes coordinated movements:
   - reaction_amused (body movement)
   - eyes_joy (eye expression)
5. Logs: "🎭 Executing coordinated body movements: reaction_amused for joy (intensity: 0.42)"
```

### 9.6 Benefits

#### Enhanced Interaction
- **Natural language requests** - Users can ask CARL to act emotions naturally
- **Entertainment value** - CARL can perform emotional demonstrations
- **Educational tool** - Shows how emotions manifest in body language
- **Social interaction** - Simulates human role-playing behavior

#### Realistic Simulation
- **Neurotransmitter-based** - Role-playing affects brain chemistry realistically
- **Coordinated responses** - Eye and body movements work together
- **Intensity scaling** - Emotional intensity affects movement execution
- **Natural timing** - Respects cooldown periods and execution timing

#### Flexibility
- **Multiple trigger patterns** - Supports "act," "pretend," "show," and question formats
- **Varied emotional range** - Covers positive, negative, and neutral emotions
- **Context awareness** - Integrates with existing emotional processing
- **Extensible system** - Easy to add new role-playing patterns

### 9.7 Technical Implementation

#### Detection Algorithm
```python
def detect_role_playing_request(self, text: str) -> Optional[str]:
    text_lower = text.lower()
    
    # Role-playing patterns mapping
    role_playing_patterns = {
        "act_amazed": ["act amazed", "act like you're amazed", "act as if amazed"],
        "pretend_scared": ["pretend to be scared", "pretend scared", "pretend afraid"],
        "show_surprised": ["show surprised", "show me surprised", "demonstrate surprised"],
        # ... additional patterns
    }
    
    # Check for matches
    for trigger, patterns in role_playing_patterns.items():
        for pattern in patterns:
            if pattern in text_lower:
                return trigger
    
    return None
```

#### Integration with Emotional Processing
```python
def update_emotion_state(self, trigger_input: str) -> Dict[str, Any]:
    # First check if this is a role-playing request
    role_playing_trigger = self.detect_role_playing_request(trigger_input)
    
    if role_playing_trigger:
        # Use the role-playing trigger instead of the original input
        trigger_input = role_playing_trigger
        self.logger.info(f"Detected role-playing request: '{trigger_input}' -> using trigger: '{role_playing_trigger}'")
    
    # Continue with normal emotional processing...
```

### 9.8 Future Enhancements

#### Planned Improvements
- **Context-aware role-playing** - Consider current emotional state when acting
- **Duration control** - Allow users to specify how long to maintain the act
- **Intensity control** - Allow users to specify emotional intensity level
- **Combination acts** - Support complex emotional combinations

#### Potential Additions
- **Emotional storytelling** - Act out emotions for narrative purposes
- **Social learning** - Learn from human emotional demonstrations
- **Emotional memory** - Remember and repeat successful role-playing
- **Interactive scenarios** - Respond to emotional cues in conversations
