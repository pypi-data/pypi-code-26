# -*- coding: utf-8 -*-

# todo table에 존재하는 todo 항목을 검색하여 찾는 함수...

import sqlite3
from Ace_todolist import list_todo as printer

def search(option=None):
    conn = sqlite3.connect("ace.db")
    cur = conn.cursor()

    # 검색한 항목을 담은 list
    search_list = []
    search_answer_list = ["i", "d", "t", "c"]

    # 어떤 방법으로 찾고 싶은 지에 대한 input 함수 / 조건문
    if option is None:
        search_type = input("How do you want to search? (i: id, t: title, d: due, c: category) ")
        while search_type not in search_answer_list:
            print()
            print("Incorrect type")
            search_type = input("How do you want to search? (i: id, t: title, d: due, c: category) ")
    else:
        search_type = option

    if search_type == "i":
        search_id = input("what id: ")
        sql = "select * from todo where id=?"
        cur.execute(sql, (search_id, ))

        rows = cur.fetchall()
        for row in rows:
            search_list.append(row)

        printer.print_list(search_list)

    elif search_type == "t":
        search_title = input("what title: ")
        search_list = contain_thing(search_title, 1)
        printer.print_list(search_list)

    elif search_type == "d":
        search_due = input("what due: ")
        search_list = contain_thing(search_due, 3)
        printer.print_list(search_list)

    elif search_type == "c":
        search_category = input("what category: ")
        search_list = contain_thing(search_category, 2)
        printer.print_list(search_list)

    cur.close()
    conn.close()

    return search_list


# 검색하는 단어를 포함하는 항목 모두 찾기
def contain_thing(what_search, num_index):

    conn = sqlite3.connect("ace.db")
    cur = conn.cursor()

    # 검색하는 단어를 포함한 모든 항목 리스트
    contain_list = []

    # 존재하는 모든 항목에 대한 리스트
    all_list = []

    # 존재하는 모든 항목 담기
    sql = "select * from todo where 1"
    cur.execute(sql)

    rows = cur.fetchall()
    for row in rows:
        all_list.append(row)

    # 검색하는 단어를 포함하는 항목 모두 찾기
    for elem in all_list:
        if what_search in elem[num_index]:
            contain_list.append(elem)

    cur.close()
    conn.close()

    return contain_list
