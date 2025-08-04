/ index.js
const express = require('express');
const app = express();
const port = 3000;

// This function performs a recursive factorial calculation, which is a CPU-intensive task.
function factorial(n) {
  if (n === 0) {
    return 1;
  }
  return n * factorial(n - 1);
}

// Global variable to hold the large data set for the memory leak simulation
let memoryHog = null;

// Endpoint for CPU-intensive task
app.get('/cpu-intensive', (req, res) => {
  console.log('Received a request for CPU-intensive task');
  
  // Perform a factorial calculation for a large number to simulate high CPU usage.
  // The size of the number determines the intensity.
  const number = 10000;
  const result = factorial(number);

  res.json({
    message: `CPU-intensive task completed. Factorial of ${number} is too large to display.`,
    result: 'Calculation done.',
  });
});

// Endpoint for memory-intensive task (simulated leak)
app.get('/memory-intensive', (req, res) => {
  console.log('Received a request for memory-intensive task');

  // Create a large array to consume a lot of memory.
  // We're creating an array of 50 million objects.
  const arraySize = 50 * 1000 * 1000; 
  
  // This will create a large data structure in the heap.
  memoryHog = new Array(arraySize).fill({
    data: 'This is a piece of data to fill up memory.',
  });
  
  // This is a common pattern that can lead to memory leaks if not handled
  // correctly, as the 'memoryHog' is a global variable that won't be garbage collected.

  res.json({
    message: `Memory-intensive task completed. ${arraySize} objects created in memory.`,
    size: memoryHog.length,
  });
});

// Endpoint to free the memory-intensive variable
app.get('/free-memory', (req, res) => {
  console.log('Received a request to free memory.');
  
  // Set the variable to null to allow garbage collection.
  memoryHog = null;
  // Trigger a manual garbage collection if the flag is enabled.
  if (global.gc) {
    global.gc();
  }

  res.json({
    message: 'Memory hog variable has been freed.',
  });
});

app.listen(port, () => {
  console.log(`Stress test app listening at http://localhost:${port}`);
});
```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: "stress-test-app", // A name for your PM2 process
    script: "./index.js",   // The main script to run
    instances: "max",        // Run on all available CPU cores
    exec_mode: "cluster",    // Use cluster mode for load balancing
    // Automatically restart the app if it exceeds 300MB of memory
    max_memory_restart: "300M", 
  }]
};
