import re

CLASS_CATEGORIES = [
    "Master Class",
    "Brunch Bunch",
    "Rush Hour Group",
    "Full Bronze Group",
    "All-Level Group",
    "Practice Session",
    "Dance Series",
    "Bronze I & II Group",
    "Encore",
    "Dance Fundamentals",
    "Wedding Group",
    "Amalgamation Group",
    "Formation",
    "Advanced Practice Session",
    "Ice Cream Social"
]

CATS_WITH_STYLE = [
    x for x in CLASS_CATEGORIES
    if x not in ["Ice Cream Social",
                 "Encore",
                 "Formation",
                 "Wedding Group",
                 "Practice Session",
                 "Advanced Practice Session",
                 "Master Class"]
]

DANCE_STYLES = [
    "Argentine Tango",
    "Bachata",
    "Bolero",
    "Cha Cha",
    "Foxtrot",
    "Hustle",
    "Lindy Hop",
    "Line Dancing",
    "Merengue",
    "Quickstep",
    "Rumba",
    "Salsa",
    "Samba",
    "Swing",
    "Tango",
    "Country Two Step",
    "Viennese Waltz",
    "Waltz",
    "West Coast Swing",
    "Zouk",
    "Tango/Swing",
    "Swing/Hustle",
    "Rumba/Hustle",
    "Foxtrot/Hustle",
    "Rumba/Merengue",
    "Waltz/Cha Cha"
]

REGEXES = {
    # Find out if it's a single time or time range
    "timestamp": re.compile(r'\d+(am|pm)' +
                            r'|\d+(am|pm)?-(\d+|\d+:\d\d)(am|pm)' +
                            r'|\d+:\d\d(am|pm)?(-(\d+:\d\d|\d+)(am|pm)?)?'),

    "CLASS_CATEGORIES": [
        re.compile(r'masterclass'),
        re.compile(r'brunchbunch'),
        re.compile(r'rushhourgroup'),
        re.compile(r'fullbronzegroup'),
        re.compile(r'all-levelgroup'),
        re.compile(r'^practicesession$'),
        re.compile(r'danceseries'),
        re.compile(r'bronzei&iigroup'),
        re.compile(r'encore'),
        re.compile(r'dancefundamentals'),
        re.compile(r'weddinggroup'),
        re.compile(r'^amalgamation'),
        re.compile(r'formation'),
        re.compile(r'^advanced'),
        re.compile(r'^(icecream)?(social)')
    ],
    "DANCE_STYLES": [
        re.compile(r'argentinetango'),
        re.compile(r'bachata'),
        re.compile(r'bolero'),
        re.compile(r'chacha'),
        re.compile(r'foxtrot'),
        re.compile(r'hustle'),
        re.compile(r'lindyhop'),
        re.compile(r'linedancing'),
        re.compile(r'merengue'),
        re.compile(r'quickstep'),
        re.compile(r'rumba'),
        re.compile(r'salsa'),
        re.compile(r'samba'),
        re.compile(r'swing'),
        re.compile(r'tango'),
        re.compile(r'countrytwostep'),
        re.compile(r'viennesewaltz'),
        re.compile(r'waltz'),
        re.compile(r'westcoastswing'),
        re.compile(r'zouk'),
        re.compile(r'foxtrot\/hustle'),
        re.compile(r'tango\/swing'),
        re.compile(r'swing\/hustle'),
        re.compile(r'rumba\/hustle'),
        re.compile(r'rumba\/merengue'),
        re.compile(r'waltz\/chacha')
    ]
}
