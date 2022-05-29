"""
这是特殊形式的仓库，所有内部定义的特殊形式都会写在这个地方

"""
# special_form = {"define": eval_define,
#                 "quote": eval_quote,
#                 "quasiquote": eval_quasiquote,
#                 "unquote": eval_unquote,
#                 "lambda": eval_lambda,
#                 "begin": eval_begin,
#                 "if": eval_if,
#                 "cond": eval_cond,
#                 "and": eval_and,
#                 "or": eval_or,
#                 "let": eval_let,
#                 "mu": eval_mu,
#                 "define-macro": eval_macro
#                 }
from scheme_reader import Pair, nil, repl_str, quotes
from scheme_error import *
SPECIAL_FORM = {}

def is_literal(expr):
    literal_expr = (int, float, bool, type(nil))
    return isinstance(expr, literal_expr)
def is_expr(expr):
    all_expr = (int, float, bool, str, type(nil), Pair)
    return isinstance(expr, all_expr)
def is_symbol(expr):
    return isinstance(expr, str)

def sp_builtin(name):
    """An annotation to convert a Python function into a BuiltinProcedure."""
    def add(fn):
        SPECIAL_FORM[name] = fn
        return fn
    return add

def valid_binding(expr):
    if not isinstance(expr, Pair):
        raise SchemeError("Not binding sub_expression")
    if len(expr) != 2:
        raise SchemeError("Invalid binding")
    name = expr.first
    val = expr.rest.first
    if not(is_symbol(name) and is_expr(val)):
        raise SchemeError("Invalid binding")
def valid_define(expr):
    if expr.first != "define":
        raise SchemeError("Not define special form")
    be_bound = expr.rest.first
    bound_to = expr.rest.rest
    name = be_bound
    if isinstance(be_bound, Pair):
        name = name.first
    if not isinstance(name, str):
        raise SchemeError("cannot create bound with {}".format(str(name)))
@sp_builtin("define")
def eval_define(expr, scheme_eval, env):
    """给环境之中添加新的变量或者是函数
    >>> env = create_global_frame()
    >>> expr = read_line('(define a 1)')
    >>> eval_define(expr, env)
    'a'
    >>> eval_single('a', env)
    1
    >>> expr1 = read_line('(define b a)')
    >>> eval_define(expr1, env)
    'b'
    >>> eval_single('b', env)
    1
    >>> expr = read_line('(define (add x y) (+ x y))')
    >>> eval_define(expr, env)
    'add'
    >>> expr = read_line('(define (foo x) 1 2 3 4 5)')
    >>> eval_define(expr, env)
    (define (foo x) 1 2 3 4 5)
    >>> expr = read_line('(define 0 1)')
    SchemeError
    """
    valid_define(expr)

    be_bound = expr.rest.first
    bound_to = expr.rest.rest
    if not isinstance(be_bound, Pair):
        # 首先绑定变量
        env.define(be_bound, scheme_eval(bound_to.first, env))
        return be_bound
    else:
        # 这里是绑定函数 def __init__(self, formals, body, env):
        name = be_bound.first
        formals = be_bound.rest
        body = bound_to
        lambda_fn = LambdaProcedure(formals, body, env)
        env.define(name, lambda_fn)
        return name

def valid_quote(expr):
    signal = expr.first
    is_quote = lambda signal: (signal in quotes or signal in quotes.values())
    if not is_quote(signal) or expr.rest.rest is not nil:
        raise SchemeError("this is not a valid quote special form")
@sp_builtin("quote")
def eval_quote(expr, scheme_eval, env):
    """
    对于quote特殊形式进行衡量，这是一个单目运算符
    >>> expr = read_line('(quote a)')
    >>> print(eval_quote(expr, create_global_frame()))
    a
    >>> expr = read_line("'hello")
    >>> print(eval_quote(expr, create_global_frame()))
    hello
    >>> expr = read_line("'(1 2 3)")
    >>> print(eval_quote(expr, create_global_frame()))
    (1 2 3)
    >>> expr = read_line("(car '(1 2 3))")
    >>> print(scheme_eval(expr, create_global_frame()))
    1
    >>> expr = read_line('(quote (1 2))')
    >>> print(eval_quote(expr, create_global_frame()))
    (1 2)

    >>> expr = read_line("(cons 'car '('(1 2)))")
    >>> print(scheme_eval(expr, create_global_frame()))
    (car (quote (1 2)))
    >>> expr = read_line("(eval (car '(1 2 3)))")
    >>> print(scheme_eval(expr, create_global_frame()))
    1
    >>> expr = read_line("(eval (cons 'car '('(1 2))))")
    >>> print(scheme_eval(expr, create_global_frame()))
    1

    """
    valid_quote(expr)

    be_quoted = expr.rest.first
    return be_quoted

def valid_begin(expr):
    if not expr.first == "begin":
        raise SchemeError("Not begin special form")
@sp_builtin("begin")
def eval_begin(expr, scheme_eval, env):
    """
    begin表达式就相当于是 begin -> () -> () -> nil 列表，返回最后一个有效结果，没有表达式返回None
    >>> s_expr = "(begin (print 3) '(+ 2 3))"
    >>> expr = read_line(s_expr)
    >>> print(scheme_eval(expr, create_global_frame()))
    3
    (+ 2 3)
    >>> s_expr = "(define x (begin (display 3) (newline) (+ 2 3)))"
    >>> expr = read_line(s_expr)
    >>> print(scheme_eval(expr, create_global_frame()))
    3
    x
    """
    valid_begin(expr)
    rest = expr.rest
    ret_val = None
    while rest is not nil:
        sub_expr = rest.first
        ret_val = scheme_eval(sub_expr, env)
        rest = rest.rest
    return ret_val

def valid_lambda(expr):
    """
    >>> is_expr(2)
    >>> True
    >>> s = "(lambda () 2)"
    >>> expr = read_line(s)
    >>> valid_lambda(expr)
    """
    if not expr.first == "lambda":
        raise SchemeError("Not lambda special form")
    if len(expr) < 3:
        raise SchemeError("Not valid lambda expression")
    second = expr.rest
    third = second.rest
    end = third.rest
    if (not isinstance(second.first, (Pair, type(nil)))) or (not is_expr(third.first)) or\
            (not (isinstance(end, (Pair, type(nil))))):
        raise SchemeError("Not valid lambda expression")
@sp_builtin("lambda")
def eval_lambda(expr, scheme_eval, env):
    """
    >>> from scheme_reader import *
    >>> from scheme import scheme_eval, create_global_frame
    >>> s = "(lambda (x y) (+ x y))"
    >>> expr = read_line(s)
    >>> print(scheme_eval(expr, create_global_frame()))
    (lambda (x y) (+ x y))
    >>> s = "((lambda (x y) (+ x y)) 5 6)"
    >>> expr = read_line(s)
    >>> print(scheme_eval(expr, create_global_frame()))
    11
    """

    valid_lambda(expr)
    formals = expr.rest.first
    body = expr.rest.rest


    lambda_fn = LambdaProcedure(formals, body, env)

    return lambda_fn

def valid_if(expr):
    if expr.first != "if":
        raise SchemeError("Not if special form")
    if len(expr) < 3:
        raise SchemeError("Invalid if expression")
@sp_builtin("if")
def eval_if(expr, scheme_eval, env):
    valid_if(expr)
    predicate = expr.rest.first
    consequent = expr.rest.rest.first
    alternative = expr.rest.rest.rest
    if is_true(scheme_eval(predicate, env)):
        return scheme_eval(consequent, env)
    else:
        if alternative is not nil:
            return scheme_eval(alternative.first, env)
        else:
            return None

def eval_quasiquote(expr, env):
    pass
@sp_builtin("unquote")
def eval_unquote(expr, scheme_eval, env):
    pass

def valid_cond(expr):
    if expr.first != "cond":
        raise SchemeError("Not cond special form")
@sp_builtin("cond")
def eval_cond(expr, scheme_eval, env):
    """
    cond表达式：对于每个子句，根据每个子句的test部分决定是否计算右边的值，
    如果没有右边的值，返回True
    >>> s = "(cond ((= 4 3) 'nope) ((= 4 4) 'hi) (else 'wait))"
    >>> expr = read_line(s)
    >>> print(scheme_eval(expr, create_global_frame()))
    hi
    >>> s = "(cond ((= 4 3) 'wat) ((= 4 4)) (else 'hm))"
    >>> expr = read_line(s)
    >>> print(scheme_eval(expr, create_global_frame()))
    True
    >>> s = "(cond ((= 4 4) 'here (+ 40 2)) (else 'wat 0))"
    >>> expr = read_line(s)
    >>> print(scheme_eval(expr, create_global_frame()))
    42
    >>> s = "(cond (False 1) (False 2))"
    >>> expr = read_line(s)
    >>> print(scheme_eval(expr, create_global_frame()))
    """
    valid_cond(expr)
    rest = expr.rest
    ret = None
    while rest != nil:
        clause = rest.first
        test, subexpr = clause.first, clause.rest
        if test == "else" or scheme_eval(test, env):
            ret = scheme_eval(Pair("begin", subexpr), env)
            if ret is None:
                ret = True
            break
        rest = rest.rest

    return ret

def valid_and(expr):
    if expr.first != "and":
        raise SchemeError("Not and special form")
@sp_builtin("and")
def eval_and(expr, scheme_eval, env):
    """
    and表达式：返回第一个为False的值，如果全True，返回末尾的值
    >>> s = '(and)'
    >>> expr = read_line(s)
    >>> print(scheme_eval(expr, create_global_frame()))
    #t
    >>> s = '(and 4 5 (+ 3 3))'
    >>> expr = read_line(s)
    >>> print(scheme_eval(expr, create_global_frame()))
    6
    >>> s = '(and #t #f 42 (/ 1 0))'
    >>> expr = read_line(s)
    >>> print(scheme_eval(expr, create_global_frame()))
    #f
    """
    valid_and(expr)
    rest = expr.rest
    ret = True
    while rest != nil:
        sub_expr = rest.first
        ret = scheme_eval(sub_expr, env)
        if not is_true(ret):
            break
        rest = rest.rest
    return ret

def valid_or(expr):
    if expr.first != "or":
        raise SchemeError("Not or special form")
def is_true(val):
    if not is_literal(val) and not is_symbol(val):
        raise SchemeError("Not a contex, cannot convert to bool")
    if isinstance(val, bool) and val == False:
        return False
    return True
@sp_builtin("or")
def eval_or(expr, scheme_eval, env):
    """
    or表达式：返回第一个为True的值，如果全False，返回False
    >>> s = '(or)'
    >>> expr = read_line(s)
    >>> print(scheme_eval(expr, create_global_frame()))
    #f
    >>> s = '(or #f (- 1 1) 1)'
    >>> expr = read_line(s)
    >>> print(scheme_eval(expr, create_global_frame()))
    0
    >>> s = '(or 4 #t (/ 1 0))'
    >>> expr = read_line(s)
    >>> print(scheme_eval(expr, create_global_frame()))
    4

    >>> env =  create_global_frame()
    >>> expr1 = read_line('(define (greater-than-5 x) (if (> x 5) #t #f))')
    >>> scheme_eval(expr1,env)
    >>> s = '(if (> 1 5) #t #f)'
    >>> expr2 = read_line(s)
    >>> print(scheme_eval(expr2,env))
    4
    """
    valid_or(expr)
    rest = expr.rest
    ret = False
    while rest != nil:
        sub_expr = rest.first
        ret = scheme_eval(sub_expr, env)
        if is_true(ret):
            break
        rest = rest.rest
    return ret

def valid_let(expr):
    if expr.first != "let":
        raise SchemeError("Not let special form")
    if len(expr) < 3:
        raise SchemeError("Invalid let expression")
@sp_builtin("let")
def eval_let(expr, scheme_eval, env):
    """

    cond表达式：对于每个子句，根据每个子句的test部分决定是否计算右边的值，
    如果没有右边的值，返回True

    >>> env = create_global_frame()
    >>> s = "(define x 5)"
    >>> expr = read_line(s)
    >>> print(scheme_eval(expr, env))
    x
    >>> s = "(define y 'bye)"
    >>> expr = read_line(s)
    >>> print(scheme_eval(expr, env))
    y
    >>> s = "(let ((x 42) (y (* x 10))) (list x y))"
    >>> expr = read_line(s)
    >>> print(scheme_eval(expr, env))
    (42 50)

    """
    valid_let(expr)
    binding_expr = expr.rest.first
    body = expr.rest.rest

    tmp_env = Frame(env)
    while binding_expr != nil:
        binding_clause = binding_expr.first
        valid_binding(binding_clause)
        binding_name = binding_clause.first
        binding_val = scheme_eval(binding_clause.rest.first, env) # 这里就是env，全部绑定之后再运算
        tmp_env.define(binding_name, binding_val)

        binding_expr = binding_expr.rest
    ret = None
    while body != nil:
        sub_expr = body.first
        ret = scheme_eval(sub_expr, tmp_env)
        body = body.rest
    return ret

def valid_mu(expr):
    if expr.first != "mu":
        raise SchemeError("Not mu special form")
@sp_builtin("mu")
def eval_mu(expr, scheme_eval, env):
    from scheme import MuProcedure
    valid_mu(expr)
    formals = expr.rest.first
    body = expr.rest.rest
    return MuProcedure(formals, body)

def valid_macro(expr):
    pass
@sp_builtin("macro")
def eval_macro(expr, scheme_eval, env):
    from scheme import MacroProcedure
    valid_macro(expr)

    be_bound = expr.rest.first
    bound_to = expr.rest.rest
    name = be_bound.first
    formals = be_bound.rest
    body = bound_to
    macro_fn = MacroProcedure(formals, body)
    env.define(name, macro_fn)
    return name

