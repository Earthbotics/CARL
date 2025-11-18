# Speech System Updates - HTTP Response Integration

## Overview

The speech recognition system has been updated to use HTTP responses from ARC instead of ScriptStart getBingSpeech calls. This provides better integration and reliability.

## Changes Made

### 1. Removed ScriptStart getBingSpeech Methods

The following methods have been removed from `ezrobot.py`:
- `execute_script()` - No longer needed with HTTP responses
- `_get_speech_variable()` - Replaced by HTTP response handling
- Updated `_speech_recognition_loop()` - Now waits for HTTP responses

### 2. Text-to-Speech Functionality

Computer speaker text-to-speech functionality has been implemented using edge-tts:
- `_speak_to_computer_speakers(text)` - Sends text to computer speakers

### 3. Updated Speech Response System

Enhanced `main.py` with:
- Better breakpoint location for debugging action execution
- Computer speaker text-to-speech integration in `_execute_verbal_action()`
- `_extract_speech_text()` method that prioritizes 'content' from 'proposed_action'
- `_speak_to_computer_speakers()` method using edge-tts

## Breakpoint Location for Action Execution

**Best breakpoint location:** `main.py` line ~1541 in the `_execute_verbal_action()` method:

```python
async def _execute_verbal_action(self, action: str, event_data: Dict) -> bool:
    """Execute a verbal response action."""
    try:
        # BREAKPOINT LOCATION: Set breakpoint here to debug action execution
        # This is where CARL decides what to say or do in response to speech
        self.log(f"🎤 Verbal action requested: {action}")
        self.log(f"🎤 Context: {event_data.get('WHAT', '')}")
        
        # Extract text to speak from the action or context
        text_to_speak = self._extract_speech_text(action, event_data)
        
        if text_to_speak:
            # Send text to computer speakers
            success = self._speak_to_computer_speakers(text_to_speak)
            if success:
                self.log(f"🔊 CARL speaking: '{text_to_speak}'")
                return True
            else:
                self.log(f"❌ Failed to speak: '{text_to_speak}'")
                return False
        else:
            self.log(f"🎤 No text to speak for action: {action}")
            return True
```

**Why this location is ideal:**
1. **Action Decision Point**: This is where CARL decides what action to take
2. **Pre-Execution**: You can inspect the action and context before execution
3. **Text-to-Speech**: You can see what text will be spoken
4. **Computer Speaker Integration**: You can verify TTS functionality
5. **Error Handling**: You can catch any issues before they occur

## Text-to-Speech Setup

### 1. Install edge-tts

Install the required text-to-speech library:
```bash
pip install edge-tts
```

### 2. Test Computer Speakers

Run the test script to verify computer speaker text-to-speech works:
```bash
python test_computer_speech.py
```

### 3. Integration with CARL

When CARL detects a speech act directed to itself, it will:
1. Extract the first recommended action from the judgment system
2. Execute the action (wave, bow, speak, etc.)
3. For verbal actions, extract text from 'proposed_action.content' or generate appropriate speech text
4. Send the text to computer speakers via edge-tts

## Speech Flow

```
User Speech → ARC HTTP Server → Flask Server → CARL Processing → Action Execution → Text-to-Speech
```

### Detailed Flow:
1. **Speech Capture**: ARC captures speech and sends to Flask server
2. **Processing**: CARL processes speech through cognitive pipeline
3. **Judgment**: Judgment system generates recommended actions
4. **Action Selection**: First recommended action is selected
5. **Execution**: Action is executed (BREAKPOINT HERE)
6. **Response**: If verbal, text is sent to computer speakers for speech synthesis

## Testing

### Test Speech Response System
```bash
python test_speech_response.py
```

### Test Computer Speaker Text-to-Speech
```bash
python test_computer_speech.py
```



### Test Complete Integration
1. Start CARL
2. Connect EZ-Robot
3. Run Bot
4. Speak to JD
5. Watch for action execution and speech response

## Troubleshooting

### Computer Speaker Text-to-Speech Issues
1. **edge-tts Not Installed**: Install with `pip install edge-tts`
2. **No Sound**: Check computer speaker settings and volume
3. **Voice Issues**: Check available voices with `python test_tts_simple.py`



### Action Execution Issues
1. **Breakpoint Not Hit**: Check if speech act detection is working
2. **No Actions**: Verify judgment system is generating recommendations
3. **TTS Errors**: Check edge-tts installation and computer audio settings

## Future Enhancements

1. **Better Speech Generation**: Use AI to generate more natural responses
2. **Emotion Integration**: Match speech tone to emotional state
3. **Context Awareness**: Generate responses based on conversation history
4. **Multiple Actions**: Execute sequences of actions instead of just the first

## Files Modified

- `ezrobot.py` - Removed ScriptStart methods and text-to-speech functionality
- `main.py` - Enhanced speech response system with computer speaker TTS and breakpoint location
- `requirements.txt` - Added edge-tts dependency
- `test_computer_speech.py` - Test script for computer speaker TTS functionality
- `test_speech_response_system.py` - Test script for complete speech response system
- `SPEECH_SYSTEM_UPDATES.md` - This documentation file 