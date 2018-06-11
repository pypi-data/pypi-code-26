import urllib.request
import json

class FeatureflagclientError404(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class FeatureflagclientErrorMalformedJson(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class Featureflagclient:

	features: {}

	source_url: ""

	def __init__(self, source_url=None, local_feature_flags=None):

		self.features = local_feature_flags or {}

		if (source_url):
			self.source_url = source_url

			try: 
				remote_feature_flag = json.loads(urllib.request.urlopen(source_url).read())
				for remote_feature in remote_feature_flag:
					if (remote_feature not in self.features):
						self.features[remote_feature] = remote_feature_flag[remote_feature]

			except urllib.error.HTTPError as e:
				raise FeatureflagclientError404("404 request not found for " + self.source_url)
			except json.decoder.JSONDecodeError as e:
				raise FeatureflagclientErrorMalformedJson("Invalid JSON found at " + self.source_url)


	def get(self, feature):
		if ( feature in self.features):
			return self.features[feature]
		else:
			return None