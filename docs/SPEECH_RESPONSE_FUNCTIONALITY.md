# CARL Speech Response Functionality

## Overview

CARL now has the ability to automatically respond to speech acts (when someone speaks to CARL) by executing the first recommended action from the judgment system. This functionality enables CARL to demonstrate its hearing and speaking senses through EZ-Robot skills and emotional expressions.

## How It Works

### 1. Speech Act Detection

CARL automatically detects when an event is a speech act by analyzing:

- **WHO field**: Identifies who is speaking (must not be empty or "Unknown")
- **Intent field**: Checks if the intent involves communication (query, request, command, inform, share, answer)
- **People field**: Verifies that people are mentioned in the event
- **WHAT field**: Looks for speech indicators like "said", "told", "asked", "spoke", "mentioned"

### 2. Recommended Action Extraction

When a speech act is detected, CARL:

1. Processes the input through the full cognitive pipeline (Perception → Judgment → Action)
2. Extracts the `recommended_actions` list from the action context
3. Takes the **first action** (index 0) as CARL's response
4. Executes that action through the appropriate system

### 3. Action Execution

CARL maps recommended actions to different execution types:

#### Physical Skills (`perform_*`)
- Maps to EZ-Robot skills like wave, bow, sit, stand, kick, point, etc.
- Executes via `send_auto_position()` command

#### Emotional Expressions (`express_*`)
- Maps to RGB animations like joy, sadness, anger, fear, surprise, etc.
- Executes via RGB Animator window

#### Social Interactions (`engage_*`, `social`)
- Defaults to friendly wave gesture
- Can be expanded for more complex social behaviors

#### Verbal Responses (`talk`, `conversation`)
- Currently logs the verbal action
- Future: Can integrate with text-to-speech systems

#### Direct EZ-Robot Commands
- Direct skill names like "wave", "bow", "point"
- Falls back to EZ-Robot command mapping

## Implementation Details

### Core Methods

```python
def _is_speech_act(self, event_data: Dict) -> bool:
    """Determine if the event is a speech act (someone speaking to CARL)."""

async def _generate_speech_response(self, action_context: Dict, event_data: Dict):
    """Generate and execute CARL's response to a speech act."""

async def _execute_speech_response_action(self, action: str, event_data: Dict) -> bool:
    """Execute a specific action as CARL's speech response."""
```

### Integration Points

The speech response functionality is integrated into the main `process_input()` method:

```python
# Execute actions
execution_result = await self.action_system.execute_action(action_context)

# Check if this is a speech act and generate response
if self._is_speech_act(event_data):
    await self._generate_speech_response(action_context, event_data)
```

### EZ-Robot Skill Mappings

| Action | EZ-Robot Skill | Description |
|--------|----------------|-------------|
| `perform_wave` | `EZRobotSkills.Wave` | Friendly wave gesture |
| `perform_bow` | `EZRobotSkills.Bow` | Respectful bow |
| `perform_sit` | `EZRobotSkills.Sit_Down` | Sit down |
| `perform_stand` | `EZRobotSkills.Stand_From_Sit` | Stand up |
| `perform_kick` | `EZRobotSkills.Kick` | Kick motion |
| `perform_point` | `EZRobotSkills.Point` | Point gesture |
| `perform_thinking` | `EZRobotSkills.Thinking` | Thinking pose |

### Emotional Expression Mappings

| Emotion | RGB Animation | Description |
|---------|---------------|-------------|
| `express_joy` | `Expressions` | Happy expression |
| `express_sadness` | `Diag Scan` | Sad expression |
| `express_anger` | `Flash` | Angry expression |
| `express_fear` | `Scanner` | Fearful expression |
| `express_surprise` | `Spin` | Surprised expression |
| `express_excited` | `Disco` | Excited animation |

## Testing

### Test Scripts

1. **`test_speech_response_simple.py`**: Tests the core logic without full app initialization
2. **`test_speech_response.py`**: Full integration test (requires app initialization)

### Test Cases

The system includes comprehensive test cases for:

- Speech act detection with various scenarios
- Action type classification
- Recommended action extraction
- EZ-Robot skill mapping
- Emotional expression mapping

### Manual Testing

To test with actual speech:

1. Start CARL and connect EZ-Robot
2. Speak to CARL through speech recognition
3. Watch for CARL's response based on recommended actions
4. Check the log for speech act detection and action execution

## Example Scenarios

### Scenario 1: Greeting Response
**Input**: "Hello CARL, how are you today?"
**Detection**: Speech act detected (WHO: "User", intent: "query")
**Judgment**: Generates recommended actions
**Response**: Executes first action (e.g., `perform_wave` → EZ-Robot wave)

### Scenario 2: Command Response
**Input**: "CARL, please sit down"
**Detection**: Speech act detected (WHO: "User", intent: "command")
**Judgment**: Generates recommended actions
**Response**: Executes first action (e.g., `perform_sit` → EZ-Robot sit)

### Scenario 3: Emotional Response
**Input**: "I'm feeling sad today"
**Detection**: Speech act detected (WHO: "User", intent: "share")
**Judgment**: Generates recommended actions
**Response**: Executes first action (e.g., `express_sadness` → RGB sad animation)

## Configuration

### Speech Act Detection Parameters

The system can be configured by modifying the detection logic in `_is_speech_act()`:

```python
# Valid intents for speech acts
valid_intents = ['query', 'request', 'command', 'inform', 'share', 'answer']

# Speech indicators in WHAT field
speech_indicators = ['said', 'told', 'asked', 'spoke', 'mentioned', 'asked me', 'told me']
```

### Action Execution Priority

Actions are executed in this priority order:

1. Physical skills (`perform_*`)
2. Emotional expressions (`express_*`)
3. Verbal responses (`talk`, `conversation`)
4. Social interactions (`engage_*`, `social`)
5. Direct EZ-Robot commands (fallback)

## Troubleshooting

### Common Issues

1. **No response generated**: Check if speech act detection is working
2. **Wrong action executed**: Verify recommended actions in judgment system
3. **EZ-Robot not responding**: Check EZ-Robot connection and skill mappings
4. **Emotional expressions not working**: Verify RGB Animator configuration

### Debug Information

The system provides detailed logging:

```
🔍 Speech act detection: WHO='Joe', intent='query', people=['Joe', 'me'], is_speech_act=True
🎤 Generating speech response...
🎤 First recommended action: 'perform_wave'
🎤 Executed skill action: wave
✅ Successfully executed speech response: 'perform_wave'
```

## Future Enhancements

### Planned Features

1. **Text-to-Speech Integration**: Convert verbal actions to actual speech
2. **Context-Aware Responses**: Consider conversation history for better responses
3. **Multi-Action Sequences**: Execute multiple actions in sequence
4. **Learning Responses**: Adapt responses based on interaction history
5. **Emotional Intelligence**: More sophisticated emotional response selection

### Integration Opportunities

- **ARC HTTP POST**: Direct integration with ARC's push-based speech system
- **Advanced NLP**: Better understanding of speech context and intent
- **Gesture Recognition**: Respond to physical gestures as well as speech
- **Multi-Modal Responses**: Combine speech, movement, and expressions

## Conclusion

The speech response functionality provides CARL with the ability to demonstrate its hearing and speaking senses through EZ-Robot skills and emotional expressions. This creates a more interactive and engaging experience for users, allowing CARL to respond naturally to speech input with appropriate physical and emotional responses.

The system is designed to be extensible, allowing for future enhancements in speech synthesis, context awareness, and more sophisticated response selection algorithms. 