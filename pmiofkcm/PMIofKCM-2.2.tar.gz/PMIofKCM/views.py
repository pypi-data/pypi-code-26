# -*- coding: utf-8 -*-
from django.http import JsonResponse
from djangoApiDec.djangoApiDec import queryString_required
from PMIofKCM import PMI
from udic_nlp_API.settings_database import uri

multilanguage_model = {
    'zh': PMI('zh', uri, ngram=True)
}

@queryString_required(['lang', 'keyword'])
def pmi(request):
    """Generate list of term data source files
    Returns:
        if contains invalid queryString key, it will raise exception.
    """
    keyword = request.GET['keyword']
    lang = request.GET['lang']
    p = multilanguage_model[lang]
    return JsonResponse(p.get(keyword, int(request.GET['num']) if 'num' in request.GET else 10), safe=False)
