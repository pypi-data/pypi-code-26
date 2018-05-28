from .daily_macro_agent import *
from .monthly_macro_agent import *
from .daily_emotion_agent import *
from .validation_agent import *
agent_mapper = {
    "水泥": get_shuini,
    "国债利差": licha,
    "CRB": get_crb,

}