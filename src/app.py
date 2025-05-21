from flask import Flask, render_template, request, jsonify
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parser import generate_intermediate_code
from src.optimizer import optimize_intermediate_code, CodeOptimizer

app = Flask(__name__)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Generate intermediate code from the submitted Python code"""
    data = request.get_json()
    python_code = data.get('code', '')
    
    # Generate intermediate code
    intermediate_code = generate_intermediate_code(python_code)
    
    # Optimize the code if requested
    optimize = data.get('optimize', False)
    if optimize:
        # Get optimization settings
        opt_settings = data.get('optimizationSettings', {})
        
        # Create a CustomOptimizer with specific settings
        optimizer = CodeOptimizer()
        
        # Track which optimizations were applied
        optimizations_applied = []
        
        # Create a copy of the intermediate code
        optimized_code = intermediate_code.copy()
        
        # Apply selected optimizations
        if opt_settings.get('constantFolding', True):
            optimized_code = optimizer.optimize_with_technique(optimized_code, 'constant_folding')
            optimizations_applied.append("Constant Folding")
            
        if opt_settings.get('constantPropagation', True):
            optimized_code = optimizer.optimize_with_technique(optimized_code, 'constant_propagation')
            optimizations_applied.append("Constant Propagation")
            
        if opt_settings.get('deadCodeElimination', True):
            optimized_code = optimizer.optimize_with_technique(optimized_code, 'dead_code_elimination')
            optimizations_applied.append("Dead Code Elimination")
            
        if opt_settings.get('combineAssignments', True):
            optimized_code = optimizer.optimize_with_technique(optimized_code, 'combine_assignments')
            optimizations_applied.append("Assignment Combinations")

        # Calculate optimization stats
        optimization_stats = calculate_optimization_stats(intermediate_code, optimized_code)
        
        return jsonify({
            'intermediate_code': intermediate_code,
            'optimized_code': optimized_code,
            'optimizations_applied': optimizations_applied,
            'optimization_stats': optimization_stats
        })
    
    return jsonify({
        'intermediate_code': intermediate_code
    })

def calculate_optimization_stats(original_code, optimized_code):
    """Calculate statistics about the optimizations applied"""
    if not original_code or not optimized_code:
        return {}
        
    original_len = len(original_code)
    optimized_len = len(optimized_code)
    
    return {
        'lines_before': original_len,
        'lines_after': optimized_len,
        'lines_removed': max(0, original_len - optimized_len),
        'reduction_percentage': round((max(0, original_len - optimized_len) / original_len) * 100) if original_len > 0 else 0
    }

if __name__ == '__main__':
    app.run(debug=True) 