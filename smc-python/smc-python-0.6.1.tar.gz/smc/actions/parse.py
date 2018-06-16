'''
Created on May 8, 2018

@author: davidlepage
'''
import csv
from smc import session
from smc.elements.network import URLListApplication

csv_filename = '/Users/davidlepage/Downloads/ODOT.csv'

if __name__ == '__main__':

    valid_protocols = ('TCP', 'UDP')
    
    session.login(url='https://172.18.1.151:8082', login='dlepage3', pwd='1970keegan', verify=False)
    for u in URLListApplication.objects.all():
        if not u.system:
            u.delete()
        
    with open(csv_filename, 'rU') as csvfile:
        reader = csv.DictReader(csvfile, dialect="excel",
                                fieldnames=['url', 'category'])
        url_list_application = {}
        for row in reader:
            if row['url'].endswith(';') or row['url'].endswith('?') or row['url'].endswith('*'):
                print("This row endswith ; %s" % row['url'])
                row['url'] = row['url'][:-1]
            url_list_application.setdefault(row['category'], []).append(
                row['url'])
#         
        from pprint import pprint
        pprint(url_list_application)
        for list_name, list_values in url_list_application.items():
            print("Adding list: %s...." % list_name)
            URLListApplication.create(name=list_name,
                url_entry=list_values)
        
                