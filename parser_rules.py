# parser_rules.py
import ply.yacc as yacc
from lexer import tokens, lexer

class Interpreter:
    def __init__(self):
        self.variables = {}
        self.had_error = False
    
    def evaluate_expression(self, expr):
        if isinstance(expr, tuple):
            if expr[0] == 'binop':
                left = self.evaluate_expression(expr[1])
                right = self.evaluate_expression(expr[3])
                op = expr[2]
                if op == '+': return left + right
                if op == '-': return left - right
                if op == '*': return left * right
                if op == '/': 
                    if right == 0:
                        print("Error: Division by zero")
                        self.had_error = True
                        return 0
                    return left / right
            elif expr[0] == 'var':
                if expr[1] not in self.variables:
                    print(f"Error: Variable '{expr[1]}' not declared")
                    self.had_error = True
                    return 0
                return self.variables.get(expr[1], 0)
            elif expr[0] == 'number':
                return expr[1]
        return expr
    
    def evaluate_condition(self, condition):
        if not condition or condition[0] != 'condition':
            return False
        
        left = self.evaluate_expression(condition[2])
        right = self.evaluate_expression(condition[3])
        op = condition[1]
        
        if op == '>': return left > right
        if op == '<': return left < right
        if op == '>=': return left >= right
        if op == '<=': return left <= right
        if op == '==': return left == right
        if op == '!=': return left != right
        return False

    def execute(self, node):
        if not node:
            return
        
        if isinstance(node, list):
            for statement in node:
                self.execute(statement)
            return

        if node[0] == 'declaration':
            for var in node[2]:
                self.variables[var] = None
        
        elif node[0] == 'assignment':
            var_name = node[1]
            if var_name not in self.variables:
                print(f"Error: Variable '{var_name}' not declared")
                self.had_error = True
            else:
                self.variables[var_name] = self.evaluate_expression(node[2])
        
        elif node[0] == 'if':
            condition_result = self.evaluate_condition(node[1])
            if condition_result:
                self.execute(node[2])
            elif len(node) > 3:  # has else branch
                self.execute(node[3])
        
        elif node[0] == 'while':
            while self.evaluate_condition(node[1]):
                self.execute(node[2])
        
        elif node[0] == 'print':
            values = []
            for expr in node[1]:
                values.append(self.evaluate_expression(expr))
            print(*values)

# Dictionary to store variables
interpreter = Interpreter()

def p_program(p):
    '''program : statement
               | program statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]
        
def p_statement(p):
    '''statement : declaration
                | assignment
                | if_statement
                | while_statement
                | for_statement
                | print_statement'''
    p[0] = p[1]

def p_declaration(p):
    '''declaration : type declaration_list SEMICOLON'''
    p[0] = ('declaration', p[1], p[2])

def p_declaration_list(p):
    '''declaration_list : ID
                       | ID COMMA declaration_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_type(p):
    '''type : INT
            | FLOAT'''
    p[0] = p[1]

def p_assignment(p):
    '''assignment : ID EQUALS expression SEMICOLON'''
    p[0] = ('assignment', p[1], p[3])

def p_if_statement(p):
    '''if_statement : IF LPAREN condition RPAREN LBRACE program RBRACE
                   | IF LPAREN condition RPAREN LBRACE program RBRACE ELSE LBRACE program RBRACE'''
    if len(p) == 8:
        p[0] = ('if', p[3], p[6])
    else:
        p[0] = ('if', p[3], p[6], p[10])

def p_while_statement(p):
    '''while_statement : WHILE LPAREN condition RPAREN LBRACE program RBRACE'''
    p[0] = ('while', p[3], p[6])

def p_for_statement(p):
    '''for_statement : FOR LPAREN assignment condition SEMICOLON ID EQUALS expression RPAREN LBRACE program RBRACE'''
    p[0] = ('for', p[3], p[4], (p[6], p[8]), p[11])

def p_print_statement(p):
    '''print_statement : PRINT LPAREN print_list RPAREN SEMICOLON'''
    p[0] = ('print', p[3])

def p_print_list(p):
    '''print_list : expression
                 | expression COMMA print_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_condition(p):
    '''condition : expression GT expression
                | expression LT expression
                | expression GE expression
                | expression LE expression
                | expression EQ expression
                | expression NE expression'''
    p[0] = ('condition', p[2], p[1], p[3])

def p_expression(p):
    '''expression : term
                 | expression PLUS term
                 | expression MINUS term'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ('binop', p[1], p[2], p[3])

def p_term(p):
    '''term : factor
            | term TIMES factor
            | term DIVIDE factor'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ('binop', p[1], p[2], p[3])

def p_factor(p):
    '''factor : NUMBER
              | ID
              | LPAREN expression RPAREN'''
    if len(p) == 2:
        if isinstance(p[1], (int, float)):
            p[0] = ('number', p[1])
        else:
            p[0] = ('var', p[1])
    else:
        p[0] = p[2]

def p_error(p):
    if p:
        print(f"Syntax error at line {p.lineno}, position {p.lexpos}: Unexpected token '{p.value}'")
    else:
        print("Syntax error: Unexpected end of input")

# Build the parser
parser = yacc.yacc()