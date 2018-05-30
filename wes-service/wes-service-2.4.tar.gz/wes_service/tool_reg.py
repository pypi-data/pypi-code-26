from bravado.client import SwaggerClient
import bravado.exception
import urllib

client = SwaggerClient.from_url("https://dockstore.org:8443/swagger.json",
                                config={'use_models': False, 'validate_responses': False})

r = client.GA4GH.toolsGet(limit=1).result()

tool = r[0]

kwargs={'id': urllib.quote(tool["id"], ""),
        'version-id': urllib.quote(tool["versions"][0]["name"], ""),
        'type': "CWL"}
cwl = client.GA4GH.toolsIdVersionsVersionIdTypeDescriptorGet(**kwargs).result()
print cwl["descriptor"]
