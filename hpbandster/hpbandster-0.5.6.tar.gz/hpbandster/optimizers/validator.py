import os
import time
import math
import copy
import logging

import numpy as np


import ConfigSpace as CS

from hpbandster.core.master import Master
from hpbandster.optimizers.iterations import SuccessiveHalving
from hpbandster.optimizers.config_generators.constant_config import ConstantConfig

class RandomSearch(Master):
	def __init__(self, config = None, num_evaluations = 1
					budget=1, **kwargs ):
		"""

		Parameters
		----------
		config: dict
			valid configuration
		num_evaluations : int
			number of independent evaluations of said configuration
		budget : float
			The budget to evaluate it on.
		"""
		if config is None:
			raise ValueError("You have to provide a valid configuration object")



		cg = ConstantConfig( config = config )

		super().__init__(config_generator=cg, **kwargs)

		self.budget = budget
		self.num_evaluations = num_evaluations
		
		
		self.config.update({
						'config'			: config,
						'budget' 			: budget,
						'num_evaluations'	: num_evalutaions,
					})


	def run(self, **kwargs):
		kwargs.update({'n_iterations': 1})
		
		super().run(**kwargs)

	def get_next_iteration(self, iteration, iteration_kwargs={}):
		"""
			Returns a SH iteration with only evaluations on the biggest budget
			
			Parameters:
			-----------
				iteration: int
					the index of the iteration to be instantiated

			Returns:
			--------
				SuccessiveHalving: the SuccessiveHalving iteration with the
					corresponding number of configurations
		"""
		
		
		budgets = [self.budget]
		ns = [self.num_evaluations]
		
		return(SuccessiveHalving(HPB_iter=iteration, num_configs=ns, budgets=budgets, config_sampler=self.config_generator.get_config, **iteration_kwargs))
