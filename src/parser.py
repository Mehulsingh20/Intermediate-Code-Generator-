import ast
import symtable

class IntermediateCodeGenerator:
    def __init__(self):
        self.code = []
        self.temp_counter = 0
        self.label_counter = 0
    
    def reset(self):
        self.code = []
        self.temp_counter = 0
        self.label_counter = 0

    def get_temp(self):
        """Generate a new temporary variable name"""
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp
    
    def get_label(self):
        """Generate a new label"""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
    
    def generate(self, source_code):
        """Generate intermediate code from Python source code"""
        self.reset()
        try:
            tree = ast.parse(source_code)
            self._process_module(tree)
            return self.code
        except SyntaxError as e:
            return [f"Error: {e}"]
    
    def _process_module(self, node):
        """Process a module node"""
        for statement in node.body:
            self._process_node(statement)
    
    def _process_node(self, node):
        """Process an AST node and generate intermediate code"""
        if isinstance(node, ast.Assign):
            self._process_assignment(node)
        elif isinstance(node, ast.Expr):
            self._process_expression(node.value)
        elif isinstance(node, ast.If):
            self._process_if(node)
        elif isinstance(node, ast.While):
            self._process_while(node)
        elif isinstance(node, ast.For):
            self._process_for(node)
        elif isinstance(node, ast.FunctionDef):
            self._process_function_def(node)
        elif isinstance(node, ast.Return):
            self._process_return(node)
        elif isinstance(node, ast.Call):
            self._process_call(node)
        elif isinstance(node, ast.Print):  # Python 2 compatibility
            self._process_print(node)
        else:
            # Handle other node types or append a comment for unsupported types
            self.code.append(f"# Unsupported node type: {type(node).__name__}")
    
    def _process_assignment(self, node):
        """Process assignment statements"""
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            # Simple assignment: x = expr
            target = node.targets[0].id
            value_temp = self._process_expression(node.value)
            self.code.append(f"{target} = {value_temp}")
        else:
            # More complex assignment patterns
            for target in node.targets:
                if isinstance(target, ast.Name):
                    value_temp = self._process_expression(node.value)
                    self.code.append(f"{target.id} = {value_temp}")
                else:
                    self.code.append(f"# Complex assignment pattern not fully supported")
    
    def _process_expression(self, node):
        """Process an expression and return a temporary variable with the result"""
        if isinstance(node, ast.BinOp):
            return self._process_binary_operation(node)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Num):
            return str(node.n)
        elif isinstance(node, ast.Str):
            return f'"{node.s}"'
        elif isinstance(node, ast.Call):
            return self._process_call(node)
        elif isinstance(node, ast.Compare):
            return self._process_compare(node)
        else:
            # For unsupported expressions, create a placeholder
            temp = self.get_temp()
            self.code.append(f"{temp} = # Unsupported expression: {type(node).__name__}")
            return temp
    
    def _process_binary_operation(self, node):
        """Process binary operations like a + b, a - b, etc."""
        left_temp = self._process_expression(node.left)
        right_temp = self._process_expression(node.right)
        result_temp = self.get_temp()
        
        if isinstance(node.op, ast.Add):
            op = "+"
        elif isinstance(node.op, ast.Sub):
            op = "-"
        elif isinstance(node.op, ast.Mult):
            op = "*"
        elif isinstance(node.op, ast.Div):
            op = "/"
        elif isinstance(node.op, ast.FloorDiv):
            op = "//"
        elif isinstance(node.op, ast.Mod):
            op = "%"
        else:
            op = "?"  # Unsupported operator
        
        self.code.append(f"{result_temp} = {left_temp} {op} {right_temp}")
        return result_temp
    
    def _process_compare(self, node):
        """Process comparison operations"""
        left = self._process_expression(node.left)
        result_temp = self.get_temp()
        
        if len(node.ops) == 1 and len(node.comparators) == 1:
            right = self._process_expression(node.comparators[0])
            
            if isinstance(node.ops[0], ast.Eq):
                op = "=="
            elif isinstance(node.ops[0], ast.NotEq):
                op = "!="
            elif isinstance(node.ops[0], ast.Lt):
                op = "<"
            elif isinstance(node.ops[0], ast.LtE):
                op = "<="
            elif isinstance(node.ops[0], ast.Gt):
                op = ">"
            elif isinstance(node.ops[0], ast.GtE):
                op = ">="
            else:
                op = "?"  # Unsupported operator
            
            self.code.append(f"{result_temp} = {left} {op} {right}")
        else:
            self.code.append(f"{result_temp} = # Complex comparison not fully supported")
        
        return result_temp
    
    def _process_if(self, node):
        """Process if statements"""
        condition_temp = self._process_expression(node.test)
        else_label = self.get_label()
        end_label = self.get_label()
        
        self.code.append(f"if {condition_temp} == False goto {else_label}")
        
        # Process the body of the if statement
        for statement in node.body:
            self._process_node(statement)
        
        self.code.append(f"goto {end_label}")
        self.code.append(f"{else_label}:")
        
        # Process the else clause if it exists
        if node.orelse:
            for statement in node.orelse:
                self._process_node(statement)
        
        self.code.append(f"{end_label}:")
    
    def _process_while(self, node):
        """Process while loops"""
        start_label = self.get_label()
        end_label = self.get_label()
        
        self.code.append(f"{start_label}:")
        condition_temp = self._process_expression(node.test)
        self.code.append(f"if {condition_temp} == False goto {end_label}")
        
        # Process the body of the while loop
        for statement in node.body:
            self._process_node(statement)
        
        self.code.append(f"goto {start_label}")
        self.code.append(f"{end_label}:")
    
    def _process_for(self, node):
        """Process for loops (simplified)"""
        iter_temp = self.get_temp()
        idx_temp = self.get_temp()
        target = node.target.id if isinstance(node.target, ast.Name) else "target"
        iterable = self._process_expression(node.iter)
        
        start_label = self.get_label()
        end_label = self.get_label()
        
        self.code.append(f"{iter_temp} = {iterable}")
        self.code.append(f"{idx_temp} = 0")
        self.code.append(f"{start_label}:")
        self.code.append(f"if {idx_temp} >= len({iter_temp}) goto {end_label}")
        self.code.append(f"{target} = {iter_temp}[{idx_temp}]")
        
        # Process the body of the for loop
        for statement in node.body:
            self._process_node(statement)
        
        self.code.append(f"{idx_temp} = {idx_temp} + 1")
        self.code.append(f"goto {start_label}")
        self.code.append(f"{end_label}:")
    
    def _process_function_def(self, node):
        """Process function definitions"""
        self.code.append(f"function {node.name}:")
        
        # Process parameters
        params = []
        for arg in node.args.args:
            if isinstance(arg, ast.Name):  # Python 3.0 to 3.7
                params.append(arg.id)
            elif hasattr(arg, 'arg'):  # Python 3.8+
                params.append(arg.arg)
        
        self.code.append(f"  params: {', '.join(params)}")
        
        # Process function body
        for statement in node.body:
            self._process_node(statement)
        
        self.code.append("end function")
    
    def _process_return(self, node):
        """Process return statements"""
        if node.value:
            value_temp = self._process_expression(node.value)
            self.code.append(f"return {value_temp}")
        else:
            self.code.append("return")
    
    def _process_call(self, node):
        """Process function calls"""
        temp = self.get_temp()
        func_name = self._get_function_name(node.func)
        
        # Process arguments
        args = []
        for arg in node.args:
            arg_temp = self._process_expression(arg)
            args.append(arg_temp)
        
        self.code.append(f"{temp} = call {func_name}({', '.join(args)})")
        return temp
    
    def _get_function_name(self, node):
        """Get the name of a function from a function node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            obj = self._process_expression(node.value)
            return f"{obj}.{node.attr}"
        else:
            return f"unknown_function"
    
    def _process_print(self, node):
        """Process print statements (Python 2) or print function calls"""
        values = []
        for value in node.values:
            value_temp = self._process_expression(value)
            values.append(value_temp)
        
        self.code.append(f"print {', '.join(values)}")


def generate_intermediate_code(source_code):
    """
    Generate intermediate code from Python source code.
    
    Args:
        source_code (str): Python source code
        
    Returns:
        list: List of intermediate code instructions
    """
    generator = IntermediateCodeGenerator()
    return generator.generate(source_code) 