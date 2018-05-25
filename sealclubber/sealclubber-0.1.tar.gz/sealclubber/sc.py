import argparse
from gooey import Gooey, GooeyParser

@Gooey
def main():
  parser = GooeyParser(description='Clubber')
  parser.add_argument('number of seals', metavar='number')
  args = parser.parse_args();
  print('That\'s seriously disgusting - you were going to club that many??')

if __name__ == '__main__':
  main()
