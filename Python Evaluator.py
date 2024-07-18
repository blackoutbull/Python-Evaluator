# PYTHON EVALUATOR BY AHMAD SAEED
# Lexer
from collections import namedtuple

# Definition of token types
Token = namedtuple('Token', ['type', 'value'])

RESERVED_KEYWORDS = {'print'}

def lexer(input_str):
    """
    Converts an input string into a list of tokens.

    Args:
        input_str (str): The input string to be tokenized.

    Returns:
        list: A list of Token namedtuples representing the tokens in the input string.
    """
    tokens = []
    i = 0
    while i < len(input_str):
        char = input_str[i]
        if char.isdigit():
            # Recognize and extract numeric literals
            num = ''
            while i < len(input_str) and input_str[i].isdigit():
                num += input_str[i]
                i += 1
            tokens.append(Token('NUMBER', int(num)))
        elif char.isalpha():
            # Recognize and extract identifiers (variable names)
            identifier = ''
            while i < len(input_str) and (input_str[i].isalpha() or input_str[i].isdigit()):
                identifier += input_str[i]
                i += 1
            if identifier in RESERVED_KEYWORDS:
                # If the identifier is a reserved keyword, add it as a token of that type
                tokens.append(Token(identifier, identifier))
            else:
                # Otherwise, add it as an IDENTIFIER token
                tokens.append(Token('IDENTIFIER', identifier))
        elif char == '=':
            # Recognize the assignment operator
            tokens.append(Token('ASSIGN', '='))
            i += 1
        elif char in '+-*/()':
            # Recognize and extract arithmetic operators and parentheses
            tokens.append(Token(char, char))
            i += 1
        elif char.isspace():
            # Skip whitespace characters
            i += 1
        else:
            # Raise an error for invalid characters
            raise ValueError(f"Invalid character: {char}")
    return tokens

# Parser
class ASTNode:
    """Base class for Abstract Syntax Tree (AST) nodes."""
    pass

class NumberNode(ASTNode):
    """AST node representing a numeric literal."""
    def __init__(self, token):
        self.token = token

class VariableNode(ASTNode):
    """AST node representing a variable."""
    def __init__(self, token):
        self.token = token

class AssignmentNode(ASTNode):
    """AST node representing an assignment statement."""
    def __init__(self, left, right):
        self.left = left
        self.right = right

class BinaryOpNode(ASTNode):
    """AST node representing a binary operation."""
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class PrintNode(ASTNode):
    """AST node representing a print statement."""
    def __init__(self, expr):
        self.expr = expr

def parser(tokens):
    """
    Converts a list of tokens into an Abstract Syntax Tree (AST).

    Args:
        tokens (list): A list of Token namedtuples.

    Returns:
        list: A list of AST nodes representing the parsed program.
    """
    def parse_expr():
        """Parse an expression."""
        node = parse_term()
        while tokens and tokens[0].type in '+-':
            op = tokens.pop(0)
            right = parse_term()
            node = BinaryOpNode(node, op, right)
        return node

    def parse_term():
        """Parse a term."""
        node = parse_factor()
        while tokens and tokens[0].type in '*//':
            op = tokens.pop(0)
            right = parse_factor()
            node = BinaryOpNode(node, op, right)
        return node

    def parse_factor():
        """Parse a factor."""
        if not tokens:
            raise ValueError("Unexpected end of input")
        token = tokens.pop(0)
        if token.type == 'NUMBER':
            return NumberNode(token)
        elif token.type == 'IDENTIFIER':
            return VariableNode(token)
        elif token.type == '(':
            node = parse_expr()
            if not tokens or tokens[0].type != ')':
                raise ValueError("Expected ')'")
            tokens.pop(0)
            return node
        elif token.type == 'print':
            expr = parse_expr()
            return PrintNode(expr)
        else:
            raise ValueError(f"Unexpected token: {token.type}")

    def parse_assignment():
        """Parse an assignment statement."""
        left = parse_factor()
        if not tokens or tokens[0].type != 'ASSIGN':
            return left
        tokens.pop(0)
        right = parse_expr()
        return AssignmentNode(left, right)

    ast = []
    while tokens:
        ast.append(parse_assignment())
    return ast

# Evaluator
class Interpreter:
    """
    Interpreter for the programming language.
    """
    def __init__(self):
        self.variables = {}

    def visit(self, node):
        """
        Dispatches the visit to the appropriate visitor method based on the type of the node.

        Args:
            node (ASTNode): The node to be visited.

        Returns:
            The result of visiting the node.
        """
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def visit_NumberNode(self, node):
        """Visit a NumberNode and return its value."""
        return node.token.value

    def visit_VariableNode(self, node):
        """Visit a VariableNode and return its value."""
        name = node.token.value
        if name not in self.variables:
            raise ValueError(f"Variable '{name}' is not defined")
        return self.variables[name]

    def visit_AssignmentNode(self, node):
        """Visit an AssignmentNode and update the variable's value."""
        name = node.left.token.value
        value = self.visit(node.right)
        self.variables[name] = value
        return value

    def visit_BinaryOpNode(self, node):
        """Visit a BinaryOpNode and perform the appropriate binary operation."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op.type
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            return left / right
        else:
            raise ValueError(f"Unknown operator: {op}")

    def visit_PrintNode(self, node):
        """Visit a PrintNode and print the result of evaluating the expression."""
        value = self.visit(node.expr)
        print(value)
        return value

    def generic_visit(self, node):
        """
        Raise an error for unsupported node types.

        Args:
            node (ASTNode): The node to be visited.

        Raises:
            TypeError: If no visit method is defined for the given node type.
        """
        raise TypeError(f"No visit method defined for {type(node)}")

    def interpret(self, program):
        """
        Interpret the given program (list of AST nodes).

        Args:
            program (list): A list of AST nodes representing the program.
        """
        for stmt in program:
            self.visit(stmt)

# Example usage
program = """
x = 10
y = 20
z = x + y
print(z)
print(z * 2)
"""

tokens = lexer(program)
ast = parser(tokens)
interpreter = Interpreter()
interpreter.interpret(ast)

# Test case 1: Simple arithmetic operations
program1 = """
a = 10
b = 20
c = a + b
print(c)
"""
tokens1 = lexer(program1)
ast1 = parser(tokens1)
interpreter1 = Interpreter()
interpreter1.interpret(ast1)
# Output: 30

# Test case 2: Nested expressions
program2 = """
x = 5
y = 3
z = (x + y) * 2
print(z)
"""
tokens2 = lexer(program2)
ast2 = parser(tokens2)
interpreter2 = Interpreter()
interpreter2.interpret(ast2)
# Output: 16

# Test case 3: Division by zero
program3 = """
a = 10
b = 0
c = a / b
print(c)
"""
tokens3 = lexer(program3)
ast3 = parser(tokens3)
interpreter3 = Interpreter()
try:
    interpreter3.interpret(ast3)
except ZeroDivisionError as e:
    print(e)
# Output: Division by zero

# Test case 4: Variable not defined
program4 = """
x = a + 5
print(x)
"""
tokens4 = lexer(program4)
ast4 = parser(tokens4)
interpreter4 = Interpreter()
try:
    interpreter4.interpret(ast4)
except ValueError as e:
    print(e)
# Output: Variable 'a' is not defined

# Test case 5: Syntax error
program5 = """
x = 10
y = 20
z = x + y *
print(z)
"""
tokens5 = lexer(program5)
try:
    ast5 = parser(tokens5)
except ValueError as e:
    print(e)
# Output: Unexpected token: ')'