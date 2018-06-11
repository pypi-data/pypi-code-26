def due_check(due):
	due_input_list = due.split("-")

	if(len(due_input_list) != 3):
		return False
	else :
		if(len(due_input_list[0]) != 4 or (due_input_list[0].isdigit() == False)):
			return False
		elif(len(due_input_list[1]) != 2 or (due_input_list[1].isdigit() == False)):
			return False
		elif(len(due_input_list[2]) != 2 or (due_input_list[1].isdigit() == False)):
			return False

	return True 
