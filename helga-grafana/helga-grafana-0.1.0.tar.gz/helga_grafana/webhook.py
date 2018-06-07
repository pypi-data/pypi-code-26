import json

from helga import log, settings
from helga.plugins.webhooks import route

logger = log.getLogger(__name__)

channel = getattr(settings, 'GRAFANA_WEBHOOK_CHANNEL', None)

# Sample json body
# ----------------
# {
#   "title": "My alert",
#   "ruleId": 1,
#   "ruleName": "Load peaking!",
#   "ruleUrl": "http://url.to.grafana/db/dashboard/my_dashboard?panelId=2",
#   "state": "alerting",
#   "imageUrl": "http://s3.image.url",
#   "message": "Load is peaking!  Do blah blah",
#   "evalMatches": [
#     {
#       "metric": "requests",
#       "tags": {},
#       "value": 122
#     }
#   ]
# }

@route(r'/grafana', methods=['POST'])
def grafana(request, client):

    payload = json.load(request.content)
    logger.debug("Got %s" % payload)

    message = "{title} : {message}"

    logger.debug(message.format(**payload))
    client.msg(channel, message.format(**payload))

    return 'ok - message sent'
