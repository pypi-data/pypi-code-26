# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

NOW = datetime.now()

NOW = datetime.now()


def stat_todo():
    conn = sqlite3.connect("ace.db")
    cur = conn.cursor()
    category_list = ['']
    finished_number = 0
    yet_number = 0
    list_all_number = 0
    due_over_number = 0
    i = 0

    sql = "select * from todo where 1"
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()

    for row in rows:
        list_all_number = list_all_number + 1
        if row[2] not in category_list[i]:
            category_list.append(row[2])
        if row[7] == 1:
            finished_number = finished_number + 1
        else:
            yet_number = yet_number + 1
            if int(row[3][:4]) < int(NOW.year):
                due_over_number = due_over_number + 1
            else:
                if row[3][5] == '0':
                    if int(row[3][6]) < int(NOW.month):
                        due_over_number = due_over_number + 1
                else:
                    if int(row[3][5:7]) < int(NOW.month):
                        due_over_number = due_over_number + 1
                    else:
                        if int(row[3][8:10]) < int(NOW.day):
                            due_over_number = due_over_number + 1
                        else:
                            due_over_number = due_over_number
    category_number = len(category_list) - 1
    if list_all_number != 0:
        print("percentage of finished list : " + str(round((finished_number/list_all_number)*100, 2)) + "% ")
        print()
        print("percentage of unfinished list : " + str(round((yet_number/list_all_number)*100, 2)) + "% ")
        print()
    else:
        print("There is not any Todo added.")
        print()
    print("number of lists : " + str(list_all_number))
    print()
    print("number of categories : " + str(category_number))
    print()
    print("number of overdue lists : " + str(due_over_number))
    print()
