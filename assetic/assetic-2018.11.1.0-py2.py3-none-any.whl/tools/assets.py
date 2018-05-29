# coding: utf-8

"""
    assetic.AssetTools  (assets.py)
    Tools to assist with using Assetic API's for assets, components and
    dimensions.
    Key tools to use are create_complete_asset, update_complete_asset and
    get_complete_asset.
    These tools use the tools object AssetToolsCompleteAssetRepresentation
"""
from __future__ import absolute_import

import six
from ..api_client import ApiClient
from ..rest import ApiException
from ..api import AssetApi
from ..api import ComponentApi
from ..models.assetic3_integration_representations_complex_asset_representation\
     import Assetic3IntegrationRepresentationsComplexAssetRepresentation
from ..models.assetic3_integration_representations_component_representation\
     import Assetic3IntegrationRepresentationsComponentRepresentation
from ..models.assetic3_integration_representations_component_dimension_representation\
     import Assetic3IntegrationRepresentationsComponentDimensionRepresentation
from ..models.assetic3_integration_representations_custom_address\
     import Assetic3IntegrationRepresentationsCustomAddress
from pprint import pformat

class AssetTools(object):
    """
    Class to manage processes that sync Assetic search data to a local DB
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client
        
        self.logger = api_client.configuration.packagelogger

        self.assetapi = AssetApi()
        self.componentapi = ComponentApi()

    def create_complete_asset(self,complete_rep):
        """
        Create an asset and it's component and dimensions
        :param complete_rep: AssetToolsCompleteAssetRepresentation
        :return: AssetToolsCompleteAssetRepresentation or None
        """

        asset = complete_rep.asset_representation  #alias with shorter name
        ##First create the asset
        newasset = self.create_asset(complete_rep.asset_representation)
        if newasset == None or len(newasset["Data"])==0:
            return None

        ##get assetguid
        asset.id = newasset["Data"][0]["Id"]
        asset.asset_id = newasset["Data"][0]["AssetId"]
        self.logger.debug("New asset guid {0}".format(asset.id))
        
        ##Next create the component(s) and dimensions(s)
        for toolcomponent in complete_rep.components:
            component = toolcomponent.component_representation
            component.asset_id = asset.asset_id
            new_component = self.create_component(component)
            if new_component == None:
                return None
            ##record component details
            component.id = new_component["Id"]
            component.name = new_component["Name"]

            ##create the dimensions for this component.
            for dimension in toolcomponent.dimensions:
                dimension.component_id = component.id
                newdimension = self.create_dimension(dimension)
                if newdimension == None:
                    return None
                dimension.id = newdimension["Id"]
                
        return complete_rep

    def update_complete_asset(self,complete_rep,setNulls=False):
        """
        Update an asset and it's component and dimensions
        :param complete_rep: AssetToolsCompleteAssetRepresentation
        :param setNulls: optional default is False.  If True then empty fields
        in the passed in object will be set to null, otherwise the default is to
        keep the existing value of fields with no defined value in the object
        :return: return code 0=success,1=error
        """
        errcode = 0

        complex_asset_representation = complete_rep.asset_representation
        #update complex asset first
        if complex_asset_representation != None:
            errcode = self.update_complex_asset(complex_asset_representation,
                    setNulls)
        if errcode > 0:
                return errcode

        ##update components
        for component in complete_rep.components:
            errcode = self.update_component(component.component_representation,
                                            setNulls)
            if errcode > 0:
                return errcode
            
            ##update dimensions
            for dimension in component.dimensions:
                errcode = self.update_dimension(dimension,setNulls)
                if errcode > 0:
                    return errcode            
        return errcode

    def get_complete_asset(self,assetid,attributelist = None):
        """
        Get an asset and it's component and dimensions
        :param assetid: Asset GUID or User friendly ID
        :param attributelist: A list of additional attributes to get, or None
        :return: AssetToolsCompleteAssetRepresentation or None
        """
        ##create an instance of the return object
        complete_asset = AssetToolsCompleteAssetRepresentation()
        #get the asset data
        asset = self.get_asset(assetid,attributelist)
        if asset == None:
            return None
        ##assign the asset data to the asset representation
        assetrep = Assetic3IntegrationRepresentationsComplexAssetRepresentation()
        ##loop through the asset representation and set the values from response
        for k,v in six.iteritems(assetrep.attribute_map):
            if v in asset and asset[v] != None and \
               k not in ("links","embedded"):
                setattr(assetrep,k,asset[v])

        complete_asset.asset_representation = assetrep

        ##array list to put component plus dimensions
        components_and_dims = []
    
        #get the component data
        searchfilter = "AssetId='{0}'".format(asset["AssetId"])
        componentlist = self.get_component_list_by_filter(searchfilter)

        ##loop through component data and assign component & dimensions
        for comprow in componentlist:
            #instantiate complete component representation
            component_dim_obj = AssetToolsComponentRepresentation()
            #instantiate component representation
            component_rep = Assetic3IntegrationRepresentationsComponentRepresentation()
            ##loop through the component representation and set the values
            for k,v in six.iteritems(component_rep.attribute_map):
                if v in comprow and comprow[v] != None and \
                   k not in ("links","embedded"):
                    setattr(component_rep,k,comprow[v])
            #assign the component to the component/dim obj
            component_dim_obj.component_representation = component_rep
            
            ##get dimensions for the component
            dimensions = self.get_dimensions(comprow["Id"])
            dims = []
            ##loop through the dimension representation and set the values
            for dimrow in dimensions:
                dim_rep = Assetic3IntegrationRepresentationsComponentDimensionRepresentation()
                for k,v in six.iteritems(dim_rep.attribute_map):
                    if v in dimrow and dimrow[v] != None and \
                       k not in ("links","embedded"):
                        setattr(dim_rep,k,dimrow[v])
                dims.append(dim_rep)
            #Add the dimension array to the component/dim object
            component_dim_obj.dimensions = dims
            ##Add component to the list
            components_and_dims.append(component_dim_obj)

        ##add component list to complete asset
        complete_asset.components = components_and_dims

        return complete_asset
    
    def create_asset(self,asset_representation):
        """
        Create an asset
        :param asset_representation: required 
        Assetic3IntegrationRepresentationsComplexAssetRepresentation
        :return: resultant asset as
        Assetic3IntegrationRepresentationsComplexAssetRepresentation
        """

        ##First make sure the object is corret
        self.logger.debug("Verify asset fields")
        mandatory_fields = ["asset_category","asset_name"]
        if self.verify_mandatory_fields(asset_representation,
            Assetic3IntegrationRepresentationsComplexAssetRepresentation,
            mandatory_fields) == False:
            return None

        ##create the asset
        self.logger.info("Create the asset {0}".format(
            asset_representation.asset_name))
        try:
            response = self.assetapi.asset_post(asset_representation)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status,e.reason,e.body))
            return None

        return response

    def create_component(self,component_representation):
        """
        Create an component for the given component ID
        :param component_representation: an instance of
        Assetic3IntegrationRepresentationsComponentRepresentation defining the
        component to create        
        :return: component response object or None
        """
        ##First make sure the object is correct & mandatory fields are defined
        self.logger.debug("Verify component fields & type {0}".format(
            type(component_representation)))
        mandatory_fields = ["asset_id","label","component_type",
                            "dimension_unit","network_measure_type"]
        if self.verify_mandatory_fields(component_representation,
            Assetic3IntegrationRepresentationsComponentRepresentation,
            mandatory_fields) == False:
            return None
        
        self.logger.info("Create the component {0}".format(
            component_representation.name))
        
        ##create the component
        try:
            component = self.componentapi.component_post(
                component_representation)
        except ApiException as e:
            msg = "Status {0}, Reason: {1} {2}".format(e.status,e.reason,e.body)
            self.logger.error(msg)
            return None
        
        return component["Data"][0]

    def create_dimension(self,dimension_representation):
        """
        Create an component for the given component ID
        :param assetid: Assetic component GUID or user friendly component ID
        :return: component response object or None
        """
        ##First make sure the object is correct & mandatory fields are defined
        self.logger.debug("Verify dimension fields")
        mandatory_fields = ["component_id","network_measure","unit",
            "record_type","network_measure_type"]
        if self.verify_mandatory_fields(dimension_representation,
            Assetic3IntegrationRepresentationsComponentDimensionRepresentation,
            mandatory_fields) == False:
            return None
        
        self.logger.info("Create the dimension for component {0}".format(
            dimension_representation.component_id))
        
        ##create the dimension
        try:
            dim = self.componentapi.component_post_dimension(
                dimension_representation.component_id,dimension_representation)
        except ApiException as e:
            msg = "Status {0}, Reason: {1} {2}".format(e.status,e.reason,e.body)
            self.logger.error(msg)
            return None
        
        return dim
    
    def verify_mandatory_fields(self,data_repr,required_repr,mandatory_fields=[]):
        """
        Verify the representation type is correct and mandatory fields not null
        :param data_repr: The representation object with the data
        :param representation_name: The expected representation
        e.g. Assetic3IntegrationRepresentationsComplexAssetRepresentation
        :param mandatory_fields: a list of fields to verify.  Optional
        :return: True (valid), False (invalid)
        """
        ##check the type is correct
        if isinstance(data_repr,required_repr) != True:
            msg ="Data object is not the required type: '{0}'".format(
                str(required_repr))
            self.logger.error(msg)
            return False
        ##check the mandatory fields are not NULL
        for field in mandatory_fields:
            if getattr(data_repr,field) == None:
                msg ="Required parameter cannot be NULL: '{0}'".format(field)
                self.logger.error(msg)
                return False                    
        return True

    def update_asset(self,complex_asset_representation,setNulls=False):
        """
        Update an asset
        :param complex_asset_representation: required
        Assetic3IntegrationRepresentationsComplexAssetRepresentation
        :param setNulls: optional, default is False.  If True then empty fields in the
        passed in object will be set to null, otherwise the default is to
        keep the existing value of fields with no defined value in the object
        :return: return code 0=success,1=error
        """
        errcode = self.update_complex_asset(complex_asset_representation,
                    setNulls)

        return errcode
    
    def update_complex_asset(self,complex_asset_representation,setNulls=False):
        """
        Update a complex asset
        :param complex_asset_representation: required
        Assetic3IntegrationRepresentationsComplexAssetRepresentation
        :param setNulls: optional, default is False.  If True then empty fields
        in the passed in object will be set to null, otherwise the default is to
        keep the existing value of fields with no defined value in the object
        :return: return code 0=success,1=error
        """
        ##First make sure the object is correct and that the assetid is defined
        if isinstance(complex_asset_representation,\
        Assetic3IntegrationRepresentationsComplexAssetRepresentation) != True:
            msg ="update_asset requires param \
                Assetic3IntegrationRepresentationsComplexAssetRepresentation"
            self.logger.error(msg)
            return 1            
        searchassetid = None
        if complex_asset_representation.id != None:
            searchassetid = complex_asset_representation.id
        elif complex_asset_representation.asset_id != None:
            searchassetid = complex_asset_representation.asset_id
        if searchassetid == None:
            msg = "update_asset requires either id or asset_id"
            self.logger.error(msg)
            return 1

        #api has a predefined set of core fields
        #can define additional asset attribute fields
        #attribute field names are the internal field names, get using metadata api

        ##first get asset as no partial put, and need last mod date
        ##(i.e.all core fields updated even if not specified in put)
        current = self.get_asset(searchassetid)
        if current == None:
            return 1
            
        ##update last_modified to reflect recent get
        complex_asset_representation.last_modified = current.get("LastModified")

        if setNulls == False:            
            ##loop through the passed in object and set the values for
            ##null fields to be that of the current asset values
            for k,v in six.iteritems(complex_asset_representation.attribute_map):
                if getattr(complex_asset_representation,k) == None \
                and v in current and current[v] != None and \
                k not in ("links","embedded","attributes"):
                    setattr(complex_asset_representation,k,current[v])

        ##now execute the update
        try:
            response = self.assetapi.asset_put(
                complex_asset_representation.id,complex_asset_representation)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status,e.reason,e.body))
            return 1
        return 0
    
    def get_asset(self,assetid,attributelist = None):
        """
        Get an component for the given asset ID
        :param assetid: Assetic asset GUID or user friendly asset ID
        :param attributelist: A list of additional attributes to get, or None
        :return: asset response object or None
        """
        if attributelist == None:
            attributelist = []
        try:
            asset = self.assetapi.asset_get(assetid,attributelist)
        except ApiException as e:
            if e.status == 404:
                msg = "Asset for Asset ID {0} not found".format(assetid)
                self.logger.error(msg)
            else:
                msg = "Status {0}, Reason: {1} {2}".format(e.status,e.reason,
                                                           e.body)
                self.logger.error(msg)
            return None

        return asset
        
    def update_component(self,component_representation,setNulls=False):
        """
        Update an asset component
        :param component_representation: required
        Assetic3IntegrationRepresentationsComponentRepresentation
        :param setNulls: optional, default is False.  If True then empty fields
        in the passed in object will be set to null, otherwise the default is to
        keep the existing value of fields with no defined value in the object
        :return: return code 0=success,>0=error
        """

        ##First make sure the object is correct & the component id is defined
        if isinstance(component_representation,\
        Assetic3IntegrationRepresentationsComponentRepresentation) != True:
            msg ="update_asset component requires param \
                Assetic3IntegrationRepresentationsComponentRepresentation"
            self.logger.error(msg)
            return 1
        
        if component_representation.id != None:
            componentid = component_representation.id
        else:
            msg = "update_component requires id to be set"
            self.logger.error(msg)
            return 1
        
        self.logger.debug("Update the component {0}".format(componentid))

        if setNulls == False:
            current = self.get_component(componentid)
            if current == None:
            #Component does not exist, or error
                return 1

            ##loop through the passed in object and set the values for
            ##null fields to be that of the current component values
            for k,v in six.iteritems(component_representation.attribute_map):
                if getattr(component_representation,k) == None \
                and v in current and current[v] != None and \
                k not in ("links","embedded"):
                    setattr(component_representation,k,current[v])
                    
        ##create instance of component api
        componentapi = ComponentApi(self.api_client)
        try:
            component = self.componentapi.component_put(componentid,
                                                   component_representation)
        except ApiException as e:
            msg = "Status {0}, Reason: {1} {2}".format(e.status,e.reason,e.body)
            self.logger.error(msg)
            return e.status

        return 0
        
    def get_component(self,componentid):
        """
        Get an component for the given component ID
        :param assetid: Assetic component GUID or user friendly component ID
        :return: component response object or None
        """
        self.logger.debug("Get the component {0}".format(componentid))
        try:
            component = self.componentapi.component_get(componentid)
        except ApiException as e:
            if e.status == 404:
                msg = "Component for Component GUID {0} not found".format(
                    componentid)
                self.logger.error(msg)
            else:
                msg = "Status {0}, Reason: {1} {2}".format(e.status,e.reason,
                                                           e.body)
                self.logger.error(msg)
            return None
        return component

    def get_component_list_by_filter(self,searchfilter):
        """
        Get an component for the given component ID 
        :param searchfilter: Search filter, same format as aset search filter
        :return: component array or empty array
        """
        kw = {'request_params_page':1,
        'request_params_page_size':500,
        'request_params_sorts':'Name-desc',
        'request_params_filters':searchfilter}
        self.logger.debug("Get the components for search filter {0}".format(
            searchfilter))
        try:
            component = self.componentapi.component_get_0(**kw)
        except assetic.rest.ApiException as e:
            msg = "Status {0}, Reason: {1} {2}".format(e.status,e.reason,e.body)
            self.logger.error(msg)
            return []
        if component["TotalResults"] > 0:
            return component["ResourceList"]
        else:
            return []
    
    def update_dimension(self,dimension_representation,setNulls=False):
        """
        Update component dimension        
        :param dimension_representation: optional
        Assetic3IntegrationRepresentationsComponentDimensionRepresentation
        :param setNulls: optional, default is False.  If True then empty fields
        in the passed in object will be set to null, otherwise the default is to
        keep the existing value of fields with no defined value in the object
        :return: return code 0=success,>0=error
        """
        ##First make sure the object is correct
        ##& the component id and dimension id are defined
        if isinstance(dimension_representation,\
        Assetic3IntegrationRepresentationsComponentDimensionRepresentation) != True:
            msg ="update_asset component requires param \
                Assetic3IntegrationRepresentationsComponentDimensionRepresentation"
            self.logger.error(msg)
            return 1
        
        if dimension_representation.id != None:
            dimensionid = dimension_representation.id
        else:
            msg = "update_dimension requires dimension id to be set (the id "\
                  "parameter, not document_id parameter which is an integer)"
            self.logger.error(msg)
            return 1

        if dimension_representation.component_id != None:
            componentid = dimension_representation.component_id
        else:
            msg = "update_dimension requires component_id to be set"
            self.logger.error(msg)
            return 1

        msg = "Update the dimension {0} for component {1}".format(
            dimensionid,componentid)
        self.logger.debug(msg)

        if setNulls == False:
            current = self.get_dimensions(componentid)
            if len(current) == 0:
                #dimension does not exist, or error
                msg = "Dimensions not found for component {0}".format(
                    componentid)
                self.logger.error(msg)
                return 1
            dim_found = False
            for dim in current:
                msg = "Dimension in component {0}, dimension to update {1}".format(
                    dim["Id"],dimensionid)
                self.logger.debug(msg)
                if dim["Id"] == dimensionid:
                    dim_found = True
                    ##loop through the passed in object and set the values for
                    ##null fields to be that of the current component values
                    for k,v in six.iteritems(dimension_representation.attribute_map):
                        if getattr(dimension_representation,k) == None \
                        and v in dim and dim[v] != None and \
                        k not in ("links","embedded"):
                            setattr(dimension_representation,k,dim[v])
                    break
            if dim_found == False:
                msg = "Dimension {0} not found for component {1}".format(
                    dimensionid,componentid)
                self.logger.error(msg)
                return 1
            
        ##create instance of component api
        componentapi = ComponentApi(self.api_client)
        try:
            dimension = self.componentapi.component_put_dimension(componentid,
                            dimensionid,dimension_representation)
        except ApiException as e:
            msg = "Status {0}, Reason: {1} {2}".format(e.status,e.reason,e.body)
            self.logger.error(msg)
            return e.status

        return 0
        
        
    def get_dimensions(self,componentid):
        """
        Get an dimension array for the given component ID
        :param assetid: Assetic component GUID or user friendly component ID
        :return: dimension response object or empty array
        """
        self.logger.debug("Get the dimensions for component {0}".format(
            componentid))
        try:
            dimensions = self.componentapi.component_get_dimension(componentid)
        except ApiException as e:
            if e.status == 404:
                msg = "Dimensions for Component {0} not found".format(assetguid)
                self.logger.error(msg)
            else:
                msg = "Status {0}, Reason: {1} {2}".format(e.status,e.reason,
                                                           e.body)
                self.logger.error(msg)
            return []
        return dimensions["ResourceList"]

    def get_asset_address_spatial(self,assetguid):
        """
        Get the address and/or spatial definition for an asset
        :param assetid: The asset GUID (TODO support friendly ID)
        assetic.Assetic3IntegrationRepresentationsCustomAddress
        :returns: geojson response or error number if error
        """
        try:
            spatial = self.assetapi.asset_search_spatial_information_by_asset_id(assetguid)
        except ApiException as e:
            if e.status == 404:
                #no spatial data, but that's ok
                return None
            else:
                msg = "Status {0}, Reason: {1} {2}".format(e.status,e.reason,
                                                           e.body)
                self.logger.error(msg)
                return int(e.status)
        return spatial
        
    def set_asset_address_spatial(self,assetguid,geojson,addr=None):
        """
        Set the address and/or spatial definition for an asset
        :param assetid: The asset GUID (TODO support friendly ID)
        :param geojson: The geojson of the spatial feature
        :param addr: Address representation.  Optional.  Of type
        assetic.Assetic3IntegrationRepresentationsCustomAddress
        :returns: 0=no error, >0 = error
        """
        if addr !=None:
            if isinstance(addr,Assetic3IntegrationRepresentationsCustomAddress)\
            == False:
                msg = "Format of address incorrect,expecting "\
                      "assetic.Assetic3IntegrationRepresentationsCustomAddress"            
                self.logger.debug(msg)
                return 1
        else:
            addr = Assetic3IntegrationRepresentationsCustomAddress()

        ##see if asset already has an address
        existing = self.get_asset_address_spatial(assetguid)
        if isinstance(existing,int):
            ## there was an error, so exit
            return existing
        if existing != None and existing["Data"]!= None and \
        existing["Data"]["properties"] != None and \
        existing["Data"]["properties"]["AssetPhysicalLocation"] != None:
            ##we have an exisiting address!
            existingaddr = existing["Data"]["properties"]["AssetPhysicalLocation"]
            if (addr.id != None and addr.id == existingaddr["id"]) \
               or addr.id == None:
                ##loop through the passed in object and set the values for
                ##null fields to be that of the current address values
                for k,v in six.iteritems(addr.attribute_map):
                    if getattr(addr,k) == None \
                    and v in existingaddr and existingaddr[v] != None and \
                    k not in ("links","embedded"):
                        setattr(addr,k,existingaddr[v])

        ##must have country
        if addr.country == None:
            addr.country = " "   
        #prepare payload
        data = {
                "SpatialData": {
                    "geometry": geojson,
                    "properties": {
                        "AssetPhysicalLocation":{
                            "StreetNumber":addr.street_number,
                            "StreetAddress":addr.street_address,
                            "CitySuburb":addr.city_suburb,
                            "State":addr.state,
                            "ZipPostcode":addr.zip_postcode,
                            "Country":addr.country}
                        },
                    "type": "Feature"
                }
            }

        ##Now add address and spatial
        try:
            spatial = self.assetapi.asset_update_spatial_information_by_asset_id(assetguid,data)
        except ApiException as e:
            msg = "Error creating spatial. Status {0}, Reason: {1} {2}".format(
                    e.status,e.reason,e.body)
            self.logger.error(msg)
            return int(e.status)
        return 0
    
class AssetToolsCompleteAssetRepresentation(object):
    """"
    A structure for defining an asset along with it's compoents
    and dimensions within the components
    """
    def __init__(self,asset_representation=None,components=None):
        """
        :param asset_representation:
        Assetic3IntegrationRepresentationsComplexAssetRepresentation
        """
        self.fieldtypes = {
            "asset_representation": "",
            "components": "list[AssetToolsComponentRepresentation]",
        }

        self._asset_representation = asset_representation
        if components == None:
            components = []
        self._components = components

        api_client = ApiClient()           
        self.logger = api_client.configuration.packagelogger

    @property
    def asset_representation(self):
        return self._asset_representation
    @asset_representation.setter
    def asset_representation(self,asset_representation):
        rep = ""
        ##check the type is correct
        if isinstance(asset_representation,
        Assetic3IntegrationRepresentationsComplexAssetRepresentation) != True:
            msg ="asset_representation is not the required type: '{0}'".format(
                "Assetic3IntegrationRepresentationsComplexAssetRepresentation")
            self.logger.error(msg)
            self._asset_representation == None
        else:
            self._asset_representation = asset_representation
        
    @property
    def components(self):
        return self._components
    @components.setter
    def components(self,components):
        if components == None:
            components = []
        validcoms = []
        self._components = []
        for com in components:
            ##check the type is correct
            if isinstance(com,
            AssetToolsComponentRepresentation) != True:
                msg ="component list value is not the required type: '{0}'"\
                      "".format(
                    "AssetToolsComponentRepresentation")
                self.logger.error(msg)
            else:
                validcoms.append(com)            
            self._components = validcoms
        
        
    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in six.iteritems(self.fieldtypes):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other

class AssetToolsComponentRepresentation(object):
    """"
    A structure for returning the created GUID and Friendly ID of
    component created via the method create_full_asset
    """
    def __init__(self,component_representation=None,dimensions=None):

        self.fieldtypes = {
            "component_representation": "Assetic3IntegrationRepresentationsComponentRepresentation",
            "dimensions": "list[Assetic3IntegrationRepresentationsComponentDimensionRepresentation]",
        }

        self._component_representation = component_representation
        self._dimensions = dimensions

        api_client = ApiClient()           
        self.logger = api_client.configuration.packagelogger

    @property
    def component_representation(self):
        return self._component_representation
    @component_representation.setter
    def component_representation(self,component_representation):
        ##check the type is correct
        if isinstance(component_representation,
        Assetic3IntegrationRepresentationsComponentRepresentation) != True:
            msg ="component_representation is not the required type: '{0}'"\
                  "".format(
                "Assetic3IntegrationRepresentationsComponentRepresentation")
            self.logger.error(msg)
            self._component_representation == None
        else:
            self._component_representation = component_representation
        
    @property
    def dimensions(self):
        return self._dimensions
    @dimensions.setter
    def dimensions(self,dimensions):
        if dimensions == None:
            dimensions = []
        validdims = []
        for dim in dimensions:
            ##check the type is correct
            if isinstance(dim,
            Assetic3IntegrationRepresentationsComponentDimensionRepresentation)\
            != True:
                msg ="dimension_representation is not the required type: '{0}'"\
                      "".format(
                    "Assetic3IntegrationRepresentationsComponentDimensionRepresentation")
                self.logger.error(msg)
            else:
                validdims.append(dim)            
            self._dimensions = validdims
        
    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in six.iteritems(self.fieldtypes):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
