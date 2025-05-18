# Python Intermediate Code Generator

A tool that generates intermediate code from Python source code, optimizes it, and displays the results through a web interface.

## Features

1. **Intermediate Code Generation**: Convert Python code to a three-address code-like intermediate representation
2. **Code Optimization**: Apply optimization techniques like constant folding, constant propagation, and dead code elimination
3. **Web Interface**: User-friendly frontend for inputting Python code and viewing results
4. **Detailed Explanation**: Documentation on the inner workings of the code generator

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/Intermediate-Code-Generator.git
cd Intermediate-Code-Generator
```

2. Create a virtual environment (optional but recommended):
```
python -m venv venv
```

3. Activate the virtual environment:
   - On Windows:
   ```
   venv\Scripts\activate
   ```
   - On macOS/Linux:
   ```
   source venv/bin/activate
   ```

4. Install dependencies:
```
pip install -r requirements.txt
```

## Usage

1. Run the application:
```
python main.py
```

2. Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

3. Enter Python code in the editor, select whether to apply optimization, and click "Generate Intermediate Code"

4. View the generated intermediate code and optimized code (if enabled)

## Project Structure

- `src/parser.py`: Parses Python code and generates intermediate code
- `src/optimizer.py`: Optimizes the generated intermediate code
- `src/app.py`: Flask web application
- `src/templates/`: HTML templates
- `src/static/`: Static assets (CSS, JavaScript)
- `main.py`: Application entry point
- `Explain.md`: Detailed explanation of how the code generator works
- `requirements.txt`: Project dependencies

## How It Works

1. **Parsing**: The Python code is parsed using the `ast` module to create an Abstract Syntax Tree (AST)
2. **Code Generation**: The AST is traversed to generate intermediate code
3. **Optimization**: The intermediate code is optimized using various techniques
4. **Display**: The results are displayed to the user through the web interface

For a detailed explanation of the inner workings, see [Explain.md](Explain.md).

## Examples

### Input (Python):
```python
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n-1)

result = factorial(5)
print("Factorial of 5 is:", result)
```

### Output (Intermediate Code):
```
function factorial:
  params: n
  t0 = n <= 1
  if t0 == False goto L0
  return 1
  goto L1
L0:
  t1 = n - 1
  t2 = call factorial(t1)
  t3 = n * t2
  return t3
L1:
end function
t4 = call factorial(5)
result = t4
t5 = call print("Factorial of 5 is:", result)
```

## License

MIT
