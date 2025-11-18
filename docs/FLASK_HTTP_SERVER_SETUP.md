# CARL Flask HTTP Server Setup Guide

## Overview

CARL now includes a Flask HTTP server that receives speech data from ARC via HTTP POST requests. This implements a proper client/server model where ARC pushes speech data to CARL instead of CARL polling ARC.

## Architecture

- **ARC (Client)**: Captures speech and sends it via HTTP POST to CARL
  - ARC HTTP server runs on IP: 192.168.56.1
  - ARC sends POST requests to CARL's Flask server
- **CARL (Server)**: Runs Flask HTTP server to receive speech data
  - Flask server listens on all interfaces (0.0.0.0)
  - Accepts connections from ARC and other clients
- **Communication**: HTTP POST requests from ARC to CARL
- **Network**: Both ARC and CARL typically run on the same machine (localhost)

## Setup Instructions

### 1. Install Dependencies

Install Flask and other required packages:

```bash
pip install -r requirements.txt
```

### 2. Start CARL

1. Run CARL application
2. Click "Run Bot" to start the Flask HTTP server
3. The server will start on port 5000 (or next available port)
4. Check the status in the EZ-Robot Status panel

### 3. Get Server Information

1. Click "Flask Server Info" button in CARL
2. Note the server URL and endpoints
3. Use this information to configure ARC

### 4. Configure ARC

#### Option A: Use the provided script template

1. Copy the content from `ARC_HTTP_POST_SCRIPT.js`
2. Create a new script in ARC's Script Collection
3. Name it `pushBingSpeech`
4. The script is configured to use `http://localhost:5000/speech` (default)
5. If CARL is on a different machine, update the URL to use the network IP

**Network Configuration:**
- **Same Machine**: Use `http://localhost:5000/speech` (recommended)
- **Different Machine**: Use `http://<CARL_IP>:5000/speech`
- **ARC Server IP**: 192.168.56.1 (for reference)

#### Option B: Create custom script

```javascript
// Custom ARC script for sending speech to CARL
var capturedText = getVar("$BingSpeech", "");

if (capturedText && capturedText !== "OK") {
    // Use localhost if CARL is on the same machine
    var url = "http://localhost:5000/speech";
    
    // Alternative: Use network IP if CARL is on different machine
    // var url = "http://192.168.1.100:5000/speech";  // Replace with CARL's IP
    
    var postData = "speech=" + encodeURIComponent(capturedText);
    var response = Net.hTTPPost(url, postData, 5000);
    print("CARL response: " + response);
}
```

### 5. Integrate with Bing Speech Recognition

1. In your Bing Speech Recognition response script, call the `pushBingSpeech` script
2. This will automatically send captured speech to CARL

Example integration:
```javascript
// In Bing Speech Recognition response script
if (getVar("$BingSpeech", "") !== "") {
    // Call the script that sends data to CARL
    ScriptStart("pushBingSpeech");
}
```

## API Endpoints

### POST /speech
Receives speech data from ARC

**Request:**
- Content-Type: `application/x-www-form-urlencoded`
- Body: `speech=<encoded_speech_text>`

**Response:**
```json
{
    "status": "success",
    "message": "Received: <speech_text>"
}
```

### GET /health
Health check endpoint

**Response:**
```json
{
    "status": "healthy",
    "bot_running": true,
    "speech_active": true,
    "timestamp": "2024-01-01T12:00:00"
}
```

### GET /status
Detailed system status

**Response:**
```json
{
    "status": "running",
    "bot_running": true,
    "speech_active": true,
    "ez_robot_connected": true,
    "total_memories": 42,
    "server_port": 5000,
    "server_host": "0.0.0.0",
    "timestamp": "2024-01-01T12:00:00"
}
```

## Testing

### 1. Test Server Health
```bash
curl http://localhost:5000/health
```

### 2. Test Speech Endpoint
```bash
curl -X POST http://localhost:5000/speech \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "speech=Hello%20CARL"
```

### 3. Test from ARC
1. Ensure CARL is running and Flask server is active
2. Trigger speech recognition in ARC
3. Check CARL logs for received speech data

## Troubleshooting

### Port Already in Use
- CARL will automatically try ports 5000-5009
- Check the status label for the actual port being used
- Update ARC script URL accordingly

### Network Connectivity Issues
- **ARC Server IP**: 192.168.56.1 (ARC's HTTP server)
- **CARL Flask Server**: Listens on 0.0.0.0 (all interfaces)
- **Same Machine**: Use `localhost` or `127.0.0.1`
- **Different Machine**: Use CARL's network IP address
- Check firewall settings if using network IP

### Connection Refused
- Ensure CARL is running and Flask server is active
- Check firewall settings
- Verify the correct port is being used
- **ARC Connectivity**: CARL will test connectivity to ARC (192.168.56.1) on startup
- **Network Access**: Use "Flask Server Info" button to get network URLs

### No Speech Received
- Check ARC script is calling the HTTP POST correctly
- Verify the `$BingSpeech` variable contains data
- Check CARL logs for any error messages

### Flask Server Not Starting
- Check if Flask is installed: `pip install Flask`
- Check for port conflicts
- Review CARL logs for error messages

## Benefits

1. **Real-time Communication**: Speech data is pushed immediately to CARL
2. **Reduced Latency**: No polling delays
3. **Better Reliability**: Direct HTTP communication
4. **Scalable**: Can handle multiple speech inputs efficiently
5. **Debugging**: Clear request/response logging

## Security Considerations

- The server runs on localhost by default
- For network access, update the host to `0.0.0.0`
- Consider adding authentication for production use
- Monitor logs for unusual activity

## Advanced Configuration

### Custom Port
Modify the `speech_server_port` variable in CARL's initialization.

### Network Access
Change `speech_server_host` from `'0.0.0.0'` to your network interface IP.

### JSON Format
Uncomment the JSON format section in the ARC script for structured data.

## Support

For issues or questions:
1. Check CARL logs for error messages
2. Verify ARC script syntax
3. Test endpoints manually with curl
4. Review this documentation 