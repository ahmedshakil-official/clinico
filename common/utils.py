import secrets
import string


def get_random_string(length=12, allowed_chars=None):
    """
    Return a securely generated random string of specified length.
    By default, uses uppercase/lowercase letters and digits.
    """
    if allowed_chars is None:
        allowed_chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(allowed_chars) for _ in range(length))
