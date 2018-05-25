from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from future.utils import raise_
from future.utils import raise_with_traceback
from future.utils import raise_from
from future.utils import iteritems

from builtins import FileExistsError
from pathlib import Path
import threading
from datetime import datetime
import simplejson as json
from queue import Queue
import queue
from time import sleep
import requests
from pprint import pprint
version = "0.0.1"

#The above future imports helps/ensures that the code is compatible
#with Python 2 and Python 3
#Read more at http://python-future.org/compatible_idioms.html

import logging
import sys
import os
import importlib
from threading import Thread
from configobj import ConfigObj

from sensesagent import log
from sensesagent.exceptions import ConfigFileNotFound




class SensesAgentConfig(object):
    """
    Contains the configuration for sensesagent. It loads the sensesagent.conf 
    configuration file and makes them available as the .config object 
    dictionary. 
    """

    def __init__(self, start_dir, config_path=None): 

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Instantiating instace with __init__(config_path={})".format(config_path))
        self.start_dir = start_dir 

        self._config_path = config_path
        self._config = None
        
       
        

    
    @property
    def config(self):
        """configobject property. This contains the dictionary from 
        sensesagent.ini file. Example function with types documented in the docstring.

        `PEP 484`_ type annotations are supported. If attribute, parameter, and
        return types are annotated according to `PEP 484`_, they do not need to be
        included in the docstring:
    
        Args:
            param1 (int): The first parameter.
            param2 (str): The second parameter.
    
        Returns:
            bool: The return value. True for success, False otherwise.
    
        .. _PEP 484:
            https://www.python.org/dev/peps/pep-0484/
    
        """
       
        if self._config == None: 
            self._config = self.load_config()

        return self._config

    @config.setter
    def config(self, config):
        self._config = config

    @property
    def config_path(self): 
        """
        Args:
            path (str): The path of the file to wrap
            field_storage (FileStorage): The :class:`FileStorage` instance to wrap
            temporary (bool): Whether or not to delete the file when the File
                instance is destructed
        
        Returns:
            BufferedFileStorage: A buffered writable file descripto        
        """
        
        if self._config_path == None: 
            return self.find_config_path()
        else: 
            return self._config_path
        
    @property
    def collectors(self):
        pass

    def load_config(self):

        #with open(self.config_path, "r") as f: 
        #config_file = f.read()
        #return config_file

        config = ConfigObj(self.config_path)
        return config

    def find_config_path(self):
        """Looks for conf directories in the following sequence: 

            1. current directory : start_dir + ./conf/sensesagent.conf
            2. conf directory above the current directory ../conf/sensesagent.conf
            3. conf in /etc/sensesagent/

            if all that fails refuse to start!
        """

        search_list = ["./conf/sensesagent.conf", 
                       "../conf/sensesagent.conf", 
                       "/etc/sensesagent/sensesagent.conf"]

        for path_str in search_list:
            test_path = Path(self.start_dir, path_str)
            if test_path.is_file():
                return test_path.as_posix()
        #If we get here then we failed!
        #try or die trying
        raise ConfigFileNotFound("Config File Not Found.")


    

class SensesAgent(object):
    """
    The SensesAgent class takes care of the following responsibilities

        1. Load the configuration
        2. Instantiate and manage the lifecycle of the collectors
        3. Ensure metrics gathhered or  created by the collectors are sent to the endpoints. 
        4. Provide remote monitoring and status of the current running agent and collectors
    """

    def __init__(self, start_dir, config_path="conf"): 
 
        self.logger = logging.getLogger(self.__class__.__name__)
        #start_dir= Path(curr_dir.parent, "tests").as_posix() 
        sa = SensesAgentConfig(start_dir)
        self.config = sa.config
        self.threads = []
        self.metric_queue = queue.Queue()
      
        senses_http_pub = SensesHttpPublisher(data_queue=self.metric_queue, 
                                              config=self.config)
        senses_http_pub.start()
        
        
    def get_collector_class(self,fqcn):
        """
        Loads the collector class. The collector is loaded as a module from 
        pythons sys.path. It also searches for the module 
        

        Args:
            fqcn (str): The Fully qualified class name of the Collector class. By default sensesagent looks for these in sensesagent.collectors. 
        
        Returns:
            Collector Class: A python class that implements sensesagent.collectors.Collector        
        """
        
    

        #TODO: Add more paths here to search for more collectors. 
        search_paths = ["sensesagent.collectors",]

        for path in search_paths:
            full_path  = path + "." + fqcn
            module_path = full_path[:full_path.rfind(".")]
            class_name = full_path[full_path.rfind(".")+1:]

            module = importlib.import_module(module_path)
            my_class = getattr(module, class_name)

            return my_class


    def run_collectors(self):
        """
        Iterates through the list of collectors, ensuring to load up their 
        configurations from the config file.
        """
       
        collectors_dict = self.config["Collectors"]
        
        for x in collectors_dict: 
            config = collectors_dict[x]
            t = threading.Thread(target=self.collector_runner, args=(config,))
            self.threads.append(t)
            t.start()
        
        while 1:
            sleep(1)

    def collector_runner(self, config):
        """
        This code runs inside a thread started by self.run_collectors. Its job 
        is to load the collector class provided in the fqcn, and then 
        pump it for data. 
        
        
        config is a dictionary containing information about the collector
        
        For example
         {'class': 'loadaverage.LoadAverageCollector',
          'device_key': 'MoBo5eQqRZ',
          'device_secure_id': 'WMyQTsETnC',
          'name': 'SystemCollector',
          'update': '5'}
         """
        
        # Get the class for the collector because this is what is used to 
        # load it. 
        fqcn = config.get("class")
        MyCollector = self.get_collector_class(fqcn)
        
        #we pass the config dict to the collector so as to 
        #make it available for use in the template
        collector = MyCollector(config=config)
        
        x = queue.Queue()
        
        while 1:
            #Collector is running. Gather data from this thread
            
            json_str = collector.json
            self.logger.debug(json_str)
            
            # We turn the data into a dict via json.loads for two reasons
            # 1. to ensure that the json string is valid
            # 2. posting the data requires it to be in dict format
            metric_data = json.loads(json_str)
        
        
            #We automatically add the timestamp
            metric_data["DeviceTimeStamp"] =  int(datetime.utcnow().timestamp())
            
            self.metric_queue.put(metric_data)
            
            pprint(metric_data)
            #get the update interval or use a default of 600 seconds
            update_interval = config.get("update", 600)
            sleep(int(update_interval))            
            

class SensesHttpPublisher(Thread):
    """Recieves data via a queue and takes care of sending the data."""

    def __init__(self, data_queue, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None, config):
        
        super().__init__(group=group, target=target, name=name,
                             daemon=daemon)
        self.args = args
        self.kwargs = kwargs
        
        class_name = self.__class__.__name__
        self.logger = logging.getLogger(class_name)
        self.logger.debug("Instanciating SensesHttpPublisher Thread")
        self.data_queue = data_queue
        
        #config object is made available to all publishers .
        self.config = config 
        
    def run(self):
        """
        Posts the data via http post. 
        """
        
        url = self.config["Main"]["url"]
        headers = {'Content-Type': 'application/json'}
        
        while True: 
            metric_data = self.data_queue.get()
            
            
            print(metric_data)
            import simplejson as json
            data = json.dumps(metric_data)
            print(data)
            
            try: 
                r = requests.post(url, data=data, headers=headers)
                print(r.status_code)
              
            except Exception as e: 
                msg = "Failed to post : {}".format(metric_data)
                self.logger.debug(msg)


def dev(): 

    """
    This is only used as an entry point to test the system during development.
    """

    curr_dir =  Path(os.path.dirname(os.path.realpath(__file__)))
    #During Development we want to use the config files that is inside ../test/

    start_dir= Path(curr_dir.parent, "tests").as_posix() 
    sa = SensesAgentConfig(start_dir)
    #config_path = sa.find_config_path(
    print(sa.config)
    print(sa.config["Collectors"])

if __name__ == "__main__":

    dev()
    
    r = requests.post(url)
    