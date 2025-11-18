// ARC Vision HTTP POST Script for CARL Object Detection
// This script sends captured vision data to CARL's Flask HTTP server
// Sends object name, color, and shape from ARC vision detection

// Retrieve the captured vision variables from ARC vision detection
var capturedObjectName = getVar("$CameraObjectName", "");
var capturedObjectColor = getVar("$CameraObjectColor", "");
var capturedObjectShape = getVar("$CameraObjectShape", "");

// If there is no captured object name, exit (primary detection required)
if (capturedObjectName === "" || capturedObjectName === "No object detected") {
  print("No captured object name to push.");
  return;
}

// Define the URL of your CARL Python agent's HTTP server endpoint
// CARL runs on the same machine as ARC, so use localhost
// If CARL is on a different machine, replace with the actual IP address
var url = "http://localhost:5000/vision";

// Alternative: If CARL is on a different machine, use the network IP
// var url = "http://192.168.1.100:5000/vision";  // Replace with CARL's actual IP

// Prepare post data with all three vision variables
var postData = "object_name=" + encodeURIComponent(capturedObjectName) + 
               "&object_color=" + encodeURIComponent(capturedObjectColor) + 
               "&object_shape=" + encodeURIComponent(capturedObjectShape);

// Set timeout (in milliseconds)
var timeout = 5000; // 5 seconds

// Send an HTTP POST from ARC to CARL
print("Sending vision data to CARL:");
print("  Object Name: " + capturedObjectName);
print("  Object Color: " + capturedObjectColor);
print("  Object Shape: " + capturedObjectShape);

var response = Net.hTTPPost(url, postData, timeout);

// Log the response received from CARL
print("Response from CARL: " + response);

// Optional: Clear the captured vision variables once they have been sent
// setVar("$CameraObjectName", "");
// setVar("$CameraObjectColor", "");
// setVar("$CameraObjectShape", "");

// Alternative JSON format (uncomment if needed):
// var jsonData = '{"object_name": "' + capturedObjectName.replace(/"/g, '\\"') + 
//                '", "object_color": "' + capturedObjectColor.replace(/"/g, '\\"') + 
//                '", "object_shape": "' + capturedObjectShape.replace(/"/g, '\\"') + '"}';
// var response = Net.hTTPPost(url, jsonData, timeout, ["Content-Type"], ["application/json"]);
