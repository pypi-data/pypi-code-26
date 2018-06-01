'''
Emitters for the HID-IO HID Layout Repository API

This file is responsible for various utility functions useful to generate different filetypes with layout data.

For example, generating list of C defines for use with keyboard firmware.
'''

from . import Layout

def basic_c_defines(
    layout,
    keyboard_prefix="KEY_",
    led_prefix="LED_",
    sysctrl_prefix="SYS_",
    cons_prefix="CONS_",
    all_caps=True,
    space_char="_"
):
    '''
    Generates a list of C defines that can be used to generate a header file

    @param layout: Layout object
    @keyboard_prefix: Prefix used for to_hid_keyboard
    @led_prefix: Prefix used for to_hid_led
    @sysctrl_prefix: Prefix used for to_hid_sysctrl
    @cons_prefix: Prefix used for to_hid_consumer
    @all_caps: Set to true if labels should be converted to all caps
    @space_char: Character to replace space with

    @returns: List of C tuples (<name>, <number>) that can be used to generate C-style defines. Each section has it's own list.
    '''
    # Keyboard Codes
    keyboard_defines = []
    for code, name in layout.json()['to_hid_keyboard'].items():
        new_name = "{}{}".format(keyboard_prefix, name.replace(' ', space_char))
        if all_caps:
            new_name = new_name.upper()
        define = (new_name, code)
        keyboard_defines.append(define)

    # LED Codes
    led_defines = []
    for code, name in layout.json()['to_hid_led'].items():
        new_name = "{}{}".format(led_prefix, name.replace(' ', space_char))
        if all_caps:
            new_name = new_name.upper()
        define = (new_name, code)
        led_defines.append(define)

    # System Control Codes
    sysctrl_defines = []
    for code, name in layout.json()['to_hid_sysctrl'].items():
        new_name = "{}{}".format(sysctrl_prefix, name.replace(' ', space_char))
        if all_caps:
            new_name = new_name.upper()
        define = (new_name, code)
        sysctrl_defines.append(define)

    # Consumer Codes
    cons_defines = []
    for code, name in layout.json()['to_hid_consumer'].items():
        new_name = "{}{}".format(cons_prefix, name.replace(' ', space_char))
        if all_caps:
            new_name = new_name.upper()
        define = (new_name, code)
        cons_defines.append(define)

    # Return list of list of tuples
    defines = [keyboard_defines, led_defines, sysctrl_defines, cons_defines]
    return defines

