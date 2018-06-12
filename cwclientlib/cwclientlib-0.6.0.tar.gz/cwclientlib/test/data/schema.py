from yams.buildobjs import EntityType, Bytes, String


class User(EntityType):
    name = String(required=True)
    picture = Bytes()
    ssh_pubkey = Bytes()
