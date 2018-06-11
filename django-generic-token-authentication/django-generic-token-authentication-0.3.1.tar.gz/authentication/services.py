from django.conf import settings

def retrieve_token_service(repository):
    """
    Creates a new token for the given user
    """
    def _retrieve(user):
        (token, refresh_token) = repository.create_token(user)
        return (token, refresh_token)

    return _retrieve

def logout_service(repository):
    """
    Deletes a single token
    """
    def _logout(user, token):
        repository.logout(user, token)

    return _logout

def logout_all_service(repository):
    """
    Deletes all tokens of user
    """
    def _logout(user):
        repository.delete_by_user(user)

    return _logout

def refresh_token_service(repository):
    """
    Refreshes a user's token
    """
    def _refresh(user, token, refresh_token):
        (token, refresh_token) = repository.refresh_token(user, token, refresh_token)
        return (token, refresh_token)

    return _refresh