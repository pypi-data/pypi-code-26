import random
from pizzashop.stories import storyList
from pizzashop.config import procpath

class Game:

	storyLength = len(storyList)

	def __init__(self, player, shop):
		self.playerName = player
		self.shopName = shop
		self.money = 10000
		self.employees = 0
		self.pizzaCount = 500
		self.dayCount = 0
		self.interest = 0
		self.maxCustomers = 0
		self.dailyNet = 0
		self.valid = True
		self.currentStory = ""
		
		with open(procpath + "/stories/story_1.txt") as intro:
			self.currentStory = intro.read()
		
	def createStory(self):
		index = random.randrange(Game.storyLength)
		
		set = storyList[index]["set"]
		amount = storyList[index]["amount"]
		file = storyList[index]["file"]
		
		if set == "money":
			self.money += amount
		elif set == "employees":
			self.employees += amount
			if self.employees < 0:
				self.employees = 0
		elif set == "pizzaCount":
			self.pizzaCount += amount
		elif set == "interest":
			self.interest += amount
			if self.interest < 0:
				self.interest = 0
		
		with open(procpath + file) as story:
			self.currentStory = story.read()
			
	def day(self):
		self.dayCount += 1
		sales = self.interest * (self.employees * 5) + 1
		actual = random.randrange(sales)
		self.maxCustomers = actual
		self.pizzaCount -= actual
		self.money -= self.employees * 250
		self.money += actual * 15
		self.dailyNet = (actual * 15) - self.employees * 250
		
		self.createStory()
		
		if self.interest > 0:
			self.interest -= 2
		
		if self.pizzaCount < 0 or self.money < 0:
			self.valid = False
			
	def info(self):
		print("Bank Account: $" + str(self.money))
		print("Shop: " + self.shopName)
		print("Employees: " + str(self.employees))
		print("Total Pizzas: " + str(self.pizzaCount))
		print("Day: " + str(self.dayCount))
		print("Publicity: " + str(self.interest))
		print("Max Customers: " + str(self.maxCustomers))
		print("Daily Net: $" + str(self.dailyNet))
			
	def getStory(self):
		print("\n")
		print(self.currentStory)
		
	def options(self):
		print("\n")
		print("'day' - Open shop for a day")
		print("'hire' - Cost: $100, Daily: $250, Add one employee")
		print("'fire' - Subtract one employee")
		print("'adv' - Cost: $100, Run one add to increase public interest")
		print("'piz' - Cost: $100, Add 100 pizzas")
		print("'quit' - To quit game")
		print("Sell Price: $15 per pizza")
		
	def hireFire(self, hire):
		if hire:
			self.money -= 100
			self.employees += 1
		else:
			self.employees -= 1
			
	def advertise(self):
		self.money -= 100
		self.interest += 1
		
	def pizzas(self):
		self.money -= 100
		self.pizzaCount += 100
	
	@staticmethod
	def displayPizza():
		with open(procpath + "\stories\pizza.txt") as pizza:
			print(pizza.read())