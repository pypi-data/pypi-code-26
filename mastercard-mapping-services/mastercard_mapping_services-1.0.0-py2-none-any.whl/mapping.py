#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2016 MasterCard International Incorporated
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list of
# conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of
# conditions and the following disclaimer in the documentation and/or other materials
# provided with the distribution.
# Neither the name of the MasterCard International Incorporated nor the names of its
# contributors may be used to endorse or promote products derived from this software
# without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#


from __future__ import absolute_import
from mastercardapicore import BaseObject
from mastercardapicore import RequestMap
from mastercardapicore import OperationConfig
from mastercardapicore import OperationMetadata
from mastercardmappingservices import ResourceConfig

class Mapping(BaseObject):
	"""
	
	"""

	__config = {
		
		"02eef2e3-4f1c-450a-9b97-52f9d2ec86ae" : OperationConfig("/send/v1/partners/{partnerId}/mappings/{mappingId}/accounts/{accountId}/additional-data", "create", [], []),
		
		"be40f5e2-e414-4072-8995-ef5bcc0a8ce0" : OperationConfig("/send/v1/partners/{partnerId}/mappings/{mappingId}/accounts", "create", [], []),
		
		"fda114aa-2f43-4ad5-8999-2cc2cf4bc603" : OperationConfig("/send/v1/partners/{partnerId}/mappings", "create", [], []),
		
		"866ccc9b-751d-4fec-b17b-31cc301d0fd9" : OperationConfig("/send/v1/partners/{partnerId}/mappings/{mappingId}/accounts/{accountId}/additional-data/{additionalDataId}", "delete", [], []),
		
		"48ff9f83-b610-40db-bde0-5b51db7fdbb4" : OperationConfig("/send/v1/partners/{partnerId}/mappings/{mappingId}", "delete", [], []),
		
		"18667c69-02ef-478c-b229-c49e8e708182" : OperationConfig("/send/v1/partners/{partnerId}/mappings/{mappingId}/accounts/{accountId}", "delete", [], []),
		
		"9256254d-208d-4599-94b2-4c2f6ec0dc80" : OperationConfig("/send/v1/partners/{partnerId}/mappings/{mappingId}/accounts", "query", [], []),
		
		"da639753-0f62-426a-8705-1209fe357eba" : OperationConfig("/send/v1/partners/{partnerId}/mappings/{mappingId}/accounts/{accountId}/additional-data", "query", [], []),
		
		"fc88da3f-2284-44a3-a427-47356fc310b7" : OperationConfig("/send/v1/partners/{partnerId}/mappings/{mappingId}/accounts/{accountId}/additional-data/{additionalDataId}", "read", [], []),
		
		"dbd5ec12-f43d-4b1e-88c1-d4e30a69be0c" : OperationConfig("/send/v1/partners/{partnerId}/mappings/{mappingId}/accounts/{accountId}", "read", [], []),
		
		"41e2fed3-82b3-4f01-ab5f-d46204852208" : OperationConfig("/send/v1/partners/{partnerId}/mappings/{mappingId}", "read", [], []),
		
		"b10a7e1a-5eb5-4757-ac79-44fbfbeb7c51" : OperationConfig("/send/v1/partners/{partnerId}/mappings", "query", [], ["ref","customer_identifier"]),
		
		"9ea6312a-f56b-4fef-930a-8bef22d7c3dd" : OperationConfig("/send/v1/partners/{partnerId}/mappings/search", "create", [], []),
		
		"b2b58b4c-f586-4b29-ab4e-903e8771a3b8" : OperationConfig("/send/v1/partners/{partnerId}/mappings/{mappingId}/accounts/{accountId}/additional-data/{additionalDataId}", "update", [], []),
		
		"3951d878-1e0c-4f60-b0e0-3ea046d7e2ce" : OperationConfig("/send/v1/partners/{partnerId}/mappings/{mappingId}", "update", [], []),
		
		"f30f54ec-de44-440a-bdc0-021002d63798" : OperationConfig("/send/v1/partners/{partnerId}/mappings/{mappingId}/accounts/{accountId}", "update", [], []),
		
	}

	def getOperationConfig(self,operationUUID):
		if operationUUID not in self.__config:
			raise Exception("Invalid operationUUID: "+operationUUID)

		return self.__config[operationUUID]

	def getOperationMetadata(self):
		return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())


	@classmethod
	def addAdditonalData(cls,mapObj):
		"""
		Creates object of type Mapping

		@param Dict mapObj, containing the required parameters to create a new object
		@return Mapping of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("02eef2e3-4f1c-450a-9b97-52f9d2ec86ae", Mapping(mapObj))






	@classmethod
	def addMappingAccount(cls,mapObj):
		"""
		Creates object of type Mapping

		@param Dict mapObj, containing the required parameters to create a new object
		@return Mapping of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("be40f5e2-e414-4072-8995-ef5bcc0a8ce0", Mapping(mapObj))






	@classmethod
	def createMapping(cls,mapObj):
		"""
		Creates object of type Mapping

		@param Dict mapObj, containing the required parameters to create a new object
		@return Mapping of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("fda114aa-2f43-4ad5-8999-2cc2cf4bc603", Mapping(mapObj))









	@classmethod
	def deleteAdditionalDataById(cls,id,map=None):
		"""
		Delete object of type Mapping by id

		@param str id
		@return Mapping of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""

		mapObj =  RequestMap()
		if id:
			mapObj.set("id", id)

		if map:
			if (isinstance(map,RequestMap)):
				mapObj.setAll(map.getObject())
			else:
				mapObj.setAll(map)

		return BaseObject.execute("866ccc9b-751d-4fec-b17b-31cc301d0fd9", Mapping(mapObj))

	def deleteAdditionalData(self):
		"""
		Delete object of type Mapping

		@return Mapping of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("866ccc9b-751d-4fec-b17b-31cc301d0fd9", self)






	@classmethod
	def deleteMappingById(cls,id,map=None):
		"""
		Delete object of type Mapping by id

		@param str id
		@return Mapping of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""

		mapObj =  RequestMap()
		if id:
			mapObj.set("id", id)

		if map:
			if (isinstance(map,RequestMap)):
				mapObj.setAll(map.getObject())
			else:
				mapObj.setAll(map)

		return BaseObject.execute("48ff9f83-b610-40db-bde0-5b51db7fdbb4", Mapping(mapObj))

	def deleteMapping(self):
		"""
		Delete object of type Mapping

		@return Mapping of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("48ff9f83-b610-40db-bde0-5b51db7fdbb4", self)






	@classmethod
	def deleteMappingAccountById(cls,id,map=None):
		"""
		Delete object of type Mapping by id

		@param str id
		@return Mapping of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""

		mapObj =  RequestMap()
		if id:
			mapObj.set("id", id)

		if map:
			if (isinstance(map,RequestMap)):
				mapObj.setAll(map.getObject())
			else:
				mapObj.setAll(map)

		return BaseObject.execute("18667c69-02ef-478c-b229-c49e8e708182", Mapping(mapObj))

	def deleteMappingAccount(self):
		"""
		Delete object of type Mapping

		@return Mapping of the response of the deleted instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("18667c69-02ef-478c-b229-c49e8e708182", self)








	@classmethod
	def listAllAccounts(cls,criteria):
		"""
		Query objects of type Mapping by id and optional criteria
		@param type criteria
		@return Mapping object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("9256254d-208d-4599-94b2-4c2f6ec0dc80", Mapping(criteria))






	@classmethod
	def listAllAdditionalData(cls,criteria):
		"""
		Query objects of type Mapping by id and optional criteria
		@param type criteria
		@return Mapping object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("da639753-0f62-426a-8705-1209fe357eba", Mapping(criteria))





	@classmethod
	def readByAdditionalDataId(cls,id,criteria=None):
		"""
		Returns objects of type Mapping by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of Mapping
		@raise ApiException: raised an exception from the response status
		"""
		mapObj =  RequestMap()
		if id:
			mapObj.set("id", id)

		if criteria:
			if (isinstance(criteria,RequestMap)):
				mapObj.setAll(criteria.getObject())
			else:
				mapObj.setAll(criteria)

		return BaseObject.execute("fc88da3f-2284-44a3-a427-47356fc310b7", Mapping(mapObj))






	@classmethod
	def readByMappingAccountId(cls,id,criteria=None):
		"""
		Returns objects of type Mapping by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of Mapping
		@raise ApiException: raised an exception from the response status
		"""
		mapObj =  RequestMap()
		if id:
			mapObj.set("id", id)

		if criteria:
			if (isinstance(criteria,RequestMap)):
				mapObj.setAll(criteria.getObject())
			else:
				mapObj.setAll(criteria)

		return BaseObject.execute("dbd5ec12-f43d-4b1e-88c1-d4e30a69be0c", Mapping(mapObj))






	@classmethod
	def readByMappingId(cls,id,criteria=None):
		"""
		Returns objects of type Mapping by id and optional criteria
		@param str id
		@param dict criteria
		@return instance of Mapping
		@raise ApiException: raised an exception from the response status
		"""
		mapObj =  RequestMap()
		if id:
			mapObj.set("id", id)

		if criteria:
			if (isinstance(criteria,RequestMap)):
				mapObj.setAll(criteria.getObject())
			else:
				mapObj.setAll(criteria)

		return BaseObject.execute("41e2fed3-82b3-4f01-ab5f-d46204852208", Mapping(mapObj))







	@classmethod
	def listByReferenceOrCustomerIdentifier(cls,criteria):
		"""
		Query objects of type Mapping by id and optional criteria
		@param type criteria
		@return Mapping object representing the response.
		@raise ApiException: raised an exception from the response status
		"""

		return BaseObject.execute("b10a7e1a-5eb5-4757-ac79-44fbfbeb7c51", Mapping(criteria))

	@classmethod
	def searchMapping(cls,mapObj):
		"""
		Creates object of type Mapping

		@param Dict mapObj, containing the required parameters to create a new object
		@return Mapping of the response of created instance.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("9ea6312a-f56b-4fef-930a-8bef22d7c3dd", Mapping(mapObj))







	def updateAdditonalData(self):
		"""
		Updates an object of type Mapping

		@return Mapping object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("b2b58b4c-f586-4b29-ab4e-903e8771a3b8", self)






	def updateMapping(self):
		"""
		Updates an object of type Mapping

		@return Mapping object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("3951d878-1e0c-4f60-b0e0-3ea046d7e2ce", self)






	def updateMappingAccount(self):
		"""
		Updates an object of type Mapping

		@return Mapping object representing the response.
		@raise ApiException: raised an exception from the response status
		"""
		return BaseObject.execute("f30f54ec-de44-440a-bdc0-021002d63798", self)






