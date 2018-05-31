import logging
import requests
from collections import namedtuple
import os
import xml.etree.ElementTree as etree

#pylint: disable=invalid-name
logger = logging.getLogger(__name__)

# for returning multiple values instead of dict/class
AgressoRequestType = namedtuple('AgressoRequest', ['headers', 'data'])

class QueryEngineService(object):
    """QueryEngineService Instance
    An instance of QueryEngineService is a handy way to wrap an QueryEngineService session
    for easy use of the QueryEngineService.
    """

    def __init__(self, username=None, password=None, client=None, instance_url=None, soap_action_base_url='http://services.agresso.com/QueryEngineService/QueryEngineV201101'):
        """Initialize the instance with the given parameters

        Available kwargs

        Password Authentication:
        * username -- Agresso username to use for authentication, required
        * password -- the password for the user, required
        * client -- the client for the user, required e.g. GP
        * instance_url -- the url to the agresso webservice, optional e.g. https://ABCORP-test.unit4cloud.com/ca_ABCORP_test_wsHost/service.svc
        """
        if all(arg is not None for arg in (username, password, client, instance_url)):
            self.username = username
            self.client = client
            self.password = password
            self.instance_url = instance_url
            self.soap_action_base_url = soap_action_base_url
            self.session = requests.Session()
        else:
            raise ValueError(
                'You must provide login information and instance url.')

    def about(self):
        """
        About() -> AboutResult: xsd:string
        AboutResponse(AboutResult: xsd:string)
        returns the raw xml as string object
        """
        return self._execute_query('About', '<quer:About/>')

    def get_template_result_as_data_set(self, template_id):
        """
        GetTemplateResultAsDataSet(input: ns0:InputForTemplateResult, credentials: ns0:WSCredentials) -> GetTemplateResultAsDataSetResult: ns0:TemplateResultAsDataSet
        """
        # TODO: Use all other params to gettemplateasdataset soap method
        """
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:quer="http://services.agresso.com/QueryEngineService/QueryEngineV201101">
                        <soapenv:Header/>
                        <soapenv:Body>
                            <quer:GetTemplateResultAsDataSet>

                                    <quer:PipelineAssociatedName>?</quer:PipelineAssociatedName>
                                </quer:input>
                                <quer:credentials>
                                    <quer:Username>{self.username}</quer:Username>
                                    <quer:Client>{self.client}</quer:Client>
                                    <quer:Password>{self.password}</quer:Password>
                                </quer:credentials>
                            </quer:GetTemplateResultAsDataSet>
                        </soapenv:Body>
                        </soapenv:Envelope>
        """
        if template_id is None or type(template_id) is not int:
            raise TypeError("You must provide a template_id of type 'int'.")
        return self._execute_query('GetTemplateResultAsDataSet', f"<quer:input><quer:TemplateId>{template_id}</quer:TemplateId></quer:input>")

    def get_template_result_as_xml(self, template_id):
        """
        GetTemplateResultAsXML(input: ns0:InputForTemplateResult, credentials: ns0:WSCredentials) -> GetTemplateResultAsXMLResult: ns0:TemplateResultAsXML
        """
        # TODO: Use all other params to gettemplateasdataset soap method

        if (template_id is None or type(template_id) is not int):
            raise TypeError("You must provide a template_id of type 'int'.")
        return self._execute_query('GetTemplateResultAsXML', f"<quer:input><quer:TemplateId>{template_id}</quer:TemplateId></quer:input>")

    def get_template_meta_data(self, template_id):
        """
        GetTemplateMetaData(templateId: xsd:long, credentials: ns0:WSCredentials) -> GetTemplateMetaDataResult: ns0:TemplateMetaData
        """
        if (template_id is None or type(template_id) is not int):
            raise TypeError("You must provide a template_id of type 'int'.")
        return self._execute_query('GetTemplateMetaData', f"<quer:templateId>{template_id}</quer:templateId>")

    def get_template_properties(self, template_id):
        """
        GetTemplateProperties(templateId: xsd:long, credentials: ns0:WSCredentials) 
        -> GetTemplatePropertiesResult: ns0:TemplateProperties
        """
        if (template_id is None or type(template_id) is not int):
            raise TypeError("You must provide a template_id of type 'int'.")
        return self._execute_query('GetTemplateProperties', f"<quer:templateId>{template_id}</quer:templateId>")

    def get_template_result_options(self):
        """
        GetTemplateResultOptions(credentials: ns0:WSCredentials) -> GetTemplateResultOptionsResult: ns0:TemplateResultOptions
        """
        return self._execute_query('GetTemplateResultOptions', '')

    def get_expression(self, template_id):
        """
        GetExpression(templateId: xsd:long, credentials: ns0:WSCredentials) -> GetExpressionResult: ns0:Expression
        """
        if (template_id is None or type(template_id) is not int):
            raise TypeError("You must provide a template_id of type 'int'.")
        return self._execute_query('GetExpression', f"<quer:templateId>{template_id}</quer:templateId>")

    def get_format_info(self, template_id):
        """
        GetFormatInfo(templateId: xsd:long, credentials: ns0:WSCredentials) -> GetFormatInfoResult: ns0:FormatInfo
        """
        if (template_id is None or type(template_id) is not int):
            raise TypeError("You must provide a template_id of type 'int'.")
        return self._execute_query('GetFormatInfo', f"<quer:templateId>{template_id}</quer:templateId>")

    def get_search_criteria(self, template_id, hide_unused=False):
        """
        GetSearchCriteria(templateId: xsd:long, hideUnused: xsd:boolean, credentials: ns0:WSCredentials) -> GetSearchCriteriaResult: ns0:SearchCriteria
        """
        if (template_id is None or type(template_id) is not int):
            raise TypeError("You must provide a template_id of type 'int'.")
        return self._execute_query('GetSearchCriteria', f"<quer:templateId>{template_id}</quer:templateId><quer:hideUnused>{hide_unused}</quer:hideUnused>")

    def get_statistical_formula(self, template_id):
        """
        GetStatisticalFormula(templateId: xsd:long, credentials: ns0:WSCredentials) -> GetStatisticalFormulaResult: ns0:StatisticalFormula
        """
        if (template_id is None or type(template_id) is not int):
            raise TypeError("You must provide a template_id of type 'int'.")
        return self._execute_query('GetStatisticalFormula', f"<quer:templateId>{template_id}</quer:templateId>")

    def get_template_list(self, form_list, description_list):
        """
        GetTemplateList(formList: xsd:string, descrList: xsd:string, credentials: ns0:WSCredentials) -> GetTemplateListResult: ns0:TemplateList
        """
        # TODO:need to check docs for this method and make the two inputs optional, if needed and formulate the params accordingly.
        if (form_list is None or description_list is None):
            raise TypeError("You must provide form and description lists.")
        return self._execute_query('GetTemplateList', f"<quer:formList>{form_list}</quer:formList><quer:descrList>{description_list}</quer:descrList>")

    # def _get_schema_from_xml(self, data):
    #     # parsexml fromstring
    #     # get schema element on xpath
    #     from bs4 import BeautifulSoup
    #     soup = BeautifulSoup(data, 'lxml-xml')
    #     # print(soup.prettify())
    #     for e in soup.find_all('element'):
    #         print(f"{e}, {e.attrs}") 

    def _execute_query(self, soap_action, params):
        payload = self._request_builder(soap_action, params)
        result = self._call_agresso('POST', payload)
        return result.text if result.status_code == 200 else ""

    def _request_builder(self, soap_action, params=''):
        if soap_action is not 'About':
            return AgressoRequestType({'Content-Type': 'text/xml;charset=UTF-8', 'Accept-Encoding': 'gzip,deflate',
                                   'SOAPAction': f'https://services.agresso.com/QueryEngineService/QueryEngineV201101/{soap_action}'},
                                  f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:quer="{self.soap_action_base_url}">
                                <soapenv:Header/>
                                <soapenv:Body>
                                    <quer:{soap_action}>
                                        {params}
                                        <quer:credentials>
                                            <quer:Username>{self.username}</quer:Username>
                                            <quer:Client>{self.client}</quer:Client>
                                            <quer:Password>{self.password}</quer:Password>
                                        </quer:credentials>
                                    </quer:{soap_action}>
                                </soapenv:Body>
                            </soapenv:Envelope>""")
        else:
            return AgressoRequestType({'Content-Type': 'text/xml;charset=UTF-8', 'Accept-Encoding': 'gzip,deflate',
                                   'SOAPAction': f'https://services.agresso.com/QueryEngineService/QueryEngineV201101/{soap_action}'},
                                  f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:quer="{self.soap_action_base_url}">
                                <soapenv:Header/>
                                <soapenv:Body>
                                    {params}
                                </soapenv:Body>
                            </soapenv:Envelope>""")

    def _call_agresso(self, method='GET', payload=None):
        """Utility method for performing HTTP call to Agresso Webservice.

        Returns a `requests.result` object.
        """
        if payload is None or type(payload) is not AgressoRequestType:
            raise ValueError

        result = self.session.request(
            method.upper(), self.instance_url, headers=payload.headers, data=payload.data)
        if result.status_code >= 300:
            raise Exception(result.status_code, result.text)
        return result