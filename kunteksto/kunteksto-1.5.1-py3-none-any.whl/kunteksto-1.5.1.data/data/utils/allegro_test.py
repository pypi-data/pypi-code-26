import os
import configparser

config = configparser.ConfigParser()
config.read('../kunteksto.conf')
print("\n\nAllegroGraph connection and environment test for Kunteksto version: " + config['SYSTEM']['version'] + " using S3Model RM: " + config['SYSTEM']['rmversion'] + "\n\n")

# Set environment variables for AllegroGraph
os.environ['AGRAPH_HOST'] = config['ALLEGROGRAPH']['host']
os.environ['AGRAPH_PORT'] = config['ALLEGROGRAPH']['port']
os.environ['AGRAPH_USER'] = config['ALLEGROGRAPH']['user']
os.environ['AGRAPH_PASSWORD'] = config['ALLEGROGRAPH']['password']
        

from franz.openrdf.connect import ag_connect
with ag_connect('Kunteksto', host=os.environ.get('AGRAPH_HOST'), port=os.environ.get('AGRAPH_PORT'),  user=os.environ.get('AGRAPH_USER'), password=os.environ.get('AGRAPH_PASSWORD')) as conn:
    print('Kunteksto Repository Size: ', conn.size())

