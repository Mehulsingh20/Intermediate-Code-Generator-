from flask import Flask, render_template, request, jsonify
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parser import generate_intermediate_code
from src.optimizer import optimize_intermediate_code

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
        optimized_code = optimize_intermediate_code(intermediate_code)
        return jsonify({
            'intermediate_code': intermediate_code,
            'optimized_code': optimized_code
        })
    
    return jsonify({
        'intermediate_code': intermediate_code
    })

if __name__ == '__main__':
    app.run(debug=True) 