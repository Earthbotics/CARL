// Retrieve the captured speech text (ensure this variable is set by your response script)
var capturedText = getVar("$BingSpeech");

// If there is no captured text, exit (you might want to add error handling)
if (capturedText === "") {
  print("No captured speech text to push.");
  return;
}

// Define the URL of your Python agent's HTTP server endpoint.
// Replace <python-agent-host> and <port> with the correct address and port of your agent's HTTP server.
var url = "http://localhost:5000/speech";

// Prepare post data.
// Here we encode the variable into a POST parameter "speech".
// If needed, you can add more parameters.
var postData = "speech=" + encodeURIComponent(capturedText);

// Optionally, you can set a timeout (in milliseconds)
var timeout = 5000; // 5 seconds

// Send an HTTP POST from ARC to the Python agent.
var response = Net.hTTPPost(url, postData, timeout);

// Log the response received from the Python agent.
print("Response from agent: " + response);