#!/usr/bin/env python3

from getpass import getpass
from subprocess import check_call
from tempfile import NamedTemporaryFile
import os

from .encryption import Encryption
from .storage import Storage


def main():
    storage = Storage()

    message = storage.get()
    content = None

    while content is None:
        if message:
            passphrase = getpass("Enter your passphrase: ")
        else:
            passphrase = None
            passphrase_confirmation = None
            while not passphrase or passphrase != passphrase_confirmation:
                passphrase = getpass("Enter your new passphrase: ")
                passphrase_confirmation = getpass("Enter the same passphrase again: ")

        encryption = Encryption(passphrase)

        if message:
            content = encryption.decrypt(message)
        else:
            content = ""

    with NamedTemporaryFile(prefix="osafe-", mode='w+t', encoding='utf-8', newline='\n') as file:
        file.write(content)
        file.seek(0)

        editor = os.environ.get('EDITOR')
        if not editor:
            print("EDITOR environment variable not set.")
            while not editor:
                editor = input("Type your preferred editor: ")

        check_call([editor, file.name])

        new_content = file.read()
        if new_content != content:
            storage.set(encryption.encrypt(new_content))


if __name__ == '__main__':
    main()
