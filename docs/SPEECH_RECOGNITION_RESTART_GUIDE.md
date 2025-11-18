# Speech Recognition Restart Guide

## Overview

This guide explains how CARL's speech recognition restart functionality works and how to troubleshoot issues when speech recognition doesn't restart properly after processing events.

## How Speech Recognition Restart Works

### 1. Normal Flow

1. **Speech Input Received**: When CARL receives speech input (via EZ-Robot Bing Speech or HTTP POST), the `_handle_speech_input()` method is called.

2. **Processing Starts**: The `speak()` method is called, which:
   - Temporarily stops speech recognition to prevent interference
   - Sets status to "Speech: Processing..."
   - Processes the input through CARL's cognitive systems

3. **Processing Completes**: When cognitive processing is complete:
   - The `finally` block in `speak()` method restarts speech recognition
   - The `_ensure_speech_recognition_active()` method is called from the cognitive processing loop
   - Status is updated to "Speech: Active"

### 2. Restart Mechanisms

#### Automatic Restart
- **In `speak()` method**: Restarts speech recognition after processing completes
- **In cognitive processing loop**: Calls `_ensure_speech_recognition_active()` when processing is complete
- **Status updates**: Automatically updates UI status labels

#### Manual Restart
- **Restart Speech Button**: Available in the EZ-Robot Status panel
- **`_restart_speech_recognition()` method**: Manually stops and restarts speech recognition
- **Useful for**: Troubleshooting and forcing restart when automatic restart fails

### 3. Key Methods

#### `_ensure_speech_recognition_active()`
```python
def _ensure_speech_recognition_active(self):
    """Ensure speech recognition is active when it should be."""
    # Only restart if EZ-Robot is connected and bot is running
    if (self.ez_robot_connected and self.cognitive_state["is_processing"]):
        if not self.speech_recognition_active:
            # Attempt to restart speech recognition
            if self.ez_robot.start_speech_recognition(self.speech_callback):
                self.speech_recognition_active = True
                # Update status labels
```

#### `_restart_speech_recognition()`
```python
def _restart_speech_recognition(self):
    """Manually restart speech recognition."""
    # Stop current speech recognition if active
    if self.speech_recognition_active and self.ez_robot:
        self.ez_robot.stop_speech_recognition()
        self.speech_recognition_active = False
    
    # Wait for cleanup
    time.sleep(1)
    
    # Start speech recognition
    if self.ez_robot.start_speech_recognition(self.speech_callback):
        self.speech_recognition_active = True
        # Update status labels
```

## Troubleshooting

### Issue: Speech Recognition Not Restarting After Processing

#### Symptoms
- Speech status shows "Speech: Processing..." even after processing completes
- No new speech input is recognized after the first input
- Status label doesn't update to "Speech: Active"

#### Diagnostic Steps

1. **Check EZ-Robot Connection**
   ```
   - Verify EZ-Robot is connected (Status: Connected)
   - Check ARC is running and HTTP server is enabled
   - Test connectivity using the connectivity test
   ```

2. **Check Bot State**
   ```
   - Ensure bot is running (Run button is disabled)
   - Check cognitive processing is active
   - Verify no API calls are in progress
   ```

3. **Check Speech Recognition State**
   ```
   - Look at speech status label in EZ-Robot Status panel
   - Check if speech_recognition_active flag is True
   - Monitor logs for restart attempts
   ```

#### Solutions

1. **Use Manual Restart**
   ```
   - Click the "Restart Speech" button in EZ-Robot Status panel
   - This will force a restart of speech recognition
   - Check if status updates to "Speech: Active"
   ```

2. **Check Logs**
   ```
   - Look for error messages in the main log
   - Check for "Failed to restart speech recognition" messages
   - Look for EZ-Robot connection errors
   ```

3. **Restart Bot**
   ```
   - Stop the bot (Stop button)
   - Wait a few seconds
   - Start the bot again (Run button)
   - This will reinitialize speech recognition
   ```

4. **Check ARC Configuration**
   ```
   - Ensure ARC HTTP server is running
   - Verify Bing Speech Recognition is configured
   - Check that $BingSpeech variable exists
   ```

### Issue: Speech Recognition Stops Unexpectedly

#### Symptoms
- Speech recognition stops without processing any input
- Status shows "Speech: Failed" or "Speech: Error"
- No error messages in logs

#### Solutions

1. **Check EZ-Robot Thread**
   ```
   - Speech recognition runs in a separate thread
   - Thread may have crashed or been interrupted
   - Use manual restart to reinitialize the thread
   ```

2. **Check Network Connectivity**
   ```
   - Verify connection to ARC server (192.168.56.1)
   - Test HTTP endpoints
   - Check firewall settings
   ```

3. **Check Bing Speech API**
   ```
   - Verify Bing Speech API credentials in ARC
   - Check API quota and limits
   - Test speech recognition in ARC directly
   ```

### Issue: Multiple Speech Inputs Not Working

#### Symptoms
- Only the first speech input is processed
- Subsequent inputs are ignored
- Speech recognition doesn't restart between inputs

#### Solutions

1. **Check Processing State**
   ```
   - Ensure cognitive_processing_complete is True
   - Check that is_processing is True
   - Verify no API calls are blocking
   ```

2. **Check Speech Recognition Loop**
   ```
   - The EZ-Robot speech recognition loop may be stuck
   - Use manual restart to reset the loop
   - Check for infinite loops or blocking operations
   ```

3. **Check Event Loop**
   ```
   - Ensure asyncio event loop is running
   - Check for unhandled exceptions
   - Verify async operations complete properly
   ```

## Testing

### Run the Test Suite
```bash
python test_speech_recognition_restart.py
```

This test suite will:
- Test speech recognition restart functionality
- Test speech act detection
- Verify multiple speech inputs work
- Check manual restart functionality

### Manual Testing Steps

1. **Start CARL**
   ```
   - Connect to EZ-Robot
   - Start the bot
   - Verify speech recognition is active
   ```

2. **Test Speech Input**
   ```
   - Speak to CARL: "Hello CARL, can you wave?"
   - Watch status change to "Processing..."
   - Wait for processing to complete
   - Verify status returns to "Active"
   ```

3. **Test Multiple Inputs**
   ```
   - Speak again: "CARL, please sit down"
   - Verify second input is processed
   - Check that speech recognition restarts
   ```

4. **Test Manual Restart**
   ```
   - Click "Restart Speech" button
   - Verify status updates
   - Test speech input after restart
   ```

## Status Indicators

### Speech Status Labels
- **"Speech: Inactive"** (gray): Speech recognition not running
- **"Speech: Active"** (green): Speech recognition listening
- **"Speech: Processing..."** (orange): Processing speech input
- **"Speech: Failed"** (red): Speech recognition failed to start
- **"Speech: Error"** (red): Error occurred during restart

### EZ-Robot Status
- **"Status: Connected"** (green): EZ-Robot connected
- **"Status: Disconnected"** (red): EZ-Robot not connected

## Configuration

### Required Settings
- EZ-Robot connected and running
- ARC HTTP server enabled
- Bing Speech Recognition configured
- Flask HTTP server running (for ARC POST requests)

### Optional Settings
- Debug mode for detailed logging
- Manual restart button for troubleshooting
- Status labels for monitoring

## Best Practices

1. **Monitor Status Labels**: Keep an eye on speech status for issues
2. **Use Manual Restart**: If automatic restart fails, use the manual button
3. **Check Logs**: Look for error messages when issues occur
4. **Test Regularly**: Run the test suite to verify functionality
5. **Restart Bot**: If issues persist, restart the entire bot

## Common Error Messages

- **"Failed to restart speech recognition"**: EZ-Robot connection issue
- **"Cannot restart speech recognition - EZ-Robot not connected"**: Connection lost
- **"Cannot restart speech recognition - Bot not running"**: Bot stopped
- **"Error ensuring speech recognition is active"**: General restart error

## Support

If you continue to experience issues:
1. Check this guide for troubleshooting steps
2. Run the test suite to identify specific problems
3. Check the logs for detailed error messages
4. Verify all required components are running
5. Use the manual restart button as a workaround 