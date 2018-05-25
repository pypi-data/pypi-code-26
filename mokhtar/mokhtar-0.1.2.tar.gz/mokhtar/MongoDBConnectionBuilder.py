from botocore.exceptions import ClientError
import json
import warnings

class MongoDBConnectionBuilder:

    @staticmethod
    def buildConnection(secretKeeperClient, secretId, versionId=None, versionStage=None, compatabilityLevel='3.6'):
        warnings.warn('buildConneciton is deprecated - use build_connection instead. This method will be removed in the next major release.', category=DeprecationWarning, stacklevel=2)
        return MongoDBConnectionBuilder.build_connection(secretKeeperClient, secretId, versionId, versionStage, compatabilityLevel)

    @staticmethod
    def build_connection(secretKeeperClient, secretId, versionId=None, versionStage=None, compatabilityLevel='3.6'):

        if compatabilityLevel != '3.6':
            raise ValueError('Currently, only \'3.6\' is supported for the value of compatabilityLevel')

        if versionId is not None:
            getSecretValueResponse = secretKeeperClient.get_secret_value(
                SecretId=secretId,
                VersionId=versionId
            )
        elif versionStage is not None:
            getSecretValueResponse = secretKeeperClient.get_secret_value(
                SecretId=secretId,
                VersionStage=versionStage
            )
        else:
            getSecretValueResponse = secretKeeperClient.get_secret_value(
                SecretId=secretId
            )

        secret = getSecretValueResponse['SecretString']
        
        secretDict = json.loads(str(secret))

        return 'mongodb+srv://{0}:{1}@{2}'.format(
            secretDict['username'],
            secretDict['password'],
            secretDict['host']
        )
