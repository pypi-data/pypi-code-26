import argparse
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--day", required = False,
	help = "fill in the important days of your life")
ap.add_argument('-w','--who', required = False,
	help = 'who loves who')
args = vars(ap.parse_args())

def info(sth):
    if sth == '21-06-1997' or '0621':
        print('happy birthday my dear cat!')
        print('iFeliz compleanos mi cato!')

    elif sth == '04-04-1999' or '0404':
        print('happy birthday dog!')
        print('feliz compleanos perro!')

    elif sth == 'dog' or 'perro':
        print('dog loves cat and dog belong to the cat')

    elif sth == 'cat' or 'cato':
        print('cat loves dog and she will never leave him')

    elif sth == '120317':
        print('this is the first day they are together, and find their life partener')

    else:
        print('oops do not have output for this input now')

if __name__ == '__main__':
    if args['day'] != None:
        info(args['day'])
    else:
        info(args['who'])
