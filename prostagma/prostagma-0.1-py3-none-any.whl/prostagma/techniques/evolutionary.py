from functools import reduce
from operator import add
import random

from prostagma.techniques.technique import SearchTechnique
from prostagma.performances.cross_validation import CrossValidation

class EvolutionaryStrategy(SearchTechnique):
	def __init__(self, parameters, model, 
			performance_validator=CrossValidation(), 
			retain=0.3, random_select=0.1, mutate_prob=0.2, 
			generations=10, population_size=20):
		super(EvolutionaryStrategy, self).__init__(parameters=parameters, 
			model=model, performance_validator=performance_validator)
		self.retain = retain
		self.random_select = random_select
		self.mutate_prob = mutate_prob
		self.generations = generations
		self.population_size = population_size

	def fit(self, X_train, y_train):
		"""
			The method calls the performance validator defined
			and uses it to compute the score for each set of parameters.
			
			@args
				X_train : ndarray -> features
				y_train : ndarray -> labels
			
			@return
				scores : dict/list with all the scores
					for each set of parameters
		"""

		# Create the Population
		population = self.create_population()

		# Train the Genetic Algorithm
		for i in range(self.generations):
			print("Generation {}" .format(i))

			for model in population:
				means, stdv = performance_validator.fit(X_train, y_train, model)

			if i < self.generations-1:
				s = self.evolve(population)
		return

	def create_population(self):
		"""
			The method creates the different networks (which are 
			the different models with different parameters).
			@args
				count : int -> number of elements that you want 
					in the population
			@return
				population list[KerasModel] 

		"""
		population = []
		for _ in range(0, self.population_size):
			parameters = self.set_random_parameters()
			population.append(self.model(parameters=parameters))
		return population

	def get_fitness(self, model):
		return model.accuracy

	def get_grade(self, population):
		""" The method returns the avg accuracy in the population 

			@args
				population : list[Model] 
			
			@return
				avg_score : float -> avg score of the population
				
		"""
		total = reduce(add, (self.get_fitness(network) for network in population))
		avg_score = float(total) / len(population)
		return avg_score

	def breed(self, mother, father):
		"""
			The method computes the crossover between two
			population.

			@args
				mother : list[Model]
				father : list[Model]
			
			@return
				children : list[Model]
		"""
		children = []
		for _ in range(2):
			child = {}
			for param in self.parameters:
				child[param] = random.choice([mother.network[param], father.network[param]])
			model = self.model()
			if self.mutate_chance > random.random():
				model = self.mutate(model)
			children.append(model)
		return children

	def mutate(self, model):
		mutation = random.choice(list(self.parameters.keys()))
		model.model[mutation] = random.choice(self.parameters[mutation])
		return model

	def evolve(self, pop):
		graded = [(self.get_fitness(model), model) for network in pop]
		graded = [x[1] for x in sorted(graded, key=lambda x: x[0], reverse=True)]
		retain_length = int(len(graded)*self.retain)

		parents = graded[:retain_length]

		for individual in graded[retain_length:]:
			if self.random_select > random.random():
				parents.append(individual)

		parents_length = len(parents)
		desired_length = len(pop) - parents_length
		children = []

		while len(children) < desired_length:
			male = random.randint(0, parents_length-1)
			female = random.randint(0, parents_length-1)

			if male != female:
				male = parents[male]
				female = parents[female]

				children_new = self.breed(male, female)

				for child_new in children_new:
					if len(children) < desired_length:
						children.append(child_new)

		parents.extend(children)
		return parents

	def get_population_accuracy(self, population):
		total_accuracy = 0
		for model in population:
			total_accuracy += network.get_accuracy

		avg_accuracy = total_accuracy / len(population)
		return avg_accuracy

	def set_random_parameters(self):
		"""
			The method should create a sample of parameters,
			given the parameters space

			@return
				parameters : dict -> dictionary with the parameters 
					to create a network. 
		"""
		raise NotImplementedError