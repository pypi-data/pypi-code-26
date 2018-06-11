import sys
import traceback


def debugger(*args, **kwargs):
    # Set variables
    for key in kwargs:
        exec "%s = kwargs['%s']" % (key, key)

    print "*** Debugger activated (run 'exit' to quit) ***"
    print "Variables passed:"
    for key in kwargs:
        print "  %s" % key

    response = raw_input(">>> ")
    while response != "exit":
        try:
            exec response
            response = raw_input(">>> ")
        except:
            print("Exception in user code:")
            print("-"*60)
            traceback.print_exc(file=sys.stdout)
            print("-"*60)
            response = raw_input(">>> ")
