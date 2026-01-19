from ply import lex
import lark
import re

# PLY词法分析器 - 预处理复合Token
class RabbitLexer:
    # 复合内置函数列表
    builtin_functions = [
        'json.parse', 'json.stringify',
        'http.get', 'http.post', 'http.fetch',
        'len', 'split', 'join', 'trim',
        'sqrt', 'pow', 'abs', 'sin', 'cos', 'tan',
        'rand', 'randint', 'max', 'min', 'sum',
        'map', 'filter', 'reduce', 'sort', 'reverse'
    ]
    
    # 内置常量
    builtin_constants = ['pi', 'e', 'inf']
    
    # 所有内置标识符
    builtin_identifiers = builtin_functions + builtin_constants
    
    tokens = (
        'NUMBER', 'ID', 'BUILTIN',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POWER', 
        'LPAREN', 'RPAREN', 'LBRACK', 'RBRACK',
        'ASSIGN', 'COMMA', 'COLON', 'SEMICOLON'
    )

    # 运算符和分隔符
    t_PLUS    = r'\+'
    t_MINUS   = r'-'
    t_TIMES   = r'\*'
    t_DIVIDE  = r'/'
    t_POWER   = r'\^|²|³'
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_LBRACK  = r'\['
    t_RBRACK  = r'\]'
    t_ASSIGN  = r'='
    t_COMMA   = r','
    t_COLON   = r':'
    t_SEMICOLON = r';'
    
    # 确保SEMICOLON被正确识别为Token
    
    # 内置标识符的正则表达式模式
    def t_BUILTIN(self, t):
        r'(json\.parse|json\.stringify|http\.get|http\.post|http\.fetch|len|split|join|trim|sqrt|pow|abs|sin|cos|tan|rand|randint|max|min|sum|map|filter|reduce|sort|reverse|pi|e|inf)(?![a-zA-Z0-9_\.])'
        return t

    # 确保内置标识符优先于普通ID匹配
    
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        # 检查是否为内置标识符
        if t.value in self.builtin_identifiers:
            t.type = 'BUILTIN'
        return t

    def t_NUMBER(self, t):
        r'\d+(_?\d+)*(\.\d+(_?\d+)*)?'
        t.value = float(t.value.replace('_', ''))
        return t

    t_ignore = ' \t\n'

    def t_error(self, t):
        print(f"非法字符: {t.value[0]}")
        t.lexer.skip(1)

# Lark语法解析器 - 支持左递归和语义完整AST
grammar = r"""
?start: program

program: (statement SEMICOLON?)*

statement: assignment
         | expr_statement
         | return_statement

assignment: ID ASSIGN expr -> assign_var
          | BUILTIN ASSIGN expr -> assign_builtin

expr_statement: expr

return_statement: "return" expr -> return_expr

?expr: expr PLUS term  -> add
     | expr MINUS term -> sub
     | term

?term: term TIMES factor -> mul
     | term DIVIDE factor -> div
     | term POWER factor -> pow
     | factor

?factor: NUMBER         -> number
       | BUILTIN        -> builtin
       | ID             -> var
       | call_expr
       | LPAREN expr RPAREN

call_expr: BUILTIN LPAREN args? RPAREN -> builtin_call
         | ID LPAREN args? RPAREN -> func_call

args: expr (COMMA expr)*
"""

class RabbitTransformer(lark.Transformer):
    def __init__(self):
        self.symbols = {}
    
    def assign_var(self, items):
        var_name, expr = items
        self.symbols[var_name.value] = expr
        return ('assign', var_name.value, expr)
    
    def assign_builtin(self, items):
        builtin_name, expr = items
        return ('assign_builtin', builtin_name.value, expr)
    
    def add(self, items):
        return ('add', items[0], items[1])
    
    def sub(self, items):
        return ('sub', items[0], items[1])
    
    def mul(self, items):
        return ('mul', items[0], items[1])
    
    def div(self, items):
        return ('div', items[0], items[1])
    
    def pow(self, items):
        return ('pow', items[0], items[1])
    
    def number(self, items):
        return ('number', items[0].value)
    
    def builtin(self, items):
        return ('builtin', items[0].value)
    
    def var(self, items):
        return ('var', items[0].value)
    
    def builtin_call(self, items):
        # 保持语义原子性：json.parse作为整体
        func_name, args = items[0].value, items[1] if len(items) > 1 else []
        return ('builtin_call', func_name, args)
    
    def func_call(self, items):
        func_name, args = items[0].value, items[1] if len(items) > 1 else []
        return ('func_call', func_name, args)
    
    def return_expr(self, items):
        return ('return', items[0])

# 完整解析流程
def parse(code):
    lexer = lex.lex(module=RabbitLexer())
    parser = lark.Lark(grammar, parser='lalr', transformer=RabbitTransformer())
    
    lexer.input(code)
    return parser.parse(code)

if __name__ == '__main__':
    # 测试代码
    test_codes = [
        "area = pi * r²",
        "data = json.parse(input_str)",
        "response = http.get('https://api.example.com')",
        "result = sqrt(4) + pow(2, 3)",
        "names = ['Alice', 'Bob']; random_name = choice(names)"
    ]
    
    for code in test_codes:
        print(f"\n解析: {code}")
        try:
            ast = parse(code)
            print(f"AST: {ast}")
        except Exception as e:
            print(f"错误: {e}")
