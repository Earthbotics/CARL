// getBingSpeech script
// Retrieve the BingSpeech text from the global variable.
var bingText = getVar("$BingSpeech", "");

// Log the retrieved text for debugging purposes.
print("Retrieved BingSpeech text: " + bingText);

// Optionally, you could send this text using HTTP response code.
// For example, if you're using an HTTP server skill with scripting,
// you might use the response text as a return value from this script.
return bingText;