# Return how many digits a number has
def count_digits(n):
    return 1 + count_digits(n%10) if n>=10 else 1

# Casts an integer to a string with n digits, filling the remainder with zeros.
def to_n_digits(x, n):
    cn = count_digits(x)
    if cn > n:
        raise Exception('Too few digits for this number.')
        return None
    else:
        return '0'*(n-cn) + str(x)
