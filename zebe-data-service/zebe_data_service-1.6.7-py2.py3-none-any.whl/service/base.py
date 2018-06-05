# -*- coding: utf-8 -*-
"""
    zebe.service.base
    ~~~~~~~~~~~~~~~~

    系统基础服务，封装基于数据库实体的基本增删改查服务

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

import logging

from sqlalchemy import func


class ModelBaseService:
    # 初始化
    def __init__(self, entity, session):
        self.entity = entity
        self.session = session()

    # 校验是否为有效的实体类型
    def __is_valid_entity(self, entity):
        return entity is not None and isinstance(entity, self.entity)

    # 获取实体类的公开属性
    @staticmethod
    def __get_public_fields_of_entity(entity):
        public_fields = []
        if hasattr(entity, '_sa_instance_state'):
            keys = entity._sa_instance_state.attrs._data.keys()
            for field in keys:
                public_fields.append(field)
        logging.info('获取实体类的公开属性成功：' + str(public_fields))
        return public_fields

    # 添加数据
    def add(self, entity):
        if self.__is_valid_entity(entity):
            self.session.add(entity)
            self.session.commit()
            self.session.close()
            logging.info('保存成功')
        else:
            logging.warning('不是自身实体类型，无法添加')

    # 批量添加数据
    def multi_add(self, entity_list):
        if entity_list is not None and isinstance(entity_list, list):
            for entity in entity_list:
                if self.__is_valid_entity(entity):
                    self.session.add(entity)
            self.session.commit()
            self.session.close()
        else:
            logging.warning('不是列表数据类型，无法添加')

    # 修改数据
    def update(self, entity):
        if self.__is_valid_entity(entity):
            session_entity = self.session.query(self.entity).filter(self.entity.id == entity.id).one_or_none()
            if session_entity is not None:
                entity_fields = self.__get_public_fields_of_entity(entity)
                for field in entity_fields:
                    # 过滤掉主键(ID)
                    if field != 'id':
                        if hasattr(session_entity, field):
                            value = getattr(entity, field)
                            setattr(session_entity, field, value)
                            logging.debug('会话中的实体类设置了属性[' + field + ']=' + str(value))
                        else:
                            logging.debug('过滤掉了主键(ID)')
                self.session.commit()
                self.session.close()
                logging.info('修改成功')
            else:
                logging.error('ID为' + str(entity.id) + '的数据不存在，无法修改')
        else:
            logging.warning('不是自身实体类型，无法修改')

    # 查询全部数据条数
    def count_all(self):
        total = self.session.query(self.entity).count()
        self.session.close()
        return total

    # 查询单条数据
    def find_one(self, data_id):
        result = None
        if data_id is not None:
            result = self.session.query(self.entity).filter(self.entity.id == data_id).one_or_none()
            self.session.close()
            logging.info('查询单条数据 -> 成功')
        else:
            logging.warning('查询单条数据 -> 失败，因为ID为空')
        return result

    # 随机查询一条数据
    def find_one_random(self):
        result = self.session.query(self.entity).order_by(func.random()).limit(1).one_or_none()
        self.session.close()
        return result

    # 查询全部数据
    def find_all(self):
        result = self.session.query(self.entity).all()
        self.session.close()
        logging.info('查询全部数据 -> 成功')
        return result

    # 分页查询数据
    def find_by_page(self, page, per_page):
        offset = (page - 1) * per_page
        result = self.session.query(self.entity).order_by(self.entity.id.asc()).offset(offset).limit(per_page).all()
        self.session.close()
        logging.info('分页查询数据 -> 成功')
        return result

    # 根据实例删除单条数据
    def delete_one(self, entity):
        if self.__is_valid_entity(entity):
            self.session.query(self.entity).filter(self.entity.id == entity.id).delete()
            self.session.commit()
            self.session.close()
            logging.info('根据实例删除单条数据 -> 成功')
        else:
            logging.warning('不是自身实体类型，无法删除')

    # 根据ID删除单条数据
    def delete_one_by_id(self, data_id):
        if data_id is not None:
            self.session.query(self.entity).filter(self.entity.id == data_id).delete()
            self.session.commit()
            self.session.close()
            logging.info('根据ID删除单条数据 -> 成功')
        else:
            logging.warning('根据ID删除单条数据 -> 失败，因为ID为空')

    # 根据ID删除多条数据
    def delete_many_by_ids(self, data_ids):
        if data_ids is not None:
            if isinstance(data_ids, list):
                data_list = self.session.query(self.entity).filter(self.entity.id.in_(data_ids))
                for data in data_list:
                    self.session.delete(data)
                self.session.commit()
                self.session.close()
                logging.info('根据ID删除多条数据 -> 成功')
            else:
                logging.warning('根据ID删除多条数据 -> 失败，因为传入的ID参数不是集合')
        else:
            logging.warning('根据ID删除多条数据 -> 失败，因为ID为空')

    # 删除全部数据
    def delete_all(self):
        self.session.query(self.entity).delete(synchronize_session=False)
        self.session.commit()
        self.session.close()
        logging.info('删除全部数据 -> 成功')
