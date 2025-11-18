# CARL Speech Recognition Integration

## Overview

CARL Version 5.4.2 now includes integrated speech recognition capabilities through JD's Bing Speech Recognition skill. This allows CARL to listen to spoken input from users in the physical world, making interactions more natural and intuitive.

## Features

### 🎤 Speech Recognition
- **Conditional Listening**: CARL only listens for speech input when the bot is actively running
- **Real-time Processing**: Captured speech is immediately processed through CARL's cognitive systems
- **Automatic Integration**: Speech input follows the same processing pipeline as typed text
- **Visual Feedback**: JD performs the "Thinking" animation while processing speech
- **State-Aware**: Speech recognition automatically starts/stops with bot state changes

### 🤖 EZ-Robot Integration
- **Automatic Connection**: Tests connection to JD at startup (default IP: 192.168.1.1:23)
- **Initialization Sequence**: JD automatically stands up and takes initial snapshot when connected
- **Status Monitoring**: Real-time status display for connection and speech recognition
- **Connection Management**: Easy connect/disconnect through GUI button

### 🧠 Cognitive Processing
- **Unified Processing**: Speech input goes through the same cognitive pipeline as text input
- **Temporary Pause**: Speech recognition pauses during cognitive processing to avoid interference
- **Automatic Resume**: Speech recognition resumes after processing is complete
- **Emotional Context**: Speech input includes emotional context and processing

## Setup Instructions

### Prerequisites
1. **JD Hardware**: Ensure JD is powered on and connected to the network
2. **ARC Software**: Make sure ARC is running with JD connected
3. **Bing Speech Recognition**: Install and configure the Bing Speech Recognition skill in ARC
4. **Network Access**: JD should be accessible at the default IP address (192.168.56.1)

### Configuration
1. **ARC Setup**: 
   - Install Bing Speech Recognition skill
   - Configure the `$BingSpeech` global variable
   - Ensure the skill is enabled and working

2. **Network Configuration**:
   - Verify JD's IP address (default: 192.168.56.1)
   - Ensure firewall allows connections to JD's port
   - Test network connectivity

### Usage
1. **Start CARL**: Launch the main application
2. **Connect EZ-Robot**: Click "Connect EZ-Robot" button
3. **Verify Connection**: Check status indicators in the GUI (should show "Waiting for Bot")
4. **Run Bot**: Click "Run Bot" button to start cognitive processing and speech recognition
5. **Start Speaking**: CARL will now listen for speech input (status should show "Active")
6. **Observe Processing**: Watch JD's "Thinking" animation during processing
7. **Stop Bot**: Click "Stop Bot" to stop cognitive processing and speech recognition

## Technical Details

### Architecture
```
User Speech → JD Microphones → Bing Speech Recognition → $BingSpeech Variable → CARL Processing
```

### Key Components

#### EZ-Robot Module (`ezrobot.py`)
- **Connection Management**: Handles connection to JD's ARC software
- **Speech Recognition Loop**: Continuous polling of `$BingSpeech` variable
- **Command Execution**: Sends commands to JD for movements and actions
- **Status Monitoring**: Tracks connection and speech recognition status

#### Main Application (`main.py`)
- **GUI Integration**: EZ-Robot connection button and status display
- **Speech Callback**: Handles captured speech and routes to cognitive processing
- **Processing Integration**: Integrates speech input with existing cognitive pipeline
- **Status Updates**: Real-time updates of connection and speech status

### Speech Recognition Flow
1. **Bot State Check**: Speech recognition only activates when bot is running
2. **Listening Phase**: JD listens for speech input (only when active)
3. **Capture**: Bing Speech Recognition captures and processes speech
4. **Variable Update**: `$BingSpeech` variable is updated with captured text
5. **Polling**: CARL polls the variable for new speech input
6. **Processing**: Captured text is processed through cognitive systems
7. **Response**: CARL generates and executes appropriate responses
8. **State Management**: Speech recognition stops when bot stops

### Error Handling
- **Connection Failures**: Graceful handling of network connection issues
- **Speech Recognition Errors**: Automatic retry and error reporting
- **Processing Interruptions**: Temporary pause/resume of speech recognition
- **Status Feedback**: Clear visual indicators of system status

## Testing

### Test Script
Run the included test script to verify functionality:
```bash
python test_ezrobot_speech.py
```

### Manual Testing
1. **Connection Test**: Verify JD connects and stands up
2. **Speech Test**: Speak clearly and observe captured text
3. **Processing Test**: Verify speech input triggers cognitive processing
4. **Response Test**: Check that JD responds appropriately to speech

## Troubleshooting

### Common Issues

#### Connection Problems
- **Check Power**: Ensure JD is powered on
- **Network Access**: Verify JD is accessible at 192.168.56.1
- **ARC Status**: Confirm ARC is running and connected to JD
- **Firewall**: Check if firewall is blocking connections

#### Speech Recognition Issues
- **Microphone**: Ensure JD's microphones are working
- **Bing Skill**: Verify Bing Speech Recognition skill is installed and configured
- **Variable**: Check that `$BingSpeech` variable is properly set up
- **Network**: Ensure stable network connection for Bing services

#### Processing Issues
- **Cognitive State**: Check if cognitive processing is complete before new input
- **Memory**: Verify sufficient system resources for processing
- **Logs**: Check application logs for error messages

### Debug Information
- **Status Indicators**: Monitor GUI status labels for real-time information
- **Console Output**: Check console for detailed error messages
- **Network Logs**: Monitor network traffic to JD
- **ARC Logs**: Check ARC software logs for skill-related issues

## Future Enhancements

### Planned Features
- **Voice Commands**: Direct voice commands for specific actions
- **Multi-language Support**: Support for multiple languages
- **Voice Synthesis**: JD speaking responses back to users
- **Environmental Awareness**: Context-aware speech processing
- **Learning Integration**: Speech-based learning and concept development

### Technical Improvements
- **Reduced Latency**: Optimize speech recognition response time
- **Better Error Recovery**: Enhanced error handling and recovery
- **Advanced Filtering**: Noise reduction and speech enhancement
- **Context Memory**: Remember conversation context across sessions

## Version History

### Version 5.3.1
- **State-Aware Speech Recognition**: Speech recognition only starts when bot is running
- **Conditional Processing**: Speech input only processed when cognitive systems are active
- **Improved Status Indicators**: Clear visual feedback for speech recognition states
- **Enhanced User Control**: Better control over when CARL listens for input

### Version 5.3.0
- **Initial Implementation**: Basic speech recognition integration
- **EZ-Robot Connection**: Automatic connection and initialization
- **GUI Integration**: Status display and connection management
- **Cognitive Integration**: Speech input processing through cognitive pipeline

---

For technical support or questions about the speech recognition feature, please refer to the main CARL documentation or contact the development team. 