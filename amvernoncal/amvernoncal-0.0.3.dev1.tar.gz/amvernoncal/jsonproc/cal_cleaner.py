import json
import re
from fuzzywuzzy import fuzz, process
from ..classification.constants_and_regexes import (REGEXES, DANCE_STYLES,
                                                    CLASS_CATEGORIES)
from ..classification.classifier import (cat_or_style_cl, cat_cl,
                                         getStylesExact, getClassesExact)
from .process_cal import (split_on_timestamps, group_event_strings,
                         generate_events)


def pre_clean_calendar(json_data):
    cal_data = []

    for list_of_objects in json_data:
        for obj in list_of_objects:
            try:
                assert 'text' in obj.keys()
                valid_obj = int(obj['text'][0])
                obj.pop('height', None)
                obj.pop('width', None)
                obj.pop('left', None)
                obj.pop('top', None)

                # Remove whitespace between dates and strings
                obj['text'] = re.sub(r'(?!\d+)\s\s+(?=\w)', '\r', obj['text'])
                obj['text'] = re.sub(r'\r\(', ' (', obj['text'])
                # Split the raw text by the carriage returns
                obj['text'] = re.split(r'\r', obj['text'])

                # Try to split on timestamps
                split_text, timestamps = split_on_timestamps(obj['text'])
                # Add date
                obj['date'] = split_text.pop(0)
                obj['text'] = split_text
                obj['timestamps'] = timestamps

                cal_data.append(obj)
            except (ValueError, IndexError):
                continue
    return cal_data


def post_clean_calendar(cal_data):
    # Fill cal_data with JSON objects that may contain dates
    for obj in cal_data:
        try:
            text_copy = obj["text"]

            if 'timestamps' in obj.keys():
                timestamps = obj['timestamps']
            else:
                timestamps = []

            # Group together related strings if there are timestamps
            if timestamps:
                obj['text'] = group_event_strings(text_copy, timestamps)
            elif "Studio Closed" in obj['text']:
                obj['text'] = group_event_strings(text_copy, [])
            else:
                # If there are no timestamps, ie, if the text says
                # 'Studio Closed' w/out a time, pass it right through
                obj['text'] = text_copy

            obj['events'] = generate_events(obj['text'])
            obj.pop('text', None)
            obj.pop('timestamps', None)
        except (ValueError, IndexError):
            continue

    # Assert that we have a full calendar
    if (len(cal_data) < 28) or (len(cal_data) > 31):
        raise SystemExit("Error: We don't have a full calendar...")
    else:
        print("Yay! We have all the calendar events!")
        return cal_data
    return cal_data


def separate_clumped_events(text_list, timestamps):
    triples = zip(text_list, text_list[1:], text_list[2:])

    i = 0
    for x, y, z in triples:
        x_type = cat_or_style_cl.classify(x)
        y_type = cat_or_style_cl.classify(y)
        if all([x_type == 'cat', y_type == 'dance_style', z in timestamps]):
            break
        else:
            i += 1

    return [text_list[:i], text_list[i:i+3], text_list[i+3:]]
