# -*- coding: utf-8 -*-

from datetime import datetime

NOW = datetime.now()


# 현재 년도, 달, 날짜의 자릿 수가 부족할 시 0을 채워 주는 함수
def format_due(due, length):
    if len(due) != length:
        due = '0'*(length-len(due)) + due
    return due


# 현재 년도, 달, 날짜
CURRENT_DATE = format_due(str(NOW.day), 2)
CURRENT_MONTH = format_due(str(NOW.month), 2)
CURRENT_YEAR = format_due(str(NOW.year), 4)


# 생략된 년도 또는 달을 현재 년도와 달로 대체하여 yyyy-mm-dd 형태의 문자열로 반환
def convert_due(due):
    # 년도 생략 시
    if len(due) == 5:
        return str(CURRENT_YEAR) + "-" + due
    # 년도 및 달 생략 시
    else:
        return str(CURRENT_YEAR) + "-" + str(CURRENT_MONTH) + "-" + due


# 항목이 만료 되었는 지 판단하는 함수
def expired(due):
    # Due Date 문자열에서 년도, 달, 날짜 추출
    due_year = due[0:4]
    due_month = due[5:7]
    due_date = due[8:]

    # 년도, 달, 날짜 순으로 비교하여 만료되었으면 0을, 만료되지 않았으면 1을 반환
    if int(due_year) < int(CURRENT_YEAR):
        return 0
    elif int(due_year) > int(CURRENT_YEAR):
        return 1
    if int(due_month) < int(CURRENT_MONTH):
        return 0
    elif int(due_month) > int(CURRENT_MONTH):
        return 1
    if int(due_date) < int(CURRENT_DATE):
        return 0
    else:
        return 1
