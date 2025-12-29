"""
Simple calculator module with basic arithmetic operations.
"""

def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract b from a."""
    return a - b

def multiply(a, b):
    """Multiply two numbers."""
    return a * b

def divide(a, b):
    """Divide a by b. Raises ValueError if b is zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def power(a, b):
    """Raise a to the power of b."""
    return a ** b

def modulo(a, b):
    """Return the remainder of a divided by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a % b

def square_root(a):
    """Calculate the square root of a number."""
    if a < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return a ** 0.5

def factorial(n):
    """Calculate the factorial of a non-negative integer."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def absolute(n):
    """Return the absolute value of a number."""
    return n if n >= 0 else -n

def is_even(n):
    """Check if a number is even."""
    return n % 2 == 0

def is_odd(n):
    """Check if a number is odd."""
    return n % 2 != 0

def average(numbers):
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

