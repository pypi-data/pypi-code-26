# -*- coding: utf-8 -*-

# 선택한 항목의 세부사항을 보여주는 함수

import sqlite3
from Ace_todolist import search

def detail(searching=None):

    conn = sqlite3.connect("ace.db")
    cur = conn.cursor()

    detail_answer_list = ["y", "n"]

    col_list = ["id", "title", "category", "due", "priority","place", "comment", "finished"]

    # 세부사항을 보고 싶은 항목 찾기, answer: 원하는 항목을 찾았는 지 찾지 못했는 지 확인하는 변수
    answer = "n"
    while answer == "n":
        print("Searching item that you want to see details...")
        lists = search.search(searching)
        print("Did you find what you want to look for?")
        answer = input("(y: Yes, n: No) : ")

        while answer not in detail_answer_list:
            print("\nIncorrect type")
            print("Did you find what you want to look for?")
            answer = input("(y: Yes, n: No) : ")

        print()

    # 세부사항을 보고 싶은 항목의 id 선택하기
    if len(lists) != 1:
        detail_id = input("choose id of item that you want to see details: ")
    else:
        detail_id = lists[0][0]

    sql = "select * from todo where id=?"
    cur.execute(sql, (detail_id, ))

    row = cur.fetchone()

    print()

    # 항목 보여주기
    for i in range(0, len(col_list)):

        # 완료 미완료를 제대로 표시하기 위한 조건문
        if i == 7:
            if row[i] == 1 :
                print(col_list[i], ":", "finished")
            else :
                print(col_list[i], ":", "unfinished")
        else :
            # 입력한 사항이 없으면 none(없음) 출력하는 것
            if row[i] == " " :
                print(col_list[i], ":", "none(empty)")
            else :
                print(col_list[i], ":", row[i])

    print()

    cur.close()
    conn.close()
