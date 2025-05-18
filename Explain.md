# Python Intermediate Code Generator - How It Works

This document explains the inner workings of the Python Intermediate Code Generator project. The project transforms Python code into an intermediate representation that resembles three-address code, a common intermediate representation used in compilers.

## Overview

The code generator follows these main steps:

1. **Parsing**: Converting Python code into an Abstract Syntax Tree (AST)
2. **Generation**: Transforming the AST into intermediate code
3. **Optimization**: Applying optimizations to the generated code
4. **Display**: Presenting the results to the user through a web interface

## 1. Parsing Phase - `parser.py`

The parsing phase uses Python's built-in `ast` module to convert Python source code into an Abstract Syntax Tree (AST). 

```python
import ast
tree = ast.parse(source_code)
```

The AST represents the syntactic structure of the code as a tree, where:
- Nodes represent language constructs (assignments, expressions, loops, etc.)
- Edges represent relationships between these constructs

The `IntermediateCodeGenerator` class traverses this AST to generate intermediate code:

- **Node Processing**: Each type of AST node (Assign, If, While, etc.) is processed with a specific method.
- **Expression Handling**: Expressions are broken down into simpler operations.
- **Control Flow**: Control structures use labels and goto statements.
- **Temporary Variables**: Complex expressions are split into smaller parts using temporary variables (t0, t1, etc.).

## 2. Generation Phase - Core Components

### 2.1 Handling Assignments

When an assignment like `x = a + b * c` is encountered, it's broken down:

```
t0 = b * c
t1 = a + t0
x = t1
```

The method `_process_assignment` handles this transformation.

### 2.2 Control Flow Structures

Control flow statements are transformed into conditional jumps and labels:

#### If Statements

```python
if condition:
    body
else:
    else_body
```

Becomes:

```
if condition == False goto L0
[body instructions]
goto L1
L0:
[else_body instructions]
L1:
```

#### While Loops

```python
while condition:
    body
```

Becomes:

```
L0:
if condition == False goto L1
[body instructions]
goto L0
L1:
```

### 2.3 Function Handling

Functions are translated with explicit parameter listings and return statements:

```python
def func(a, b):
    return a + b
```

Becomes:

```
function func:
  params: a, b
  t0 = a + b
  return t0
end function
```

## 3. Optimization Phase - `optimizer.py`

The optimizer applies several techniques to improve the intermediate code:

### 3.1 Constant Folding

This evaluates constant expressions at compile time:

```
t0 = 2 + 3
x = t0
```

Becomes:

```
t0 = 5
x = t0
```

### 3.2 Constant Propagation

This replaces variables with their known constant values:

```
x = 5
y = x + 2
```

Becomes:

```
x = 5
y = 5 + 2
```

Which may then be further optimized by constant folding.

### 3.3 Dead Code Elimination

This removes assignments to variables that are never used:

```
x = a + b
y = c + d
z = x + 2  # Only x is used
```

Becomes:

```
x = a + b
z = x + 2
```

### 3.4 Consecutive Assignment Combination

This combines consecutive assignments that can be merged:

```
t0 = a + b
x = t0 * 2
```

Becomes:

```
x = (a + b) * 2
```

## 4. Web Interface - `app.py` and Templates

The web interface is built using Flask and provides:

1. A code editor for entering Python code (using CodeMirror)
2. Options to enable/disable optimization
3. Display of generated intermediate code
4. Display of optimized code (when enabled)

## 5. Project Structure

- `src/parser.py`: Handles parsing and generating intermediate code
- `src/optimizer.py`: Implements optimization techniques
- `src/app.py`: Flask web application
- `src/templates/`: HTML templates for the web interface
- `src/static/`: Static assets (CSS, JavaScript)
- `main.py`: Entry point to run the application
- `requirements.txt`: Project dependencies

## 6. Limitations and Future Improvements

- **Limited Language Support**: Currently handles basic Python constructs but not more advanced features.
- **Optimization Scope**: More advanced optimizations could be implemented.
- **Code Analysis**: Better analysis of code could provide more insights.
- **Code Visualization**: Showing the AST or control flow graph could be helpful.
- **User Experience**: The UI could be enhanced with more features.

## 7. Technical Details

### Temporary Variable Generation

Temporary variables (t0, t1, etc.) are created to hold intermediate results:

```python
def get_temp(self):
    """Generate a new temporary variable name"""
    temp = f"t{self.temp_counter}"
    self.temp_counter += 1
    return temp
```

### Label Generation

Labels (L0, L1, etc.) are used for control flow:

```python
def get_label(self):
    """Generate a new label"""
    label = f"L{self.label_counter}"
    self.label_counter += 1
    return label
```

## 8. Running the Project

1. Install the dependencies with `pip install -r requirements.txt`
2. Run the application with `python main.py`
3. Open a web browser and navigate to `http://127.0.0.1:5000`
4. Enter Python code in the editor and click "Generate Intermediate Code"

The project provides a practical demonstration of compiler techniques and how high-level code is transformed into lower-level representations. 