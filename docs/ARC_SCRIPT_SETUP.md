# ARC Script Setup Guide

## Problem Identified
The test results show that the `getBingSpeech` script doesn't exist in ARC, which is why you're getting the error:
```
Error: ControlCommand Error for 'Script Collection' sending 'ScriptStart'. Unknown script: getBingSpeech
```

## Solution: Create Required Scripts in ARC

### Step 1: Open ARC Script Collection
1. Open ARC (EZ-Robot software)
2. Go to the "Script Collection" window
3. Click "New Script" or the "+" button to create a new script

### Step 2: Create getBingSpeech Script
1. Name the script: `getBingSpeech`
2. Copy and paste this code:

```javascript
// Script: getBingSpeech
// Purpose: Get the value of $BingSpeech variable
// Usage: Called by Python to retrieve captured speech

var speechText = getVar("$BingSpeech");
if (speechText != null && speechText != "") {
    return speechText;
} else {
    return "";
}
```

3. Save the script

### Step 3: Create clearBingSpeech Script (DISABLED)
**Note**: This step has been disabled. The clearBingSpeech functionality is no longer used.

~~1. Create another new script~~
~~2. Name the script: `clearBingSpeech`~~
~~3. Copy and paste this code:~~

```javascript
// Script: clearBingSpeech (DISABLED)
// Purpose: Clear the $BingSpeech variable
// Usage: Called by Python to clear speech after processing (DISABLED)

setVar("$BingSpeech", "");
return "cleared";
```

~~4. Save the script~~

### Step 4: Test the Scripts
1. In ARC, go to the "Script Collection" window
2. Find the `getBingSpeech` script
3. Click "Run" to test it
4. It should return the current value of `$BingSpeech` (or empty string if no speech)

### Step 5: Verify Bing Speech Recognition
1. Go to the "Bing Speech Recognition" window in ARC
2. Make sure it's configured with your API key
3. Test that speech recognition works within ARC
4. Verify that the `$BingSpeech` variable is being populated when you speak

## Testing After Setup

### Run the Test Script
```bash
python test_speech_variable_access.py
```

You should now see:
- `getBingSpeech` script returns actual speech text (or empty string)
- No more "Unknown script" errors

### Test in CARL
1. Start CARL
2. Click "Connect EZ-Robot"
3. Click "Run Bot"
4. Speak to JD
5. Check that speech appears in CARL's input field

## Expected Results

### Before Script Creation
```
1. Testing Script Collection method:
   Status: 200
   Response: Error: ControlCommand Error for 'Script Collection' sending 'ScriptStart'. Unknown script: getBingSpeech
```

### After Script Creation
```
1. Testing Script Collection method:
   Status: 200
   Response: [actual speech text or empty string]
```

## Troubleshooting

### Script Not Found
- Make sure the script name is exactly `getBingSpeech` (case sensitive)
- Check that the script is saved in the Script Collection
- Try running the script manually in ARC first

### Script Returns Error
- Check the script syntax in ARC
- Make sure `getVar()` and `setVar()` functions are available
- Verify that `$BingSpeech` variable exists

### No Speech Captured
- Check Bing Speech Recognition configuration
- Test speech recognition directly in ARC
- Verify microphone permissions

## Alternative Approach

If you can't create scripts in ARC, you can also:

1. **Use ARC's built-in variable access** (if available)
2. **Check ARC documentation** for the correct variable access method
3. **Contact EZ-Robot support** for guidance on variable access

## Next Steps

Once the scripts are created:
1. The speech recognition should work properly
2. CARL will be able to capture and process speech from JD
3. The error messages will stop appearing
4. Speech will flow through CARL's cognitive pipeline correctly 