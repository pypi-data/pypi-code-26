# -*- coding: utf-8 -*-

import sqlite3
from Ace_todolist import list_todo
from Ace_todolist import search
from Ace_todolist import input_check
from Ace_todolist import now_date

def edit_todo(searching, target):
    conn = sqlite3.connect("ace.db")
    cur = conn.cursor()

    loop = 'y'

    # 반복에 대해 yes라고 응답하면 반복
    while loop == 'y' or loop == 'Y':

        # 검색코드
        lists = search.search(searching)

        while len(lists) == 0:
            print("Nothing found! Please retry.")
            print()
            lists = search.search(searching)

        # 변경할 항목 선택
        if len(lists) != 1:
            target_id = input("Record id? ")
            while not target_id.isdigit():
                target_id = input("Record id? ")
        else:
            target_id = lists[0][0]

        column_list = ['title', 'due', 'due', 'fin', 'priority', 'category', 'place', 'comment']
        if target is None:
            select = input("\nWhat do you want to edit? \n\n Title => title"
                           "\n Due date => due \n Finished => fin"
                           "\n priority => priority \n category = > category"
                           "\n place = > place \n comment = > comment\n")

            while select not in column_list:
                print("Incorrect type")
                select = input("\nWhat do you want to edit?\n\n Title => title"
                               "\n Due date => due\n Finished => fin"
                               "\n priority => priority\n category = > category"
                               "\n place = > place\n comment = > comment\n")
        else:
            select = target

    # 변경내용 작성
        # 타이틀 변경
        if 'title' in select:
            sel_title = input("\nTitle?")
            cur.execute("update todo set title = ? where id =?", (sel_title, target_id))

        # 기한 변경
        elif 'due' in select:
            set_due = input("\nDue date? ")
            while not input_check.due_check(set_due):
                print("wrong input. type again.")
                print()
                set_due = input("Due date? (yyyy-mm-dd or mm-dd or dd)")
                print()
                if len(set_due) < 10:
                    set_due = now_date.convert_due(set_due)
            cur.execute("update todo set due = ? where id =?", (set_due, target_id))

        # 중요도 변경
        elif 'priority' in select:
            sel_priority = input("\nPriority? ")
            cur.execute("update todo set priority = ? where id =?", (sel_priority, target_id))
            while not input_check.priority_check(sel_priority):
                print("Wrong input")
                sel_priority = input("Priority ? (1 to 5) ")
            cur.execute("update todo set priority = ? where id =?", (sel_priority, target_id))

        # 완료/미완료 변경
        elif 'fin' in select:
            sel_finished = input("\nFinished (1: yes, 0: no)? ")
            cur.execute("update todo set finished = ? where id =?", (sel_finished, target_id))
            while not input_check.finished_check(sel_finished):
                print("Wrong input")
                sel_finished = input("\nFinished (1: yes, 0: no)? ")
                cur.execute("update todo set finished = ? where id =?", (sel_finished, target_id))

        # 카테고리 변경
        elif 'category' in select:
            sel_category = input("\nCategory? ")
            cur.execute("update todo set category = ? where id =?", (sel_category, target_id))

        # 장소 변경
        elif 'place' in select:
            sel_place = input("\nPlace? ")
            cur.execute("update todo set place = ? where id =?", (sel_place, target_id))

        # 세부사항 변경
        elif 'comment' in select:
            sel_comment = input("\nComment? ")
            cur.execute("update todo set comment = ? where id =?", (sel_comment, target_id))

        conn.commit()

        loop = input("\nanything else you want to edit? (yes: y no: n): ")

    # 변경된 리스트 출력
    list_todo.list_all()
    conn.close()
