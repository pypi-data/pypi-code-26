# coding: utf-8

"""
    Assetic.bulk_export.py
    Tools to facilitate bulk export of data from assetic and
    syncing exported data to a local sql server database
    
    Checks if there are files to download from from Export All task
    Downloads the file and saves locally to then process
    Uses file system to record pending & processed export jobs
    Data is written to a temp db table and then the 'merge' SQL is used
    to update/insert records in the permanant table

    Alternatively save to file server as csv. This option uses the documents api
    to record exports in progress, so no need for a db table to manage export

    If number of records is less than 10,000 then export is immediate
"""
#from __future__ import absolute_import

import pyodbc
import sys
import datetime
import dateutil.parser
import string  #(use string.lower instead of str.lower for py2.7)
import functools
import os
import io
import shutil
from contextlib import contextmanager
from pprint import pformat
import six
import time
import codecs
import csv

from ..api_client import ApiClient
from ..rest import ApiException
from ..api import DocumentApi
from ..api import SearchApi
from ..api import BackgroundWorkerApi
from . import BulkProcesses
from ..models.assetic3_integration_representations_document_representation\
    import Assetic3IntegrationRepresentationsDocumentRepresentation
class SyncToLocalProcesses(object):
    """
    Class to manage processes that sync Assetic search data to a local DB
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client
        
        self.logger = api_client.configuration.packagelogger

        ##create instance of search api
        self.searchapi = SearchApi(self.api_client)
        ##create instance of document API
        self.docapi = DocumentApi(self.api_client)
        
        self._workingdir = os.getcwd()
        
    @property
    def workingdir(self):
        """
        Gets current working directory.
        """
        if self._workingdir == None:
            self._workingdir = os.getcwd()
        return self._workingdir

    @workingdir.setter
    def workingdir(self, value):
        """
        Sets a new current working directory.
        :param value: the working directory to use
        """
        if os.path.isdir(value) == True:
            self._workingdir = value
        else:
            raise ApiException(
                status=1,
                reason="Invalid workingdir set: `{0}`"
                .format(value)
            )

    def dbsync_initiate(self,dbserver,dbname,profiles,incremental=True,username=None,password=None,driver="ODBC Driver 13 for SQL Server"):
        """
        For each profile in profiles array create new exports and log export
        task ID in db for later 'finalisation' step
        With this method there are no files used to manage process
        By default it is intended that it will only gets records modified
        since last sync date, however this is not yet implemented. All records
        are therefore downloaded.  The parameter incremental will at a future
        point be utilised to control this behaviour
        :param dbserver: database instance (SQL Server)
        :param dbname: database name.  Assumes trusted connection
        :param profiles: an array of SearchProfileRespresentation instances
        :param incremental: True/False.
        Apply incremental export if True (default).  
        Default=True, however not implemented yet.
        :param username: database username. Optional.
        If None then trusted connection.  Password required if not None
        :param password: database password.  Optional, used with username
        :param driver: default="ODBC Driver 13 for SQL Server". Could also use
        "SQL Server" but this is an old driver and must use trusted connection
        :returns: no errors = 0, error=>0. 
        """
        self.logger.info("Starting dbsync_initiate")
        dbtools = DB_Tools(dbserver,dbname,username,password,driver)
        ##loop through the list of profiles and create exports
        errorcode = 0
        for profile in profiles:
            errorcode = self.create_export_task_db(profile,dbtools,incremental)
            if errorcode != 0:
                self.logger.info("Exiting dbsync_initiate with error")
                return errorcode
        self.logger.info("Finished dbsync_initiate")
        return errorcode
                
    def dbsync_finalise(self,dbserver,dbname,username=None,password=None,driver="ODBC Driver 13 for SQL Server"):
        """
        Finalise sync by checking for documents created by background worker
        process and downloading those files to an array (not to disk)
        The downloaded data is synced and the task flagged as complete
        :param dbserver: database instance (SQL Server)
        :param dbname: database name.
        :param username: database username. Optional.
        If None then trusted connection.  Password required if not None
        :param password: database password.  Optional, used with username
        :param driver: default="ODBC Driver 13 for SQL Server". Could also use
        "SQL Server" but this is an old driver and must use trusted connection
        :returns: no errors = 0, error=>0. 
        """
        self.logger.info("Starting dbsync_finalise")
        returncode = 0
        dbtools = DB_Tools(dbserver,dbname,username,password,driver)
        ##get list of in-progress tasks from db
        returncode,tasks = self.get_active_task_doclist_db(dbtools)
        if returncode > 0:
            self.logger.info("Exiting dbsync_finalise with error")
            return returncode
        if tasks == None:
            self.logger.info("No active task exports ready for download")
        else:
            ##Prepare SQL for updating manager table on a per profile basis
            sql = """update assetic_sync_manager set documentid = ?,
                    status = ?, date_last_modified=getdate()
                    where oid=CONVERT(uniqueidentifier,?)"""
            ##get generated document ID for task
            for task in tasks:
                ##get document data
                docid = task.documentid
                docdata = self.get_document(docid)
                if docdata == None:
                    msg = "[{0}] export file contains no data."\
                          "Please check search profile.  Task ID:{1}".format(
                        task.profilename)
                    self.logger.warning(msg)
                else:
                    profile = task.profile
                    self.logger.info("Processing document {0} for profile {1} "
                        "for task {2}".format(docid,profile.profilename,
                        task.taskguid))
                    ##get column mappings and data types for search profile
                    datadef = self.get_search_columns(profile.profileguid)
                    ##build target table (method first checks if existing)
                    returncode = self.build_table_from_search(dbtools,
                                datadef,profile,False)
                    if returncode != 0:
                        self.logger.info("Exiting dbsync_finalise with error")
                        return returncode
                    returncode = self.csv_string_to_db(docdata,profile,dbtools,
                                datadef)

                    ##update assetic_sync_manager
                    if returncode == 0:
                        status = "Processed"
                    else:
                        status = "Error"
                    vals = [docid,status,task.oid]
                    returncode = dbtools.execute_single(sql,vals)
                    if returncode != 0:
                        self.logger.error("Error updating"
                                    " assetic_sync_manager_table")
        self.logger.info("Finished dbsync_finalise")
        return returncode
        
    def initiate_export_task_to_file(self,profile,hidecontroldoc=False,doc_group=None, doc_category=None,doc_subcategory=None):
        """
        Given a search profile initiate a bulk export job and record details
        in a document link in Assetic.
        :param profile: The search profile guid
        :Param hidecontroldoc: once export file created, set log status as deleted
        :Param doc_group: optional document group id (int)
        :Param doc_group: optional document category id (int)
        :Param doc_group: optional document sub category id (int)
        Returned: return code 0=success,1=error
        """
        #first see how may rows are returned, if less than 10,000
        #can use the search get rather than batch - quicker as no
        #background worker process
        totalrecords=self.get_total_count_for_search(profile.profileguid)

        if totalrecords < 0:
            return 1
        
        if 0 < totalrecords <= 10000: 
            #use standard search api to get data
            csvstring = self.run_search_for_pages(profile.profileguid)
            if csvstring == None:
                return 1
            fullfilename = os.path.join(self.workingdir,
                                        profile.profilename + ".csv")
            chk = self.csvstring_to_file(csvstring,fullfilename)
            if chk != 0:
                return chk

            ##record as processed
            self.create_immediate_export_as_doclink(profile.profilename,\
                    profile.profileguid,hidecontroldoc,doc_group,doc_category,\
                    doc_subcategory)
            msg = "Immediate creation of csv file {0}".format(fullfilename)
            self.logger.info(msg)
        else:
            ##else create background worker export task
            taskid = self.create_export_task(profile.profileguid)
            
            if taskid != None:
                chk = self.create_export_task_as_doclink(profile.profilename,
                        profile.profileguid,
                        taskid,doc_group,doc_category,doc_subcategory)
                if chk == 0:
                    msg = "Background workder export task created for {0}".format(
                        profile.profilename)
                    self.logger.info(msg)                    
            else:
                return 1                
        return 0

    def finalise_export_task_to_file(self,hidecontroldoc):
        """
        Given a search profile initiate a bulk export job and record details
        in a document link in Assetic.
        :param hidecontroldoc: Delete the document record used to manage the export
        Returned: return code 0=success,1=error
        """
        ##get outstanding exports awaiting download
        docs = self.get_active_export_tasks_from_doclink()
        if len(docs) == 0:
            #none to process
            self.logger.info("No background export tasks to process")
            return 0
        
        ##loop through the documents and parse the task id from string
        for doc in docs:
            x = doc["ExternalId"]
            try:
                taskid = x[x.find("TaskId=")+8:x.find(";")]
            except Exception as ex:
                "Unable to parse Task ID from external ID {0} for document"\
                " {1}  Error is : {2}".format(x,doc["Id"],ex)
                self.logger.error(msg)
            else:
                ##get the document ID for the export file
                status,exportdocid = self.get_export_docid(taskid)
                if exportdocid == None:
                    msg = "Status of export is {0} for task {1} profile {2}"\
                          "".format(status, taskid,doc["label"])
                    self.logger.info()
                #get the document as a string
                csvstring = self.get_document(exportdocid)
                if csvstring != None:
                    n=doc["Label"]
                    name = n[len("Export Backup Process Task for "):len(n)]
                    fullfilename = os.path.join(self.workingdir,name + ".csv")
                    ##save document to file
                    chk = self.csvstring_to_file(csvstring,fullfilename)
                    if chk == 0:
                        ##flag export to file as complete
                        chk = self.update_completed_export_task_as_doclink(doc,
                                        exportdocid,hidecontroldoc)
                        if chk == 0:
                            msg = "Successfully downloaded csv {0} for "\
                                  "task {0} profile {2}".format(
                                    fullfilename,taskid,name)
                            self.logger.info(msg)
                        
    def create_export_task_db(self,profile,dbtools,incremental):
        """
        Given a search profile initiate a bulk export job for dbsync
        :param profile: The search profile guid
        :param dbtools: instance of DB_Tools
        :param incremental: incremental update supported True/False
        Returned: return code 0=success,1=error
        """
        #verify sync table is up to date
        returncode = self.upgrade_assetic_sync_manager_table(dbtools)
        if returncode != 0:
            return returncode
            
        #will first see how many rows in export, apply a filter if incremntal       
        qfilter = None
        if incremental == True:
            ##uses a date filter.  Get server time rather than local time
            ##TODO get last datetime successfully executed from documents api
            lastdate = None
            ##TODO get current datetime from api, or use a timeoffset config?
            currentdate = None
            if lastdate != None and currentdate != None:
                lastdate = results[0]
                currentdate = datetime.datetime.now().isoformat()
                qfilter = "{0} >={1},{0}<={2}".format(
                    profile.lastdatefield,lastdate,currentdate)
                
        #see how may rows are returned, if less than 10,000
        #can use the search get rather than batch - quicker as no
        #background worker process
        totalrecords=self.get_total_count_for_search(profile.profileguid
                        ,qfilter)

        ##Prepare SQL to be used to write task details to database
        sql = """insert into assetic_sync_manager
            (oid,taskid, profileid,profilename,tablename,keyfield,logtable,
            useinternalnames,replacespaces,spacedelimiter,status,
            date_initiated,date_last_modified)
            values (NEWID(),?,?,?,?,?,?,?,?,?,?,getdate(),getdate())"""

        #Now export immediately or initiate background worker export
        if 0 < totalrecords <= 10000: 
            #use standard search api to get data
            csvstring = self.run_search_for_pages(profile.profileguid)
            if csvstring == None:
                return 0
            metadata = self.get_search_columns(profile.profileguid)
            returncode = self.csv_string_to_db(csvstring,profile,dbtools,metadata)
            if returncode != 0:
                return returncode            
            ##update as processed
            record = "not required", profile.profileguid,profile.profilename,\
                     profile.tablename,profile.keyfield,profile.logtable,\
                     profile.useinternalnames,profile.replacespaces,\
                     profile.spacedelimiter,"Complete"
            returncode = dbtools.execute_single(sql,record)
        else:
            ##else create export task
            taskid = self.create_export_task(profile.profileguid)
            
            if taskid != None:
                record = taskid, profile.profileguid,profile.profilename,\
                         profile.tablename,profile.keyfield,profile.logtable,\
                         profile.useinternalnames,profile.replacespaces,\
                         profile.spacedelimiter,"In Progress"
                returncode = dbtools.execute_single(sql,record)
            else:
                returncode = 1
                
        return returncode
    
    def create_export_task(self,profileguid):
        """
        Given a search profile initiate a bulk export job
        :param profileguid: The search profile guid
        Returned: taskid or None if error
        """
        try:
            taskid = self.searchapi.search_post_export_profile(profileguid)
        except ApiException as e:
            self.logger.error('Status {0}, Reason: {1} {2}'.format(
                e.status,e.reason,e.body))
            return None
        return taskid

    def get_export_docid(self,exporttaskguid):
        """
        Given a background worker export job GUID check status
        Param1: the guid of the export task
        Returned: A tuple (2 fields)
        1. The status or None if profile not found
        2. docid if ready for download, otherwise None
        """
        bwapi = BackgroundWorkerApi(self.api_client)
        try:
            response = bwapi.background_worker_get(exporttaskguid)
        except ApiException as e:
            msg="Create background worker task for {0}".format(exporttaskguid)
            self.logger.error('{0}: Status {0}, Reason: {1}'.format(
                msg,e.status,e.reason))
            return None,None            
        status = response.get("Status")
        docid = None

        if status == "Completed":
            docid = response.get("DocumentId")
        return status,docid

    def csvstring_to_file(self,csvstring,fullfilename):
        """
        Given an array of strings, write each string to file as a new row
        :param datarows: String array
        :param fullfilename: The file to save including directory path
        Returned: 0 if success, else error number
        """
        try:
            if six.PY2:
                with open(fullfilename, 'w') as out_file:
                    out_file.write(csvstring)
                self.logger.info("Created file {0}".format(fullfilename))
            else:
                with open(fullfilename, 'w', newline = "",
                          encoding="UTF-8") as out_file:
                    out_file.write(csvstring)
                self.logger.info("Created file {0}".format(fullfilename))                
        except Exception as e:
            self.logger.error("Error creating file {0}: {1}".format(
            fullfilename,e))
            return 1
        return 0

    def get_document(self,docid):
        """
        Gets document from Assetic, but doesn't write to disk
        Param docid: document ID to retrieve
        Returned: the data component of the document only. File not saved
        """
        #client = assetic.ApiClient(self.conf.host,"Authorization",self.auth)
        docapi = DocumentApi(self.api_client)
        try:
            data = docapi.document_get_document_file(docid)
        except ApiException as e:
            self.logger.error('Status {0}, Reason: {1} {2}'.format(
                e.status,e.reason,e.body))
            returncode = int(e.status)
            return None        
        ##ensure encoding is ok
        datadec = self.decode_bom(data)
        return datadec
    
    def decode_bom(self,data):
        """
        Remove BOM from data
        Param data: Data to decode
        Returned: input data decoded to UTF-8
        """
        if sys.version_info < (3,0):
            if data.startswith(codecs.BOM_UTF8):
                self.logger.debug("removing BOM_UTF8 codec from document start")
                data = data.strip(codecs.BOM_UTF8)
            return data            
        else:
            #v3.  Remove BOM if present
            if data.startswith(codecs.BOM_UTF8.decode("utf8")):
                self.logger.debug("removing BOM_UTF8 codec from document start")
                data = data.strip(codecs.BOM_UTF8.decode("utf8"))
            return data
    
    def get_active_task_doclist_db(self,dbtools):
        """
        get active tasks frm assetic_sync_manager table using filter
        status='inprogress'
        Param dbtools: dbtools object        
        Returned: a list of active tasks and document id
        """

        ##have added a new field to assetic_sync_manager Feb2017
        ##check to see it is there and create if not
        returncode,existingcolumns = dbtools.get_columns_for_table(
                                        "assetic_sync_manager")
        if returncode !=0:
            return returncode,None
        if "replacespaces" not in existingcolumns:
            ##need to create
            sql = "alter table assetic_sync_manger add replacespaces bit"
            returncode = dbtools.execute_single(sql)
        if returncode !=0:
            self.logger.error('Table assetic_sync_manger missing field "replacespaces"')
            return returncode,None
        ##Add spacedelimiter field to allow an underscore or other delimiter
        ##to replace the space.  Must also set replacespaces = True to use
        if "spacedelimiter" not in existingcolumns:
            ##need to create
            sql = "alter table assetic_sync_manager add "\
                  "spacedelimiter [nvarchar](50)"
            returncode = dbtools.execute_single(sql)
        if returncode !=0:
            self.logger.error('Table assetic_sync_manger missing field '\
                              '"spacedelimiter"')
            return returncode,None        
        activetasks = []

        #get all tasks
        sql = """select convert(nvarchar(36),oid),taskid, profileid,profilename,
            tablename,keyfield,logtable,useinternalnames,replacespaces,
            spacedelimiter from assetic_sync_manager where status='In Progress'
            order by [date_initiated] asc"""
        returncode,tasks = dbtools.execute_select(sql)
        if returncode != 0:
            return returncode,None
        
        ##format to task representation
        for task in tasks:
            ##first check if export document ready
            taskstatus,docid = self.get_export_docid(task[1])
            if docid != None:
                tr = ExportTaskRepresentation()
                pr = SearchProfileRepresentation()
                tr.oid = task[0]
                tr.taskguid = task[1]
                tr.documentid = docid
                pr.profileguid = task[2]
                pr.profilename = task[3]
                pr.tablename = task[4]
                pr.keyfield = task[5]
                pr.logtable = task[6]
                pr.useinternalnames = task[7]
                pr.replacespaces = task[8]
                pr.spacedelimiter = task[9]
                tr.profile = pr
                activetasks.append(tr)
            else:
                msg = "Export file for profile [{0}] is not ready for download"\
                      ".  The status of the background worker process is [{1}]"\
                      ".  Please retry later when the file is ready".format(
                          task[3],taskstatus)
                self.logger.info(msg)
        return returncode,activetasks
        
    def csv_string_to_db(self,csvstring,profile,dbtools,metadata):
        """
        For a given single column array sync data to db.
        Assums data in column is comma delimited, but no need to split
        Assumes a header row
        param csvstring: a string of csv data (multiple lines)
        param profile: instance of SearchProfileRepresentation
        param dbtools: instance of dbtools
        param metadata: instance of search profile column metadata
        Returned: 0 if success, else 1
        """

        dbtable = profile.tablename
        keyfield = profile.keyfield
        logtable = profile.logtable
                    
        #get list of columns
        bIsHeader = True
        allrows = []
        saved_row = []
        csvarray = csvstring.splitlines()

        reader = csv.reader(csvarray)
        for row in reader:
            if bIsHeader == True:
                bIsHeader = False
                if profile.useinternalnames == True:
                    columnmap = metadata.get("ResourceList")
                    columns=[]
                    #switch the column headers with internal names
                    for header in row:
                        #find header in metadata and get internal name
                        for columnset in columnmap:
                            if columnset.get('Label') == header:
                                columns.append(columnset.get('Name'))
                                break
                    self.logger.debug("Using internal field names for column names")
                elif profile.replacespaces == True:
                    ##replace spaces in field name with delimiter
                    if profile.spacedelimiter == None:
                        ##remove whitespaces from label
                        profile.spacedelimiter = ""
                    columns = []
                    for header in row:
                        columns.append(header.replace(" ",profile.spacedelimiter))
                    self.logger.debug("Using label names without whitespaces from\
                        column names")
                else:
                    columns = row
                #self.logger.debug("CSV file columns: {0}, count {1}".format(columns,len(columns)))
            else:
                #cater for carriage returns in a column
                if len(saved_row):
                    row_tail = saved_row.pop()  #gets last item in the list
                    row[0] = row_tail + '\r' +row[0]  # reconstitute field broken by newline
                    row = saved_row + row       # and reassemble the row (possibly only partially)
                if len(row) >= len(columns):
                    decodedrow = row
                    if sys.version_info < (3,0):
                        #need to encode as unicode for python 2 otherwise issues
                        #with special characters
                        try:
                            decodedrow = [field.decode("utf8") for field in row]
                        except:
                            decodedrow = row
                    allrows.append(decodedrow)
                    saved_row = []
                else:
                    saved_row = row
        returncode = dbtools.data_sync_to_db(allrows,columns,dbtable,keyfield,logtable)
        return returncode

    def get_total_count_for_search(self,searchguid,searchfilter=None):
        """
        Get the total results and return
        Param searchguid: the search profile guid
        Param searchfilter: optional filter
        Returned: number of records
        """
        kw = {'request_params_id':searchguid,
            'request_params_page':1,
            'request_params_page_size':1}
        if searchfilter != None:
            kw['request_params_filters'] = searchfilter

        try:
            sg = self.searchapi.search_get(**kw)
        except ApiException as e:
            self.logger.error('Status {0}, Reason: {1}'.format(
                e.status,e.reason))
            returncode = int(e.status)
            return -1
        totalrecords=int(sg['TotalResults'])
        return totalrecords
    
    def run_search_for_pages(self,searchguid,searchfilter=None):
        """
        Use to get data across multiple pages
        Limited to 10,000 records.
        Formats data as comma delimited, but no need to split
        Includes a header row
        Param searchguid: the search profile guid
        Param searchfilter: optional filter
        Returned: search data as csv or None
        """

        ##set parameters for search
        numpagesize = 500  #max number of pagess
        startpage = 1
        pagelimit = 20
        kw = {'request_params_id':searchguid,
            'request_params_page':startpage,
            'request_params_page_size':numpagesize}
        
        if searchfilter != None:
            kw['request_params_filters'] = searchfilter
            
        ##Get first page of results
        try:
            sg = self.searchapi.search_get(**kw)
        except ApiException as e:
            msg = "Run search for pages"
            self.logger.error('{0}: Status {1}, Reason: {2}'.format(
                msg,e.status,e.reason))
            returncode = int(e.status)
            return None
        morepages = True
        totalresults=int(sg.get('TotalResults'))
        if totalresults == 0:
            morepages = False
            return None
        numpages = int(sg.get('TotalPages')) - (startpage-1)
        self.logger.debug('Total Pages: {0}'.format(numpages))
        if pagelimit > int(numpages):
            ##page limit defines the number of pages we'll process
            pagelimit = numpages
        if numpages <= pagelimit:
            morepages = False
        endpage = (startpage-1) + pagelimit
        self.logger.debug("Start page: {0}, End page: {1}, pages left: {2}".format(startpage, endpage,numpages))
        
        ##get actual data from nested output
        resourcelist = sg.get('ResourceList')
        resource = resourcelist[0]
        data = resource.get('Data')
        ##Copy as alldata becuase we will be appending to this
        alldata = data
        
        ##Get a list of columns
        columns = map( lambda x: x.keys(), data )
        if six.PY2:
            columns = reduce( lambda x,y: x+y, columns )
        else:
            columns = functools.reduce( lambda x,y: x|y, columns )

        self.logger.debug("First page, columns are: {0}".format(columns))
        ##Write list of columns to the 'all' list as this may grow
        allcolumns = columns

        ##Now loop through remaining pages
        if numpages > 1:
            for pagenum in range(startpage + 1,endpage +1):
                ##set page number to get
                kw['request_params_page']=pagenum
                self.logger.debug('Page: {0}'.format(kw['request_params_page']))

                ##Now get results for this page
                try:
                    sg = self.searchapi.search_get(**kw)
                except ApiException as e:
                    msg = "Run search for pages - additional pages"
                    self.logger.error('{0}: Status {1}, Reason: {2}'.format(
                        msg,e.status,e.reason))
                    returncode = int(e.status)
                    return None
                
                totalresults=int(sg.get('TotalResults'))
                if totalresults == 0:
                    morepages = False
                    break
                ##get actual data from nested output
                resourcelist = sg.get('ResourceList')
                resource = resourcelist[0]
                data = resource.get('Data')

                #Get column list for this page - there may be new columns
                columns = map( lambda x: x.keys(), data )
                if six.PY2:
                    columns = reduce( lambda x,y: x+y, columns )
                    ##Add new column list to "allcolumns", will get unique list later
                    allcolumns = allcolumns + columns
                    #append new data to "alldata"
                    alldata = alldata + data
                else:
                    columns = functools.reduce( lambda x,y: x|y, columns )
                    ##merge column list sets
                    allcolumns = allcolumns | columns
                    #append new data to "alldata"
                    alldata.extend(data)

                #debug comment
                self.logger.debug("in page loop, columns are: {0}".format(
                    columns))

                if startpage + pagenum > 20:
                    ##catchall escape
                    morepages = False
                    break
        if six.PY2:
            ##column list not unique, so get unique list using set
            columns = list(set(allcolumns))
        elif sys.version_info.minor==4:
            ##python 3.4, csv writer error if pass in set, so make it a list
            columns = list(allcolumns)
        else:
            ##for PY3 the list is already unique, able to build unique using merge
            columns = allcolumns

        #set csv writer output to string
        if six.PY2:
            output = io.BytesIO()
            writer = csv.writer(output)
        else:
            output = io.StringIO()
            writer = csv.writer(output,quoting=csv.QUOTE_NONNUMERIC)

        ##write header columns
        writer.writerow(columns)
        #loop through data and write to csv  
        for i_r in alldata:
            #map data to column list by key to avoid issues with column order
            if six.PY2:
                writer.writerow(map(lambda x: i_r.get( x, "" ).encode('utf-8')
                                    ,columns))
            else:
                writer.writerow(list(
                    map(lambda x: i_r.get( x, "" ),columns)))
                
        csvdata = output.getvalue()
        output.close()
        return csvdata

    def build_assetic_sync_manager_table(self,dbserver,dbname,username=None,password=None,driver="ODBC Driver 13 for SQL Server"):
        """
        Builds the db table used to manager the sync process
        Assumes trusted connection to database
        param dbserver: the name of the SQL Server instance
        param dbname: the name of the the SQL Server database
        Returned: Success (Boolean) - True if no error 
        """
        dbtools = DB_Tools(dbserver,dbname,username,password,driver)
        sqlchk = "select object_id('assetic_sync_manager') as objectid"
        sqlcreate = """CREATE TABLE assetic_sync_manager(
            [oid] [uniqueidentifier],            
            [taskid] [nvarchar](50),
            [profileid] [nvarchar](50),
            [profilename] [nvarchar](100),
            [tablename] [nvarchar](50),
            [keyfield] [nvarchar](50),
            [logtable] [nvarchar](50),
            [documentid] [nvarchar](50),
            [useinternalnames] bit,
            [replacespaces] bit,
            [spacedelimiter] [nvarchar](50),
            [date_initiated] datetime,
            [date_last_modified] datetime,
            [status] [nvarchar](50))"""
        returncode, result = dbtools.execute_select(sqlchk)
        if returncode == 0 and result[0][0] == None: 
            returncode = dbtools.execute_single(sqlcreate)
        return returncode

    def upgrade_assetic_sync_manager_table(self,dbtools):
        """
        Builds the db table used to manager the sync process
        param dbtools: initiated instance of dbtools
        Returned: Success=0, nonzero = error 
        """
        ##have added a new field to assetic_sync_manager Feb2017
        ##check to see it is there and create if not
        returncode,existingcolumns = dbtools.get_columns_for_table("assetic_sync_manager")
        if returncode !=0:
            return returncode
        if "replacespaces" not in existingcolumns:
            ##need to create
            sql = "alter table assetic_sync_manager add replacespaces bit"
            returncode = dbtools.execute_single(sql)
        if returncode !=0:
            self.logger.error('Table assetic_sync_manger missing field "replacespaces"')
            return returncode
        ##Add spacedelimiter field to allow an underscore or other delimiter
        ##to replace the space.  Must also set replacespaces = True to use
        if "spacedelimiter" not in existingcolumns:
            ##need to create
            sql = "alter table assetic_sync_manager add "\
                  "spacedelimiter [nvarchar](50)"
            returncode = dbtools.execute_single(sql)
        if returncode !=0:
            self.logger.error('Table assetic_sync_manger missing field '\
                              '"spacedelimiter"')
            return returncode
        ##all good
        return 0
        
    def build_table_from_search(self,dbtools,metadata,profile,printonly=False):
        """
        Builds the sync target db table based on search fields
        Optionally print creation SQL instead of creating
        Can use standalone.  Is also used when sync is peformed
        :param dbtools: instance of dbtools
        :param metadata: instance of search profile metadata.
        if None then profile ID will be used to get the metadata from api
        Assetic3IntegrationRepresentationsSearchMetadataRepresentationList
        :param profile: instance of search profile definition
        :param printonly: If true the column name is based on the
        user visible field label in export, else internal field name is used
        default is False
        If true then table is not created but SQL for table create is.
        Allows manual edit of datatypes and manual creation of table.
        Returned: 0=Success, 1=error
        """
        if metadata == None:
            metadata = self.get_search_columns(profile.profileguid)
        if metadata == None:
            return 1
        sqlchk = "select object_id('{0}') as objectid".format(profile.tablename)
        resourcelist = metadata.get("ResourceList")
        columnddl = []
        for columndef in resourcelist:
            #by default set column name to user friendly column header
            #in export file
            colname = "[{0}]".format(columndef.get("Label"))
            if profile.useinternalnames == True:
                #change column name to assetic internal field name for the label
                colname = "[{0}]".format(columndef.get("Name"))
            elif profile.replacespaces == True:
                ##replace spaces in field name with delimiter
                if profile.spacedelimiter == None:
                    ##remove whitespaces from label
                    profile.spacedelimiter = ""
                #replace whitespaces from Label names
                colname = colname.replace(" ",profile.spacedelimiter)
            #set datatype
            datatype = "nvarchar(500)"    #default datatype - e.g System.String
            typedef = columndef.get("Type").lower()
            if typedef.find('integer') > 0:
                datatype = 'int'
            elif typedef.find('double') > 0:
                datatype = 'float'
            elif typedef.find('decimal') > 0:
                datatype = 'float'
            elif typedef.find('datetime') > 0:
                datatype = 'datetime'
            elif typedef.find('bool') > 0:
                datatype = 'bit'
            #set NULL/NOT NULL
            allownull = "NULL"
            if colname.lower() == profile.keyfield.lower():
                allownull = "NOT NULL CONSTRAINT [{0}_PK] PRIMARY KEY "\
                            "CLUSTERED".format(profile.tablename)
                datatype = "nvarchar(100)"
            columnddl.append("{0} {1} {2}".format(colname,datatype,allownull))

        #finalise create string                 
        sqlcreate = "create table {0}({1})".format(profile.tablename,
                        ",".join(columnddl))
        #check to see if table exists
        returncode, result = dbtools.execute_select(sqlchk)
        
        if returncode == 0 and result[0][0] == None:
            if printonly == True:
                print(sqlcreate)
            else:
                #create table
                returncode = dbtools.execute_single(sqlcreate)
        elif returncode == 0 and result[0][0] != None:
            self.logger.debug("Target table [{0}] already exists".format(profile.tablename))
        return returncode
    
    def get_search_columns(self,profileid):
        """
        Use the api to get column mappings for search profile
        Param profileid: search profile guid
        Returned: array of SearchProfileColumnRepresentation or None if error or
        profile not found
        """

        try:
            response = self.searchapi.search_get_profile_metadata(profileid)
        except ApiException as e:
            self.logger.error('Status {0}, Reason: {1}'.format(
                e.status,e.reason))
            returncode = int(e.status)
            return None
        return response               

    def create_immediate_export_as_doclink(self,profilename,profileguid,hidecontroldoc=False,doc_group=None, doc_category=None,doc_subcategory=None):
        """
        Use Assetic documents to record the completed export of a profile
        For this case the export was completed in one step
        Allow document status of deleted, can still find history via API but
        not clog up searches with these documents.
        :Param profilename: name of profile
        :Param profileguid: The GUID of the search profile
        :Param hidecontroldoc: once created, set status as deleted
        :Param doc_group: optional document group id (int)
        :Param doc_group: optional document category id (int)
        :Param doc_group: optional document sub category id (int)
        :Returned: 0=success, else error
        """
        ###Document categorisation - initialise document properties object and populate
        document = Assetic3IntegrationRepresentationsDocumentRepresentation()
        docurl = "{0}/Search/AdvancedSearchProfile/SPDashboard/Default/{1}"\
                      "".format(self.config.host,profileguid)
        document.document_group = doc_group
        document.document_category = doc_category
        document.document_sub_category = doc_subcategory
        document.document_link = docurl
        document.label = "Export Backup Process Task for {0}".format(
            profilename)
        document.external_id = "Immediate export via paginated search"

        ###Perform upload
        try:
            doc = self.docapi.document_post(document)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status,e.reason,e.body))
            return 1
        ##Now optionally delete the record, it's retained with status 500
        if hidecontroldoc == True:
            try:
                doc = self.docapi.document_delete(doc["Id"])
            except ApiException as e:
                self.logger.error("Status {0}, Reason: {1} {2}".format(
                    e.status,e.reason,e.body))
                return 1
        return 0

    def create_export_task_as_doclink(self,profilename,profileguid,taskid,doc_group=None, doc_category=None,doc_subcategory=None):
        """
        Use Assetic documents to record the creation of a search profile export
        via the background worker task
        :Param profilename: The name of the search profile
        :Param profileguid: The GUID of the search profile
        :Param task: guid of background worker export task
        :Param doc_group: optional document group id (int)
        :Param doc_group: optional document category id (int)
        :Param doc_group: optional document sub category id (int)
        :Returned: 0=success, else error
        """

        ###Document categorisation - initialise document properties object and populate
        document = Assetic3IntegrationRepresentationsDocumentRepresentation()
        docurl = "{0}/Search/AdvancedSearchProfile/SPDashboard/Default/{1}"\
                      "".format(self.config.host,profileguid)
        document.document_group = doc_group
        document.document_category = doc_category
        document.document_sub_category = doc_subcategory
        document.document_link = docurl
        document.external_id = "TaskID={0};DocumentId={1}".format(
            taskid,"Not Processed")
        document.label = "Export Backup Process Task for {0}".format(
            profilename)

        ###Perform upload
        try:
            doc = self.docapi.document_post(document)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status,e.reason,e.body))
            return 1
        return 0

    def update_completed_export_task_as_doclink(self,document,exportdocid,hidecontroldoc=False):
        """
        Use Assetic documents to record the completed export of a profile
        Allow document status of deleted, can still find history via API but
        not clog up searches with these documents.
        :Param document: json Assetic3IntegrationRepresentationsDocumentRepresentation
        :Param exportdocid: The document ID of the exported document
        :Param hidecontroldoc: optionally delete if True.  Default = False
        :Returned: 0=success, else error
        """
        ##Flag export as processed by replacing "Not Processed" with export id
        if "Not Processed" in document["ExternalId"]:
            document["ExternalId"] = document["ExternalId"].replace("Not Processed",
                                        exportdocid)
        else:
            ##just in case....
            document["ExternalId"] = "DocumentId={0}".format(exportdocid)
        ###Perform upload
        try:
            doc = self.docapi.document_put(document["Id"],document)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status,e.reason,e.body))
            return 1
        ##Now optionally delete the record, it's retained with status 500
        if hidecontroldoc == True:
            try:
                doc = self.docapi.document_delete(document["Id"])
            except ApiException as e:
                self.logger.error("Status {0}, Reason: {1} {2}".format(
                    e.status,e.reason,e.body))
                return 1
        return 0

    def get_active_export_tasks_from_doclink(self):
        """
        Use Assetic documents to get a list of active background worker exports
        :Returned: A list of document representations or empty list if none.
        """
        ##set search criteria as keyword args
        searchfilter = "label~contains~'Export Backup Process Task for'"\
                       "~and~ExternalId~contains~'Not Processed'"
        numpagesize = 500

        documents = list()
        ##loop for 10 pages, add task Ids to list, break when no results
        for numpage in range(1,11):
            kw = {"request_params_page":numpage,
                "request_params_page_size":numpagesize,
                "request_params_filters":searchfilter}

            ###Perform get
            try:
                docs = self.docapi.document_get(**kw)
            except ApiException as e:
                self.logger.error("Status {0}, Reason: {1} {2}".format(
                    e.status,e.reason,e.body))
                break
            documents = documents + docs["ResourceList"]
            if len(docs["ResourceList"]) < numpagesize:
                #last page so break
                break

        return documents

    def initiate_export_process(self,searchid,dbtools):
        """
        For a given search profile initiate the bulk export
        Returned: True = Success, False = Error
        Also create a file named after the task id.  This file is in the
        'inprogress' folder.
        Later we can check this folder for 'inprogress' tasks
        OBSOLETE
        """
        taskid = self.create_export_task_db(searchid,dbtools)
        if taskid == None:
            return False
        return True

    def get_csv_if_ready_process(self):
        """
        Look in the working folder 'inprogress' for file
        The file name is the guid of a job.  Check if job is complete
        and if so, download the file to the 'awaitingsync' folder
        OBSOLETE
        """
        sourcedir = self.workingdir + "/inprogress"
        downloaddir = self.workingdir + "/csvexports"
        processedjobs = self.workingdir + "/processedjobs"
        files = os.listdir(sourcedir)
        for filename in files:
            csvfile = get_document_and_save(filename,downloaddir)
            if csvfile != None:
                shutil.move(sourcedir + "/" + filename,processedjobs + "/" + filename)
            else:
                shutil.move(sourcedir + "/" + filename,downloaderror + "/" + filename)

    def dbsync_csvfile_process(self,dbserver,dbname,profiles,username=None,password=None,driver="ODBC Driver 13 for SQL Server"):
        """
        Look in the working folder 'csvexports' for file
        The file name is the profile name of the job.
        Upload to database and move to csvsynced folder
        """
        sourcedir = self.workingdir + "/inprogress/"
        downloaddir = self.workingdir + "/csvexports"
        processedcsv = self.workingdir + "/processedcsv"
        errorcsv = self.workingdir + "/errorcsv"


        files = os.listdir(downloaddir)
        if len(files) == 0:
            return
        dbtools = DB_Tools(dbserver,dbname,username,password,driver)
        for filename in files:
            self.logger.debug(filename)
            fullfilename = downloaddir + "/" + filename
            for profile in profiles:
                if profile.profilename + ".csv" == filename:
                    self.logger.debug("profile: {0},file: {1}".format(profile.profilename,filename))
                    success = self.csvfile_to_db(fullfilename,profile,dbtools)
                    #dt = datetime.datetime.utcnow().isoformat()
                    dt = str(int(time.time()))
                    filename = dt + "_" + filename
                    if success:
                        shutil.move(fullfilename,processedcsv + "/" + filename)
                    else:
                        shutil.move(fullfilename,errorcsv + "/" + filename)

    def csvfile_to_db(self,csvfile,profile,dbtools):
        """
        For a given csv file sync data to db.  Assumes a header row
        param csvfile: the full filename and path of csv file
        param profile: instance of SearchProfileRepresentation
        Param dbtools: dbtools object        
        Returned: 0 if success, else 1
        """

        dbtable = profile.tablename
        keyfield = profile.keyfield
        logtable = profile.logtable
        
        #get list of columns
        bIsHeader = True
        allrows = []
        saved_row = []

        with open(csvfile, 'rt', encoding='utf-8', newline = '') as csvfile:
            readCSV = csv.reader(csvfile,delimiter=',')
            for row in readCSV:
                if bIsHeader == True:
                    bIsHeader = False
                    columns = row
                else:
                    #cater for carriage returns in a column
                    if len(saved_row):
                        row_tail = saved_row.pop()  #gets last item in the list
                        row[0] = row_tail + '\r' +row[0]  # reconstitute field broken by newline
                        row = saved_row + row       # and reassemble the row (possibly only partially)
                    if len(row) >= len(columns):
                        allrows.append(row)
                        saved_row = []
                    else:
                        saved_row = row
        returncode = dbtools.data_sync_to_db(allrows,columns,dbtable,keyfield,logtable)
        return returncode

class SearchProfileRepresentation(object):
    """"
    A structure for defining table metadata and relationships between
    search profile names, id's and tables
    """
    def __init__(self,profileguid=None,profilename=None,tablename=None,keyfield=None,logtable=None,useinternalnames=False,replacespaces=False,spacedelimiter=None,lastdatefield=None):
        """
        SearchProfileRepresentation - a model defining metadata for syncing a
        search profile to a local database table via bulk export api
        """
        self.fieldtypes = {
            "profileguid": "str",
            "profilename": "str",
            "tablename": "str",
            "keyfield": "str",
            "logtable": "str",
            "useinternalnames":"bool",
            "replacespaces":"bool",
            "lastdatefield":"string"
        }
        self._profileguid = profileguid
        self._profilename = profilename
        self._tablename = tablename
        self._keyfield = keyfield
        self._logtable = logtable
        self._useinternalnames = useinternalnames
        self._replacespaces = replacespaces
        self._spacedelimiter = spacedelimiter
        self._lastdatefield = lastdatefield
        
    @property
    def profileguid(self):
        return self._profileguid
    @profileguid.setter
    def profileguid(self,profileguid):
        self._profileguid = profileguid
    
    @property
    def profilename(self):
        return self._profilename
    @profilename.setter
    def profilename(self,profilename):
        self._profilename = profilename

    @property
    def tablename(self):
        return self._tablename
    @tablename.setter
    def tablename(self,tablename):
        self._tablename = tablename

    @property
    def keyfield(self):
        return self._keyfield
    @keyfield.setter
    def keyfield(self,keyfield):
        self._keyfield = keyfield

    @property
    def logtable(self):
        return self._logtable
    @logtable.setter
    def logtable(self,logtable):
        self._logtable = logtable

    @property
    def useinternalnames(self):
        return self._useinternalnames
    @useinternalnames.setter
    def useinternalnames(self,useinternalnames):
        self._useinternalnames = useinternalnames

    @property
    def replacespaces(self):
        return self._replacespaces
    @replacespaces.setter
    def replacespaces(self,replacespaces):
        self._replacespaces = replacespaces

    @property
    def spacedelimiter(self):
        return self._spacedelimiter
    @spacedelimiter.setter
    def spacedelimiter(self,spacedelimiter):
        self._spacedelimiter = spacedelimiter

    @property
    def lastdatefield(self):
        return self._lastdatefield
    @lastdatefield.setter
    def lastdatefield(self,lastdatefield):
        self._lastdatefield = lastdatefield

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

class ExportTaskRepresentation(object):
    """"
    A structure for defining table metadata and relationships between
    search profile names, id's and tables
    """
    def __init__(self,oid=None,taskguid=None,documentid=None,profile=None):
        """
        SearchProfileRepresentation - a model defining metadata for syncing a
        search profile to a local database table via bulk export api
        """
        self.fieldtypes = {
            "oid": "str",
            "taskguid": "str",
            "documentid": "str",
            "profile": "SearchProfileRepresentation"
        }
        self._oid = oid
        self._taskguid = taskguid
        self._documentid = documentid
        self._profile = profile

    @property
    def oid(self):
        return self._oid
    @oid.setter
    def oid(self,oid):
        self._oid = oid
        
    @property
    def taskguid(self):
        return self._taskguid
    @taskguid.setter
    def taskguid(self,taskguid):
        self._taskguid = taskguid

    @property
    def documentid(self):
        return self._documentid
    @documentid.setter
    def documentid(self,documentid):
        self._documentid = documentid
        
    @property
    def profile(self):
        return self._profile
    @profile.setter
    def profile(self,profile):
        self._profile = profile

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

class DB_Tools(object):
    """
    Class to manage connections to databases and typical processes
    """
    def __init__(self,dbserver,dbname,username=None,password=None,driver="ODBC Driver 13 for SQL Server"):
        """
        Initialise DB_Tools class
        :param dbserver: database instance (SQL Server)
        :param dbname: database name.
        :param username: database username. Optional.
        If None then trusted connection.  Password required if not None
        :param password: database password.  Optional, used with username
        :param driver: Optional. default="ODBC Driver 13 for SQL Server".
        Could also use "SQL Server" but this is an old driver and must use
        trusted connection for that driver
        """
        api_client = ApiClient()         
        self.logger = api_client.configuration.packagelogger
        self.logger.debug("Initiated Database module")
        driver = self.check_sql_server_driver(driver)
        if driver == None:
            raise ValueError("ODBC Driver [{0}] not found".format(driver))
        if username == None:
            self.connstr = "Driver={" + driver + "};" + """
            Server={0};Database={1};Trusted_Connection=yes;
            APP=Assetic Asset Sync""".format(dbserver,dbname)
            #;Charset=utf-8
        else:
            self.connstr = "Driver={" + driver + "};" + """
            Server={0};Database={1};UID={2};PWD={3};
            APP=Assetic Asset Sync""".format(dbserver,dbname,username,password)

    def check_sql_server_driver(self,driver):
        """
        Check that the driver passed in is installed.  If not found will
        find a SQL Server driver to use
        Will log a warning if passed in driver not found 
        :param driver: driver name
        :returns: driver name or none if no valid drivers found
        """
        try:
            drivers = pyodbc.drivers()
            if len(drivers) == 0:
                ##can't get driver list so have to assume ok
                return driver
            if driver in drivers:
                ##passed in driver exists
                return driver
            ##look for a driver.  Best to use more recent drivers so will look
            ##for drivers in a specific order
            preferred_drivers = ["ODBC Driver 13 for SQL Server",
                                 "ODBC Driver 11 for SQL Server",
                                 "SQL Server Native Client 11.0",
                                 "SQL Server Native Client 10.0",
                                 "SQL Server"]
            for preferred_driver in preferred_drivers:
                if preferred_driver in drivers:
                    msg = "Using default ODBC driver [{0}] because driver "\
                          "[{1}] not installed".format(preferred_driver,driver)
                    self.logger.warning(msg)
                    return preferred_driver
            ##not in list
                return None
        except:
            ##can't get driver list so have to assume ok
            return driver

    @contextmanager
    def open_db_connection(self, commit=False):
        """
        Use contextmanager to manage connections so we cleanup connection
        as we go to avoid database locking issues on exception
        """
        self.logger.debug("in open db connection")
        try:
            connection = pyodbc.connect(self.connstr)
        except pyodbc.Error as err:
            self.logger.error(str(err),exc_info=True)
            raise err
        except Exception as ex:
            self.logger.error(ex,exc_info=True)
            raise ex
        try:
            if sys.version_info < (3,0):
                connection.setencoding(str, 'utf-8')
                connection.setencoding(unicode, 'utf-16le')
                connection.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
                connection.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-16le')
                #connection.setencoding(str, encoding='utf-8')
                #connection.setencoding(unicode, encoding='utf-8', ctype=pyodbc.SQL_WCHAR)

            cursor = connection.cursor()
            yield cursor
        except pyodbc.DatabaseError as err:
            cursor.rollback()
            self.logger.error(str(err),exc_info=True)
            raise err
        except UnicodeDecodeError as ex:
            self.logger.error(str(err),exc_info=True)
            cursor.rollback()
            raise ex            
        except Exception as ex:
            cursor.rollback()
            self.logger.error(ex,exc_info=True)
            raise ex
        else:
            if commit:
                cursor.commit()
            else:
                cursor.rollback()
        finally:
            connection.close()
                        
    def data_sync_to_db(self,allrows,columns,dbtable,keyfield,logtable):
        """
        For a array containing csv delimted data sync to db.
        Assums data in columns parameter is the headers for the csv array
        Param1 allrows: the array of data to sync
        Param2 columns: the list of column headers in same order as data
        Param3 dbtable: the database table to sync with
        Param4 keyfield: the primary key used to determine if new or update
        Param5 logtable: the name of the table to log inserts,updates,deletes
        Returned: 0= Success (no db error) else 1 (Exception)
        """
    
        #name for tmp table we'll write data dump to
        tmpdbtable = "#{0}_tmp".format(dbtable)

        #get list of columns in target table (first check if it exists)
        existingcolumns = []
        returncode,dbtable_exists = self.chk_table_exists(dbtable)
        if returncode != 0:
            return returncode
        if dbtable_exists == True:
            returncode,existingcolumns = self.get_columns_for_table(dbtable)
            if returncode != 0:
                return returncode
        if len(existingcolumns) == 0:
            ##no existing output table so match to columns passed in
            #use [:] (strip) to instead of columns.copy() for 2.7 compatibility
            existingcolumns = columns[:]

        #get list of columns in log table (first check if it exists)
        existinglogcolumns = []
        returncode,log_exists = self.chk_table_exists(logtable)
        if returncode != 0:
            return returncode
        if log_exists == True:
            returncode,existinglogcolumns = self.get_columns_for_table(logtable)
            if returncode != 0:
                return returncode
        if len(existinglogcolumns) == 0:
            #no existing log table so set to be same as target table
            #use [:] (strip) to instead of .copy() for 2.7 compatibility            
            existinglogcolumns = existingcolumns[:]

        #make sure key field in target table
        #unicode lower() handled differently in PY2 and PY3
        keyexists = True
        if six.PY3 == True:
            if (keyfield.lower().strip('[').strip(']') in map(
            str.lower, existingcolumns)) == False:
                keyexists = False
        else:
            if (keyfield.lower().strip('[').strip(']') in map(
            string.lower, existingcolumns)) == False:
                keyexists = False
                
        if keyexists == False:        
            msg=("Key field '{0}' is not a column in the table '{1}', task will"
                " not be processed").format(keyfield,dbtable)
            self.logger.error(msg)
            return 1
        
        #make sure key field in log table
        #unicode lower() handled differently in PY2 and PY3
        keyexists = True
        if six.PY3 == True:
            if (keyfield.lower().strip('[').strip(']') in map(
            str.lower, existinglogcolumns)) == False:
                keyexists = False
        else:
            if (keyfield.lower().strip('[').strip(']') in map(
            string.lower, existinglogcolumns)) == False:
                keyexists = False
                
        if keyexists == False:
            msg=("Key field [{0}] is not a column in the table [{1}], task will"
            " not be processed").format(keyfield,logtable)
            self.logger.error(msg)
            return 1
        else:
            #don't need key field for log data output so remove from list
            for chk in existinglogcolumns:
                if chk.lower() == keyfield.lower().strip('[').strip(']'):
                    existinglogcolumns.remove(chk)
                    break

        ##get the database table column names and build the various tables
        insertcolumns = []
        diffinsertcolumns = []
        diffupdatecolumns = []
        origvaluecols = []
        createtmpcolsbyselect = []
        logcreatecolumns = []
        logoutputcolumns = []
        #add a "?" for each column to use in sql parameter settings
        parammark = []

        #'columns' is the complete list of columns in the source data
        for column in columns:
            insertcolumns.append("[{0}]".format(column))
            parammark.append("?")
            if column in existingcolumns:
                diffinsertcolumns.append("[{0}]".format(column))
                diffupdatecolumns.append("a.[{0}]=c.[{0}]".format(column))
                createtmpcolsbyselect.append("[{0}]".format(column))
                if column.lower() != keyfield.lower().strip('[').strip(']'):
                    logcreatecolumns.append("[{0}]".format(column))
            else:
                ##this column will be loaded in tmp table, but not synced
                msg = ("column [{0}] in export data is not in table [{1}] "
                       "and will be excluded").format(column,dbtable)
                self.logger.warning(msg)
                ##set a default datatype since it's not in target table
                createtmpcolsbyselect.append("convert(nvarchar(500),'') as [{0}]"
                        .format(column))
                
        for logcolumn in existinglogcolumns:
            if (logcolumn in columns and logcolumn in existingcolumns):
                logoutputcolumns.append("[{0}]".format(logcolumn))
            else:
                if (logcolumn not in ['action','syncdate']):
                    ##this column in log table will be ignored
                    msg = ("column [{0}] in log table is not in either the "
                       "export data or the target table [{1}] and so it "
                       "will be ignored").format(
                           logcolumn,dbtable)
                    self.logger.warning(msg)

        #need to remove spurious characters from tmpdbtable street number field 
        sqlstnumupdate = None
        strnumwords = ["asset","street","number"]
        for insertcol in diffinsertcolumns:
            if all(word in insertcol.lower() for word in strnumwords):
                #Asset Street Number is in the column name
                sqlstnumupdate = "update {0} set {1} = "\
                      "replace(replace({1},'=',''),'\"','')".format(
                      tmpdbtable,insertcol)            
            
        sqltblchktmp =  "select object_id('{0}')".format(tmpdbtable)
        sqltruncatetmp = "drop table  {0}".format(tmpdbtable)
        sqlcreatetmp = """select {0} into {1} from {2} where 1=0""".format(
            ",".join(createtmpcolsbyselect),tmpdbtable,dbtable)
        
        #determine if primary key set for tables, if not prepare sql
        sqlsetkeynotnull = None
        sqlkeypk = None
        knullable = None
        if dbtable_exists == False:
            sqlsetkeynotnull = "alter table {0} alter column {1} "\
                    "nvarchar(500) not null".format(dbtable,keyfield)
            sqlkeypk = "alter table {0} add CONSTRAINT {0}_key_PK PRIMARY KEY("\
                       "{1})".format(dbtable,keyfield)
            knullable == "NO"
        else:
            ##target table exists, check if key field is not null
            keychk,keyinfo = self.get_column_info(dbtable,
                                    keyfield.strip("[").strip("]"))
            if keychk != 0:
                msg = "Unable to get column info for key field {0}".format(
                    keyfield)
                self.logger.warning(msg)                
            else:
                kcollation = keyinfo[0]
                knullable =  keyinfo[1]
                kmax = keyinfo[2]
        sqltempkeynotnull = None
        if knullable != None and knullable.upper() == "YES":
            msg = "Key field {0} in table {1} should be set as 'NOT NULL'"\
                  " with a unique index/primary key constraint".format(
                      keyfield,dbtable)
            self.logger.warning(msg)
            ##SQL to make the key field nullable
            sqltempkeynotnull = "alter table {0} alter column {1} nvarchar({2})"\
                            " COLLATE {3} not null".format(tmpdbtable,
                            keyfield,kmax,kcollation)
        sqltempkeypk = "alter table {0} add CONSTRAINT tmp{1}key_PK PRIMARY KEY"\
                       "({2})".format(tmpdbtable,dbtable,keyfield)
        
        sqlcreate = """create table {0} ({1} nvarchar(500))
            """.format(dbtable,"nvarchar(500),".join(insertcolumns ))
        
        sqllogcreate = """select convert([nvarchar](10),'') as action,
            {1},convert([datetime],getdate()) as [syncdate],{2} into {0}
            from {3} where 1=0""".format(
                logtable,keyfield,
                ",".join(logcreatecolumns),dbtable)

        ##Now create insert string
        sqlinsert = "insert into {0} (".format(tmpdbtable)
        sqlinsert = sqlinsert + ",".join(insertcolumns ) + ") values ("
        sqlinsert = sqlinsert + ",".join(parammark ) + ")"

        ##Now add data to sql insert string and do insert
        ##(using 'insertmany' effectively row by row)                   
        ##now refresh base table from temp table where there are changes
        ##write the change to the archive file
        ##TODO output all columns for updated record (original record)
        sqldiff = """
        WITH diff as ( select {2}
            FROM {0}
            except select {2}
            FROM {1}
            )
            MERGE {1} as a using diff as c on
            (c.{5} COLLATE database_default=a.{5} COLLATE database_default)
            when MATCHED then update set {3}
            When not matched then insert
            ({2}) 
            values ({2})
            output $action,inserted.{5},getdate(),deleted.{6} into {4}
            ([action],{5},[syncdate],{7});
        """.format(tmpdbtable,dbtable,",".join(diffinsertcolumns),
                   ",".join(diffupdatecolumns),logtable,keyfield,
                   ",deleted.".join(logoutputcolumns),
                   ",".join(logoutputcolumns))

        ##Now execute all the sql statements in the one transaction block
        ##Bit slow opening & closing db connection, but transaction block
        ##works well
        try:
            with self.open_db_connection(True) as cursor:
                #if permanent table not exist then create
                if dbtable_exists == False:
                    #table not found - create permament table for current data
                    self.logger.debug(sqlcreate)
                    cursor.execute(sqlcreate)
                    if sqlsetkeynotnull != None:
                        self.logger.debug(sqlsetkeynotnull)
                        cursor.execute(sqlsetkeynotnull)
                    if sqlkeypk != None:                    
                        self.logger.debug(sqlkeypk)
                        cursor.execute(sqlkeypk)
                        
                #check if temporary table exists
                self.logger.debug(sqltblchktmp)
                cursor.execute(sqltblchktmp)
                row = cursor.fetchone()
                if row[0] == None:
                    self.logger.debug(sqlcreatetmp)
                    cursor.execute(sqlcreatetmp)
                    if sqltempkeynotnull != None:
                        #set the key field as not null
                        self.logger.debug(sqltempkeynotnull)
                        cursor.execute(sqltempkeynotnull)
                        sqltempkeynotnull = None
                else:
                    self.logger.debug(sqltruncatetmp)
                    cursor.execute(sqltruncatetmp)
                    
                #if log table not exist then create
                if log_exists == False:
                    #table not found - create permament table for logging changes
                    self.logger.debug(sqllogcreate)
                    cursor.execute(sqllogcreate)
                ##write all the data to the temp table in db.
                self.logger.debug(sqlinsert)
                cursor.executemany(sqlinsert,allrows)
                ##update street number field to remove spurious chars
                if sqlstnumupdate != None:
                    self.logger.debug(sqlstnumupdate)
                    cursor.execute(sqlstnumupdate)
                ##set pk on tmp table if not null set on field
                if sqltempkeynotnull == None:
                    self.logger.debug(sqltempkeypk)
                    cursor.execute(sqltempkeypk)
                ##execute diff statement to populate permanent tables from temp table
                self.logger.debug(sqldiff)
                cursor.execute(sqldiff)
                ##drop temp table
                self.logger.debug(sqltruncatetmp)
                cursor.execute(sqltruncatetmp)
        except Exception as ex:
            self.logger.exception(ex)
            return 1
        return 0

    def get_columns_for_table(self,dbtable):
        """
        Get list of columns in database table
        :param dbtable: The database table
        :returns: Tuple - 0= success (no db error), else 1 and
        results (an array of columns)
        """
        sql = """select column_name from Information_schema.columns 
            where table_name='{0}' order by ORDINAL_POSITION asc""".format(
                dbtable)
        returncode,results = self.execute_select(sql)
        if returncode > 0:
            msg = "Error checking columns for table [{0}]. ".format(dbtable)
            self.logger.error(msg)
            return returncode,None
        
        msg = "No columns found for table [{0}]. "\
                "Check that table exists and columns can be selected "\
                "from INFORMATION_SCHEMA.COLUMNS".format(dbtable)
        if results == None:
            self.logger.error(msg)
            return 1,None
        if returncode == 0 and len(results) == 0:
            self.logger.error(msg)
            return 1,None
        columnarr  = []
        for result in results:
            ##results come back as a tuple even though only 1 column per record
            columnarr.append(result[0])
        return returncode,columnarr

    def get_column_info(self,dbtable,column):
        """
        Get info about a column
        :param dbtable: The database table
        :returns: Tuple - 0= success (no db error), else 1 and
        array of collation_name, nullable, max_size
        """
        sql = """select COLLATION_NAME,IS_NULLABLE,
            CHARACTER_MAXIMUM_LENGTH from INFORMATION_SCHEMA.COLUMNS
            where COLUMN_NAME='{0}' and TABLE_NAME='{1}'""".format(
                column,dbtable)
        returncode,results = self.execute_select(sql)
        if returncode > 0:
            msg = "Error checking column [{0}] for table [{1}]. ".format(
                column,dbtable)
            self.logger.error(msg)
            return returncode,None
        
        msg = "No column [{0}] found for table [{1}]. "\
                "Check that table exists and column can be selected "\
                "from INFORMATION_SCHEMA.COLUMNS".format(column,dbtable)
        if results == None:
            self.logger.error(msg)
            return 1,None
        if returncode == 0 and len(results) == 0:
            self.logger.error(msg)
            return 1,None
        
        for result in results:
            ##results come back as a tuple even though only 1 column per record
            columninfo = result
        if len(columninfo) !=3:
               returncode = 1
        return returncode,columninfo
    
    def chk_table_exists(self,dbtable):
        """
        checks if db table exists
        :param dbtable: The database table
        :returns: tuple, returncode indicating if there was an erorr (nonzero)
        and True/False for table existance
        """
        sql = "select object_id('{0}')".format(dbtable)
        returncode,results = self.execute_select(sql)
        if returncode != 0:
            msg = "Error checking if table [{0}] exists. ".format(dbtable)
            self.logger.error(msg)
            return returncode,None
        exists = True
        if results[0][0] == None:
            exists = False

        return returncode,exists
  
    def execute_select(self,sql):
        """
        Helper method to run an SQL select
        param sql: SQL select statement
        Returned: Tuple - 0= success (no db error), else 1 and
        results (an array of results)
        """
        self.logger.debug(sql)
        try:
            with self.open_db_connection(True) as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()
        except Exception as ex:
            self.logger.exception(ex)
            return 1, None

        return 0, results                

    def execute_single(self,sql,datarow=None):
        """
        Helper method to run a single record SQL insert, update, or delete
        param sql: the sql statement
        param datarow is optional parameter.  Has data as tuple for sql
        Returned: 0= Success (no db error) else 1 (Exception)
        """
        self.logger.debug(sql)
        self.logger.debug(datarow)
        try:
            with self.open_db_connection(True) as cursor:
                if datarow != None:
                    cursor.execute(sql,datarow)
                else:
                    cursor.execute(sql)
        except Exception as ex:
            self.logger.exception(ex)
            return 1
        return 0

    def execute_many(self,sql,datarows):
        """
        Helper method to run a multiple record SQL insert, update, or delete
        Returned: 0= Success (no db error) else 1 (Exception)
        """
        try:
            with self.open_db_connection(True) as cursor:
                cursor.executemany(sql,datarows)
        except Exception as ex:
            self.logger.exception(ex)
            return 1
        return 0

##class UTF8Recoder:
##    def __init__(self, f, encoding):
##        self.reader = codecs.getreader(encoding)(f)
##    def __iter__(self):
##        return self
##    def next(self):
##        return self.reader.next().encode("utf-8")
##
##class UnicodeReader:
##    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
##        f = UTF8Recoder(f, encoding)
##        self.reader = csv.reader(f, dialect=dialect, **kwds)
##    def next(self):
##        '''next() -> unicode
##        This function reads and returns the next line as a Unicode string.
##        '''
##        row = self.reader.next()
##        return [unicode(s, "utf-8") for s in row]
##    def __iter__(self):
##        return self
