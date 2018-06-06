from hpbandster.core.base_config_generator import base_config_generator




class ConstantConfig(base_config_generator):
	"""
		class used for validation
	"""

	def __init__(self, config, **kwargs):
		"""

		Parameters:
		-----------

		config: dict
			The configuration that will be validated
		**kwargs:
			see  hyperband.config_generators.base.base_config_generator for additional arguments
		"""

		super().__init__(**kwargs)
		self.config= configs


	def get_config(self, budget):
		return(self.config, {})
