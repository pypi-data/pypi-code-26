# from https://github.com/codemasteroy/py-viitenumero


def format_for_print(viitenumero):
    print_viitenumero = ''
    c = 0

    digits = list(viitenumero)
    digits.reverse()

    for digit in digits:
        if c > 0 and c % 4 == 0:
            print_viitenumero = ' ' + print_viitenumero
        print_viitenumero = digit + print_viitenumero
        c += 1

    return print_viitenumero


def calculate_viitenumero(prefix_number, for_print=False):
    if int(prefix_number) == 0:
        return('Error: Prefix Number must be composed only of numbers')
    if 100 > int(prefix_number):
        return('Error: Prefix Number must be at least 3 digits excluding 0 in front')

    multiplier = [7, 3, 1]
    t = 0
    c = 0

    digits = list(prefix_number)
    digits.reverse()

    for digit in digits:
        t += int(digit) * multiplier[c % 3]
        c += 1

    check_digit = (((t % 10) * 10) - t) % 10
    viitenumero = "{}{}".format(prefix_number, check_digit)

    if for_print:
        return format_for_print(viitenumero)
    else:
        return viitenumero


def generate_viitenumero(event_id, random_number, order_id):
    return calculate_viitenumero(
        str(event_id) +
        str(random_number) +
        str(order_id),
        True
    )
