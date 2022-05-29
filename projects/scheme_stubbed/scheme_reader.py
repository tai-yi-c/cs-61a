"""This module implements the built-in data types of the Scheme language, along
with a parser for Scheme expressions.

In addition to the types defined in this file, some data types in Scheme are
represented by their corresponding type in Python:
    number:       int or float
    symbol:       string
    boolean:      bool
    unspecified:  None

The __repr__ method of a Scheme value will return a Python expression that
would be evaluated to the value, where possible.

The __str__ method of a Scheme value will return a Scheme expression that
would be read to the value, where possible.
"""

from __future__ import print_function  # Python 2 compatibility

import numbers

from ucb import main, trace, interact
from scheme_tokens import tokenize_lines, DELIMITERS
from buffer import Buffer, InputReader, LineReader

# Pairs and Scheme lists

class Pair(object):
    """A pair has two instance attributes: first and rest. rest must be a Pair or nil

    >>> s = Pair(1, Pair(2, nil))
    >>> s
    Pair(1, Pair(2, nil))
    >>> print(s)
    (1 2)
    >>> print(s.map(lambda x: x+4))
    (5 6)
    """
    def __init__(self, first, rest):
        from scheme_builtins import scheme_valid_cdrp, SchemeError
        if not scheme_valid_cdrp(rest):
            raise SchemeError("cdr can only be a pair, nil, or a promise but was {}".format(rest))
        self.first = first
        self.rest = rest

    def __repr__(self):
        return 'Pair({0}, {1})'.format(repr(self.first), repr(self.rest))

    def __str__(self):
        s = '(' + repl_str(self.first)
        rest = self.rest
        while isinstance(rest, Pair):
            s += ' ' + repl_str(rest.first)
            rest = rest.rest
        if rest is not nil:
            s += ' . ' + repl_str(rest)
        return s + ')'

    def __len__(self):
        n, rest = 1, self.rest
        while isinstance(rest, Pair):
            n += 1
            rest = rest.rest
        if rest is not nil:
            raise TypeError('length attempted on improper list')
        return n

    def __eq__(self, p):
        if not isinstance(p, Pair):
            return False
        return self.first == p.first and self.rest == p.rest
    # def __iter__(self):
    #     return self
    # def __next__(self):
    #     if self is nil:
    #         raise StopIteration()
    #     else:
    #         ret = self.first
    #         self = self.rest
    #         return ret
    def map(self, fn):
        """Return a Scheme list after mapping Python function FN to SELF.
        >>> s = Pair(1, Pair(2, Pair(3, nil)))
        >>> from scheme_builtins import *
        >>> s.map(scheme_oddp)
        Pair(True, Pair(False, Pair(True, nil)))
        """

        mapped = fn(self.first)
        if self.rest is nil or isinstance(self.rest, Pair):
            return Pair(mapped, self.rest.map(fn))
        else:
            raise TypeError('ill-formed list (cdr is a promise)')

class nil(object):
    """The empty list"""

    def __repr__(self):
        return 'nil'

    def __str__(self):
        return '()'

    def __len__(self):
        return 0

    def map(self, fn):
        return self

nil = nil() # Assignment hides the nil class; there is only one instance

# Scheme list parser

# Quotation markers
quotes = {"'":  'quote',
          '`':  'quasiquote',
          ',':  'unquote'}


# 目前输入 '(1 2 3) 会报错

def convert_to_pair(s):
    """
    >>> p = convert_to_pair("(+ 1 2) (+ 3 4)")
    >>> print([i for i in p])

    >>> p = convert_to_pair("(lambda () 2)")
    >>> print(p)
    >>> p

    >>> isinstance(nil, Pair)
    >>> isinstance(nil, type(nil))
    >>> len(p)
    """

    return scheme_read(Buffer(tokenize_lines([s])))

_is_single = lambda first, src:  first !="(" and first != ")" and first not in quotes # and not src.more_on_line
_map = lambda single: nil if single == "nil" else single
_is_combination = lambda first, src: (first == "(" or first in quotes) # and src.more_on_line
def scheme_read(src):

    """Read the next expression from SRC, a Buffer of tokens.

    # 单体测试
    >>> scheme_read(Buffer(tokenize_lines(['nil'])))
    nil
    >>> scheme_read(Buffer(tokenize_lines(['1'])))
    1
    >>> scheme_read(Buffer(tokenize_lines(['true'])))
    True

    # 复合表达式测试
    >>> scheme_read(Buffer(tokenize_lines(['(+ 1 2)'])))
    Pair('+', Pair(1, Pair(2, nil)))
    >>> scheme_read(Buffer(tokenize_lines(['(+ (+ 1 3) 2)'])))
    Pair('+', Pair(Pair('+', Pair(1, Pair(3, nil))), Pair(2, nil)))
    >>> scheme_read(Buffer(tokenize_lines(["(1 3)"])))
    Pair(1, Pair(3, nil))

    # quotes测试
    >>> scheme_read(Buffer(tokenize_lines(["'1"])))
    Pair("quote", Pair(1, nil))
    >>> scheme_read(Buffer(tokenize_lines(["('3)"])))
    Pair(Pair("quote", Pair(3, nil)), nil)
    >>> scheme_read(Buffer(tokenize_lines(["'(1 3)"])))
    Pair("quote", Pair(Pair(1, Pair(3, nil)), nil))
    >>> scheme_read(Buffer(tokenize_lines(["('1 3)"])))
    Pair(Pair("quote", Pair(1, nil)), Pair(3, nil))
    >>> scheme_read(Buffer(tokenize_lines(["('(1 3) 3)"])))
    Pair(Pair("quote", Pair(Pair(1, Pair(3, nil)), nil)), Pair(3, nil))
    >>> scheme_read(Buffer(tokenize_lines(["(+ '1 2)"])))
    Pair('+', Pair(Pair("quote", Pair(1, nil)), Pair(2, nil)))
    >>> scheme_read(Buffer(tokenize_lines(["(cons 'car '('(1 2)))"])))
    Pair('cons', Pair(Pair("'", Pair('car', nil)), Pair(Pair("'", Pair(Pair("'", Pair(Pair(1, Pair(2, nil)), nil)), nil)), nil)))
    >>> scheme_read(Buffer(tokenize_lines(["'('(1 2))"])))
    Pair("'", Pair(Pair("'", Pair(Pair(1, Pair(2, nil)), nil)), nil))
    >>> scheme_read(Buffer(tokenize_lines(["(cons 1 nil)"])))
    Pair("cons", Pair(1, Pair(nil, nil)))

    # 错误测试
    >>> scheme_read(Buffer(tokenize_lines([")"])))
    SyntaxError
    >>> scheme_read(Buffer(tokenize_lines(["("])))
    SyntaxError
    >>> scheme_read(Buffer(tokenize_lines(["(1 2 3 4"])))
    SyntaxError
    >>> scheme_read(Buffer(tokenize_lines(["'1 2"])))
    SyntaxError
    """
    if src.current() is None:
        raise EOFError
    # BEGIN PROBLEM 1/2
    "*** YOUR CODE HERE ***"
    # 正常输入和异常输入：符合scheme列表的就是正常输入，不符合的就是异常输入
    # 这里的正常输入就是可以转化为Pair递归列表的输入，不管表达式什么的，只要求转化成为列表
    first = src.pop_first()
    if _is_single(first, src): # 可能正确的单体表达式
        return _map(first)
    elif _is_combination(first, src): # 可能正确的复合表达式
        if first in quotes:
            return Pair(quotes[first], Pair(scheme_read(src), nil))
        else:
            return read_tail(src)
    else: # 一定有哪里错了
        raise SyntaxError("expression is wrong")

    # END PROBLEM 1/2
def read_tail(src):
    """Return the remainder of a list in SRC, starting before an element or ).

    >>> read_tail(Buffer(tokenize_lines([')'])))
    nil
    >>> read_tail(Buffer(tokenize_lines(['2 3)'])))
    Pair(2, Pair(3, nil))
    """
    # 语义，读取到第一个无匹配的括号为止

    try:
        if src.current() is None:
            raise SyntaxError('unexpected end of file')
        # BEGIN PROBLEM 1
        "*** YOUR CODE HERE ***"
        first = src.pop_first()
        if first == ")":# 读到这个表达式的尾部了
            return nil
        else:
            if first == "(":
                left = read_tail(src)
                # src上一步被改变了
                tail = read_tail(src)
                return Pair(left, tail)
            elif first in quotes:
                head = Pair(quotes[first], Pair(scheme_read(src), nil))
                tail = read_tail(src)
                return Pair(head, tail)
            else:
                return Pair(_map(first), read_tail(src))
        # END PROBLEM 1
    except EOFError:
        raise SyntaxError('unexpected end of file')

# Convenience methods
# @trace
def buffer_input(prompt='scm> '):
    """Return a Buffer instance containing interactive input."""
    return Buffer(tokenize_lines(InputReader(prompt)))

def buffer_lines(lines, prompt='scm> ', show_prompt=False):
    """Return a Buffer instance iterating through LINES."""
    if show_prompt:
        input_lines = lines
    else:
        input_lines = LineReader(lines, prompt)
    return Buffer(tokenize_lines(input_lines))

def read_line(line):
    """Read a single string LINE as a Scheme expression."""
    return scheme_read(Buffer(tokenize_lines([line])))

def repl_str(val):
    """Should largely match str(val), except for booleans and undefined."""
    if val is True:
        return "#t"
    if val is False:
        return "#f"
    if val is None:
        return "undefined"
    if isinstance(val, numbers.Number) and not isinstance(val, numbers.Integral):
        return repr(val)  # Python 2 compatibility
    return str(val)

# Interactive loop
def read_print_loop():
    """Run a read-print loop for Scheme expressions."""
    while True:
        try:
            src = buffer_input('read> ')
            while src.more_on_line:
                expression = scheme_read(src)
                print('str :', expression)
                print('repr:', repr(expression))
        except (SyntaxError, ValueError) as err:
            print(type(err).__name__ + ':', err)
        except (KeyboardInterrupt, EOFError):  # <Control>-D, etc.
            print()
            return

@main
def main(*args):
    if len(args) and '--repl' in args:
        read_print_loop()
