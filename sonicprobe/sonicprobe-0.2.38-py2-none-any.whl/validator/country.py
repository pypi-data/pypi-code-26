#!/usr/bin/python
# -*- coding: utf-8 -*-

from sonicprobe import helpers

COUNTRIES   = {
    'ad':   'Andorra',
    'ae':   'United Arab Emirates',
    'af':   'Afghanistan',
    'ag':   'Antigua and Barbuda',
    'ai':   'Anguilla',
    'al':   'Albania',
    'am':   'Armenia',
    'an':   'Netherlands Antilles',
    'ao':   'Angola',
    'aq':   'Antarctica',
    'ar':   'Argentina',
    'as':   'American Samoa',
    'at':   'Austria',
    'au':   'Australia',
    'aw':   'Aruba',
    'az':   'Azerbaijan',
    'ba':   'Bosnia Hercegovina',
    'bb':   'Barbados',
    'bd':   'Bangladesh',
    'be':   'Belgium',
    'bf':   'Burkina Faso',
    'bg':   'Bulgaria',
    'bh':   'Bahrain',
    'bi':   'Burundi',
    'bj':   'Benin',
    'bm':   'Bermuda',
    'bn':   'Brunei Darussalam',
    'bo':   'Bolivia',
    'br':   'Brazil',
    'bs':   'Bahamas',
    'bt':   'Bhutan',
    'bv':   'Bouvet Island',
    'bw':   'Botswana',
    'by':   'Belarus (Byelorussia)',
    'bz':   'Belize',
    'ca':   'Canada',
    'cc':   'Cocos Islands',
    'cd':   'Congo, The Democratic Republic of the',
    'cf':   'Central African Republic',
    'cg':   'Congo',
    'ch':   'Switzerland',
    'ci':   'Ivory Coast',
    'ck':   'Cook Islands',
    'cl':   'Chile',
    'cm':   'Cameroon',
    'cn':   'China',
    'co':   'Colombia',
    'cr':   'Costa Rica',
    'cs':   'Czechoslovakia',
    'cu':   'Cuba',
    'cv':   'Cape Verde',
    'cx':   'Christmas Island',
    'cy':   'Cyprus',
    'cz':   'Czech Republic',
    'de':   'Germany',
    'dj':   'Djibouti',
    'dk':   'Denmark',
    'dm':   'Dominica',
    'do':   'Dominican Republic',
    'dz':   'Algeria',
    'ec':   'Ecuador',
    'ee':   'Estonia',
    'eg':   'Egypt',
    'eh':   'Western Sahara',
    'er':   'Eritrea',
    'es':   'Spain',
    'et':   'Ethiopia',
    'fi':   'Finland',
    'fj':   'Fiji',
    'fk':   'Falkland Islands',
    'fm':   'Micronesia',
    'fo':   'Faroe Islands',
    'fr':   'France',
    'fx':   'France, Metropolitan FX',
    'ga':   'Gabon',
    'gb':   'United Kingdom (Great Britain)',
    'gd':   'Grenada',
    'ge':   'Georgia',
    'gf':   'French Guiana',
    'gh':   'Ghana',
    'gi':   'Gibraltar',
    'gl':   'Greenland',
    'gm':   'Gambia',
    'gn':   'Guinea',
    'gp':   'Guadeloupe',
    'gq':   'Equatorial Guinea',
    'gr':   'Greece',
    'gs':   'South Georgia and the South Sandwich Islands',
    'gt':   'Guatemala',
    'gu':   'Guam',
    'gw':   'Guinea-bissau',
    'gy':   'Guyana',
    'hk':   'Hong Kong',
    'hm':   'Heard and McDonald Islands',
    'hn':   'Honduras',
    'hr':   'Croatia',
    'ht':   'Haiti',
    'hu':   'Hungary',
    'id':   'Indonesia',
    'ie':   'Ireland',
    'il':   'Israel',
    'in':   'India',
    'io':   'British Indian Ocean Territory',
    'iq':   'Iraq',
    'ir':   'Iran',
    'is':   'Iceland',
    'it':   'Italy',
    'jm':   'Jamaica',
    'jo':   'Jordan',
    'jp':   'Japan',
    'ke':   'Kenya',
    'kg':   'Kyrgyzstan',
    'kh':   'Cambodia',
    'ki':   'Kiribati',
    'km':   'Comoros',
    'kn':   'Saint Kitts and Nevis',
    'kp':   'North Korea',
    'kr':   'South Korea',
    'kw':   'Kuwait',
    'ky':   'Cayman Islands',
    'kz':   'Kazakhstan',
    'la':   'Laos',
    'lb':   'Lebanon',
    'lc':   'Saint Lucia',
    'li':   'Lichtenstein',
    'lk':   'Sri Lanka',
    'lr':   'Liberia',
    'ls':   'Lesotho',
    'lt':   'Lithuania',
    'lu':   'Luxembourg',
    'lv':   'Latvia',
    'ly':   'Libya',
    'ma':   'Morocco',
    'mc':   'Monaco',
    'md':   'Moldova Republic',
    'mg':   'Madagascar',
    'mh':   'Marshall Islands',
    'mk':   'Macedonia, The Former Yugoslav Republic of',
    'ml':   'Mali',
    'mm':   'Myanmar',
    'mn':   'Mongolia',
    'mo':   'Macau',
    'mp':   'Northern Mariana Islands',
    'mq':   'Martinique',
    'mr':   'Mauritania',
    'ms':   'Montserrat',
    'mt':   'Malta',
    'mu':   'Mauritius',
    'mv':   'Maldives',
    'mw':   'Malawi',
    'mx':   'Mexico',
    'my':   'Malaysia',
    'mz':   'Mozambique',
    'na':   'Namibia',
    'nc':   'New Caledonia',
    'ne':   'Niger',
    'nf':   'Norfolk Island',
    'ng':   'Nigeria',
    'ni':   'Nicaragua',
    'nl':   'Netherlands',
    'no':   'Norway',
    'np':   'Nepal',
    'nr':   'Nauru',
    'nt':   'Neutral Zone',
    'nu':   'Niue',
    'nz':   'New Zealand',
    'om':   'Oman',
    'pa':   'Panama',
    'pe':   'Peru',
    'pf':   'French Polynesia',
    'pg':   'Papua New Guinea',
    'ph':   'Philippines',
    'pk':   'Pakistan',
    'pl':   'Poland',
    'pm':   'St. Pierre and Miquelon',
    'pn':   'Pitcairn',
    'pr':   'Puerto Rico',
    'pt':   'Portugal',
    'pw':   'Palau',
    'py':   'Paraguay',
    'qa':   'Qatar',
    're':   'Reunion',
    'ro':   'Romania',
    'ru':   'Russia',
    'rw':   'Rwanda',
    'sa':   'Saudi Arabia',
    'sb':   'Solomon Islands',
    'sc':   'Seychelles',
    'sd':   'Sudan',
    'se':   'Sweden',
    'sg':   'Singapore',
    'sh':   'St. Helena',
    'si':   'Slovenia',
    'sj':   'Svalbard and Jan Mayen Islands',
    'sk':   'Slovakia (Slovak Republic)',
    'sl':   'Sierra Leone',
    'sm':   'San Marino',
    'sn':   'Senegal',
    'so':   'Somalia',
    'sr':   'Suriname',
    'st':   'Sao Tome and Principe',
    'sv':   'El Salvador',
    'sy':   'Syria',
    'sz':   'Swaziland',
    'tc':   'Turks and Caicos Islands',
    'td':   'Chad',
    'tf':   'French Southern Territories',
    'tg':   'Togo',
    'th':   'Thailand',
    'tj':   'Tajikistan',
    'tk':   'Tokelau',
    'tm':   'Turkmenistan',
    'tn':   'Tunisia',
    'to':   'Tonga',
    'tp':   'East Timor',
    'tr':   'Turkey',
    'tt':   'Trinidad, Tobago',
    'tv':   'Tuvalu',
    'tw':   'Taiwan',
    'tz':   'Tanzania',
    'ua':   'Ukraine',
    'ug':   'Uganda',
    'uk':   'United Kingdom',
    'um':   'United States Minor Islands',
    'us':   'United States of America',
    'uy':   'Uruguay',
    'uz':   'Uzbekistan',
    'va':   'Vatican City',
    'vc':   'Saint Vincent, Grenadines',
    've':   'Venezuela',
    'vg':   'Virgin Islands (British)',
    'vi':   'Virgin Islands (USA)',
    'vn':   'Viet Nam',
    'vu':   'Vanuatu',
    'wf':   'Wallis and Futuna Islands',
    'ws':   'Samoa',
    'ye':   'Yemen',
    'yt':   'Mayotte',
    'yu':   'Yugoslavia',
    'za':   'South Africa',
    'zm':   'Zambia',
    'zr':   'Zaire',
    'zw':   'Zimbabwe'}

class SPValidatorCountry:
    def __init__(self):
        pass

    @staticmethod
    def getCountry(value):
        """
        returns the country name from country code

        @return string
        """
        if not helpers.has_len(value):
            return False

        return COUNTRIES.get(str(value).lower(), False)

    @staticmethod
    def getCountries():
        """
        returns all available country codes

        @return dict
        """
        return COUNTRIES

    @staticmethod
    def validate(value):
        """
        checks if given value is a valid country codes

        @param string value
        @return bool
        """
        if not helpers.has_len(value):
            return False

        return COUNTRIES.has_key(str(value).lower())
