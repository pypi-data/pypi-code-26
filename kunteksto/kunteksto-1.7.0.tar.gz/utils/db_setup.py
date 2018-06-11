# Setup AllegroGraph and BaseX for the tutorial
import os
import sys
import configparser
import requests
from requests.auth import HTTPDigestAuth

try:
    from BaseXClient import BaseXClient
except:
    print("Could not find the BaseXClient")
try:    
    from franz.openrdf.connect import ag_connect
except:
    print("Could not find the AllegroGraph client.")

dirpath = os.getcwd()
curdir = os.path.basename(dirpath)

print("\nThe current directory name is : " + curdir)

if curdir != 'kunteksto':
    print("ERROR: You are not in the kunteksto directory. Change to the 'kunteksto' directory and run 'utils/db_setup.py'\n")
    raise SystemExit
    
config = configparser.ConfigParser()
config.read('kunteksto.conf')
print("\nDatabase setup for Kunteksto version: " + config['SYSTEM']['version'] + " using S3Model RM: " + config['SYSTEM']['rmversion'] + "\n\n")

if config['ALLEGROGRAPH']['status'].upper() == "ACTIVE":    
    print('Checking AllegroGraph connections.\n')
    # Set environment variables for AllegroGraph
    os.environ['AGRAPH_HOST'] = config['ALLEGROGRAPH']['host']
    os.environ['AGRAPH_PORT'] = config['ALLEGROGRAPH']['port']
    os.environ['AGRAPH_USER'] = config['ALLEGROGRAPH']['user']
    os.environ['AGRAPH_PASSWORD'] = config['ALLEGROGRAPH']['password']
            
    try:
        with ag_connect(config['ALLEGROGRAPH']['repo'], host=os.environ.get('AGRAPH_HOST'), port=os.environ.get('AGRAPH_PORT'),  user=os.environ.get('AGRAPH_USER'), password=os.environ.get('AGRAPH_PASSWORD')) as conn:
            conn.clear(contexts='ALL_CONTEXTS')
            print('Initial Kunteksto RDF Repository Size: ', conn.size(), '\n')
            conn.addFile(os.path.join(dirpath,'s3model','s3model.owl'), serverSide=True)    
            conn.addFile(os.path.join(dirpath, 's3model','s3model_3_1_0.rdf'), serverSide=True)    
            print('Current Kunteksto RDF Repository Size: ', conn.size(), '\n')
            print('AllegroGraph connections are okay.\n\n')
    except:
        print("Could not establish a connection to AllegroGraph. Check to see that the server is running and the kunteksto.conf values are correct.\n\n")
        
else:
    print("AllgroGraph option is not active in kunteksto.conf.")

if config['BASEX']['status'].upper() == "ACTIVE":    
    # Setup BaseX
    # create session
    print('Checking BaseX connections.\n')
    try:
        session = BaseXClient.Session(config['BASEX']['host'], int(config['BASEX']['port']), config['BASEX']['user'], config['BASEX']['password'])
        # create new database
        session.create(config['BASEX']['dbname'], "")
        print(session.info())
    
        # run query on database
        print(session.execute("xquery doc("+config['BASEX']['dbname']+")"))
    except:
        session = None
        print("Could not establish a BaseX connection. Check to see that the server is running and the kunteksto.conf values are correct.\n\n")
    
    finally:
        # close session
        if session:
            session.close()
            print('BaseX connections are okay.\n\n')
else:
    print("BaseX option is not active in kunteksto.conf.\n\n")


if not config['MARKLOGIC']['status'].upper() == "ACTIVE":
    print("\nThe MarkLogic option is INACTIVE. Nothing to do.\n\n")
    sys.exit(0)

xmloption = True if config['MARKLOGIC']['loadxml'].upper() == "TRUE" else False
rdfoption = True if config['MARKLOGIC']['loadrdf'].upper() == "TRUE" else False
jsonoption = True if config['MARKLOGIC']['loadjson'].upper() == "TRUE" else False

if not xmloption and not rdfoption and not jsonoption:
    print("\nNone of the MarkLogic options are active. Nothing to do.\n\n")
    sys.exit(0)

print("\nPreparing to setup MarkLogic 9.\n")

dbname = config['MARKLOGIC']['dbname']
hostip = config['MARKLOGIC']['hostip']
port = config['MARKLOGIC']['port']
user = config['MARKLOGIC']['user']
pw = config['MARKLOGIC']['password']

# Check if dbname exists already, if it does then clear it and reload the RM RDF & ontology
headers = {"Content-Type": "application/json", 'user-agent': 'Kunteksto'}
payload = {"format":'json'}
url = 'http://' + hostip + ':' + '8002' + '/manage/v2/databases/' + dbname
print("Checking for " + url)
r = requests.get(url, auth=HTTPDigestAuth(user, pw), headers=headers, json=payload)
if r.status_code == 200:
    print("Clearing " + url)
    payload = {"operation":'clear-database'}
    url = 'http://' + hostip + ':' + '8002' + '/manage/v2/databases/' + dbname
    r = requests.post(url, auth=HTTPDigestAuth(user, pw), headers=headers, json=payload)
else:    
    # Attempt to create the DB
    headers = {"Content-Type": "application/json", 'user-agent': 'Kunteksto'}
    payload = {"database-name":dbname}
    url = 'http://' + hostip + ':8002/manage/v2/databases'
    print("Checking for " + url)    
    r = requests.post(url, auth=HTTPDigestAuth(user, pw), headers=headers, json=payload)
    
    if r.status_code != 201:
        print("\nCannot create the database " + dbname + " on http://" + hostip + ":8002/manage/v2/databases" )
        print("\nCheck your settings and your ML9 system. Process aborted!")
        sys.exit(-1)
    else:
        print("Created Database " + dbname)
        
    # Attempt to create the Forests
    numforests = int(config['MARKLOGIC']['forests'])
    hostname = config['MARKLOGIC']['hostname']
    for fid in range(0, numforests):
        payload = {"forest-name": dbname + '-' + str(fid), "host": hostname, "database": dbname}
        r = requests.post('http://' + hostip + ':8002/manage/v2/forests', auth=HTTPDigestAuth(user, pw), headers=headers, json=payload)    
        if r.status_code != 201:
            print(r.status_code)
            print("Cannot create the forest " + dbname + '-' + str(fid) + " for database " + dbname + " on host " + hostname)
            print("\nCheck your settings and your ML9 system. Process aborted!")
            sys.exit(-1)
        else:
            print("Created Forest " + dbname + '-' + str(fid))
    
    # Set up REST API 
    payload = {
      "rest-api": {
        "name": "kunteksto-app-server-" + port,
        "database": dbname,
        "modules-database": "kunteksto-modules",
        "port": port,
        "xdbc-enabled": "true",
        "forests-per-host": numforests,
        "error-format": "json"
      }
    }
    
    r = requests.post('http://' + hostip + ':8002/LATEST/rest-apis', auth=HTTPDigestAuth(user, pw), headers=headers, json=payload)    
    if r.status_code != 201:
        print("\nCannot create the REST API for " + dbname + " on http://" + hostip + ":" + port )
        print("\nCheck your settings and your ML9 system or maybe it already exists.")
    else:
        print("Created REST API for " + dbname + " at http://" + hostip + ":" + port)

# Write the RM RDF and ontology to ML9
with open(os.path.join('s3model','s3model.owl'), 'r') as owlfile:
    owlStr=owlfile.read()    
    headers = {"Content-Type": "application/xml", 'user-agent': 'Kunteksto'}
    url = 'http://' + hostip + ':' + port + '/v1/documents?uri=/s3model/s3model.owl'
    r = requests.put(url, auth=HTTPDigestAuth(user, pw), headers=headers, data=owlStr)                                
    
with open(os.path.join('s3model','s3model_3_1_0.rdf'), 'r') as rdffile:
    rdfStr=rdffile.read()    
    headers = {"Content-Type": "application/xml", 'user-agent': 'Kunteksto'}
    url = 'http://' + hostip + ':' + port + '/v1/documents?uri=/s3model/s3model_3_1_0.rdf'
    r = requests.put(url, auth=HTTPDigestAuth(user, pw), headers=headers, data=rdfStr)                                

print("\nDatabase Setup is finished.\n\n")