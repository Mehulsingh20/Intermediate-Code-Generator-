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
    
    const clearBtn = document.getElementById("clearBtn");
    if (clearBtn) {
        clearBtn.addEventListener("click", clearCode);
    }
    
    // Set up optimization checkbox controls
    setupOptimizationControls();
});

function setupOptimizationControls() {
    // Main optimization checkbox
    const mainOptCheckbox = document.getElementById("optimizeCheckbox");
    const techniqueCheckboxes = [
        document.getElementById("constFoldingCheck"),
        document.getElementById("constPropCheck"), 
        document.getElementById("deadCodeCheck"),
        document.getElementById("combineAssgCheck")
    ];
    
    // When main checkbox changes, update all technique checkboxes
    if (mainOptCheckbox) {
        mainOptCheckbox.addEventListener("change", function() {
            const isChecked = mainOptCheckbox.checked;
            techniqueCheckboxes.forEach(checkbox => {
                if (checkbox) {
                    checkbox.checked = isChecked;
                    checkbox.disabled = !isChecked;
                }
            });
        });
    }
}

function clearCode() {
    if (editor) {
        editor.setValue("");
    }
    resetOutputs();
}

function resetOutputs() {
    document.getElementById("intermediateOutput").innerText = "Generate intermediate code to see results...";
    document.getElementById("optimizedOutput").innerText = "Generate optimized code to see results...";
    document.getElementById("linesBefore").innerText = "-";
    document.getElementById("linesAfter").innerText = "-";
    document.getElementById("opsRemoved").innerText = "-";
    document.getElementById("sizeReduction").innerText = "-";
    document.getElementById("optimizationsList").innerHTML = "<li class='list-group-item'>Run code generation first to see details</li>";
}

async function generateIntermediateCode() {
    if (!editor) return;
    
    const pythonCode = editor.getValue();
    const optimize = document.getElementById("optimizeCheckbox").checked;
    
    // Get optimization settings
    const optimizationSettings = {
        constantFolding: document.getElementById("constFoldingCheck")?.checked ?? true,
        constantPropagation: document.getElementById("constPropCheck")?.checked ?? true,
        deadCodeElimination: document.getElementById("deadCodeCheck")?.checked ?? true,
        combineAssignments: document.getElementById("combineAssgCheck")?.checked ?? true
    };
    
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
                optimize: optimize,
                optimizationSettings: optimizationSettings
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
            
            // Calculate and display optimization statistics
            displayOptimizationStats(data.intermediate_code, data.optimized_code, data.optimizations_applied || []);
        } else {
            document.getElementById("optimizedOutput").innerText = 
                "Optimization not applied";
            resetOptimizationStats();
        }
        
        // Show the optimized code tab
        const optimizedTab = document.getElementById("optimized-tab");
        if (optimizedTab) {
            optimizedTab.click();
        }
        
    } catch (error) {
        console.error("Error:", error);
        document.getElementById("intermediateOutput").innerText = 
            "Error: " + error.message;
        document.getElementById("optimizedOutput").innerText = 
            "Error: " + error.message;
    }
}

function displayOptimizationStats(originalCode, optimizedCode, optimizationsApplied) {
    if (!originalCode || !optimizedCode) return;
    
    const linesBefore = originalCode.length;
    const linesAfter = optimizedCode.length;
    const opsRemoved = Math.max(0, linesBefore - linesAfter);
    const reductionPercent = linesBefore > 0 ? Math.round((opsRemoved / linesBefore) * 100) : 0;
    
    // Update statistics
    document.getElementById("linesBefore").innerText = linesBefore;
    document.getElementById("linesAfter").innerText = linesAfter;
    document.getElementById("opsRemoved").innerText = opsRemoved;
    document.getElementById("sizeReduction").innerText = `${reductionPercent}%`;
    
    // Clear and update optimizations list
    const optimizationsListElement = document.getElementById("optimizationsList");
    optimizationsListElement.innerHTML = "";
    
    // If server didn't provide optimizations applied, generate generic ones
    if (!optimizationsApplied || optimizationsApplied.length === 0) {
        const constFolding = document.getElementById("constFoldingCheck")?.checked;
        const constProp = document.getElementById("constPropCheck")?.checked;
        const deadCode = document.getElementById("deadCodeCheck")?.checked;
        const combineAssign = document.getElementById("combineAssgCheck")?.checked;
        
        if (constFolding) {
            optimizationsListElement.innerHTML += `<li class="list-group-item text-success">Constant folding applied</li>`;
        }
        if (constProp) {
            optimizationsListElement.innerHTML += `<li class="list-group-item text-success">Constant propagation applied</li>`;
        }
        if (deadCode) {
            optimizationsListElement.innerHTML += `<li class="list-group-item text-success">Dead code elimination applied</li>`;
        }
        if (combineAssign) {
            optimizationsListElement.innerHTML += `<li class="list-group-item text-success">Assignment combinations applied</li>`;
        }
    } else {
        // Display server-provided optimizations
        optimizationsApplied.forEach(opt => {
            optimizationsListElement.innerHTML += `<li class="list-group-item text-success">${opt}</li>`;
        });
    }
    
    if (optimizationsListElement.innerHTML === "") {
        optimizationsListElement.innerHTML = `<li class="list-group-item">No optimizations applied</li>`;
    }
}

function resetOptimizationStats() {
    document.getElementById("linesBefore").innerText = "-";
    document.getElementById("linesAfter").innerText = "-";
    document.getElementById("opsRemoved").innerText = "-";
    document.getElementById("sizeReduction").innerText = "-";
    document.getElementById("optimizationsList").innerHTML = "<li class='list-group-item'>Optimization not enabled</li>";
} 