#!/usr/bin/env python
import sys
import automation_direct_stock as ads

def main(args):
    if (len(args) == 1):
        return ads.isInStock(args[0])
    else:
        return "bad arguments"

if __name__ == '__main__':
    main(sys.argv)