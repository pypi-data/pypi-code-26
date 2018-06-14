""" Calc code example """


class Calc():
    """ Calculator Class """

    def __init__(self, first, second):
        self._first = first
        self._second = second

    def sum_call(self):
        """ Sum Def """
        return self._first+self._second

    def div_call(self):
        """ Div Def """
        return self._first/self._second

    def mult_call(self):
        """ Mult Def """
        return self._first*self._second

    def sub_call(self):
        """ Subs Def """
        return self._first-self._second


def main():
    """ Initiate the Calc """

    first_value = 500
    second_value = 39

    # Object creation
    calc_run = Calc(first_value, second_value)

    # Sum
    print("Sum of {} + {} is: {}".format(first_value, second_value,
                                         calc_run.sum_call()))

    # Division
    print("Division of {} / {} is: {}".format(first_value, second_value,
                                              calc_run.div_call()))

    # Multiplication
    print("Multiplication of {} * {} is: {}".format(first_value, second_value,
                                                    calc_run.mult_call()))

    # Subtraction
    print("Subtraction of {} - {} is: {}".format(first_value, second_value,
                                                 calc_run.sub_call()))


if __name__ == '__main__':
    main()
