from typing import Iterable, Tuple

import hjson

from plover.steno_dictionary import StenoDictionary
from plover.steno import normalize_steno, STROKE_DELIMITER


class HjsonDictionary(StenoDictionary):
    '''
    Stenography dictionary for Hjson files.

    Format:

    {
      Translation 1:
      [
        STROKE_1
        STROKE_2
      ]
      Translation 2:
      [
        STROKE_1
      ]
    }

    etc.
    '''

    def _load(self, filename: str):
        '''
        Populates the dictionary entries for Plover from a file.

        :param filename: The file path of the dictionary to load.
        '''

        self.update(HjsonDictionary.load_hjson_file(filename))

    def _save(self, filename: str):
        '''
        Saves off the current dictionary state in Plover to a file.

        :param filename: The file path of the dictionary to save to.
        '''

        # Group dictionary by value
        data = {}

        for strokes, translation in self._dict.items():
            # Need to join the multi-stroke entries into one stroke string first
            stroke = STROKE_DELIMITER.join(strokes)
            data.setdefault(translation, []).append(stroke)
            data[translation] = sorted(data[translation])

        # Write out the data
        with open(filename, 'w', encoding='utf-8') as out_file:
            hjson.dump(data, out_file,
                       sort_keys=True, ensure_ascii=False, encoding='utf-8')

    @staticmethod
    def load_hjson_file(filename: str) -> Iterable[Tuple[Tuple[str], str]]:
        '''
        Loads an Hjson dictionary file and provides an iterable to its
        stroke to translation mappings.

        :param filename: The file path of the Hjson dictionary to load.
        :return: An iterable that provides tuples of stroke tuple, translation.
        '''

        # Load the data
        with open(filename, 'r', encoding='utf-8') as in_file:
            data = hjson.load(in_file, encoding='utf-8')

        # Provide tuples of stroke tuple, translation
        for translation, strokes in data.items():
            for stroke in strokes:
                yield (normalize_steno(stroke), translation)
