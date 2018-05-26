from nssm.service import Service, ServiceConfiguration
from nssm.exceptions import *

config = ServiceConfiguration(
    arguments=r"C:\Users\ldelgado\projects\MATS\webgui\pynssm\tests\dummy.py",
    startup_dir=r"C:\MoCA\dummy",
    display_name="Test Service",
    description="This is a demo service",
    stdout=r"C:\MoCA\dummy\test_service_stdout.log",
    stderr=r"C:\MoCA\dummy\test_service_stderr.log"
)

service = Service("test_service",
                  r"C:\Users\ldelgado\Envs\nssm\Scripts\python.exe")

try:
    service.remove()
except ServiceRemoveException as err:
    print err.message

# try:
#     service.install()
# except ServiceInstallException:
#     print err.message
#
# service.configure(config)
# service.start()
# print service.status()
# service.stop()
# print service.status()
