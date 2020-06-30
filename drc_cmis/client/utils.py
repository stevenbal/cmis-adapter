from django.utils.crypto import get_random_string as _get_random_string


def get_random_string(number: int = 6) -> str:
    allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return _get_random_string(length=number, allowed_chars=allowed_chars)
