# ARC Variable Access Guide for Speech Recognition

## Problem
The current implementation tries to use `getVar()` and `setVar()` functions directly through the EZ-Robot API, but ARC doesn't recognize these functions. We need to implement a proper way to access the `$BingSpeech` variable.

## Current Issue
```
Error: Unknown function: getVar.
```

## Solutions

### Option 1: ARC Script-Based Variable Access
Create a script in ARC that can access and return variable values:

1. **Create an ARC Script**:
   ```javascript
   // Script: GetBingSpeech.js
   function getBingSpeech() {
       var speechText = getVar("$BingSpeech", "");
       print("BingSpeech: " + speechText);
       return speechText;
   }
   
   // Call the function
   getBingSpeech();
   ```

2. **Execute Script via API**:
   ```python
   def get_speech_variable(self) -> str:
       script_url = f'{self.base_url}%22Script%20Collection%22,%22ScriptStart%22,%22GetBingSpeech%22)'
       response = requests.get(script_url, timeout=2)
       # Parse response to extract the printed value
       return self._parse_script_output(response.text)
   ```

### Option 2: HTTP Response Parsing
Some ARC installations return variable values in HTTP responses:

```python
def get_speech_variable(self) -> str:
    # Try different API endpoints
    endpoints = [
        f'{self.base_url}%22Variables%22,%22Get%22,%22{self.bing_speech_variable}%22)',
        f'{self.base_url}%22System%22,%22GetVariable%22,%22{self.bing_speech_variable}%22)',
        f'{self.base_url}%22Global%20Variables%22,%22Get%22,%22{self.bing_speech_variable}%22)'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=2)
            if response.status_code == 200:
                # Parse response for variable value
                return self._extract_variable_from_response(response.text)
        except Exception as e:
            continue
    
    return ""
```

### Option 3: WebSocket or TCP Connection
ARC might support WebSocket or TCP connections for real-time variable access:

```python
import websocket
import json

def connect_websocket(self):
    ws = websocket.create_connection("ws://192.168.56.1:8080")
    ws.send(json.dumps({"command": "getVariable", "name": "$BingSpeech"}))
    response = ws.recv()
    return json.loads(response)["value"]
```

### Option 4: File-Based Variable Access
ARC might store variables in files that can be accessed:

```python
def get_speech_from_file(self) -> str:
    try:
        # Check if ARC stores variables in a file
        file_path = "/path/to/arc/variables.json"  # Adjust path
        with open(file_path, 'r') as f:
            variables = json.load(f)
            return variables.get("$BingSpeech", "")
    except Exception as e:
        return ""
```

## Recommended Implementation

### Step 1: Test ARC API Endpoints
First, test what endpoints are available in your ARC installation:

```python
def test_arc_endpoints(self):
    """Test various ARC API endpoints to find variable access."""
    test_endpoints = [
        "Variables",
        "Global Variables", 
        "System",
        "Script Collection",
        "Bing Speech Recognition"
    ]
    
    for endpoint in test_endpoints:
        try:
            url = f'{self.base_url}%22{endpoint}%22,%22Get%22,%22test%22)'
            response = requests.get(url, timeout=2)
            print(f"Endpoint {endpoint}: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            print(f"Endpoint {endpoint}: Error - {e}")
```

### Step 2: Create ARC Script
Create a script in ARC that can access the variable and return it:

```javascript
// ARC Script: SpeechAccess.js
function getSpeechVariable() {
    var speech = getVar("$BingSpeech", "");
    if (speech && speech !== "") {
        print("SPEECH_DETECTED:" + speech);
        setVar("$BingSpeech", ""); // Clear after reading
    }
}

// Run continuously
while (true) {
    getSpeechVariable();
    sleep(1000);
}
```

### Step 3: Implement Response Parsing
Parse the script output to extract speech:

```python
def _parse_script_output(self, output: str) -> str:
    """Parse script output for speech detection."""
    lines = output.split('\n')
    for line in lines:
        if line.startswith("SPEECH_DETECTED:"):
            return line.replace("SPEECH_DETECTED:", "").strip()
    return ""
```

## Testing the Implementation

### Test Script
```python
def test_variable_access():
    robot = EZRobot()
    
    # Test different approaches
    print("Testing ARC endpoints...")
    robot.test_arc_endpoints()
    
    # Test script execution
    print("Testing script execution...")
    result = robot.execute_script("SpeechAccess")
    print(f"Script result: {result}")
```

## Alternative Approach: Direct Integration

If variable access is too complex, consider a direct integration approach:

1. **ARC Event System**: Configure ARC to send HTTP requests when speech is detected
2. **Webhook Integration**: Set up a webhook that ARC calls when `$BingSpeech` changes
3. **Shared Database**: Use a shared database or file that both ARC and CARL can access

## Current Workaround

For now, the implementation uses a simulation approach that doesn't actually capture speech. To enable real speech recognition:

1. **Install the proper ARC script** for variable access
2. **Test the available API endpoints** in your ARC installation
3. **Implement the appropriate variable access method** based on your findings
4. **Replace the simulation method** with real variable access

## Next Steps

1. **Research your specific ARC version** and its API capabilities
2. **Test the suggested endpoints** to find which ones work
3. **Create the necessary ARC scripts** for variable access
4. **Implement the working solution** in the EZ-Robot module
5. **Test thoroughly** with real speech input

The current error occurs because we're trying to use functions that don't exist in the ARC API. The solution requires understanding your specific ARC installation and implementing the appropriate variable access method. 