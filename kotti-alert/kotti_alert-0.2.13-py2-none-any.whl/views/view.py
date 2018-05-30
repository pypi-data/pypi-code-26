# -*- coding: utf-8 -*-

"""
Created on 2016-07-01
:author: Oshane Bailey (b4.oshany@gmail.com)
"""
import urllib2
from pyramid.view import view_config
from pyramid.view import view_defaults

from kotti_alert import _
from kotti_alert.resources import Alert, SeenBy
from kotti_alert.fanstatic import css_and_js
from kotti_alert.views import BaseView


@view_config(
    name='kotti-alert',
    renderer='kotti_alert:templates/message.pt')
class AlertMessageView(BaseView):

    def __call__(self):
        cookie_str = self.request.cookies.get("kotti-alerts", "")
        cookie_str = urllib2.unquote(cookie_str).decode('utf8')
        alert_ids = []
        if cookie_str:
            cookies = cookie_str.split(",")
            for cookie in cookies:
                try:
                    alert_ids.append(
                        int(cookie.replace(" ", ""))    
                    )
                except TypeError as e:
                    print e
        
        user = None
        
        if self.request.user:
            user = self.request.user
        
        alert = Alert.get_by_priority(
            user=user,
            excludes=alert_ids
        )
        return {
            "alert": alert
        }


class AlertControlPanel(BaseView):
    """Control panel for kotti alerts."""
    
    @view_config(name="all-alerts",
                 permission="admin",
                 root_only=True,
                 renderer="kotti_alert:templates/list.pt")
    def list_alerts(self):
        status = self.request.params.get("status", "active")
        alerts = []
        if status == "all":
            alerts = Alert.query.all()
        elif status == "expired":
            alerts = Alert.get_expired_alerts()
        elif status == "disabled":
            alerts = Alert.get_disabled_alerts()
        else:
            alerts = Alert.get_active_alerts()
        return {
            "alerts": alerts
        }


@view_defaults(context=Alert, permission='view')
class AlertViews(BaseView):
    """ Views for :class:`kotti_alert.resources.CustomContent` """

    @view_config(name='view', renderer='kotti_alert:templates/alert.pt')
    def default_view(self):
        return {}

    @view_config(name="update-seen-by", request_method="POST", renderer="json")
    def update_seen_by(self):
        if not self.request.user:
            return {"message": "Not a valid user"}
    
        SeenBy.add(self.context.id, self.request.user.name)
        return {"message": "Seen by list has been updated"}
