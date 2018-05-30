#!/usr/local/bin/python3.5
# encoding: utf-8
'''
 -- Export metadata from sheepdog

 is a description

It defines classes_and_methods

@author:     David Steinberg

@copyright:  2018 UCSC Genomics Institute. All rights reserved.

@license:    Apache 2

@contact:    davidcs@ucsc.edu
@deffield    updated: May 22, 2018
'''

import sys
import os
import csv
import json

import csv
import jsonschema
import functools
import json
import os

import requests
from pmap.core import pmap

from io import StringIO

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from pkg_resources._vendor.appdirs import __version_info__

__all__ = []
__version__ = 0.1
__date__ = '2018-05-22'
__updated__ = '2018-05-23'

class Exporter:
    '''
    Export JSON following the DCP metadata including a 
    manifest of all files and any available URL data.
    '''
    def __init__(self, credentials_filename, base_url):
        self.base_url = base_url
        self.access_token = self.access_token(
            credentials_filename)
        self.sheep_url = '{}/api/v0/submission'.format(base_url)
        self.indexd_url = '{}/index/index/'.format(base_url)
        self.schema = self.init_schema()
    
    
    def init_schema(self):
        '''
        Returns the JSON schema for the resulting output.
        '''
        data_object_schema = {
            'type': 'object',
            'required': ['id', 'urls'],
            'properties': {
              'id': {
                'type': 'string',
                'description': 'REQUIRED\nAn identifier unique to this Data Object.'
              },
              'name': {
                'type': 'string',
                'description': 'OPTIONAL\nA string that can be optionally used to name a Data Object.'
              },
              'size': {
                'type': 'string',
                'format': 'int64',
                'description': 'REQUIRED\nThe computed size in bytes.'
              },
              'created': {
                'type': 'string',
                'format': 'date-time',
                'description': 'REQUIRED\nTimestamp of object creation in RFC3339.'
              },
              'updated': {
                'type': 'string',
                'format': 'date-time',
                'description': 'OPTIONAL\nTimestamp of update in RFC3339, identical to create timestamp in systems\nthat do not support updates.'
              },
              'version': {
                'type': 'string',
                'description': 'OPTIONAL\nA string representing a version.'
              },
              'mime_type': {
                'type': 'string',
                'description': 'OPTIONAL\nA string providing the mime-type of the Data Object.\nFor example, \'application/json\'.'
              },
              'checksums': {
                'type': 'array',
                'items': {
                      "type": "object",
                      "properties": {
                        "checksum": {
                          "type": "string",
                          "description": "REQUIRED\nThe hex-string encoded checksum for the Data."
                        },
                        "type": {
                          "type": "string",
                          "description": "OPTIONAL\nThe digest method used to create the checksum. If left unspecified md5\nwill be assumed.\n\npossible values:\nmd5                # most blob stores provide a checksum using this\nmultipart-md5      # multipart uploads provide a specialized tag in S3\nsha256\nsha512"
                        }
                      }
                    },
                
                'description': 'REQUIRED\nThe checksum of the Data Object. At least one checksum must be provided.'
              },
              'urls': {
                'type': 'array',
                    'items': {
                    "type": "object",
                    "properties": {
                      "url": {
                        "type": "string",
                        "description": "REQUIRED\nA URL that can be used to access the file."
                      },
                      "system_metadata": {
                          "type": "object",
                          "additionalProperties": True,
                          "description": "OPTIONAL\nThese values are reported by the underlying object store.\nA set of key-value pairs that represent system metadata about the object."
                      },
                      "user_metadata": {
                          "type": "object",
                          "additionalProperties": True,
                          "description": "OPTIONAL\nA set of key-value pairs that represent metadata provided by the uploader."
                        }
                    }
                },
                'description': 'OPTIONAL\nThe list of URLs that can be used to access the Data Object.'
              },
              'description': {
                'type': 'string',
                'description': 'OPTIONAL\nA human readable description of the contents of the Data Object.'
              },
              'aliases': {
                'type': 'array',
                'items': {
                  'type': 'string'
                },
                'description': "OPTIONAL\nA list of strings that can be used to find this Data Object.\nThese aliases can be used to represent the Data Object's location in\na directory (e.g. \'bucket/folder/file.name\') to make Data Objects\nmore discoverable."
              }
            }
          }
        
        
        schema = {
            'type': 'object',
            'properties': {
                'metadata': {
                    'type': 'object'},
                'data_objects': {
                    'type': 'array',
                    'items': data_object_schema},
                }
            }
        return schema
    
    def headers(self):
        '''
        Return the headers dict that includes the access token for 
        creating a request.
        '''
        return {'Authorization': 'bearer ' + self.access_token}
    
    def access_token(self, filename):
        '''
        Get a fence access token using a path to a credentials.json
        and return that token.
        '''
        auth_url = '{}/user/credentials/cdis/access_token'.format(self.base_url)
        print('Using {} to get an access token.'.format(filename))
        try:
            json_data = open(filename).read()
            keys = json.loads(json_data)
        except Exception as e:
            print('Failed to find your credentials! Check your credentials path: {} \n {}'.format(filename, str(e)))
            return None
        print('Getting access token from {} .'.format(auth_url))
        try:
            access_token = requests.post(auth_url, json=keys).json()['access_token']
        except Exception as e:
            print('Failed to authenticate! Check the URL {} \n {}'.format(auth_url, str(e)))
            return None
        return access_token
    
    def get_dictionary(self, program, project):
        '''
        Gets the schema for a program and project and returns
        it as a dict.
        '''
        dictionary_url = '{}/{}/{}/_dictionary'.format(self.sheep_url, program, project)
        response = requests.get(
            dictionary_url,
            headers=self.headers())
        return response.json()
    
    def get_schema_for_type(self, program, project, my_type):
        '''
        Return the JSON schema for a given program, project, and type.
        '''
        dictionary_url = '{}/{}/{}/_dictionary/{}'.format(self.sheep_url, program, project, my_type)
        return requests.get(
            dictionary_url,
            headers=self.headers()).json()
    
    def get_submissions_by_type(self, program, project, my_type):
        '''
        Returns all the submissions for a given program, 
        project, type triplet.
        '''
        url = '{}/{}/{}/export/?node_label={}&format=json'.format(self.sheep_url, program, project, my_type)
        response = requests.get(url, headers=self.headers())
        return response.json()['data']
    
    def get_json_submission_by_type(self, program, project, my_type):
        '''
        Returns the JSON version of a program, project, type triplet
        and returns a list of dictionaries.
        '''
        print('Requesting {} submissions.'.format(my_type))
        dict_list = self.get_submissions_by_type(program, project, my_type)
        
        if len(dict_list) > 0:
            print('Got {} {} submissions.'.format(len(dict_list), my_type))
        return dict_list
    
    def get_programs(self):
        '''
        Returns the list of projects for a given program.
        '''
        programs_url = '{}/'.format(self.sheep_url)
        raw_programs = requests.get(programs_url, headers=self.headers()).json()['links']
        return [os.path.basename(x) for x in raw_programs]
    
    def get_projects(self, program):
        '''
        Returns the list of projects for a given program.
        '''
        projects_url = '{}/{}/'.format(self.sheep_url, program)
        raw_projects = requests.get(projects_url, headers=self.headers()).json()['links']
        return [os.path.basename(x) for x in raw_projects]
    
    def get_all_submissions(self, program, project):
        '''
        Export all of the types for a given program and project
        and return them as a dictionary with keys for each type.
        '''
        print('Getting dictionary for {}-{}'.format(program, project))
        submission_dictionary = self.get_dictionary(program, project)
        # FIXME why does root return an empty string?
        filter_keys = ['root', '_all']
        key_list = [os.path.basename(x) for x in submission_dictionary['links']]
        filtered_keys = list(filter(lambda x: x not in filter_keys, key_list))
        submission_list = pmap(lambda x: self.get_json_submission_by_type(program, project, x), filtered_keys)
        return dict(zip(filtered_keys, submission_list))
    
    def get_indexd_doc(self, indexd_id):
        '''
        Get the indexd document for a given indexd_id.
        '''
        response = requests.get("{}/{}".format(self.indexd_url, indexd_id))
        if response.status_code != 200:
            print('F', end='', flush=True)
        else:
            print('.', end='', flush=True)
        return response.json()
    
    def get_indexd_docs(self, id_list):
        '''
        Takes a list of ids and returns the indexd documents
        associated with them.
        '''
        return pmap(self.get_indexd_doc, id_list)
    
    def safe_indexd_to_dos(self, indexd_doc):
        '''
        Will throw a useful exception if the conversion to
        DOS fails (usually because the item wasn't found).
        '''
        try:
            return self.indexd_doc_to_dos(indexd_doc)
        except Exception as e:
            #print('indexd doc failed to convert {}'.format(indexd_doc))
            #print(str(e))
            return {}
    
    def indexd_doc_to_dos(self, indexd_doc):
        '''
        Converts an indexd doc into a Data Object for serialization.
        '''
        # TODO whats the name?
        if not indexd_doc.get('file_name', None):
            name = ""
        else:
            name = indexd_doc['file_name']
        data_object = {
            "id": indexd_doc['did'],
            "name": name,
            'created': indexd_doc['created_date'],
            'updated': indexd_doc['updated_date'],
            "size": str(indexd_doc['size']),
            "version": indexd_doc['rev']
        }
        # parse out checksums
        data_object['checksums'] = []
        for k in indexd_doc['hashes']:
            data_object['checksums'].append(
                {'checksum': indexd_doc['hashes'][k], 'type': k})
    
        # parse out the urls
        data_object['urls'] = []
        for url in indexd_doc['urls']:
            data_object['urls'].append({
                'url': url})
           
        return data_object
    
    
    def is_type_data_category(self, program, project, my_type):
        '''
        Returns True if the category is a data file so we
        know whether to grab the submissions indexd document.
        '''
        data_file_categories = ['data_file', 'metadata_file', 'index_file']
        type_schema = self.get_schema_for_type(program, project, my_type)
        if type_schema.get('category', '') in data_file_categories:
            return True
        else:
            return False
    
    def submission_manifest(self, submission_list):
        '''
        Generates a manifest for the given type given the list
        of submissions for that type.
        '''
        # FIXME this changes in the next release to object_id
        id_key = 'object_id'
        id_list = [x[id_key] for x in submission_list]
        return [self.safe_indexd_to_dos(x) for x in self.get_indexd_docs(id_list)]
    
    
    def manifest(self, program, project, submissions):
        '''
        Generates a file manifest from a list of submissions
        by checking for the category in the JSON schema and
        getting the object from indexd as necessary.
        '''
        keys = [os.path.basename(x) for x in submissions.keys()]
        print('Checking which types have associated data files...')
        data_keys = [x[1] for x in filter(lambda x: x[0], zip(pmap(lambda x: self.is_type_data_category(program, project, x), keys), keys))]
        print('Found {} types with data files: '.format(len(data_keys)))
        print(', '.join(data_keys))
        print('Getting URL paths from indexd... (.=success, F=failure)')
        return functools.reduce(lambda x, y: x + y, pmap(lambda x: self.submission_manifest(submissions[x]), data_keys))
        
    
    def validate_output(self, output):
        jsonschema.validate(output, self.schema)
    
    def export(self, program, project):
        '''
        Exports a given program and project as a dictionary
        and returns that dictionary.
        '''
        print('Requesting metadata submissions.')
        submissions = self.get_all_submissions(program, project)
        print('Received all metadata submissions!')
        print('Generating file manifest, this may take some time...')
        manifest = self.manifest(program, project, submissions)
        # Some last minute QA
        pruned_manifest = list(filter(lambda x: x != {}, manifest))
        print('')
        if {} in manifest:
            print('       WARNING SOME FILES COULD NOT BE FOUND!!!!')
            print('There was a problem finding paths for some of the files.')
            print('This could be due to an error in loading the metadata.')
            print('Please contact the system administrator!')
        output = {'metadata': submissions, 'data_objects': pruned_manifest}
        self.validate_output(output)
        return output


def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
    program_name = os.path.basename(sys.argv[0])
    program_version = '{}'.format(__version__)
    program_build_date = str(__updated__)
    program_license = '''
    sheepdog-exporter {}
    

  Created by David Steinberg on {}.
  Copyright 2018 Genomics Institute. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
'''.format(program_version, str(__date__))

    try:
        print('''
                                       __  _
                                   .-.'  `; `-._  __  _
                                  (_,         .-:'  `; `-._
                                ,'o"(        (_,           )
                               (__,-'      ,'o"(            )>
                                  (       (__,-'            )
                                   `-'._.--._(             )
                                      |||  |||`-'._.--._.-'
                                                 |||  |||
            o                    o                                    o          
            |                    |                                    |          
        o-o O--o o-o o-o o-o   o-O o-o o--o     o-o \ / o-o  o-o o-o -o- o-o o-o 
         \  |  | |-' |-' |  | |  | | | |  |     |-'  o  |  | | | |    |  |-' |   
        o-o o  o o-o o-o O-o   o-o o-o o--O     o-o / \ O-o  o-o o    o  o-o o    {}
                         |                |             |                        
                         o             o--o             o    
                                             
                         Export DCP metadata from the CLI!!!
        '''.format(program_version))
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('program', nargs='?', type=str, help='The DCP Program to export. Leave blank to list programs.')
        parser.add_argument('project', nargs='?', type=str, help='The DCP Project to export. Leave blank to list projects.')
        parser.add_argument('--dcp-url', type=str, help='The URL of the DCP service (default: https://dcp.bionimbus.org', default='https://dcp.bionimbus.org')
        parser.add_argument('--credentials', type=str, help='The path to your DCP credentials.json (default: ./credentials.json)', default='./credentials.json')
        parser.add_argument('--output-path', type=str, help='The path to place the resulting export (default: ./)', default='./')
        
        
        # Process arguments
        args = parser.parse_args()

        exporter = Exporter(
            args.credentials,
            args.dcp_url)
        
        if not args.program:
            programs = exporter.get_programs()
            print('Programs available at {}:'.format(args.dcp_url))
            print('')
            print("     {}".format('\n     '.join(programs)))
            print('')
            print('Try entering `sheepdog-exporter {}` to list projects!'.format(programs[0]))
        
        elif args.program and not args.project:
            projects = exporter.get_projects(args.program)
            print('Projects for program {}:'.format(args.program))
            print('')
            print("     {}".format('\n     '.join(projects)))
            print('')
            print('Try entering `sheepdog-exporter {program} {project}` to output "{program}-{project}.json"!'.format(project=projects[0], program=args.program))
        elif args.program and args.project:
            print('Exporting {}-{} from {}'.format(args.program, args.project, args.dcp_url))
            try:
                exported = exporter.export(
                    args.program, args.project)
            except Exception as e:
                print('        Exporting failed!')
                print(str(e))
                return 1
            output_path = '{}/{}-{}.json'.format(
                args.output_path, args.program, args.project)
            try:
                outfile = open(output_path, 'w')
                json.dump(exported, outfile)
            except Exception as e:
                print('Failed to create output JSON, does the directory exist?')
                print(str(e))
                return 1
            
            print('''\n\n       Successfully exported metadata!
            
            ''')
            lengths = [len(exported['metadata'][k]) for k in exported['metadata'].keys()]
            keys = exported['metadata'].keys()
            content = filter(lambda x: x[1] > 0, zip(keys, lengths))
            pretty_content = "\n".join(['{} {}'.format(os.path.basename(x[0]).ljust(56), x[1]) for x in content])
            print(pretty_content)
            print('')
            print('{} paths have been written to the Data Object manifest!'.format(len(exported['data_objects'])))
            print('\nThe output has been written to {}!'.format(output_path))
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        print('\nReceived keyboard interrupt, exiting!')
        return 0
    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    sys.exit(main())