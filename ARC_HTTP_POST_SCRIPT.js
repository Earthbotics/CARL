// ARC HTTP POST Script for CARL Speech Recognition
// This script sends captured speech data to CARL's Flask HTTP server
// Replace <python-agent-host> and <port> with your CARL server details

// pushBingSpeech.js
// Retrieve the captured speech text from Bing Speech Recognition
var capturedText = getVar("$BingSpeech", "");

// If there is no captured text, exit
if (capturedText === "" || capturedText === "OK") {
  print("No captured speech text to push.");
  return;
}

// Define the URL of your CARL Python agent's HTTP server endpoint
// CARL runs on the same machine as ARC, so use localhost
// If CARL is on a different machine, replace with the actual IP address
var url = "http://localhost:5000/speech";

// Alternative: If CARL is on a different machine, use the network IP
// var url = "http://192.168.1.100:5000/speech";  // Replace with CARL's actual IP

// Prepare post data with the captured speech
var postData = "speech=" + encodeURIComponent(capturedText);

// Set timeout (in milliseconds)
var timeout = 5000; // 5 seconds

// Send an HTTP POST from ARC to CARL
print("Sending speech to CARL: " + capturedText);
var response = Net.hTTPPost(url, postData, timeout);

// Log the response received from CARL
print("Response from CARL: " + response);

// Optional: Clear the captured text once it has been sent
// setVar("$BingSpeech", "");

// Alternative JSON format (uncomment if needed):
// var jsonData = '{"speech": "' + capturedText.replace(/"/g, '\\"') + '"}';
// var response = Net.hTTPPost(url, jsonData, timeout, ["Content-Type"], ["application/json"]); 