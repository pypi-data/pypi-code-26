logging_config = dict(version=1,
                      disable_existing_loggers=False,
                      formatters={'verbose': {'format': '[%(asctime)s] - '
                                                        '%(levelname)-8s - '
                                                        '%(process)d - '
                                                        '%(filename)s:%(lineno)d '
                                                        '(%(funcName)s) - '
                                                        '%(message)s'}},
                      handlers={'console': {'class': 'logging.StreamHandler',
                                            'level': 'DEBUG',
                                            'formatter': 'verbose',
                                            'stream': 'ext://sys.stdout'},
                                # 'info_file_handler': {'class': 'logging.handlers.RotatingFileHandler',
                                #                       'level': 'INFO',
                                #                       'formatter': 'verbose',
                                #                       'filename': 'info.log',
                                #                       'maxBytes': 10485760,     # 10MB
                                #                       'backupCount': 20,
                                #                       'encoding': 'utf8'},
                                # 'error_file_handler': {'class': 'logging.handlers.RotatingFileHandler',
                                #                        'level': 'ERROR',
                                #                        'formatter': 'verbose',
                                #                        'filename': 'errors.log',
                                #                        'maxBytes': 10485760,    # 10MB
                                #                        'backupCount': 20,
                                #                        'encoding': 'utf8'}
                                },
                      loggers={'controller_module': {'level': 'ERROR',
                                                     'handlers': ['console'],
                                                     'propagate': False},
                               'relay_module': {'level': 'ERROR',
                                                'handlers': ['console'],
                                                'propagate': False}},
                      root={'level': 'ERROR',
                            'handlers': ['console']}
                      )