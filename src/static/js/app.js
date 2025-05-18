// Initialize CodeMirror
let editor = null;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize CodeMirror editor
    const pythonCodeElement = document.getElementById("pythonCode");
    if (pythonCodeElement) {
        editor = CodeMirror.fromTextArea(pythonCodeElement, {
            mode: "python",
            theme: "monokai",
            lineNumbers: true,
            indentUnit: 4,
            lineWrapping: true
        });
    }
    
    // Set up event listeners
    const generateBtn = document.getElementById("generateBtn");
    if (generateBtn) {
        generateBtn.addEventListener("click", generateIntermediateCode);
    }
});

async function generateIntermediateCode() {
    if (!editor) return;
    
    const pythonCode = editor.getValue();
    const optimize = document.getElementById("optimizeCheckbox").checked;
    
    try {
        // Update UI to show loading state
        document.getElementById("intermediateOutput").innerText = "Generating...";
        document.getElementById("optimizedOutput").innerText = "Generating...";
        
        // Send the code to the server
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: pythonCode,
                optimize: optimize
            })
        });
        
        // Process the response
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Display the results
        if (data.intermediate_code) {
            document.getElementById("intermediateOutput").innerText = 
                data.intermediate_code.join('\n');
        }
        
        if (data.optimized_code) {
            document.getElementById("optimizedOutput").innerText = 
                data.optimized_code.join('\n');
        } else {
            document.getElementById("optimizedOutput").innerText = 
                "Optimization not applied";
        }
        
        // Show the intermediate code tab
        const intermediateTab = document.getElementById("intermediate-tab");
        if (intermediateTab) {
            intermediateTab.click();
        }
        
    } catch (error) {
        console.error("Error:", error);
        document.getElementById("intermediateOutput").innerText = 
            "Error: " + error.message;
    }
} 