"""
Utility functions for common operations.
"""

def format_name(first_name, last_name):
    """Format first and last name into full name."""
    return f"{first_name} {last_name}".strip()

def get_initials(name):
    """Get initials from a full name."""
    parts = name.split()
    if not parts:
        return ""
    return "".join([part[0].upper() for part in parts if part])

def reverse_string(text):
    """Reverse a string."""
    return text[::-1]

def capitalize_words(text):
    """Capitalize the first letter of each word."""
    return " ".join([word.capitalize() for word in text.split()])

def count_words(text):
    """Count the number of words in a string."""
    if not text or not text.strip():
        return 0
    return len(text.split())

