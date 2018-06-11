import os
from pizzashop.game import Game

def initializeGame():
	os.system('cls')
	print("Welcome to Pizza Shop!\n")
	print("Please give some info...")
	Game.displayPizza()
	player = input("Player Name: ")
	shop = input("Pizza Shop Name: ")
	
	return { "player": player, "shop": shop }
	
def endGame():
	os.system('cls')
	print("You've either ran out of money or pizzas!")
	print("Play again? yes or no")
	cmd = input()
	if cmd == 'yes':
		return False
	else:
		return True
		
def main():
	
	startInfo = initializeGame()
	gamePlay = Game(startInfo["player"], startInfo["shop"])
	
	while True:
		os.system('cls')
		gamePlay.info()
		gamePlay.getStory()
		gamePlay.options()
	
		cmd = input()
	
		if cmd == "day":
			gamePlay.day()
		elif cmd == "hire":
			gamePlay.hireFire(True)
		elif cmd == "fire":
			gamePlay.hireFire(False)
		elif cmd == "adv":
			gamePlay.advertise()
		elif cmd == "piz":
			gamePlay.pizzas()
		elif cmd == "quit":
			break
	
		if not gamePlay.valid:
			if endGame():
				break
			else:
				main()
				break