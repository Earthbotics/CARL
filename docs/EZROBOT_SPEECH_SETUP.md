# EZ-Robot Speech Recognition Setup Guide

## Overview

This guide explains how to set up speech recognition for CARL using EZ-Robot's Bing Speech Recognition system. The implementation uses a **manual control sequence** where Python directly controls the speech recognition cycle via HTTP commands.

## Manual Control Sequence

The speech recognition now follows this exact sequence:

1. **Start Listening**: Call `ControlCommand("Bing Speech Recognition", "StartListening")` via HTTP
2. **Wait for Capture**: Allow time for Bing API to process speech (6 seconds)
3. **Check for Speech**: Call `getBingSpeech` script to check if anything was captured
4. **Process Speech**: If speech was captured, process it through CARL's cognitive systems
5. **Clear Variable**: After analysis, call `getBingSpeech` again to clear the variable (DISABLED - clearBingSpeech functionality has been disabled)
6. **Stop Listening**: Call `ControlCommand("Bing Speech Recognition", "StopListening")` via HTTP
7. **Repeat**: Start the cycle again

## Prerequisites

1. **EZ-Robot ARC Software**: Make sure ARC is installed and running
2. **JD Robot**: Ensure JD is powered on and connected to the network
3. **HTTP Server**: Enable the HTTP server in ARC's System window
4. **Bing Speech Recognition**: Configure Bing Speech Recognition in ARC
5. **$BingSpeech Variable**: Create this variable in ARC's Variables window

## Setup Steps

### 1. Enable HTTP Server in ARC

1. Open ARC (EZ-Robot software)
2. Go to the **System** window
3. Enable **HTTP Server**
4. Note the IP address and port (default: 192.168.56.1)

### 2. Configure Bing Speech Recognition

1. In ARC, go to the **Bing Speech Recognition** window
2. Configure your Bing Speech API credentials
3. Test the speech recognition to ensure it's working
4. Make sure the `$BingSpeech` variable is created and accessible

### 3. Create Required Scripts

#### Script 1: getBingSpeech

Create a new script in ARC's **Script Collection** window named `getBingSpeech`:

```javascript
// Script: getBingSpeech
// Purpose: Return the current value of $BingSpeech variable
// Usage: Called by Python to check for captured speech

// Retrieve the captured phrase from the global variable
var capturedText = getVar("$BingSpeech", "");

// Output the captured text to the console for debugging
print("getBingSpeech: " + capturedText);

// Return the captured text
return capturedText;
```

#### Script 2: clearBingSpeech (DISABLED)

**Note**: This script has been disabled. The clearBingSpeech functionality is no longer used.

~~Create a new script in ARC's **Script Collection** window named `clearBingSpeech`:~~

```javascript
// Script: clearBingSpeech (DISABLED)
// Purpose: Clear the $BingSpeech variable
// Usage: Called by Python to clear speech after processing (DISABLED)

setVar("$BingSpeech", "");
return "cleared";
```

### 4. Test the Setup

Run the test script to verify everything is working:

```bash
python test_ezrobot_manual_sequence.py
```

## How the System Works

The speech recognition system uses a manual control sequence with proper timing:

1. **Start Listening**: Sends HTTP command to start Bing Speech Recognition
2. **Wait for Processing**: Waits 10 seconds for Bing API to process speech input
3. **Check for Speech**: Calls `getBingSpeech` script to retrieve captured text
4. **Process Speech**: If speech is captured, processes it through CARL's cognitive systems
5. **Stop Listening**: Sends HTTP command to stop listening
6. **Pause Between Cycles**: Waits 10 seconds before starting the next listening cycle

This approach ensures:
- Adequate time for Bing API to process speech (10 seconds)
- No overlapping speech recognition attempts
- Proper clearing of the speech variable between cycles
- Integration with CARL's cognitive processing pipeline

### HTTP Commands Used

- **Start Listening**: `ControlCommand("Bing Speech Recognition", "StartListening")`
- **Stop Listening**: `ControlCommand("Bing Speech Recognition", "StopListening")`
- **Get Speech**: `ScriptStart("getBingSpeech")`
- **Clear Speech**: `ScriptStart("clearBingSpeech")` (DISABLED)

### Key Features

- **Manual control**: Python directly controls the speech recognition cycle
- **Explicit logging**: Each step is logged for debugging
- **Error handling**: Better error handling with manual control
- **Flexible timing**: Adjustable listening duration and delays

## Troubleshooting

### Common Issues

1. **Script not found**: Make sure both scripts are created in ARC's Script Collection
2. **Variable not accessible**: Ensure `$BingSpeech` variable exists in Variables window
3. **HTTP connection failed**: Check that HTTP server is enabled in ARC
4. **No speech captured**: Verify Bing Speech Recognition is properly configured
5. **Script timeout**: The script may take time to execute; increase timeout if needed
6. **Timing issues**: The system now waits 10 seconds for Bing API processing and 10 seconds between cycles

### Debug Steps

1. **Test connection**: Run `test_ezrobot_manual_sequence.py` to test basic connectivity
2. **Check script execution**: Verify scripts can be executed manually in ARC
3. **Monitor console**: Check ARC's console for debug output from scripts
4. **Test variable access**: Manually test `$BingSpeech` variable access in ARC
5. **Test HTTP commands**: Verify StartListening and StopListening commands work

### Error Messages

- **"Script not found"**: Create the missing script in ARC
- **"Variable not found"**: Create the `$BingSpeech` variable in ARC
- **"HTTP connection failed"**: Enable HTTP server in ARC
- **"Timeout error"**: Increase timeout values or check network connectivity

## Integration with CARL

Once speech recognition is working, speech input will:

1. Be captured by the manual control sequence
2. Passed to CARL's speech input handler
3. Processed through CARL's cognitive pipeline
4. Generate appropriate responses
5. Trigger JD's thinking animation during processing

## Testing

### Test Individual Commands

Run the test script to verify each component:

```bash
python test_ezrobot_manual_sequence.py
```

This will test:
1. Individual HTTP commands
2. Manual speech recognition sequence
3. Speech recognition with callback

### Expected Log Output

When working correctly, you should see logs like:

```
🔍 Starting listening via HTTP command...
🔍 Waiting for Bing API to process speech (10 seconds)...
🔍 Checking if speech was captured...
🔍 getBingSpeech returned: 'Hello CARL'
🎤 Captured speech: 'Hello CARL'
🔍 Calling speech callback with: 'Hello CARL'
🔍 Analysis complete, calling getBingSpeech again to clear...
🔍 getBingSpeech after analysis returned: ''
🔍 Stopping listening...
```

## Configuration Options

### Timing Settings

You can adjust the timing values in the Python code:
- `time.sleep(10)`: Time to wait for Bing API to process speech (10 seconds)
- `time.sleep(10)`: Delay between listening cycles (10 seconds)

### Variable Name

If you need to use a different variable name, update:
- The variable name in both scripts
- The `bing_speech_variable` property in the `EZRobot` class

## Performance Notes

- **Cycle Time**: Each speech recognition cycle takes approximately 22 seconds (10s processing + 10s pause + overhead)
- **Accuracy**: Depends on Bing Speech Recognition configuration
- **Latency**: Minimal latency between speech capture and processing
- **Reliability**: Manual control provides better error handling and debugging
- **Timing**: 10-second processing window with 10-second pause between cycles

## Future Enhancements

Potential improvements:
- Adjustable listening duration
- Multiple language support
- Voice activity detection
- Noise cancellation
- Speaker identification

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run the test script to identify specific problems
3. Verify all prerequisites are met
4. Check ARC's console for error messages
5. Ensure all scripts are properly created and accessible 