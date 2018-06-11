# -*- coding: utf-8 -*-

from Ace_todolist import list_todo
from Ace_todolist import edit_todo
from Ace_todolist import create_db
from Ace_todolist import add_todo
from Ace_todolist import remove_todo
from Ace_todolist import stat_todo
from Ace_todolist import search
from Ace_todolist import detail
import argparse

UPWARD_OPTIONS = ["t", "c", "p", "d"]
DOWNWARD_OPTIONS = ["T", "C", "P", "D"]


# 정렬 함수 (option은 정렬 대상, status는 정렬 방식(오름차/내립차순), finished는 완료 여부에 따른 출력 방식을 결정)


# 프로그램 실행코드
def run_program():
    # 개행을 위한 print()
    print()
    parser = argparse.ArgumentParser()

    parser.add_argument("--add", help="add item", action="store_true")
    parser.add_argument("--list", choices=["a", "f"],
                        help= "print list of items(a: list of all items, f: split view of list based on completion)")
    parser.add_argument("--edit", choices=["title", "category", "due", "priority",
                                           "fin", "place", "comment"],
                                help="edit item based on title, category, ..., comment")
    parser.add_argument("--stat", help="statistics of items", action="store_true")
    parser.add_argument("--search", choices=["i", "t", "c", "d"],
                                    help="search item based on (i : ID, t: title, c : category, d: due)")
    parser.add_argument("--detail", help="print details of item", action="store_true")
    parser.add_argument("--remove", help="remove item", action="store_true")
    parser.add_argument("--version", action="version", version="version 1.0")
    parser.add_argument("--sort", choices=["t", "c", "p", "d", "T", "C", "P", "D"],
                                    help="option for sorting (t : title, c: category, p: priority, d: due)")

    args = parser.parse_args()

    if args.add:
        add_todo.add_todo()
    elif args.list:
        if args.list == "f":
            select2 = 1
            if args.sort in UPWARD_OPTIONS:
                status = list_todo.sort(UPWARD_OPTIONS.index(args.sort)+1, 0, select2)
            elif args.sort in DOWNWARD_OPTIONS:
                status = list_todo.sort(DOWNWARD_OPTIONS.index(args.sort)+1, 1, select2)
            else:
                list_todo.list_finished_unfinished()
        else:
            select2 = 0
            if args.sort in UPWARD_OPTIONS:
                status = list_todo.sort(UPWARD_OPTIONS.index(args.sort)+1, 0, select2)
            elif args.sort in DOWNWARD_OPTIONS:
                status = list_todo.sort(DOWNWARD_OPTIONS.index(args.sort)+1, 1, select2)
            else:
                list_todo.list_all()
        # 옵션 입력(기본값은 오름차순, 동일한 옵션을 입력할 시 차순 변경)
        while 1:
            option = input("Sort in other way or quit this section:\n"
                           "(t: title, c: category, p: priority, d: due, q: quit)? ")
            if option == 'q':
                break
            while option not in UPWARD_OPTIONS and option not in DOWNWARD_OPTIONS:
                print("Wrong input!\n")
                option = input("Sort in other way or quit this section:\n"
                               "(t: title, c: category, p: priority, d: due, q: quit)? ")
            if option in UPWARD_OPTIONS:
                option = UPWARD_OPTIONS.index(option) + 1
            elif option in DOWNWARD_OPTIONS:
                option = UPWARD_OPTIONS.index(option) + 1
            # 옵션에 따른 정렬 및 출력 함수
            status = list_todo.sort(int(option), status, select2)
    elif args.edit:
        target = args.edit
        if not args.search:
            searching = None
        else:
            searching = args.search
        edit_todo.edit_todo(searching, target)
    elif args.detail:
        if not args.search:
            detail.detail()
        else:
            detail.detail(args.search)
    elif args.remove:
        if not args.search:
            remove_todo.remove_todo()
        else:
            remove_todo.remove_todo(args.search)
    elif args.search:
        search.search(args.search)
    elif args.stat:
        stat_todo.stat_todo()
    else:
        print("Hello!, This is ACE TODO APPLICATION")
        print("If you want to run action of ACE, confirm options(-h or --help)")
        print()


if __name__ == "__main__":
    create_db.create_db()
    run_program()
