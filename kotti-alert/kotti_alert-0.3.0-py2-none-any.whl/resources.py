# -*- coding: utf-8 -*-

"""
Created on 2016-07-01
:author: Oshane Bailey (b4.oshany@gmail.com)
"""

import datetime
from kotti import Base, DBSession
from kotti.interfaces import IDefaultWorkflow
from kotti.resources import Content, Document
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Unicode,
    String,
    Boolean,
    DateTime
)
from sqlalchemy.types import (
    Date
)
from sqlalchemy.sql import func, exists
import transaction
from zope.interface import implements
from sqlalchemy.orm import relationship

from kotti_alert import _


class SeenBy(Base):
    
    date_added = Column(DateTime, default=func.now())
    alert_id = Column(
        Integer,
        ForeignKey('alerts.id', onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True)
    username = Column(
        Unicode(100),
        ForeignKey('principals.name', onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True)

    @classmethod
    def check(cls, alert_id, username):
        alert = cls.query.filter(
            cls.alert_id == alert_id,
            cls.username == username
        ).first()
        return True if alert is not None else False

    @classmethod
    def add(cls, alert_id, username):
        with transaction.manager:
            alert = cls(alert_id=alert_id, username=username)
            DBSession.add(alert)
                


class Alert(Document):
    """ A custom content type. """

    implements(IDefaultWorkflow)

    id = Column(Integer, ForeignKey('documents.id'), primary_key=True)
    end_date = Column(Date, default=func.now())
    alert_status = Column(String, default="info")
    alert_type = Column(String, default="alert")
    priority = Column(Integer, default=10)
    active = Column(Boolean, default=False)
    track_user = Column(Boolean, default=True)
    username_or_group = Column(Unicode(100))
    seen_by = relationship("SeenBy", cascade="save-update, merge, delete")
    

    type_info = Content.type_info.copy(
        name=u'Alert',
        title=_(u'Site Alert'),
        add_view=u'add_alert',
        addable_to=[u'Document']
    )
    
    def __init__(self, **kwargs):
        super(Alert, self).__init__(**kwargs)
        self.in_navigation = False

    def get_status_title(self):
        if self.alert_status == "info":
            return "General"
        elif self.alert_status == "warning":
            return "Warning"
        elif self.alert_status == "danger":
            return "Important"
        return ""

    def is_active(self):
        return self.end_date >= datetime.date.today()
    
    @classmethod
    def get_all(cls, user=False, excludes=[]):
        """Get the latest alert by priority
        
        :params user_or_group:      Username or group to filter by.
        :params exludes:            List of user IDs to exclude from the result
                                    set.
        :params user:               Current logged in user object. If set to
                                    None, then all alerts will be returned
                                    without performing any user query.
                                    If set to False, user roles will be
                                    performed in the query.
        
        :returns Alert:             Returns the first matching alert object,
                                    else None.
        """
        query = cls.query.outerjoin(
            SeenBy
        )
        if excludes:
            query = query.filter(
                ~cls.id.in_(excludes)
            )
        if user:
            query = query.filter(
                (cls.username_or_group == user.name) |
                (cls.username_or_group.in_(user.groups)) |
                (cls.username_or_group == '')
            )
        elif user is None:
            query = query.filter(
                cls.username_or_group == ''
            )
        return query

    @classmethod
    def get_active_alerts(cls, user=False, excludes=[]):
        """Get the latest active alerts by priority
        
        :params user_or_group:      Username or group to filter by.
        :params exludes:            List of user IDs to exclude from the result
                                    set.
        :params user:               Current logged in user object. If set to
                                    None, then all alerts will be returned
                                    without performing any user query.
                                    If set to False, user roles will be
                                    performed in the query.
        
        :returns Alert:             Returns the first matching alert object,
                                    else None.
        """
        query = cls.get_all(user=user, excludes=excludes)
        return query.filter(
            cls.active == True,
            cls.end_date >= datetime.date.today()
        ).order_by(
            cls.priority.asc(),
            cls.modification_date.desc()
        )

    @classmethod
    def get_expired_alerts(cls, user=False, excludes=[]):
        """Get all expired alerts by priority
        
        :params user_or_group:      Username or group to filter by.
        :params exludes:            List of user IDs to exclude from the result
                                    set.
        :params user:               Current logged in user object. If set to
                                    None, then all alerts will be returned
                                    without performing any user query.
                                    If set to False, user roles will be
                                    performed in the query.
        
        :returns Alert:             Returns the first matching alert object,
                                    else None.
        """
        query = cls.get_all(user=user, excludes=excludes)
        return query.filter(
            cls.end_date < datetime.date.today()
        ).order_by(
            cls.priority.asc(),
            cls.modification_date.desc()
        )

    @classmethod
    def get_disabled_alerts(cls, user=False, excludes=[]):
        """Get all disabled alerts by priority
        
        :params user_or_group:      Username or group to filter by.
        :params exludes:            List of user IDs to exclude from the result
                                    set.
        :params user:               Current logged in user object. If set to
                                    None, then all alerts will be returned
                                    without performing any user query.
                                    If set to False, user roles will be
                                    performed in the query.
        
        :returns Alert:             Returns the first matching alert object,
                                    else None.
        """
        query = cls.get_all(user=user, excludes=excludes)
        return query.filter(
            cls.end_date < datetime.date.today()
        ).order_by(
            cls.priority.asc(),
            cls.modification_date.desc()
        )
      
    @classmethod
    def get_by_priority(cls, user=False, excludes=[]):
        """Get the latest alert by priority
        
        :params user_or_group:      Username or group to filter by.
        :params exludes:            List of user IDs to exclude from the result
                                    set.
        :params user:               Current logged in user object. If set to
                                    None, then all alerts will be returned
                                    without performing any user query.
                                    If set to False, user roles will be
                                    performed in the query.
        
        :returns Alert:             Returns the first matching alert object,
                                    else None.
        """
        query = cls.get_all(user=user, excludes=excludes)
        query = query.filter(
            cls.active == True,
            cls.end_date >= datetime.date.today()
        )
        return query.order_by(
            cls.priority.asc(),
            cls.modification_date.desc()
        ).limit(1).first()
        