"""Start Conan promote

"""
import sys
from conan.conan_promote import ConanPromote


def run():
    """Create Conan promote instance and run

    Collect user arguments as
    """
    promote = ConanPromote()
    promote.run(sys.argv[1:])


if __name__ == '__main__':
    run()
