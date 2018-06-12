# -*- coding: utf-8 -*-

import sqlite3
from Ace_todolist import now_date

COLUMN = ["title", "category", "priority", "due"]
SORT = ["asc", "desc"]

# 각 행의 크기
WIDTH_ID = 4
WIDTH_TITLE = 61
WIDTH_CATEGORY = 16
WIDTH_PRIORITY = 10
WIDTH_DUE = 11
COLUMN_SIZE = [WIDTH_ID, WIDTH_TITLE, WIDTH_CATEGORY, WIDTH_DUE, WIDTH_PRIORITY]

# 각 행의 라벨
ID = "ID"
TITLE = "TITLE"
CATEGORY = "CATEGORY"
PRIORITY = "PRIORITY"
DUE = "DUE"
COLUMN_LABEL = [ID, TITLE, CATEGORY, DUE, PRIORITY]

# 각 행의 라벨 공백
SPACE_ID = int((WIDTH_ID - len(ID)) / 2)
SPACE_TITLE = int((WIDTH_TITLE - len(TITLE)) / 2)
SPACE_CATEGORY = int((WIDTH_CATEGORY - len(CATEGORY)) / 2)
SPACE_PRIORITY = int((WIDTH_PRIORITY - len(PRIORITY)) / 2)
SPACE_DUE = int((WIDTH_DUE - len(DUE)) / 2)
SPACE_COLUMN = [SPACE_ID, SPACE_TITLE, SPACE_CATEGORY, SPACE_DUE, SPACE_PRIORITY]

# 문자열 색 코드
BLACK = "\x1b[30m"
WHITE = "\x1b[37m"
RED = "\x1b[31m"
BLUE = "\x1b[34m"
YELLOW = "\x1b[33m"
MAGENTA = "\x1b[35m"
RESET = "\x1b[0m"


# 입력 받은 리스트를 콘솔에 출력
def print_list(rows):

    # 개행을 위한 print()
    print()
    # 표의 각 행 라벨 검은 색으로 출력
    print(label_string(BLACK))
    # 이중 가로 선 출력
    print(line_string("="))
    count = 0
    # 각 항목 출력
    for row in rows:
        due = str(row[3])
        fin = row[-1]
        # 매 다섯 번 째 열 마다 가로 선 출력
        if count == 5:
            print(line_string())
            count = 0
        # 만료되지 않은 항목 중 완료하지 않은 항목 노란색으로 출력
        if fin == 0 and now_date.expired(due):
            print(todo_string(YELLOW, row))
            count += 1
        # 완료하지 않은 상태로 만료된 항목 빨간 색으로 출력
        elif fin == 0:
            print(todo_string(RED, row))
            count += 1
        # 완료한 항목 파란 색으로 출력
        else:
            print(todo_string(BLUE, row))
            count += 1
    # 개행을 위한 print
    print()


# 전체 TODO 리스트 출력
def list_all(where=" ", data="ace.db"):
    conn = sqlite3.connect(data)
    cur = conn.cursor()

    # 기본 옵션
    if where == " ":
        sql = "select * from todo where 1"
        rows_fin = []
    # 남은 Due Date 기준 정렬
    elif where == 'due asc' or where == 'due desc':
        sql = "select * from todo where finished = 0 order by " + where
        sql2 = "select * from todo where finished = 1 order by " + where
        cur.execute(sql2)
        rows_fin = cur.fetchall()
    # 기타 옵션
    else:
        sql = "select * from todo order by " + where
        rows_fin = []
    cur.execute(sql)

    rows = cur.fetchall()
    for row in rows_fin:
        rows.append(row)
    conn.close()

    print_list(rows)
    print("(※ RED: Expired, BLUE: Finished, YELLOW : Unfinished)")
    print('\n')


# 완료/미완료 TODO 리스트 구분지어 출력
def list_finished_unfinished(where=" ", data="ace.db"):
    conn = sqlite3.connect(data)
    cur = conn.cursor()

    # 기본 옵션
    if where == " ":
        sql_finished = "select * from todo where finished = 0"
        sql_unfinished = "select * from todo where finished = 1"
    # 정렬 옵션
    else:
        sql_finished = "select * from todo where finished = 0 order by " + where
        sql_unfinished = "select * from todo where finished = 1 order by " + where
    cur.execute(sql_finished)

    rows_finished = cur.fetchall()

    cur.execute(sql_unfinished)
    rows_unfinished = cur.fetchall()

    print()
    # 미완료 항목 출력
    print("****Undone Todo List****")
    print_list(rows_finished)

    print()
    # 완료 항목 출력
    print("****Done Todo List****")
    print_list(rows_unfinished)
    print("(※ RED: Expired, BLUE: Finished, YELLOW : Unfinished)")
    print('\n')


# 각 항목에 대한 문자열 생성
def todo_string(color, row, line=WHITE):
    i = 0
    string = ""
    while i < len(COLUMN_SIZE):
        if i != 4:
            element = str(row[i])
        else:
            element = str(star(row[i]))
        string += color + element + " " * (COLUMN_SIZE[i] - len(element))
        if i < len(COLUMN_SIZE) - 1:
            string += line + "|"
        else:
            string += RESET
        i += 1
    return string


# 구분 선에 대한 문자열 생성
def line_string(shape="-", color=WHITE):
    string = color
    for size in COLUMN_SIZE:
        string += shape * size
        if size != COLUMN_SIZE[-1]:
            string += "+"
        else:
            string += RESET
    return string


# 라벨에 대한 문자열 생성
def label_string(color, line=WHITE):
    string = ""
    i = 0
    while i < len(COLUMN_LABEL):
        string += "\x1b[1m" + color + " " * SPACE_COLUMN[i] + COLUMN_LABEL[i] + " " * SPACE_COLUMN[i]
        if i < len(COLUMN_LABEL) - 1:
            string += RESET + line + "|"
        else:
            string += RESET
        i += 1
    return string


def star(number, star1="☆", star2="★"):
    return star2 * number + star1 * (5 - number)


def sort(option, status, finished):
    if finished == 0:
        if option == status:
            list_all(COLUMN[option-1] + " " + SORT[1])
            return 0
        else:
            list_all(COLUMN[option-1] + " " + SORT[0])
            return option
    else:
        if option == status:
            list_finished_unfinished(COLUMN[option-1] + " " + SORT[1])
            return 0
        else:
            list_finished_unfinished(COLUMN[option-1] + " " + SORT[0])
            return option
