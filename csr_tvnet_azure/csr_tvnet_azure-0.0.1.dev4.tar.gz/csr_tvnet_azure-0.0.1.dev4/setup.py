from distutils.core import setup
project_name = 'csr_tvnet_azure'
project_ver = '0.0.1.dev4'
setup(
    name=project_name,
    packages=[],
    version=project_ver,
    description='Wrapper pypi package to install csr_tvnet and csr_azure_utils pypi packages',
    author='Saravanakumar Periyaswamy',
    author_email='sarperiy@cisco.com',
    # use the URL to the github repo
    url='https://github4-chn.cisco.com/csr1000v-azure/' + project_name,
    download_url='https://github4-chn.cisco.com/csr1000v-azure/' + project_name + '/archive/' + \
        project_ver + '.tar.gz',
    keywords=['cisco', 'azure', 'guestshell', 'csr1000v'],
    classifiers=[],
    license="MIT",
    install_requires=[
        'azure-storage-file==1.1.0',
        'csr_azure_utils>=0.0.11.dev',
        'csr_tvnet>=0.0.1.dev-25',
        'paramiko'
    ]
)
