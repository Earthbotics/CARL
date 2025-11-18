// ARC Vision HTTP POST Script for CARL Object Detection
// This script sends captured vision data to CARL's Flask HTTP server
// Sends object name and color from ARC vision detection (includes faces in object name)
// Modified to maintain a queue of last 7 detected items to avoid duplicates

// Clear variables before the loop to ensure clean state
var capturedObjectName = "";
var capturedObjectColor = "";
var lastSentObject = "";
var lastSentTime = 0;
var timeoutDuration = 30000; // 30 seconds in milliseconds

// Queue to store last 7 detected items (FIFO - First In, First Out)
var detectedItemsQueue = [];
var maxQueueSize = 7;

// Main detection loop
while (true) {
    // Retrieve the captured vision variables from ARC vision detection
    capturedObjectName = getVar("$CameraObjectName");
    capturedObjectColor = getVar("$CameraObjectColor");
    
    // If there is no captured object name, continue loop
    if (capturedObjectName === "" || capturedObjectName === "No object detected") {
        print("No captured object or face to process.");
        sleep(1000); // Wait 1 second before next check
        continue;
    }
    
    // Create a unique identifier for this detection (name + color)
    var detectionIdentifier = capturedObjectName + "|" + capturedObjectColor;
    
    // Check if this detection is already in our recent detection queue
    var isAlreadyDetected = false;
    for (var i = 0; i < detectedItemsQueue.length; i++) {
        if (detectedItemsQueue[i] === detectionIdentifier) {
            isAlreadyDetected = true;
            break;
        }
    }
    
    // If detection is already in queue, skip it
    if (isAlreadyDetected) {
        print("Detection '" + capturedObjectName + "' already detected recently, skipping...");
        sleep(1000); // Wait 1 second before next check
        continue;
    }
    
    // Check if this is a new detection or enough time has passed since last send
    var currentTime = Date.now();
    var isNewObject = (capturedObjectName !== lastSentObject);
    var hasTimedOut = (currentTime - lastSentTime) >= timeoutDuration;
    
    if (!isNewObject && !hasTimedOut) {
        print("Detection already sent recently, waiting...");
        sleep(1000); // Wait 1 second before next check
        continue;
    }
    
    // Add this detection to our detection queue
    detectedItemsQueue.push(detectionIdentifier);
    
    // Remove oldest item if queue exceeds maximum size
    if (detectedItemsQueue.length > maxQueueSize) {
        var removedItem = detectedItemsQueue.shift(); // Remove first (oldest) item
        print("Removed from queue: " + removedItem);
    }
    
    print("Current detection queue (" + detectedItemsQueue.length + "/" + maxQueueSize + "):");
    for (var i = 0; i < detectedItemsQueue.length; i++) {
        print("  " + (i+1) + ". " + detectedItemsQueue[i]);
    }
    
    // Define the URL of your CARL Python agent's HTTP server endpoint
    // CARL runs on the same machine as ARC, so use localhost
    // If CARL is on a different machine, replace with the actual IP address
    var url = "http://localhost:5000/vision";
    
    // Alternative: If CARL is on a different machine, use the network IP
    // var url = "http://192.168.1.100:5000/vision"; // Replace with CARL's actual IP
    
    // Prepare post data with object name and color (faces are included in object name)
    var postData = "object_name=" + encodeURIComponent(capturedObjectName) + 
                   "&object_color=" + encodeURIComponent(capturedObjectColor);
    
    // Set timeout for HTTP request (in milliseconds)
    var requestTimeout = 5000; // 5 seconds for the HTTP request itself
    
    // Send an HTTP POST from ARC to CARL
    print("Sending NEW vision data to CARL:");
    print(" Object/Face Name: " + capturedObjectName);
    print(" Object Color: " + capturedObjectColor);
    print(" Detection Identifier: " + detectionIdentifier);
    
    var response = Net.hTTPPost(url, postData, requestTimeout);
    
    // Log the response received from CARL
    print("Response from CARL: " + response);
    
    // Update tracking variables
    lastSentObject = capturedObjectName;
    lastSentTime = currentTime;
    
    // Clear the captured vision variables after successful send
    setVar("$CameraObjectName", "");
    setVar("$CameraObjectColor", "");
    
    // Wait 30 seconds before allowing next detection (as requested)
    print("Waiting 30 seconds before next detection...");
    sleep(30000); // 30 second timeout
    
    // Alternative JSON format (uncomment if needed):
    // var jsonData = '{"object_name": "' + capturedObjectName.replace(/"/g, '\\"') + 
    //                '", "object_color": "' + capturedObjectColor.replace(/"/g, '\\"') + '"}';
    // var response = Net.hTTPPost(url, jsonData, requestTimeout, ["Content-Type"], ["application/json"]);
}
