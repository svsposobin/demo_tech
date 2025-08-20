from secrets import token_urlsafe


def generate_session_token(_len: int = 32) -> str:
    """Случайный URL-Безопасный токен"""
    return token_urlsafe(_len)
