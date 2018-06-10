import os
from pizzashop.game import Game

globGame = 0

def initializeGame():
	os.system('cls')
	print("Welcome to Pizza Shop!\n")
	print("Please give some info...")
	Game.displayPizza()
	player = input("Player Name: ")
	shop = input("Pizza Shop Name: ")
	global globGame
	globGame = Game(player, shop)
	
def endGame():
	os.system('cls')
	print("You've either ran out of money or pizzas!")
	print("Play again? yes or no")
	cmd = input()
	if cmd == 'yes':
		initializeGame()
		return False
	else:
		return True
		
def main():
	
	initializeGame()
	
	while True:
		os.system('cls')
		globGame.info()
		globGame.getStory()
		globGame.options()
	
		cmd = input()
	
		if cmd == "day":
			globGame.day()
		elif cmd == "hire":
			globGame.hireFire(True)
		elif cmd == "fire":
			globGame.hireFire(False)
		elif cmd == "adv":
			globGame.advertise()
		elif cmd == "piz":
			globGame.pizzas()
		elif cmd == "quit":
			break
	
		if not globGame.valid:
			if endGame():
				break