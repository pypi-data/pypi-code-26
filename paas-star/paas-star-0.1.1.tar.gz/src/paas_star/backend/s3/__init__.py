import typing
from boto import connect_s3
from apistar.http import QueryString
from boto.s3.connection import OrdinaryCallingFormat

from toolkit.frozen import FrozenSettings
from star_builder import Component

from .dummy_s3 import DummyS3
from ..mongo.mongo import Mongo
from .s3 import S3 as S3Connection

S3 = typing.TypeVar('S3')


class S3Component(Component):

    async def resolve(self, settings: FrozenSettings,
                mongo: Mongo,
                project: QueryString="pangu") -> S3:
        if settings.PAAS_CLUSTER in ["adr", "research"]:
            col = mongo[settings.S3_CONFIG_DB][settings.S3_CONFIG_COLLECTION]
            keys = await col.find_one(
                {
                    "project": project
                },
                {
                    "aws_access_key_id": 1,
                    "aws_secret_access_key": 1,
                    "_id": 0
                })

            if not keys:
                keys = {"aws_access_key_id": settings.ACCESS_KEY,
                        "aws_secret_access_key": settings.SECRET_KEY}
            # 公有云
            return S3Connection(
                **keys,
                host=settings.S3_HOST,
                is_secure=False,
                calling_format=OrdinaryCallingFormat(),
            )
        else:
            # 私有云
            return DummyS3(mongo)
