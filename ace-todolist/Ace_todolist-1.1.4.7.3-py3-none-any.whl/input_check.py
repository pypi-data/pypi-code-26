# -*- coding: utf-8 -*-

from Ace_todolist import now_date

# Due의 입력에 대한 확인
def date_check(due):
    max_date = 31
    max_month = 12
    longer_months = [1, 3, 5, 7, 8, 10, 12]

    if len(due) < 10:
        due = now_date.convert_due(due)

    due_tokens = due.split("-")
    year = int(due_tokens[0])
    month = int(due_tokens[1])
    date = int(due_tokens[2])

    if month not in longer_months:
        max_date = 30
    if month == 2:
        max_date = 28
        if (year % 4 == 0 and year & 100 != 0) or year % 400 == 0:
            max_date = 29

    if month < 1 or month > max_month:
        return False
    if date < 1 or date > max_date:
        return False
    return True


def due_check(due):
    tokens_length = [1, 2, 2, 4]

    due += '-0'
    due_input_list = due.split("-")
    token_number = len(due_input_list)

    for token in due_input_list:
        if not token.isdigit():
            return False
    if token_number > 4 or token_number < 2:
        return False
    else:
        index = len(due_input_list) - 1
        for token in due_input_list:
            if len(token) != tokens_length[index]:
                return False
            index -= 1
    return True


# 우선순위 입력에 대한 확인
def priority_check(priority):
    if not priority.isdigit():
        return False
    if int(priority) >= 6 or int(priority) < 1:
        return False
    return True


# 완료 여부 입력에 대한 확인
def finished_check(finished):
    if not finished == '1' and not finished == '0':
        return False
    return True
