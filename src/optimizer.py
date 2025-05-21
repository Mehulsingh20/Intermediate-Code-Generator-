class CodeOptimizer:
    def __init__(self):
        self.code = []
        self.variable_values = {}
        self.used_vars = set()
        self.defined_vars = set()

    def optimize(self, intermediate_code):
        """
        Apply optimization techniques to the intermediate code.
        
        Args:
            intermediate_code (list): List of intermediate code instructions
            
        Returns:
            list: Optimized intermediate code
        """
        self.code = intermediate_code.copy()
        
        # Apply multiple optimization passes
        self._remove_comments()
        self._constant_folding()
        self._constant_propagation()
        self._dead_code_elimination()
        self._combine_consecutive_assignments()
        
        return self.code

    def optimize_with_technique(self, intermediate_code, technique):
        """
        Apply a specific optimization technique to the intermediate code.
        
        Args:
            intermediate_code (list): List of intermediate code instructions
            technique (str): Name of the optimization technique to apply
            
        Returns:
            list: Optimized intermediate code after applying the specific technique
        """
        self.code = intermediate_code.copy()
        
        # Apply the specified optimization technique
        if technique == 'constant_folding':
            self._constant_folding()
        elif technique == 'constant_propagation':
            self._constant_propagation()
        elif technique == 'dead_code_elimination':
            self._analyze_variable_usage()
            self._dead_code_elimination()
        elif technique == 'combine_assignments':
            self._combine_consecutive_assignments()
        elif technique == 'remove_comments':
            self._remove_comments()
        
        return self.code
    
    def _remove_comments(self):
        """Remove comment lines from the code"""
        self.code = [line for line in self.code if not line.strip().startswith('#')]
    
    def _constant_folding(self):
        """Apply constant folding optimization"""
        for i in range(len(self.code)):
            line = self.code[i]
            
            # Look for arithmetic operations with constants
            if '=' in line and any(op in line.split('=')[1] for op in ['+', '-', '*', '/', '%']):
                parts = line.split('=', 1)
                result_var = parts[0].strip()
                expr = parts[1].strip()
                
                try:
                    # Try to evaluate the expression if it contains only constants
                    if all(token.isdigit() or token in ['+', '-', '*', '/', '%', ' '] 
                           for token in expr.split()):
                        # Replace multiple spaces with a single space
                        expr = ' '.join(expr.split())
                        # Evaluate the expression
                        result = eval(expr)
                        self.code[i] = f"{result_var} = {result}"
                except:
                    # If evaluation fails, keep the original line
                    pass
    
    def _constant_propagation(self):
        """Apply constant propagation optimization"""
        # First pass: identify constants
        constants = {}
        for line in self.code:
            if '=' in line:
                parts = line.split('=', 1)
                var = parts[0].strip()
                value = parts[1].strip()
                
                # Check if the right side is a constant
                try:
                    if value.isdigit() or (value.startswith('"') and value.endswith('"')):
                        constants[var] = value
                except:
                    pass
        
        # Second pass: propagate constants
        for i in range(len(self.code)):
            line = self.code[i]
            
            # Skip lines that define constants
            if '=' in line:
                parts = line.split('=', 1)
                var = parts[0].strip()
                if var in constants and parts[1].strip() == constants[var]:
                    continue
            
            # Replace variables with their constant values
            for var, value in constants.items():
                # Make sure we're replacing whole variable names, not parts
                line = self._replace_var_with_value(line, var, value)
            
            self.code[i] = line
    
    def _replace_var_with_value(self, line, var, value):
        """Replace a variable with its value, ensuring we don't replace parts of other variables"""
        tokens = []
        current_token = ""
        i = 0
        
        while i < len(line):
            if line[i].isalnum() or line[i] == '_':
                current_token += line[i]
            else:
                if current_token == var:
                    tokens.append(value)
                elif current_token:
                    tokens.append(current_token)
                tokens.append(line[i])
                current_token = ""
            i += 1
        
        if current_token == var:
            tokens.append(value)
        elif current_token:
            tokens.append(current_token)
        
        return "".join(tokens)
    
    def _analyze_variable_usage(self):
        """Analyze which variables are used after being defined"""
        self.used_vars = set()
        self.defined_vars = set()
        
        # First pass: collect variable definitions
        for line in self.code:
            if '=' in line and not line.strip().startswith('if') and 'goto' not in line:
                var = line.split('=', 1)[0].strip()
                self.defined_vars.add(var)
        
        # Second pass: collect variable uses
        for line in self.code:
            if '=' in line and not line.strip().startswith('if') and 'goto' not in line:
                # Right side of assignment
                expr = line.split('=', 1)[1].strip()
                # Add all defined variables that appear in the expression
                for var in self.defined_vars:
                    if var in expr.split():
                        self.used_vars.add(var)
            elif 'if' in line:
                # Condition in if statements
                for var in self.defined_vars:
                    if var in line.split():
                        self.used_vars.add(var)
            elif 'goto' not in line and ':' not in line:
                # Other statements
                for var in self.defined_vars:
                    if var in line.split():
                        self.used_vars.add(var)
    
    def _dead_code_elimination(self):
        """Eliminate assignments to variables that are never used"""
        self._analyze_variable_usage()
        
        new_code = []
        for line in self.code:
            if '=' in line and not line.strip().startswith('if') and 'goto' not in line:
                var = line.split('=', 1)[0].strip()
                if var in self.used_vars or var.startswith('t') or var == "result":
                    new_code.append(line)
            else:
                new_code.append(line)
        
        self.code = new_code
    
    def _combine_consecutive_assignments(self):
        """Combine consecutive assignments where possible"""
        i = 0
        while i < len(self.code) - 1:
            curr_line = self.code[i]
            next_line = self.code[i+1]
            
            # Check if current line assigns to a temp variable and next line uses only that temp
            if '=' in curr_line and '=' in next_line:
                curr_parts = curr_line.split('=', 1)
                next_parts = next_line.split('=', 1)
                
                temp_var = curr_parts[0].strip()
                
                # If the temp var is only used once in the next line's right side
                if temp_var in next_parts[1].split() and next_parts[1].count(temp_var) == 1:
                    # Replace the temp var in the next line with its value
                    new_expr = next_parts[1].replace(temp_var, '(' + curr_parts[1].strip() + ')')
                    self.code[i+1] = f"{next_parts[0]} {new_expr}"
                    
                    # Remove the current line (temp var assignment)
                    self.code.pop(i)
                    continue
            
            i += 1


def optimize_intermediate_code(intermediate_code):
    """
    Optimize the intermediate code.
    
    Args:
        intermediate_code (list): List of intermediate code instructions
        
    Returns:
        list: Optimized intermediate code
    """
    optimizer = CodeOptimizer()
    return optimizer.optimize(intermediate_code) 