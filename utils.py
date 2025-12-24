def format_name(first, last):
    """Format first and last name."""
    return f"{first} {last}"

def get_initials(name):
    """Get initials from a name."""
    parts = name.split()
    return "".join([p[0].upper() for p in parts if p])

