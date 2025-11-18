# CARL Speech System Troubleshooting Guide

## Overview

This guide helps you troubleshoot issues with CARL's speech system, including text-to-speech (TTS), speech recognition, and speech response functionality.

## Quick Diagnostic Tests

### 1. Test Basic Text-to-Speech
```bash
python test_tts_simple.py
```
**Expected Result**: You should hear CARL speak through your computer speakers.

### 2. Test Complete Speech System
```bash
python test_speech_response_system.py
```
**Expected Result**: Multiple speech tests with clear audio output.

### 3. Test from CARL Interface
- Click "Test Text-to-Speech" button
- Click "Test EZ-Robot Speech" button
- Check the logs for detailed results

## Common Issues and Solutions

### Issue 1: No Audio Output from CARL

#### Symptoms
- CARL processes speech input but doesn't speak
- No audio heard during tests
- Logs show TTS success but no sound

#### Diagnostic Steps

1. **Check Computer Audio**
   ```
   - Verify speakers/headphones are connected and working
   - Check Windows volume settings
   - Test with other applications (YouTube, music player)
   - Ensure audio output device is set as default
   ```

2. **Check edge-tts Installation**
   ```bash
   pip install edge-tts
   python -c "import edge_tts; print('edge-tts installed successfully')"
   ```

3. **Test Windows Text-to-Speech**
   ```
   - Open Windows Settings > Time & Language > Speech
   - Test the "Preview voice" feature
   - Ensure a voice is selected and working
   ```

4. **Check for Audio Conflicts**
   ```
   - Close other applications that might use audio
   - Check Windows audio settings for exclusive mode
   - Restart audio services if needed
   ```

#### Solutions

1. **Fix Audio Output**
   ```
   - Set correct default audio device
   - Increase system volume
   - Check for muted applications
   - Restart audio drivers
   ```

2. **Reinstall edge-tts**
   ```bash
   pip uninstall edge-tts
   pip install edge-tts
   ```

3. **Use Different Voice**
   - The system automatically selects a voice
   - You can modify voice selection in `_speak_to_computer_speakers()` method

### Issue 2: Speech Recognition Not Working

#### Symptoms
- CARL doesn't respond to speech input
- Speech status shows "Inactive" or "Failed"
- No speech input detected

#### Diagnostic Steps

1. **Check EZ-Robot Connection**
   ```
   - Verify EZ-Robot is connected (Status: Connected)
   - Check ARC is running and HTTP server enabled
   - Test network connectivity to 192.168.56.1
   ```

2. **Check Speech Recognition Status**
   ```
   - Look at speech status label in EZ-Robot Status panel
   - Check if speech_recognition_active is True
   - Monitor logs for restart attempts
   ```

3. **Test ARC Configuration**
   ```
   - Verify Bing Speech Recognition is configured in ARC
   - Check that $BingSpeech variable exists
   - Test speech recognition directly in ARC
   ```

#### Solutions

1. **Restart Speech Recognition**
   ```
   - Click "Restart Speech" button
   - Stop and start the bot
   - Check logs for restart success
   ```

2. **Fix ARC Configuration**
   ```
   - Ensure ARC HTTP server is running
   - Configure Bing Speech API credentials
   - Test speech recognition in ARC
   ```

3. **Check Network**
   ```
   - Verify connection to 192.168.56.1
   - Check firewall settings
   - Test HTTP endpoints
   ```

### Issue 3: Speech Act Detection Not Working

#### Symptoms
- CARL doesn't recognize when someone is speaking to him
- No response generated to speech input
- Speech input processed but no action taken

#### Diagnostic Steps

1. **Check Event Data**
   ```
   - Verify WHO field is populated
   - Check intent classification
   - Ensure people list includes "CARL"
   ```

2. **Test Speech Act Detection**
   ```python
   # Test with direct command
   event_data = {
       "WHO": "User",
       "WHAT": "Hello CARL, can you wave?",
       "intent": "command",
       "people": ["CARL"]
   }
   is_speech_act = app._is_speech_act(event_data)
   ```

3. **Check OpenAI Analysis**
   ```
   - Monitor logs for OpenAI analysis results
   - Verify WHO, intent, and people fields are correct
   - Check for analysis errors
   ```

#### Solutions

1. **Improve Speech Input**
   ```
   - Speak clearly and directly to CARL
   - Use CARL's name in speech
   - Make requests or ask questions
   ```

2. **Check Analysis Quality**
   ```
   - Verify OpenAI API is working
   - Check API quota and limits
   - Monitor analysis accuracy
   ```

### Issue 4: Speech Response Not Generated

#### Symptoms
- Speech act detected but no response
- No text extracted for speech
- Action execution fails

#### Diagnostic Steps

1. **Check Action Context**
   ```
   - Verify recommended_actions list is populated
   - Check action classification
   - Monitor action execution logs
   ```

2. **Test Text Extraction**
   ```python
   # Test text extraction
   extracted_text = app._extract_speech_text("talk", event_data)
   print(f"Extracted text: {extracted_text}")
   ```

3. **Check Verbal Action Execution**
   ```
   - Monitor _execute_verbal_action logs
   - Check for TTS errors
   - Verify speech text is generated
   ```

#### Solutions

1. **Fix Action Generation**
   ```
   - Check judgment system output
   - Verify action context is properly formed
   - Monitor cognitive processing
   ```

2. **Improve Text Extraction**
   ```
   - Check proposed_action content
   - Verify fallback text generation
   - Monitor extraction logic
   ```

### Issue 5: Computer Speaker TTS Issues

#### Symptoms
- No audio output from computer speakers
- TTS initialization failures
- Voice selection problems

#### Diagnostic Steps

1. **Check edge-tts Installation**
   ```python
   # Test edge-tts availability
   import edge_tts
   import asyncio
   
   async def test_edge_tts():
       voices = await edge_tts.list_voices()
       print(f"Found {len(voices)} voices")
   
   asyncio.run(test_edge_tts())
   ```

2. **Check Audio Settings**
   ```
   - Verify computer speakers are working
   - Check Windows volume settings
   - Test with other applications
   ```

3. **Test TTS Functionality**
   ```python
   # Test TTS directly
   success = app._speak_to_computer_speakers("Test message")
   print(f"TTS test: {'Success' if success else 'Failed'}")
   ```

#### Solutions

1. **Fix edge-tts Issues**
   ```
   - Install edge-tts: pip install edge-tts
   - Check Python environment
   - Verify voice availability
   ```

2. **Fix Audio Issues**
   ```
   - Check speaker connections
   - Adjust Windows volume
   - Test with different audio devices
   ```

## Advanced Troubleshooting

### Debug Mode
Enable debug mode to get detailed logs:
1. Click "Debug Mode: ON" button
2. Use "Step" button to advance processing
3. Monitor detailed logs for issues

### Log Analysis
Check logs for:
- TTS initialization errors
- Speech recognition failures
- Action execution errors
- Network connectivity issues

### System Requirements
- Windows 10/11 with working audio
- Python 3.8+ with edge-tts
- Computer speakers or headphones
- EZ-Robot with ARC software (for speech recognition only)
- Network connectivity to 192.168.56.1 (for EZ-Robot)

## Test Scripts

### Basic TTS Test
```bash
python test_tts_simple.py
```

### Complete System Test
```bash
python test_speech_response_system.py
```

### Speech Recognition Test
```bash
python test_speech_recognition_restart.py
```

## Expected Behavior

### Normal Operation
1. **Speech Input**: User speaks to CARL
2. **Recognition**: Speech is recognized and processed
3. **Analysis**: OpenAI analyzes the speech
4. **Detection**: Speech act is detected
5. **Response**: CARL generates and speaks a response
6. **Restart**: Speech recognition restarts for next input

### Audio Output
- CARL should speak through computer speakers
- Speech should be clear and understandable
- Multiple speech patterns should work
- Volume should be appropriate

### Status Indicators
- **Speech: Active** (green) - Listening for input
- **Speech: Processing...** (orange) - Processing speech
- **Speech: Failed** (red) - Recognition failed
- **Speech: Error** (red) - System error

## Getting Help

If issues persist:
1. Run all test scripts
2. Check logs for error messages
3. Verify system requirements
4. Test individual components
5. Use debug mode for detailed analysis

## Common Error Messages

- **"edge-tts not installed"**: Install with `pip install edge-tts`
- **"Failed to restart speech recognition"**: Check EZ-Robot connection
- **"Cannot restart speech recognition"**: Verify bot is running
- **"Error speaking to computer speakers"**: Check audio settings
- **"ARC connectivity test failed"**: Check network and ARC configuration 