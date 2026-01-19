from ply import lex
import lark
import re

# ---------- PLY 词法器 ----------
class RabbitLexer:
    # 复合内置函数/常量
    builtin_identifiers = [
        'json.parse', 'json.stringify',
        'http.get', 'http.post', 'http.fetch',
        'len', 'split', 'join', 'trim',
        'sqrt', 'pow', 'abs', 'sin', 'cos', 'tan',
        'rand', 'randint', 'max', 'min', 'sum',
        'map', 'filter', 'reduce', 'sort', 'reverse',
        'pi', 'e', 'inf'
    ]

    tokens = (
        'NUMBER', 'ID', 'BUILTIN',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POWER',
        'LPAREN', 'RPAREN', 'LBRACK', 'RBRACK',
        'ASSIGN', 'COMMA', 'COLON', 'SEMICOLON'
    )

    # 运算符与分隔符
    t_PLUS   = r'\+'
    t_MINUS  = r'-'
    t_TIMES  = r'\*'
    t_DIVIDE = r'/'
    t_POWER  = r'\^|²|³'
    t_LPAREN = r'\('        # 修复空串
    t_RPAREN = r'\)'
    t_LBRACK = r'\['
    t_RBRACK = r'\]'
    t_ASSIGN = r'='
    t_COMMA  = r','
    t_COLON  = r':'

    def t_SEMICOLON(self, t):
        r';'
        return t

    # 修复：先整体匹配，再判断是否为内置标识符
    def t_BUILTIN(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*'
        if t.value in self.builtin_identifiers:
            t.type = 'BUILTIN'
        else:
            t.type = 'ID'
        return t

    def t_NUMBER(self, t):
        r'\d+(_?\d+)*(\.\d+(_?\d+)*)?'
        t.value = float(t.value.replace('_', ''))
        return t

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        return t

    t_ignore = ' \t\n'

    def t_error(self, t):
        print(f"非法字符: {t.value[0]}")
        t.lexer.skip(1)

# ---------- Lark 语法 ----------
grammar = r"""
?start: program

program: statement*

statement: assignment
         | expr_statement
         | return_statement

assignment: ID ASSIGN expr -> assign_var
          | BUILTIN ASSIGN expr -> assign_builtin

expr_statement: expr

return_statement: "return" expr -> return_expr

?expr: expr PLUS term   -> add
     | expr MINUS term  -> sub
     | term

?term: term TIMES factor -> mul
     | term DIVIDE factor -> div
     | term POWER factor  -> pow
     | factor

?factor: NUMBER         -> number
       | BUILTIN        -> builtin
       | ID             -> var
       | call_expr
       | LPAREN expr RPAREN

call_expr: BUILTIN LPAREN args? RPAREN -> builtin_call
         | ID      LPAREN args? RPAREN -> func_call

args: expr (COMMA expr)*
"""

# ---------- Transformer ----------
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

    def add(self, items):  return ('add', items[0], items[1])
    def sub(self, items):  return ('sub', items[0], items[1])
    def mul(self, items):  return ('mul', items[0], items[1])
    def div(self, items):  return ('div', items[0], items[1])
    def pow(self, items):  return ('pow', items[0], items[1])

    def number(self, items):  return ('number', items[0].value)
    def builtin(self, items): return ('builtin', items[0].value)
    def var(self, items):     return ('var', items[0].value)

    def builtin_call(self, items):
        func_name, args = items[0].value, items[1] if len(items) > 1 else []
        return ('builtin_call', func_name, args)

    def func_call(self, items):
        func_name, args = items[0].value, items[1] if len(items) > 1 else []
        return ('func_call', func_name, args)

    def return_expr(self, items):
        return ('return', items[0])

# ---------- 统一解析入口 ----------
def parse(code):
    # 1. PLY 词法
    lexer = lex.lex(object=RabbitLexer())
    lexer.input(code)
    tokens = list(iter(lexer.token, None))

    # 2. 生成 Lark 可用 token 串（去掉分号）
    token_stream = ' '.join(
        f'{t.type}:{repr(t.value)}'
        for t in tokens
        if t.type != 'SEMICOLON'
    )

    # 3. Lark 解析
    parser = lark.Lark(grammar, parser='lalr', transformer=RabbitTransformer())
    return parser.parse(code)   # 直接解析原始代码即可

# ---------- 自测 ----------
if __name__ == '__main__':
    tests = [
        "area = pi * r²",
        "data = json.parse(input_str)",
        "response = http.get('https://api.example.com')",
        "result = sqrt(4) + pow(2, 3)",
        "x = 10; y = x * 2"
    ]
    for src in tests:
        print(f"\n解析: {src}")
        try:
            ast = parse(src)
            print("AST:", ast)
            print("成功解析!")
        except Exception as e:
            print("错误:", type(e).__name__, e)
            import traceback
            traceback.print_exc()