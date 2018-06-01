import json
import re
from fuzzywuzzy import fuzz, process
from ..classification.constants_and_regexes import (REGEXES, DANCE_STYLES,
                                                    CLASS_CATEGORIES)
from ..classification.classifier import (cat_or_style_cl, cat_cl, 
                                         determine_structure, getClassesExact,
                                         getStylesExact)


def generate_events(events_lists):
    # TODO: generate events based on what we're told is the event structure,
    # not just assuming from the length
    event_objects = []
    keys_to_map = []
    for events_strings in events_lists:
        if len(events_strings) == 3:
            keys_to_map = ['Event', 'Style', 'Time']
        elif len(events_strings) == 2:
            # Find out if the other element is a style or timestamp
            if REGEXES['timestamp'].search(events_strings[1]):
                keys_to_map = ['Event', 'Time']
            else:
                keys_to_map = ['Event', 'Style']
        else:
            keys_to_map = ['Event']

        event_object = dict(zip(keys_to_map, events_strings))
        event_objects.append(event_object)

    return event_objects


def merge_strings(text_list):
    # Try all possible pairs of strings until we get a pair that
    # produce the same match
    pairs = zip(text_list, text_list[1:])

    for x, y in pairs:
        x_type = cat_or_style_cl.classify(x)
        y_type = cat_or_style_cl.classify(y)

        # Return a match if x+y gets the same match as just x
        if x_type != y_type:
            # Assert that we x and y are the same time
            continue

        # Generate potential matches for both x and xy
        xy = "{} {}".format(x, y)
        if x_type == "cat":
            xy_type = cat_cl.classify(xy)
            potential_matches = getClassesExact([x, xy])
        elif x_type == "dance_style":
            potential_matches = getStylesExact([x, xy])

        potential_match_x = potential_matches[0][0]
        potential_match_xy = potential_matches[0][1]
        if potential_match_x.upper() in potential_match_xy.upper():
            match = potential_match_xy

        x_index = text_list.index(x)
        y_index = x_index + 1
        text_copy = text_list[:x_index] + [match] + text_list[y_index + 1:]
        # Return the match as well as the element to replace
        return text_copy


def group_event_strings(text_list, timestamps):
    text_list = [x for x in text_list if x != ""]
    groups = []
    start = 0

    for index, string in enumerate(text_list):
        if string in timestamps:
            # Add all the string up to and including the timestamp to a list
            group = text_list[start:index + 1]
            # Add that list grouping together strings to text_copy
            groups.append(group)
            start = index + 1
        elif string == "Studio Closed":
            groups.append(text_list)
            break

    for index, group in enumerate(groups):
        # Merge classes and styles that are spread over two lines
        structure = determine_structure(group, timestamps)
        if structure == "SPREAD":
            groups[index] = merge_strings(group)
        elif structure == "CLOSING":
            groups[index] = ["Studio Closed"]
        elif structure == "CLOSING_DOUBLE":
            groups[index] = ["Studio Closed: {}".format(group[1])]
        elif structure == "CLOSING_SPREAD_TIME":
            groups[index] = ["Studio Closed: {}".format(group[1]), group[2]]
        elif structure == "CLOSING_SPREAD":
            groups[index] = ["Studio Closed: {}".format(group[1])] + group[2:]
        elif structure == "CAT_AND_TIME":
            groups[index] = [group[0], group[1]]
        elif structure == "CAT_AND_STYLE":
            groups[index] = [group[0], group[1]]
        else:
            groups[index] = group

    return groups


def split_on_timestamps(text_list):
    # Get all the timestamps for the current date_object
    timestamps = [
        x.group(0) for x in
        list(map(lambda y: REGEXES['timestamp'].search(y), text_list)) if x
    ]

    if not timestamps:
        return (text_list, [])
    else:
        text_copy = []
        for string in text_list:
            text_copy.append(string)
            for timestamp in timestamps:
                if timestamp in string:
                    text_copy[-1] = string.replace(timestamp, '')
                    text_copy.append(timestamp)
                    break
        text_copy = [x.strip() for x in text_copy]
        return (text_copy, timestamps)
