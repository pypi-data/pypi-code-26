# -*- coding: utf-8 -*-

import sqlite3
from Ace_todolist import now_date
from Ace_todolist import input_check

# 항목 추가 함수
def add_todo():
    conn = sqlite3.connect("ace.db")
    cur = conn.cursor()

    yn_list = ['y', 'Y', 'n', 'N']
    place_default = ' '
    comment_default = ' '

    title = input("Todo ? ")
    print()

    due = input("Due date? (yyyy-mm-dd or mm-dd or dd)")
    print()
    while not input_check.due_check(due) or not input_check.date_check(due):
        if not input_check.due_check(due):
            print("Wrong input. Type again.")
            print()
            due = input("Due date? (yyyy-mm-dd or mm-dd or dd)")
            print()
        elif not input_check.date_check(due):
            print("Invalid date or month. Type again.")
            print()
            due = input("Due date? (yyyy-mm-dd or mm-dd or dd)")
            print()
    # 년도 또는 달 생략 시 현재 년도와 달로 대체
    if len(due) < 10:
        due = now_date.convert_due(due)

    category = input("Category ? ")
    print()

    priority = input("Priority ? (1 to 5) ")
    print()
    while not input_check.priority_check(priority):
        print("Wrong input. Type again.")
        print()
        priority = input("Priority ? (1 to 5) ")
        print()

    edit_place = input("Want to add Place ? (y / n) ")
    print()
    while edit_place not in yn_list:
        print("Wrong input. Type again.")
        print()
        edit_place = input("Want to add Place ? (y / n) ")
        print()
    if (edit_place == 'y') or (edit_place == 'Y'):
        place = input("Place ? ")
        print()
    else:
        place = place_default

    edit_comment = input("Want to add Comment ? (y / n) ")
    print()
    while edit_comment not in yn_list:
        print("Wrong input. Type again.")
        print()
        edit_comment = input("Want to add Comment ? (y / n) ")
        print()
    if (edit_comment == 'y') or (edit_comment == 'Y'):
        comment = input("Comment ? ")
        print()
    else:
        comment = comment_default

    data = ((title, category, priority, due, place, comment), )
    sql = "insert into todo (title, category, priority, due, place, comment, finished) values (?, ?, ?, ?, ?, ?,0);"
    cur.executemany(sql, data)

    conn.commit()
    conn.close()
    # 개행을 위한 print()
