import hashlib

def file_checksum(*args):
    if len(args) == 0:
        raise AttributeError("Checksum error: a file path is required.")
    file_path = args[0]
    hash_algo = 'md5'
    if len(args) > 1:
        hash_algo = args[1]
    if hash_algo not in ['md5', 'sha1']:
        raise AttributeError(f"Checksum error: {hash_algo} is not a supported checksum algorithm.")
    if hash_algo == 'md5':
        hash_provider = hashlib.md5()
    else:
        hash_provider = hashlib.sha1()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_provider.update(chunk)
    return hash_provider.hexdigest()