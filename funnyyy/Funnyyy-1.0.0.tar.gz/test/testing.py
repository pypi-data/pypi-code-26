from funnyyy.first_package.first import PackOne
from funnyyy.second_package.second import PackSecond


def main():

    pack_one = PackOne()
    pack_two = PackSecond()

    pack_one.process()
    pack_two.process()


if __name__ == "__main__":
    main()
