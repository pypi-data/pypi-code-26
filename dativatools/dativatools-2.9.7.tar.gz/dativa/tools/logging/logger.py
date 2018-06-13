import logging
import sys

###########################################
#                                         #
#             HERE BE DRAGONS             #
#                                         #
#                                         #
#     .     _///_,                        #
#   .      / ` ' '>                       #
#     )   o'  __/_'>                      #
#    (   /  _/  )_\'>                     #
#     ' "__/   /_/\_>                     #
#         ____/_/_/_/                     #
#        /,---, _/ /                      #
#       ""  /_/_/_/                       #
#          /_(_(_(_                 \     #
#         (   \_\_\\_               )\    #
#          \'__\_\_\_\__            ).\   #
#          //____|___\__)           )_/   #
#          |  _  \'___'_(           /'    #
#           \_ (-'\'___'_\      __,'_'    #
#           __) \  \\___(_   __/.__,'     #
#        ,((,-,__\  '", __\_/. __,'       #
#                     '"./_._._-'         #
#                                         #
# THIS FILE NEEDS TO HAVE AUTOMATED TESTS #
#                                         #
###########################################


def log_to_stdout(logger_name="dativa", level=logging.DEBUG):
    # set up logging
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger
