#coding=utf-8

from fmtlabels.fmt import analyze
from fmtlabels.fmt import splitField
from fmtlabels.fmt import marshal

def lbl_fmttab(output, category, rows):
    data = {}
    for row in rows:
        if 'review_text' in row:
            text = row['review_text']
        elif 'content' in row:
            text = row['content']
        else:
            continue
        if not text in data:
            analyzeResult = analyze(category, text)
            data[text] = analyzeResult
        else:
            analyzeResult = data[text]

        if not 're_rating' in row:
            continue

        opkey = row['review_type'] + '.' + \
                row['review_subtype'] + '=' + \
                str(row['review_rating'])
        if opkey in analyzeResult['opinionsMap']:
            op = analyzeResult['opinionsMap'][opkey]
            if 'keyword_err' in row:
                op['aspectError'] = 0 if row['keyword_err'] in [None, '', 0 , '0'] else 1
            if 're_rating' in row:
                op['polarityCheck'] = int(row['re_rating']) if not row['re_rating'] in [None, ''] else op['polarity']
            if 'sentiment_words' in row:
                op['suggestion']['addOpinionTerms'] = splitField(row['sentiment_words'])
            if 'exclude_words' in row:
                op['suggestion']['excludeOpinionTerms'] = splitField(row['exclude_words'])

            if 'sentiment_words' in row and 'exclude_words' in row:
                op['suggestion'] = {
                    'addAspectTerms': None,
                    'addOpinionTerms': splitField(row['sentiment_words']),
                    'excludeOpinionTerms': splitField(row['exclude_words']),
                }
            if 'mark' in row:
                op['mark'] = row['mark']
                if str(row['mark']).find('对比关系') >= 0:
                    op['errType'] = 1005
                elif str(row['mark']).find('垃圾评论') >= 0:
                    analyzeResult['is_spam'] = True
                elif str(row['mark']).find('错别字') >= 0:
                    op['errType'] = 1006
                elif row['mark'] in [None, '']:
                    if op.get('aspectError',None) == 0 and \
                        op.get('polarity',None) == op.get('polarityCheck', None):
                        op['errType'] = 0
    marshal(output, category, data)
