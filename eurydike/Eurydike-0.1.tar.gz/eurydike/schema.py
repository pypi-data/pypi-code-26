def get_schema():
    return {
            "eventdetectors": {
                "description": "Root node for alcathous specific entries.",
                "type": "array",
                "items": {
                    "oneOf": [
                        {
                            "description": "on threshold",
                            "type": "object",
                            "properties": {
                                "name": {
                                    "description": "unqiue name for event detector",
                                    "type": "string"
                                },
                                "type": {
                                    "description": "detector type identifier",
                                    "type": "string",
                                    "enum": ["onthreshold"]
                                },
                                "comparator": {
                                    "description": "GREATERTHAN/GT/>, LOWERTHAN/LT/<, EQUALTO/==",
                                    "type": "string",
                                    "enum": ["GREATERTHAN", "GT", ">", "LOWERTHAN", "LT", "<", "EQUALTO", "==",
                                             "greaterthan", "gt", "lowerthan", "lt", "equalto"]
                                },
                                "threshold": {
                                    "description": "threshold in combintation with comparator and value from topic-sub",
                                    "type": "number"
                                },
                                "topic-pub": {
                                    "type": "string"
                                },
                                "topic-sub": {
                                    "type": "string"
                                },
                                "active": {
                                    "description": "entry ignored if set to False",
                                    "type": "boolean"
                                },
                                "responses": {
                                    "description": "leave value empty or remove line for no response",
                                    "type": "object",
                                    "properties": {
                                        "on-violation": {
                                            "description": "on detection of a threshold violation send this value to "
                                                           "topic-pub",
                                            "type": ["string", "null"]
                                        },
                                        "on-restoration": {
                                            "description": "on the event of returning to valid values send this value "
                                                           "to topic-pub",
                                            "type": ["string", "null"]
                                        }
                                    },
                                    "additionalProperties": False
                                }
                            },
                            "required": ["type", "comparator", "threshold", "topic-sub", "topic-pub", "active"],
                            "additionalProperties": False
                        },
                        {
                            "description": "on band",
                            "type": "object",
                            "properties": {
                                "name": {
                                    "description": "unqiue name for event detector",
                                    "type": "string"
                                },
                                "type": {
                                    "description": "detector type identifier",
                                    "type": "string",
                                    "enum": ["onband"]
                                },
                                "upper-threshold": {
                                    "description": "upper threshold for on band detection",
                                    "type": "number"
                                },
                                "lower-threshold": {
                                    "description": "lower threshold for on band detection",
                                    "type": "number"
                                },
                                "topic-pub": {
                                    "type": "string"
                                },
                                "topic-sub": {
                                    "type": "string"
                                },
                                "active": {
                                    "description": "entry ignored if set to False",
                                    "type": "boolean"
                                },
                                "responses": {
                                    "description": "leave value empty or remove line for no response",
                                    "type": "object",
                                    "properties": {
                                        "on-violation": {
                                            "description": "on detection of a threshold violation send this value to "
                                                           "topic-pub",
                                            "type": "string"
                                        },
                                        "on-restoration": {
                                            "description": "on the event of returning to valid values send this value "
                                                           "to topic-pub",
                                            "type": "string"
                                        }
                                    },
                                    "additionalProperties": False
                                }
                            },
                            "required": ["type", "lower-threshold", "upper-threshold", "topic-sub", "topic-pub",
                                         "active"],
                            "additionalProperties": False
                        }
                    ]
                },
                "additionalItems": False
            }
           }

