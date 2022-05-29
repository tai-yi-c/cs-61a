def a_plus_abs_b(a, b):

    if b < 0:
        f = sum(a,-b)
    else:
        f = sum(a,b)
    return f(a, b)

f(1,2)