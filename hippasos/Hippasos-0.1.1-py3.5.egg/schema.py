def get_schema():
    return {
            "sound-mappings": {
                "description": "Root node for hippasos specific entries.",
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "description": "unique name for sound event",
                            "type": "string"
                        },
                        "sound-file": {
                            "description": "uri to sound file. must be ogg or wav.",
                            "type": "string"
                        },
                        "topic-sub": {
                            "description": "react to published values on this channel",
                            "type": "string"
                        },
                        "message-value": {
                            "description": "react to this message content",
                            "type": "string"
                        },
                        "volume": {
                            "description": "0..1 - volume relative to system volume",
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1
                        },
                        "active": {
                            "description": "entry ignored if set to False",
                            "type": "boolean"
                        }
                    },
                    "required": ["active", "volume", "message-value", "topic-sub", "sound-file", "name"],
                    "additionalProperties": False
                },
                "additionalProperties": False
            }
           }
