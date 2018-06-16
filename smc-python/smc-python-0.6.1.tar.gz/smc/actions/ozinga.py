import csv
from smc import session
from smc.elements.service import TCPService, UDPService
from smc.api.exceptions import CreateElementFailed

csv_filename = 'OzingaServices.csv'

if __name__ == '__main__':

    valid_protocols = ('TCP', 'UDP')
    
    session.login(url='http://172.18.1.26:8082', api_key='kKphtsbQKjjfHR7amodA0001', timeout=45)
    
    with open(csv_filename, 'rU') as csvfile:
        reader = csv.DictReader(csvfile, dialect="excel",
                                fieldnames=['Name', 'Protocol', 'Port Start', 'Port End'])
    
        for row in reader:
            protocol = row.get('Protocol')
            if protocol in valid_protocols:
                try:
                    if protocol == 'TCP':
                        svc = TCPService.create(
                            name=row.get('Name'),
                            min_dst_port=row.get('Port Start'),
                            max_dst_port=row.get('Port End', None),
                            comment='added by api')
                    elif protocol == 'UDP':
                        svc = UDPService.create(
                            name=row.get('Name'),
                            min_dst_port=row.get('Port Start'),
                            max_dst_port=row.get('Port End', None),
                            comment='added by api')
                    print("Successfully created service: %s, type: %s" % (svc.name, protocol))
                except CreateElementFailed as e:
                    print("Skipping element: %s" % e)
        
        print("Done.")
    session.logout()
    