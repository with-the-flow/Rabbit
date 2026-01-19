# cli.py  Rabbit 第二天完整版
GRAMMAR = r"""
?start: stmt+
?stmt: call | assign
call: NAME "(" [expr ("," expr)*] ")"
assign: NAME "=" expr
?expr: term
     | expr PLUS term   -> add
term : literal | NAME -> var | call
literal: STRING -> string | NUMBER -> number

STRING  : "\"" (/[^"\\]/ | "\\" /./)* "\""
NUMBER  : /\d+(\.\d+)?/
NAME    : /[a-zA-Z_][a-zA-Z0-9_]*/
PLUS    : "+"

%import common.WS
%ignore WS
"""

# ---------- AST 节点 ----------
class String:
    def __init__(self, s): self.s = s
class Number:
    def __init__(self, n): self.n = float(n)
class Call:
    def __init__(self, name, args): self.name, self.args = name, args
class Var:
    def __init__(self, name): self.name = name
class Assign:
    def __init__(self, name, val): self.name, self.val = name, val
class Add:
    def __init__(self, left, right): self.left, self.right = left, right

# ---------- 运行时 ----------
env = {}

def eval_expr(node):
    if isinstance(node, String):   return node.s
    if isinstance(node, Number):   return node.n
    if isinstance(node, Var):      return env[node.name]
    if isinstance(node, Call):
        args = [eval_expr(a) for a in node.args]
        if node.name == "print":
            print(*args)                      # 无 return
        elif node.name == "input":
            return input(*args)
        else: raise NameError(node.name)
    if isinstance(node, Assign):
        env[node.name] = eval_expr(node.val)  # 无 return
    if isinstance(node, Add):
        l = eval_expr(node.left)
        r = eval_expr(node.right)
        if isinstance(l, (int, float)) and isinstance(r, (int, float)):
            return l + r
        return str(l) + str(r)
    
# ---------- Lark 转换 ----------
from lark import Lark, Transformer
class ToAST(Transformer):
    def string(self, s): return String(s[0][1:-1])
    def number(self, n): return Number(float(n[0]))
    def var(self, v):    return Var(str(v[0]))
    def call(self, c):
        name, *args = c
        return Call(str(name), args)
    def assign(self, a):
        name, val = a
        return Assign(str(name), val)
    def add(self, items): return Add(items[0], items[2])
parser = Lark(GRAMMAR, parser='lalr')

# ---------- 入口 ----------
if __name__ == "__main__":
    import sys
    code = sys.stdin.read()
    tree = parser.parse(code)
    stmts = ToAST().transform(tree)
    for stmt in stmts.children:
        eval_expr(stmt)          # 只管执行，不打印返回值