# Setup AllegroGraph and BaseX for the tutorial
import os
import configparser
try:
    from BaseXClient import BaseXClient
except:
    print("Could not find the BaseXClient")
try:    
    from franz.openrdf.connect import ag_connect
except:
    print("Could not find the AllegroGraph client.")

dirpath = os.getcwd()
foldername = os.path.basename(dirpath)
print("\nThe current directory name is : " + foldername)

if foldername != 'kunteksto':
    print("ERROR: You are not in the kunteksto directory.\n")
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
            conn.addFile(dirpath + '/s3model/s3model.owl', serverSide=True)    
            conn.addFile(dirpath + '/s3model/s3model_3_1_0.rdf', serverSide=True)    
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
