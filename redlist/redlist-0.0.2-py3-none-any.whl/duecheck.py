# -*- coding: utf-8 -*- 
def isdue(due):
	dateNtime = due.split(' ')
	if len(dateNtime) != 2:
		return False
	date = dateNtime[0].split('-')
	time = dateNtime[1].split(':')
	if len(dateNtime) != 2 or len(date) != 3 or len(time) != 3:
		return False
	if not istime(due):
		print("Can't input due Because due must not before current time")
		return False
	for key in date:
		if key.isdigit() == 0 :
			return False
	for key in time:
		if key.isdigit() == 0:
			return False
	return (1000<=int(date[0]) and int(date[0])<=9999) and (1<=int(date[1]) and int(date[1])<=12) and (1<=int(date[2]) and int(date[2])<=31) and (0<=int(time[0]) and int(time[0])<=24) and (0<=int(time[1]) and int(time[1])<=60) and (0<=int(time[2]) and int(time[2])<=60)

def istime(due):
    """False if time has passed, True if time has not passed"""
    import datetime
    dNt = due.split(' ')
    d = dNt[0].split('-')
    t = dNt[1].split(':')
    now = datetime.datetime.now()
    N_dNt = str(now).split(' ')
    N_d = N_dNt[0].split('-')
    N_t = N_dNt[1].split(':')
    if int(d[0])<int(N_d[0]):
        return False
    elif int(d[0])>int(N_d[0]):
        return True
    elif int(d[1])<int(N_d[1]):
        return False
    elif int(d[1])>int(N_d[1]):
        return True
    elif int(d[2])<int(N_d[2]):
        return False
    elif int(d[2])>int(N_d[2]):
        return True
    elif int(t[0])<int(N_t[0]):
        return False
    elif int(t[0])>int(N_t[0]):
        return True
    elif int(t[1])<int(N_t[1]):
        return False
    elif int(t[1])>int(N_t[1]):
        return True
    elif float(t[2])<=float(N_t[2]):
        return False
    else:
        return True
