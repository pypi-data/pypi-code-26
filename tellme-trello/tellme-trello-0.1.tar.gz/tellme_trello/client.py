from trello import TrelloClient
from tellme_trello import settings


def get_client():
    client = TrelloClient(
        api_key=settings.API_KEY,
        api_secret=settings.API_SECRET,
        token=settings.TOKEN,
        token_secret=settings.TOKEN_SECRET)
    return client
