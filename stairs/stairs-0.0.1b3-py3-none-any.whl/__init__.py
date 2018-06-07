from .transaction import Transaction


def configure(url: str):
    if not url:
        from stairs.errors import BadDatabaseError
        raise BadDatabaseError('bad database URI: cannot be empty')

    from . import conf
    conf.DATABASE_URL = url


__all__ = ('Transaction',)
