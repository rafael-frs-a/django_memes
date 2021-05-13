def inverse_case(text):
    return ''.join(c.lower() if c.isupper() else c.upper() for c in text)
