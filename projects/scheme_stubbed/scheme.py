"""A Scheme interpreter and its read-eval-print loop."""
from __future__ import print_function  # Python 2 compatibility

import sys
import os

from scheme_builtins import *
# from scheme_special_form import *
from scheme_reader import *
from ucb import main, trace


##############
# Eval/Apply #
##############
# def add_quote(args):
#     return args
#     if args == nil:
#         return nil
#     else:
#         return Pair(Pair("quote", Pair(args.first, nil)), add_quote(args.rest))
def eval_single(expr, env):
    # expr的几类情况：int float bool nil string
    # 数据：int float bool nil
    # 函数名: string且能够在env之中找到
    # 特殊形式: string 且被定义在特殊形式之中
    """
    >>> expr = read_line('odd?')
    >>> scheme_eval(expr, create_global_frame())
    #[odd?]
    >>> expr = read_line('display')
    >>> scheme_eval(expr, create_global_frame())
    #[display]
    >>> expr = read_line('+')
    >>> scheme_eval(expr, create_global_frame())
    #[+]
    >>> expr = read_line('1')
    >>> scheme_eval(expr, create_global_frame())
    1
    >>> expr = read_line('begin')
    >>> expr in SPECIAL_FORM
    True
    >>> global_frame = create_global_frame()
    >>> global_frame.define("a", 2)
    >>> son_frame = Frame(global_frame)
    >>> expr = read_line('a')
    >>> scheme_eval(expr, create_global_frame())
    2

    """
    if is_literal(expr):
        return expr
    else:

        # expr是函数(包括自定义函数)或者变量名
        if expr in env:
            return env[expr]
        # expr是special form
        elif expr in SPECIAL_FORM:
            return SPECIAL_FORM[expr]
        else:
            raise SchemeError(str(expr) + " is unknown")

def eval_combination(expr, env, tail_flag = False):
    """对于组合表达式，获取函数名，再获取参数，然后apply函数到参数上
    >>> expr = read_line('(+ 1 2)')
    >>> eval_combination(expr, create_global_frame())
    3
    >>> expr = read_line('(* 3 4 (- 5 2) 1)')
    >>> eval_combination(expr, create_global_frame())
    36
    >>> expr = read_line('((lambda (x) (* x x)) 5)')
    >>> eval_combination(expr, create_global_frame())
    25
    >>> global_frame = create_global_frame()
    >>> son_frame = Frame(global_frame)
    >>> son_frame.define("a", 2)
    >>> grand_son_frame = Frame(son_frame)
    >>> expr = read_line('(* 3 4 (- 5 a) 1)')
    >>> scheme_eval(expr, grand_son_frame)
    36
    (define (-enumerate s rank) (if (null? s) nil (cons (cons rank cons ((car s) nil)_enumerate
                  ((cdr s) (+ rank 1))))))
    """
    if not isinstance(expr, Pair):
        raise SchemeError("wrong combination")

    # 有可能不是operator 那样的话，在具体执行的时候报错
    # 组合表达式有一元运算符，二元运算符，多元运算符
    indicator = scheme_eval(expr.first, env)
    operands = None
    if isinstance(indicator, Procedure):
        operands = scheme_map(env['eval'], expr.rest, env)
    elif isinstance(indicator, SpecForm):
        operands = expr.rest
    elif isinstance(indicator, MacroProcedure):
        operands = expr.rest

    else:
        raise SchemeError("indicator is invalid")
    return scheme_apply(indicator, operands, env)

def scheme_eval(expr, env, _ = None):
    """

    重写scheme_eval函数：
    参数：
        expr：
            第一种可能：单体类型，直接输出单体
            第二种可能：Pair类型，第Pair.first是element，Pair.rest是剩下的Pair;element可能是单体或者是Pair
        env:
            Frame类型，通过define和[]方法进行添加和访问
    返回：
        表达式求值 or
        错误信息
    逻辑：
        对于单体类型，直接返回单体
        对于Pair类型，进行表达式求值。首先衡量Pair.first获取操作符，然后衡量Pair.rest获取参数，之后进行求值。Pair.first仍然有可能是表达式，所以可以继续递归衡量。


    >>> expr = read_line('(+ 2 2)')
    >>> expr
    Pair('+', Pair(2, Pair(2, nil)))
    >>> scheme_eval(expr, create_global_frame())
    4
    >>> expr = read_line('odd?')
    >>> print(scheme_eval(expr, create_global_frame()))
    #[odd?]
    >>> expr = read_line('(+ 1 2)')
    >>> print(scheme_eval(expr, create_global_frame()))
    3
    >>> expr = read_line('(* 3 4 (- 5 2) 1)')
    >>> print(scheme_eval(expr, create_global_frame()))
    36
    >>> expr = read_line('(define x 15)')
    >>> print(scheme_eval(expr, create_global_frame()))
    x
    >>> expr = read_line('(quote (1 2))')
    >>> scheme_eval(expr, create_global_frame())
    Pair(1, Pair(2, nil))
    >>> expr = read_line("(cons 'car '('(1 2)))")
    >>> print(scheme_eval(expr, create_global_frame()))
    (car (quote (1 2)))
    >>> expr = read_line("(eval (cons 'car '('(1 2))))")
    >>> print(scheme_eval(expr, create_global_frame()))
    1
    >>> expr = read_line("(eval 1)")
    >>> print(scheme_eval(expr, create_global_frame()))
    1
    >>> expr = read_line("(eval '1)")
    >>> print(scheme_eval(expr, create_global_frame()))
    1
    >>> env = create_global_frame()
    >>> 'eval' in env
    True
    >>> expr = read_line("(eval '(+ 1 2))")
    >>> print(scheme_eval(expr, env))
    3
    >>> expr = read_line("(cons 1 nil)")
    >>> expr
    Pair("cons", Pair(1, Pair('nil', nil))
    >>> print(scheme_eval(expr, env))
    1

    尾递归测试
    >>> expr = read_line('(define (sum k n result) (if (= k n) result (sum (+ k 1) n (+ k result))))')
    >>> env = create_global_frame()
    >>> scheme_eval(expr, env)
    'sum'
    >>> env['sum'].tail_rec_flag
    True
    >>> expr1 = read_line('(sum 1 100 0)')
    >>> scheme_eval(expr1, env)


    >>> expr = read_line("((/ 1 0) (print 5))")
    >>> scheme_eval(expr, env)
    SchemeError

    """
    # 单体类型
    if not isinstance(expr, Pair):
        return eval_single(expr, env)
    # 复合类型
    comb_ret = eval_combination(expr, env)

    return comb_ret

def scheme_apply(indicator, args, env):
    """Apply Scheme PROCEDURE to argument values ARGS (a Scheme list) in
    environment ENV.
    假定，args已经全部是数字

    >>> env = create_global_frame()
    >>> fn = env["+"]
    >>> s = Pair(1, Pair(2, Pair(3, nil)))
    >>> scheme_apply(fn, s, create_global_frame())
    6

    >>> s = nil
    >>> scheme_apply(fn, s, create_global_frame())
    0
    >>> fn = env["modulo"]
    >>> s = Pair(3, Pair(2, nil))
    >>> scheme_apply(fn, s, create_global_frame())
    1
    >>> fn = env["abs"]
    >>> s = Pair(-3, nil)
    >>> scheme_apply(fn, s, create_global_frame())
    3
    >>> fn = env["eval"]
    >>> s = Pair(-3, nil)
    >>> scheme_apply(fn, s, create_global_frame())
    -3
    """
    # PROBLEM 2
    #
    if not isinstance(indicator, (Procedure, SpecForm, MacroProcedure)) or (not isinstance(args, Pair) and args is not nil):

        raise SchemeError("wrong expression: Indicator or Args is wrong")

    if isinstance(indicator, (Procedure, MacroProcedure)):
        return indicator.apply(args, env)
    else:
        return indicator.apply(args, scheme_eval, env)

################
# Environments #
################

class Frame(object):
    """An environment frame binds Scheme symbols to Scheme values."""

    def __init__(self, parent):
        """An empty frame with parent frame PARENT (which may be None)."""
        "Your Code Here"
        # Note: you should define instance variables self.parent and self.bindings
        self.parent = parent
        self.bindings = {}
    def __repr__(self):
        if self.parent is None:
            return '<Global Frame>'
        s = sorted(['{0}: {1}'.format(k, v) for k, v in self.bindings.items()])
        return '<{{{0}}} -> {1}>'.format(', '.join(s), repr(self.parent))

    def define(self, symbol, value):
        """Define Scheme SYMBOL to have VALUE."""
        self.bindings[symbol] = value
    def __getitem__(self, item):
        """找不到就往父本找，实在找不到就返回None"""
        if item in self.bindings:
            return self.bindings[item]
        else:
            if self.parent:
                return self.parent[item]
            else:
                return None
    def __contains__(self, item):
        """如果自己不包含，就看看父本包不包含"""
        if item in self.bindings:
            return True
        else:
            if self.parent:
                return item in self.parent
            else:
                return False

    # BEGIN PROBLEM 2/3
    "*** YOUR CODE HERE ***"
    # END PROBLEM 2/3

##############
# Procedures #
##############

class Procedure(object):
    """The supertype of all Scheme procedures."""

def scheme_procedurep(x):
    """
    >>> expr = scheme_eval(read_line('odd?'), create_global_frame())
    >>> scheme_procedurep(expr)
    True
    """
    return isinstance(x, Procedure)

def check_formals(fn, args):
    """
    检验内部函数的形参
    """
    if not isinstance(args, Pair) and args is not nil:
            raise SchemeError("wrong in apply")
    arg_num = len(args)

    formals_list_num = len(fn.__code__.co_varnames)
    min_formals_num = fn.__code__.co_argcount

    min_num = min_formals_num
    if min_formals_num != formals_list_num:
        max_num = float('inf')
    else:
        max_num = min_formals_num
    if arg_num < min_num or arg_num > max_num:
        raise SchemeError("{} arguments to {} arguments expected but {} given".format(min_num, max_num, arg_num))

class BuiltinProcedure(Procedure):
    """A Scheme procedure defined as a Python function."""

    def __init__(self, fn, use_env=False, name='builtin'):
        self.name = name
        self.fn = fn
        self.use_env = use_env

    def __str__(self):
        return '#[{0}]'.format(self.name)

    def apply(self, args, env):
        """Apply SELF to ARGS in ENV, where ARGS is a Scheme list.
        # 假定args的所有参数都是单个表达式而不是复合表达式

        >>> env = create_global_frame()
        >>> plus = env.bindings['+']
        >>> twos = Pair(2, Pair(2, nil))
        >>> plus.apply(twos, env)
        4

        >>> fn = env["+"]
        >>> s = Pair(1, Pair(2, Pair(3, nil)))
        >>> fn.apply(s, create_global_frame())
        6

        >>> s = nil
        >>> fn.apply(s, create_global_frame())
        0
        >>> fn = env["modulo"]
        >>> s = Pair(3, Pair(2, nil))
        >>> fn.apply(s, create_global_frame())
        1
        >>> fn = env["abs"]
        >>> s = Pair(-3, nil)
        >>> fn.apply(s, create_global_frame())
        3
        >>> fn = env["cons"]
        >>> s = Pair(1, Pair(nil, nil))
        >>> fn.apply(s, create_global_frame())
        Pair(1, nil)
        """
        # BEGIN PROBLEM 2
        "*** YOUR CODE HERE ***"

        def get_arg_list(args):
            if args is nil:
                return []
            else:
                first = args.first
                # if self.use_env and  isinstance(args.first, str):
                #     first = env[args.first]
                return [first] + get_arg_list(args.rest)

        if self.use_env:
            args = args.first
            return self.fn(args, env)
        else:
            check_formals(self.fn, args)
            arg_list = get_arg_list(args)
            return self.fn(*arg_list)
        # END PROBLEM 2

class LambdaProcedure(Procedure):
    """A procedure defined by a lambda expression or a define form."""

    def __init__(self, formals, body, env, tail_rec_flag = False):
        """A procedure with formal parameter list FORMALS (a Scheme list),
        whose body is the Scheme list BODY, and whose parent environment
        starts with Frame ENV."""
        self.formals = formals
        self.body = body
        self.env = env
        self.tail_rec_flag = tail_rec_flag

    # BEGIN PROBLEM 3
    "*** YOUR CODE HERE ***"
    def apply(self, args, _):

        def bound_name_to_value(formals, args, cur_env):
            if args is nil:
                return
            else:
                cur_env.define(formals.first, args.first)
                bound_name_to_value(formals.rest, args.rest, cur_env)

        if len(args) != len(self.formals):
            raise SchemeError("{} arguments is expected but {} was given".format(len(self.formals), len(args)))
        cur_env = Frame(self.env)
        bound_name_to_value(self.formals, args, cur_env)

        if self.tail_rec_flag:
            return Thunk(Pair("begin",self.body), cur_env)
        else:
            return scheme_eval(Pair("begin", self.body), cur_env)
    # END PROBLEM 3
    def __str__(self):

        return str(Pair('lambda', Pair(self.formals, self.body)))

    def __repr__(self):
        return 'LambdaProcedure({0}, {1}, {2})'.format(
            repr(self.formals), repr(self.body), repr(self.env))

def add_builtins(frame, funcs_and_names):
    """Enter bindings in FUNCS_AND_NAMES into FRAME, an environment frame,
    as built-in procedures. Each item in FUNCS_AND_NAMES has the form
    (NAME, PYTHON-FUNCTION, INTERNAL-NAME)."""
    for name, fn, proc_name in funcs_and_names:
        frame.define(name, BuiltinProcedure(fn, name=proc_name))

#################
# Special Forms #
#################

class SpecForm(object):
    def __init__(self, indicator, fn):
        self.indicator = indicator
        self.fn = fn
    def apply(self, body, eval_fn, env):
        return self.fn(Pair(self.indicator, body), eval_fn, env)
SPECIAL_FORM = {}

def is_literal(expr):
    # 这里有缺陷
    literal_expr = (int, float, bool, type(nil))
    return isinstance(expr, literal_expr) or expr is None
def is_expr(expr):
    all_expr = (int, float, bool, str, type(nil), Pair)
    return isinstance(expr, all_expr)
def is_symbol(expr):
    return isinstance(expr, str)

def sp_builtin(name):
    """An annotation to convert a Python function into a BuiltinProcedure."""
    def add(fn):
        SPECIAL_FORM[name] = SpecForm(name, fn)
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
        if is_tail_recursion(expr, env):
            lambda_fn.tail_rec_flag = True
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
        if test == "else":
            if subexpr != nil:
                ret = scheme_eval(Pair("begin", subexpr), env)
            else:
                ret = True
            break
        condition = scheme_eval(test, env)
        if is_true(condition):
            if subexpr != nil:
                ret = scheme_eval(Pair("begin", subexpr), env)
            else:
                ret = condition
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
    if expr.first != "define-macro":
        raise SchemeError("Not define-macro experssion")
    if len(expr) < 3  :
        raise SchemeError("Invalid define-macro expression")

    be_bound = expr.rest.first
    if not isinstance(be_bound, Pair):
        raise SchemeError("Invalid define-macro expression")
    else:
        while be_bound != nil:
            if not is_symbol(be_bound.first):
                raise SchemeError("Invalid define-macro expression")
            be_bound = be_bound.rest
@sp_builtin("define-macro")
def eval_macro(expr, scheme_eval, env):
    """
    >>> str1 = "(define-macro (for formal iterable body) (list 'map (list 'lambda (list formal) body) iterable))"
    >>> expr1 = read_line(str1)
    >>> env = create_global_frame()
    >>> scheme_eval(expr1, env)
    >>> env['for'].formals

    >>> env['for'].body

    >>> str2 = "(define (map f lst) (if (null? lst) nil (cons (f (car lst)) (map f (cdr lst)))))"
    >>> expr2 = read_line(str2)
    >>> scheme_eval(expr2, env)

    >>> str3 = "(for i '(1 2 3) (* i i))"
    >>> expr3 = read_line(str3)
    >>> scheme_eval(expr3, env)


    """
    valid_macro(expr)

    be_bound = expr.rest.first
    bound_to = expr.rest.rest
    name = be_bound.first
    formals = be_bound.rest
    body = bound_to
    macro_fn = MacroProcedure(formals, body)
    env.define(name, macro_fn)
    return name

# Utility methods for checking the structure of Scheme programs
def validate_form(expr, min, max=float('inf')):
    """Check EXPR is a proper list whose length is at least MIN and no more
    than MAX (default: no maximum). Raises a SchemeError if this is not the
    case.

    >>> validate_form(read_line('(a b)'), 2)
    """
    if not scheme_listp(expr):
        raise SchemeError('badly formed expression: ' + repl_str(expr))
    length = len(expr)
    if length < min:
        raise SchemeError('too few operands in form')
    elif length > max:
        raise SchemeError('too many operands in form')

def validate_formals(formals):
    """Check that FORMALS is a valid parameter list, a Scheme list of symbols
    in which each symbol is distinct. Raise a SchemeError if the list of
    formals is not a list of symbols or if any symbol is repeated.

    >>> validate_formals(read_line('(a b c)'))
    """
    symbols = set()
    def validate_and_add(symbol, is_last):
        if not scheme_symbolp(symbol):
            raise SchemeError('non-symbol: {0}'.format(symbol))
        if symbol in symbols:
            raise SchemeError('duplicate symbol: {0}'.format(symbol))
        symbols.add(symbol)

    while isinstance(formals, Pair):
        validate_and_add(formals.first, formals.rest is nil)
        formals = formals.rest

    # here for compatibility with DOTS_ARE_CONS
    if formals != nil:
        validate_and_add(formals, True)

def validate_procedure(procedure):
    """Check that PROCEDURE is a valid Scheme procedure."""
    if not scheme_procedurep(procedure):
        raise SchemeError('{0} is not callable: {1}'.format(
            type(procedure).__name__.lower(), repl_str(procedure)))

#################
# Dynamic Scope #
#################

class MuProcedure(Procedure):
    """A procedure defined by a mu expression, which has dynamic scope.
     _________________
    < Scheme is cool! >
     -----------------
            \   ^__^
             \  (oo)\_______
                (__)\       )\/\
                    ||----w |
                    ||     ||
    """

    def __init__(self, formals, body):
        """A procedure with formal parameter list FORMALS (a Scheme list) and
        Scheme list BODY as its definition."""
        self.formals = formals
        self.body = body


    def __str__(self):
        return str(Pair('mu', Pair(self.formals, self.body)))

    def __repr__(self):
        return 'MuProcedure({0}, {1})'.format(
            repr(self.formals), repr(self.body))
    def apply(self, args, env):

        def bound_name_to_value(formals, args):
            if args is nil:
                return
            else:
                cur_env.define(formals.first, args.first)
                bound_name_to_value(formals.rest, args.rest)

        if len(args) != len(self.formals):
            raise SchemeError("{} arguments is expected but {} was given".format(len(self.formals), len(args)))
        cur_env = Frame(env)
        bound_name_to_value(self.formals, args)

        return scheme_eval(Pair("begin", self.body), cur_env)
class MacroProcedure(object):
    def __init__(self, formals, body):
        """macro的参数传进来之前已经被加上了quote修饰
        """
        self.formals = formals
        self.body = body
    def apply(self, args, env):
        def bound_name_to_value(formals, args):
            if args is nil:
                return
            else:
                env.define(formals.first, args.first)
                bound_name_to_value(formals.rest, args.rest)
        if len(args) != len(self.formals):
            raise SchemeError("define-macro:{} arguments is expected but {} was given".format(len(self.formals), len(args)))
        bound_name_to_value(self.formals, args)
        body = Pair("begin", self.body)
        expr = scheme_eval(body, env)
        return scheme_eval(expr, env)
##################
# Tail Recursion #
##################


# Make classes/functions for creating tail recursive programs here?

def complete_apply(procedure, args, env):
    """Apply procedure to args in env; ensure the result is not a Thunk.
    Right now it just calls scheme_apply, but you will need to change this
    if you attempt the optional questions."""

    # Add stuff here?
    val = scheme_apply(procedure, args, env)
    return val

# BEGIN PROBLEM 8
"*** YOUR CODE HERE ***"
def is_tail_recursion(expr, env):
    """
    >>> env = create_global_frame()
    >>> env.define("sum", LambdaProcedure(0,0,env))
    >>> expr = read_line('(define (sum k n result) (if (= k n) result (sum (+ k 1) n (+ k result))))')
    >>> body = read_line( '(if (= k n) result (sum (+ k 1) n (+ k result)))')
    >>> body

    >>> signature = read_line( '(sum k n result)')
    >>> signature

    >>> is_tail_recursion(expr, env)
    True
    """
    def match_procedure(body, signature):
        if len(body) != len(signature):
            return False
        if body.first == signature.first:
            return True
        else:
            return False
    def match_specform(form, signature):
        str_indicator = form.first
        if str_indicator == "if":
            pred = form.rest.rest.first
            altern = form.rest.rest.rest.first
            return match(pred, signature) and match(altern, signature) # 这里可能有问题
        elif str_indicator == "cond":
            sub_clause_set = form.rest
            while sub_clause_set != nil:
                sub_clause = sub_clause_set.first
                altern = sub_clause.rest.first
                if not match(altern, signature):
                    return False
                sub_clause_set = sub_clause_set.rest
            return True
        elif str_indicator == "begin":
            rest = form.rest
            while rest.rest != nil:
                rest = rest.rest
            return match(rest.first, signature)
        elif str_indicator == "let":
            body = form.rest.rest
            return match(Pair("begin", body), signature)
        else:
            return False

    def match(body, signature):
        if not isinstance(body, Pair):
            return True # 单个元素视为尾递归？
        else:
            indicator = scheme_eval(body.first, env)
            if isinstance(indicator, Procedure):
                return match_procedure(body, signature)
            elif isinstance(indicator, SpecForm):
                return match_specform(body, signature)
            else:
                return False

    signature = expr.rest.first
    body = expr.rest.rest
    return match(Pair("begin", body), signature)



class Thunk(object):
    """
    Thunk是完成尾递归优化的特殊类型，代替类。存储尾递归函数的函数体和当前的环境。
    每次函数调用时，如果发现是尾递归函数，那么就直接返回Thunk
    """
    def __init__(self, expr, env):
        self.expr = expr
        self.env = env

# END PROBLEM 8



####################
# Extra Procedures #
####################

def scheme_map(fn, s, env):
    """
    将fn作用在s的每一个元素上，返回的仍然是Pair
    >>> expr = scheme_eval(read_line('odd?'), create_global_frame())
    >>> s = Pair(1, Pair(2, Pair(3, nil)))
    >>> ret = scheme_map(expr, s,create_global_frame())
    >>> ret
    Pair(True, Pair(False, Pair(True, nil)))
    >>> s == ret
    """
    validate_type(fn, scheme_procedurep, 0, 'map')
    validate_type(s, scheme_listp, 1, 'map')
    return s.map(lambda x: complete_apply(fn, Pair(x, nil), env))

def scheme_filter(fn, s, env):
    validate_type(fn, scheme_procedurep, 0, 'filter')
    validate_type(s, scheme_listp, 1, 'filter')
    head, current = nil, nil
    while s is not nil:
        item, s = s.first, s.rest
        if complete_apply(fn, Pair(item, nil), env):
            if head is nil:
                head = Pair(item, nil)
                current = head
            else:
                current.rest = Pair(item, nil)
                current = current.rest
    return head

def scheme_reduce(fn, s, env):
    """
    >>> expr = scheme_eval(read_line('+'), create_global_frame())
    >>> s = Pair(1, Pair(2, Pair(3, nil)))
    >>> ret = scheme_reduce(expr, s,create_global_frame())
    >>> ret
    6
    """
    validate_type(fn, scheme_procedurep, 0, 'reduce')
    validate_type(s, lambda x: x is not nil, 1, 'reduce')
    validate_type(s, scheme_listp, 1, 'reduce')
    value, s = s.first, s.rest
    while s is not nil:
        value = complete_apply(fn, scheme_list(value, s.first), env)
        s = s.rest
    return value

################
# Input/Output #
################

def read_eval_print_loop(next_line, env, interactive=False, quiet=False,
                         startup=False, load_files=()):
    """Read and evaluate input until an end of file or keyboard interrupt."""
    if startup:
        for filename in load_files:
            scheme_load(filename, True, env)
    while True:
        try:
            src = next_line()
            while src.more_on_line:
                expression = scheme_read(src)
                result = scheme_eval(expression, env)
                while isinstance(result, Thunk):
                    result = scheme_eval(result.expr, result.env)
                if not quiet and result is not None:
                    print(repl_str(result))
        except (SchemeError, SyntaxError, ValueError, RuntimeError) as err:
            if (isinstance(err, RuntimeError) and
                'maximum recursion depth exceeded' not in getattr(err, 'args')[0]):
                raise
            elif isinstance(err, RuntimeError):
                print('Error: maximum recursion depth exceeded')
            else:
                print('Error:', err)
                import logging
                logging.exception(err)
        except KeyboardInterrupt:  # <Control>-C
            if not startup:
                raise
            print()
            print('KeyboardInterrupt')
            if not interactive:
                return
        except EOFError:  # <Control>-D, etc.
            print()
            return

def scheme_load(*args):
    """Load a Scheme source file. ARGS should be of the form (SYM, ENV) or
    (SYM, QUIET, ENV). The file named SYM is loaded into environment ENV,
    with verbosity determined by QUIET (default true)."""
    if not (2 <= len(args) <= 3):
        expressions = args[:-1]
        raise SchemeError('"load" given incorrect number of arguments: '
                          '{0}'.format(len(expressions)))
    sym = args[0]
    quiet = args[1] if len(args) > 2 else True
    env = args[-1]
    if (scheme_stringp(sym)):
        sym = eval(sym)
    validate_type(sym, scheme_symbolp, 0, 'load')
    with scheme_open(sym) as infile:
        lines = infile.readlines()
    args = (lines, None) if quiet else (lines,)
    def next_line():
        return buffer_lines(*args)

    read_eval_print_loop(next_line, env, quiet=quiet)

def scheme_open(filename):
    """If either FILENAME or FILENAME.scm is the name of a valid file,
    return a Python file opened to it. Otherwise, raise an error."""
    try:
        return open(filename)
    except IOError as exc:
        if filename.endswith('.scm'):
            raise SchemeError(str(exc))
    try:
        return open(filename + '.scm')
    except IOError as exc:
        raise SchemeError(str(exc))

def create_global_frame():
    """Initialize and return a single-frame environment with built-in names."""
    env = Frame(None)
    env.define('eval',
               BuiltinProcedure(scheme_eval, True, 'eval'))
    env.define('apply',
               BuiltinProcedure(complete_apply, True, 'apply'))
    env.define('load',
               BuiltinProcedure(scheme_load, True, 'load'))
    env.define('procedure?',
               BuiltinProcedure(scheme_procedurep, False, 'procedure?'))
    env.define('map',
               BuiltinProcedure(scheme_map, True, 'map'))
    env.define('filter',
               BuiltinProcedure(scheme_filter, True, 'filter'))
    env.define('reduce',
               BuiltinProcedure(scheme_reduce, True, 'reduce'))
    env.define('undefined', None)
    add_builtins(env, BUILTINS)
    return env


if __name__ == "__main__":
    str1 = "(define-macro (for formal iterable body) (list 'map (list 'lambda (list formal) body) iterable))"
    expr1 = read_line(str1)
    env = create_global_frame()
    scheme_eval(expr1, env)

    str2 = "(define (map f lst) (if (null? lst) nil (cons (f (car lst)) (map f (cdr lst)))))"
    expr2 = read_line(str2)
    scheme_eval(expr2, env)

    str3 = "(for i '(1 2 3) (* i i))"
    expr3 = read_line(str3)
    ret = scheme_eval(expr3, env)
    print(ret)

# @main
# def run(*argv):
#     import argparse
#     parser = argparse.ArgumentParser(description='CS 61A Scheme Interpreter')
#     parser.add_argument('--pillow-turtle', action='store_true',
#                         help='run with pillow-based turtle. This is much faster for rendering but there is no GUI')
#     parser.add_argument('--turtle-save-path', default=None,
#                         help='save the image to this location when done')
#     parser.add_argument('-load', '-i', action='store_true',
#                        help='run file interactively')
#     parser.add_argument('file', nargs='?',
#                         type=argparse.FileType('r'), default=None,
#                         help='Scheme file to run')
#     args = parser.parse_args()
#
#     import scheme
#     scheme.TK_TURTLE = not args.pillow_turtle
#     scheme.TURTLE_SAVE_PATH = args.turtle_save_path
#     sys.path.insert(0, '')
#     sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(scheme.__file__))))
#
#     next_line = buffer_input
#     interactive = True
#     load_files = []
#
#     if args.file is not None:
#         if args.load:
#             load_files.append(getattr(args.file, 'name'))
#         else:
#             lines = args.file.readlines()
#             def next_line():
#                 return buffer_lines(lines)
#             interactive = False
#
#     read_eval_print_loop(next_line, create_global_frame(), startup=True,
#                          interactive=interactive, load_files=load_files)
#     tscheme_exitonclick()