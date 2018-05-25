"""AMIVCRM Client using suds-jurko"""

from contextlib import contextmanager
import html
from suds.client import Client as SOAPClient


URL = "https://crm.amiv.ethz.ch/service/v2/soap.php?wsdl"
APPNAME = "AMIV Kontakt: Internal: Customer Relationship Management"


class AMIVCRM(object):
    """Client providing easy access to entries and entry lists.

    Attributes:
        username (str): the soap username
        password (str): the soap password
        url (str): CRM url
        appname (str): the soap appname
    """
    def __init__(self, username, password, url=URL, appname=APPNAME):
        self.client = SOAPClient(url)
        self.appname = appname
        self.username = username
        self.password = password

    def get(self, module_name, query="", order_by="", select_fields=None):
        """Get list of module entries matching the query.

        Args:
            module_name (str): CRM module, e.g. 'Accounts' for companies
            query (str): SQL query
            order_by (str): SQL order by
            select_fields (list): Fields the CRM should return

        Yields:
            dict: Parsed entry
        """
        with self._session() as session_id:
            response = self.client.service.get_entry_list(
                session=session_id,
                module_name=module_name,
                query=query,
                order_by=order_by,
                select_fields=select_fields,
                offset=0)

            for entry in response.entry_list:
                yield self._parse(entry)

    def getentry(self, module_name, entry_id, select_fields=None):
        """Get single entry specified by id.

        Args:
            entry_id (str): The ID of the entry (duh.)
            module_name (str): CRM module, e.g. 'Accounts' for companies
            elect_fields (list): Fields the crm should return

        Returns:
            dict: Result, None if nothing found.
        """
        with self._session() as session_id:
            response = self.client.service.get_entry(
                id=entry_id,
                session=session_id,
                module_name=module_name,
                select_fields=select_fields)
        parsed = self._parse(response.entry_list[0])

        # If the entry doesn't exist, the response
        # contains the field 'deleted' set to '1'
        # regardless of selected fields in query
        if parsed.get('deleted') == '1':
            return None
        return parsed

    @contextmanager
    def _session(self):
        """Session context, yields the session id for requests."""
        # Login
        auth = {'user_name': self.username, 'password': self.password}
        session_id = self.client.service.login(auth, self.appname).id

        yield session_id

        # Logout
        self.client.service.logout(session_id)

    @staticmethod
    def _safe_str(item):
        """Escape strings from CRM.

        First of all if its a string it is actually a suds Text class.
        In some environments this seems not to play along well with unicode.
        (Although it is a subclass of str)
        Therefore explicitly cast it to a str and unescape html chars.

        Possible improvement: Check if soap returns anything else but strings.
        If not, the if statement might be removed.
        """
        if isinstance(item, str):
            return html.unescape(str(item))
        return item

    @staticmethod
    def _parse(entry):
        """Turn result object into dict."""
        return {item.name: AMIVCRM._safe_str(item.value)
                for item in entry.name_value_list}
