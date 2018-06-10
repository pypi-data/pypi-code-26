# pylint: disable=E0611
from libcppjieba import get_default_keyword_extractor ,\
    get_default_textrank_extractor

from libcppjieba import KeywordExtractor ,\
      TextRankExtractor 
# pylint: enable=E0611

TextRank = TextRankExtractor
TFIDF = KeywordExtractor

def _textrank(self,sentence, topK=20, withWeight=False):
    if not withWeight:
        return self.textrank_no_weight(sentence,topK)
    else:
        return self.textrank_with_weight(sentence,topK)

setattr(TextRank,"textrank",_textrank)

keywordExtractor = get_default_keyword_extractor()
textrankExtractor = get_default_textrank_extractor()

extract_tags = keywordExtractor.extract_tags
textrank = textrankExtractor.textrank

