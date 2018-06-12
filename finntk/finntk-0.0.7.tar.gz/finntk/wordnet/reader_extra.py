def sort_file(filename):
    with open(filename, 'rb') as fp:
        lines = fp.readlines()
    lines.sort()
    with open(filename, 'wb') as fp:
        for line in lines:
            fp.write(line)

    def _sort_sense_index(self):
        data_dir = self._get_data_dir()
        sort_file(pjoin(data_dir, "dict", "index.sense"))



    def fi_lemma_key(self, en_lemma, fi_lemma_str):
        name = fi_lemma_str.replace(' ', '_')
        tup = (name, self._pos_numbers[en_lemma.synset().pos()],
               en_lemma._lexname_index, en_lemma._lex_id, "", "")
        return ("%s%%%d:%02d:%02d:%s:%s" % tup).lower()

    def _make_sense_map(self):
        fi_synsets = fiwn.all_synsets()
        en_synsets = wordnet.all_synsets()
        en2fi = {}
        while 1:
            fi_synset = next(fi_synsets)
            en_synset = next(en_synsets)
            while fi_synset.definition() == '[empty]':
                fi_synset = next(fi_synsets)
            assert en_synset.definition() == fi_synset.definition()
            en2fi[(en_synset.pos(), en_synset.offset())] = \
                (fi_synset.pos(), fi_synset.offset())

    def lemma_count(self, lemma):
        if not self._counts:
            self._counts = calc_fiwn_counts()
        return self._counts[lemma.key()]



def synset_surf_to_lemma(synset, surf):
    lemmas = synset.lemmas()
    for lemma in lemmas:
        if lemma.name().replace('_', ' ') == surf:
            return lemma


def calc_fiwn_counts():
    en2fi = {}
    for synset_key, fi_lemma_str, en_lemma_str, rel, extra in get_transl_iter():
        pos, offset = synset_key[0], int(synset_key[1:], 10)
        if rel != "synonym":
            continue

        en_synset = wordnet.synset_from_pos_and_offset(pos, offset)
        en_lemma = synset_surf_to_lemma(en_synset, en_lemma_str)
        assert en_lemma is not False

        print("fiwn.synset_from_pos_and_offset(pos, offset)", pos, offset)
        fi_lemma_key = fiwn.fi_lemma_key(en_lemma, fi_lemma_str)
        fi_lemma = fiwn.lemma_from_key(fi_lemma_key)
        #fi_synset = fi_lemma.synset()
        assert fi_lemma is not False

        en2fi.setdefault(en_lemma.key(), []).append(fi_lemma.key())
    counts = {}
    for en, fis in en2fi.items():
        for fi in fis:
            counts.setdefault(fi, 0.0)
            counts[fi] += en.count() / len(fis)
    return counts


        self._counts = None





    def open(self, filename):
        if filename == "lexnames":
            return wordnet.open("lexnames")
        return open(fiwn_resman.get_res(filename))

