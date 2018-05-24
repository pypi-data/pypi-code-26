import json
import re
from fuzzywuzzy import fuzz, process
from textblob.classifiers import NaiveBayesClassifier
from textblob.classifiers import PositiveNaiveBayesClassifier
from .constants_and_regexes import REGEXES, DANCE_STYLES, CLASS_CATEGORIES


def determine_structure(group, timestamps=[]):
    length = len(group)
    types = []
    for i in group:
        if i in timestamps:
            types.append("timestamp")
        elif "Studio Closed" in i:
            types.append("closing")
        else:
            i_type = cat_or_style_cl.classify(i)
            if i_type == "cat":
                i_type = cat_cl.classify(i)
            types.append(i_type)
    if "closing" in types:
        if length == 1:
            return "CLOSING"
        elif length == 2:
            return "CLOSING_DOUBLE"
        elif length > 2 and group[2] in timestamps:
            return "CLOSING_SPREAD_TIME"
        else:
            return "CLOSING_SPREAD"
    elif length == 2:
        if "cat" in types[0]:
            if types[1] == "timestamp":
                return "CAT_AND_TIME"
            elif types[1] == "dance_style":
                return "CAT_AND_STYLE"
        elif types[0] == "dance_style":
            if types[1] == "timestamp":
                return "STYLE_AND_TIME"
            else:
                return "STYLE AND UNKNOWN"
    elif length == 3:
        if ("cat" in types[0]
                and types[1] == "dance_style"
                and types[2] == "timestamp"):
            return "CAT_STYLE_TIME"
        else:
            return "SPREAD"
    elif length % 2 == 0 and length > 2:
        return "SPREAD"
    elif length % 2 == 1 and length > 3:
        return "CLUMPED"
    else:
        return "OTHER"


def getStylesExact(text):
    style_matches = []
    text_copy = text
    indices_to_drop = []
    for i, original_string in enumerate(text_copy):
        string = original_string.lower().replace(' ', '')
        matches = [x.group() for x in list(map(lambda y: y.search(string),
                   REGEXES["DANCE_STYLES"])) if x and x.group() == string]
        if matches:
            match = process.extractOne(matches[0], DANCE_STYLES)[0]
            style_matches.append(match)
        indices_to_drop.append(i)

    text = [x for i, x in enumerate(text) if i not in indices_to_drop]
    return (style_matches, text)


def getClassesExact(text):
    class_matches = []
    text_copy = text
    indices_to_drop = []
    for i, original_string in enumerate(text_copy):
        string = original_string.lower().replace(' ', '')
        matches = [x.group() for x in list(map(lambda y: y.search(string),
                   REGEXES["CLASS_CATEGORIES"])) if x]
        if matches:
            match = process.extractOne(matches[0], CLASS_CATEGORIES)[0]
            class_matches.append(match)
            indices_to_drop.append(i)
        else:
            class_matches.append(original_string)
            indices_to_drop.append(i)
        indices_to_drop.append(i)
    text = [x for i, x in enumerate(text) if i not in indices_to_drop]
    return (class_matches, text)


def custom_extractor(document):
    tokens = document.split()
    first_word, last_word = tokens[0], tokens[-1]
    feats = {}
    feats["first({0})".format(first_word)] = True
    feats["last({0})".format(last_word)] = True
    feats["first_upper({0})".format(first_word.upper())] = True
    feats["last_upper({0})".format(last_word.upper())] = True
    feats["num_tokens({0})".format(len(tokens))] = True
    has_slash = "/" in document
    feats["has_slash({0})".format(has_slash)] = True
    has_closing = "Studio Closed" in document
    feats["has_closing({0})".format(has_closing)] = True
    return feats


cat_or_style_trainer = [
    ("BRUNCH BUNCH", "cat"),
    ("RUSH HOUR GROUP", "cat"),
    ("FULL BRONZE GROUP", "cat"),
    ("ALL LEVEL GROUP", "cat"),
    ("DANCE SERIES", "cat"),
    ("BRONZE I & II GROUP", "cat"),
    ("DANCE FUNDAMENTALS", "cat"),
    ("Amalgamation GROUP", "cat"),
    ("ICE CREAM SOCIAL", "cat"),
    ("ENCORE", "cat"),
    ("FORMATION", "cat"),
    ("WEDDING GROUP", "cat"),
    ("PRACTICE SESSION", "cat"),
    ("ADVANCED PRACTICE SESSION", "cat"),
    ("MASTER CLASS", "cat"),
    ("MARTIN DONTIGNY COACHING", "cat"),
    ("PATTY CONTENTA COACHING", "cat"),
    ("BACHATA", "dance_style"),
    ("BOLERO", "dance_style"),
    ("CHA CHA", "dance_style"),
    ("FOXTROT", "dance_style"),
    ("HUSTLE", "dance_style"),
    ("LINDY HOP", "dance_style"),
    ("MERENGUE", "dance_style"),
    ("QUICKSTEP", "dance_style"),
    ("RUMBA", "dance_style"),
    ("SALSA", "dance_style"),
    ("SAMBA", "dance_style"),
    ("SWING", "dance_style"),
    ("TANGO", "dance_style"),
    ("WALTZ", "dance_style"),
    ("WEST COAST SWING", "dance_style"),
    ("TANGO/SWING", "dance_style"),
    ("FOXTROT/HUSTLE", "dance_style"),
    ("WALTZ/CHA CHA", "dance_style"),
    ("Studio Closed", "closing"),
    ("STUDIO CLOSED", "closing"),
    ("Practice Party", "cat")
]

cat_trainer = [
    ("BRUNCH BUNCH", "cat_w_style"),
    ("RUSH HOUR GROUP", "cat_w_style"),
    ("FULL BRONZE GROUP", "cat_w_style"),
    ("ALL LEVEL GROUP", "cat_w_style"),
    ("DANCE SERIES", "cat_w_style"),
    ("BRONZE I & II GROUP", "cat_w_style"),
    ("DANCE FUNDAMENTALS", "cat_w_style"),
    ("AMALGAMATION GROUP", "cat_w_style"),
    ("ENCORE", "no_style_cat"),
    ("FORMATION", "no_style_cat"),
    ("WEDDING GROUP", "no_style_cat"),
    ("PRACTICE SESSION", "no_style_cat"),
    ("ADVANCED PRACTICE SESSION", "no_style_cat"),
    ("MASTER CLASS", "no_style_cat"),
    ("CLASS", "no_style_cat"),
    ("ICE CREAM SOCIAL", "no_style_cat"),
    ("Practice Party", "no_style_cat")
]

cats = [
    "BRUNCH BUNCH",
    "RUSH HOUR GROUP",
    "FULL BRONZE GROUP",
    "ALL LEVEL GROUP",
    "GROUP",
    "DANCE SERIES",
    "BRONZE I & II GROUP",
    "DANCE FUNDAMENTALS",
    "AMALGAMATION GROUP",
    "ICE CREAM SOCIAL",
    "ENCORE",
    "FORMATION",
    "WEDDING GROUP",
    "PRACTICE SESSION",
    "ADVANCED PRACTICE SESSION",
    "MASTER CLASS",
    "COACHING",
    "MARTIN DONTIGNY COACHING",
    "PATTY CONTENTA COACHING",
    "Party"
]

styles = [
    "ARGENTINE TANGO",
    "BACHATA",
    "BOLERO",
    "CHA CHA",
    "FOXTROT",
    "LINDY HOP",
    "MERENGUE",
    "RUMBA",
    "SALSA",
    "SAMBA",
    "SWING",
    "TANGO",
    "COUNTRY TWO STEP",
    "VIENNESE WALTZ",
    "WALTZ",
    "WEST COAST SWING",
    "ZOUK",
    "FOXTROT/HUSTLE",
    "RUMBA/MERENGUE",
    "WALTZ/CHA CHA"
]

test = [
    ("ALL LEVEL", "cat"),
    ("GROUP", "cat"),
    ("WEDDING", "cat"),
    ("CHA", "dance_style"),
    ("LINDY", "dance_style")
]

cat_or_style_cl = NaiveBayesClassifier(cat_or_style_trainer,
                                       feature_extractor=custom_extractor)

cat_cl = NaiveBayesClassifier(cat_trainer,
                              feature_extractor=custom_extractor)
