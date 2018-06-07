def get_schema():
    return {
            "controller": {
                "description": "Root node for epidaurus specific entries.",
                "type": "object",
                "properties": {
                    "value-idle": {
                        "description": "idle mode output - heating system does nothing",
                        "type": "number",
                    },
                    "value-min": {
                        "description": "minimum output for active (=heating) system",
                        "type": "number"
                    },
                    "value-max": {
                        "description": "maximum value for heater",
                        "type": "number"
                    },
                    "pid-max-output": {
                        "description": "for normalization purposes. this is the expected maximum output of the pid "
                                       "controller",
                        "type": "number"
                    },
                    "idle-mode-threshold": {
                        "description": "if temperature is this value above set-point, set output to volt-idle "
                                       "value.",
                        "type": "number"
                    },
                    "topics-sub": {
                        "type": "object",
                        "properties": {
                            "set-point": {
                                "description": "receive new set point via this topic",
                                "type": "string"
                            },
                            "input": {
                                "description": "receive input (=temperature) updates via this topic",
                                "type": "string"
                            }
                        },
                        "required": ["set-point", "input"],
                        "additionalProperties": False
                    },
                    "topics-pub": {
                        "type": "object",
                        "properties": {
                            "output": {
                                "description": "publish resulting output voltage to this topic",
                                "type": "string"
                            }
                        },
                        "required": ["output"],
                        "additionalProperties": False
                    },
                    "pid": {
                        "type": "object",
                        "properties": {
                            "p-gain": {
                                "type": "number"
                            },
                            "i-gain": {
                                "type": "number"
                            },
                            "d-gain": {
                                "type": "number"
                            },
                            "update-interval": {
                                "description": "in seconds (in fact not used anywhere)",
                                "type": "number"
                            },
                            "windup-guard": {
                                "description": "protect integral term from windup",
                                "type": "number"
                            }
                        },
                        "required": ["p-gain", "i-gain", "d-gain", "update-interval", "windup-guard"],
                        "additionalProperties": False
                    },
                },
                "required": ["value-idle", "value-min", "value-max", "pid-max-output", "idle-mode-threshold",
                             "topics-sub", "topics-pub", "pid"],
                "additionalProperties": False
            }
           }