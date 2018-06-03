
from cooked_input import *

# prompt_str = "Enter a number between -1 and 10, but not 0"
# validators = [RangeValidator(-10, 10), NoneOfValidator(0)]
# response = get_input(prompt=prompt_str, convertor=IntConvertor(), validators=validators, default=5)
# print(response)

# input_str = u"""
#     10
#
#     true
#     """
#
# bool_convertor = BooleanConvertor()
# # result = get_input(prompt='enter a boolean (True/False)', convertor=bool_convertor)
# result = get_boolean()
# print(result)

# lv = LengthValidator()
# result = get_input(cleaners=StripCleaner(), validators=lv)
# print(result)

# input_str = u"""
#     1
#     3,4,5,6,7
#     2,3,4
#     """


# input_str = """
#             licorice
#             booger
#             lemon
#             """
colors = ['red', 'green', 'blue']
good_flavors = ['cherry', 'lime', 'lemon', 'orange']
bad_flavors = 'licorice'
choices_validator = ChoicesValidator(choices=colors)
good_flavor_validator = ChoicesValidator(choices=good_flavors)
bad_flavor_validator = ChoicesValidator(choices=bad_flavors)
not_in_choices_validator = NoneOfValidator(validators=[bad_flavor_validator])
strip_cleaner = StripCleaner()
lower_cleaner = CapitalizationCleaner()
strip_and_lower_cleaners = [strip_cleaner, lower_cleaner]

validators = [good_flavor_validator, not_in_choices_validator]
result = get_input(cleaners=strip_and_lower_cleaners, validators=validators, default='cherry')
print(result)
