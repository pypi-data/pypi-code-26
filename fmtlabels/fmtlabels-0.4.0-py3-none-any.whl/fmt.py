#coding=utf-8

import json
import requests
import time
import os

aspectTypeMap = {
    'petfood':{
        '产品.产品真伪': 'authenticity.fake product',
        '产品.健康': 'product.safety',
        '产品.分量': 'product.product weight',
        '产品.功效': 'product.product effect',
        '产品.味道': 'product.taste',
        '产品.外观': 'package.appearance',
        '产品.效期': 'inventory.expiration date',
        '产品.气味': 'product.product odor',
        '产品.质地': 'product.product texture',
        '产品.质量': 'product.product quality',
        '产品.适口性': 'product.product palatability',
        '产品.配方': 'product.ingredients',
        '产品.食品安全': 'product.safety',
        '价格.价格': 'price.price satisfaction',
        '包装.包装使用': 'package.package design',
        '包装.包装设计': 'package.package design',
        '包装.包装质量': 'package.package design',
        '品牌.信赖': 'branding.brand equity',
        '品牌.其他品牌形象': 'branding.brand equity',
        '品牌.忠诚度': 'branding.loyalty',
        '品牌.总体品牌形象': 'branding.brand equity',
        '品牌.推荐/介绍': 'branding.brand equity',
        '总体评价.总体评价': '',
        '服务.售后服务': 'service.customer service',
        '服务.客服-人员态度（沟通能力）': 'service.customer service',
        '服务.客服-及时性': 'service.customer service',
        '服务.客服-态度': 'service.customer service',
        '服务.客服-负责性/解决问题的能力': 'service.customer service',
        '服务.服务机制': 'service.customer service',
        '服务.服务评价': 'service.customer service',
        '活动.优惠': 'promotion',
        '活动.其他': 'promotion',
        '活动.其他/赠品': 'promotion.promotion',
        '活动.活动': 'promotion.promotion',
        '活动.赠品': 'promotion.promotion',
        '物流.仓库服务': 'logistics.logistic service',
        '物流.快递员服务': 'logistics.logistic service',
        '物流.快递服务': 'logistics.logistic service',
        '物流.物流服务（条款）': 'logistics.logistic service',
        '物流.费用': 'logistics.logistics fee',
        '物流.通用': '',
        '物流.速度': 'logistics.express speed',
        'others.others': '',
    }
}

nlpaddr = 'http://40.125.161.9:23210/api/sentiment/analysis' \
    if not 'NLP_ADDR' in os.environ else os.environ['NLP_ADDR']
rs = requests.Session()

def analyze(category, text):
    payload={'category':category,'text':text}
    for retry in [0,1,2]:
        try:
            resp = rs.post(nlpaddr, data=payload, timeout=2)
            rjson = resp.json()
            break
        except:
            time.sleep(1)
            if retry == 2:
                print('analyze failed:', category, text)
                raise
    if rjson['ok'] != True:
        if 'error' in rjson.keys():
            raise Exception(text, rjson['error']['reason'])
        raise Exception(text)

    opinions = []
    opinionsMap = {}
    result = {
        'text': text,
        'is_spam': False,
        'opinions': opinions,
        'opinionsMap': opinionsMap,
    }
    for aspect in rjson['data']:
        if aspect['emt_words'] == ['垃圾评论']:
            result['is_spam'] = True
            continue

        opinion = {
            'aspectType': aspect['levels'][0],
            'aspectSubtype': aspect['levels'][1],
            'polarity': aspect['review_rating'],
            'aspectTerm': splitField(aspect['matched_key'], []),
            'opinionTerm': [] if aspect['emt_words'] == None else aspect['emt_words'],
            'rule': None,
            'aspectError': None,
            'polarityCheck': None,
            'errType': None,
            'suggestion': {
                'addAspectTerms': None,
                'addOpinionTerms': None,
                'excludeOpinionTerms': None,
            },
            'mark': None,
        }
        opinions.append(opinion)
        opinionsMap[opinionKey(opinion)] = opinion
        result['textPolarity'] = aspect['text_emotion']
    return result

def opinionKey(opinion):
    return opinion['aspectType'] + '.' + \
           opinion['aspectSubtype'] + '=' + \
           str(opinion['polarity'])

def splitField(s, noneval = None):
    return noneval if s in ['', None] else str(s).split(',')

def marshal(output, category, data):
    #output: stream
    #data: dict{'...': { sample_data }, ...}
    if category in aspectTypeMap:
        aspMap = aspectTypeMap[category]
    else:
        aspMap = {}
    for (_, record) in data.items():
        replacedOpinions = []
        for op in record['opinions']:
            aspectType = op['aspectType'].lower() + '.' + op['aspectSubtype']
            if aspectType in aspMap:
                newType = aspMap[aspectType]
                if newType == '':
                    continue
                levels = newType.split('.')
                op['aspectType'] = levels[0]
                if len(levels) >= 2:
                    op['aspectSubtype'] = levels[1]
                else:
                    op['aspectSubtype'] = None
                replacedOpinions.append(op)
            else:
                raise Exception('Unknown aspect type:' + aspectType)
        record['opinions'] = replacedOpinions
        del record['opinionsMap']
        json.dump(record, output, ensure_ascii=False)
        output.write('\n')
