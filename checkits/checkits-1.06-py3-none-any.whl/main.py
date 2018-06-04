import sqlite3
import function
from colorama import init, Fore, Style

init(convert=True)

is_login = 0
current_id = 0
data = []
todo_data = []

def mainmenu_pre_login():
    create_login_db()

    while True:
        print(Fore.CYAN + """
          ***   *                    *         *   *  *
         *   *  *                    *         *   *  *
        *       ****    ***    ***   *  *      *  *** *
        *       *   *  *   *  *   *  * *       *   *  *
        *       *   *  *****  *      **        *   *  *
        *       *   *  *      *      **        *   *  *
         *   *  *   *  *   *  *   *  * *       *   *   
          ***   *   *   ***    ***   *  *      *   ** *
        """ + Style.RESET_ALL + "https://github.com/OSS-A-1/SQLiteDB\n")

        print("[0] 로그인")
        print("[1] 가입")
        print("[2] 종료")
        cho = input(">> ")

        while (not cho.isdigit()) or (cho.isdigit() and not (0 <= int(cho) <= 2)):
            print(Fore.RED + "\n0 ~ 2 사이의 숫자만을 입력해야 합니다." + Style.RESET_ALL)
            cho = input(">> ")

        cho = int(cho)
        print()

        if cho == 0:
            login()
        elif cho == 1:
            register()
        elif cho == 2:
            return
        if is_login == 1:
            mainmenu_aft_login()
            return

def mainmenu_aft_login():
    while True:
        print("\n메인메뉴\n")
        print("[0] 할일 보기")
        print("[1] 할일 추가")
        print("[2] 할일 관리")
        print("[3] 카테고리 관리")
        print("[4] 사용자 정보 보기")
        print("[5] 프로그램 정보 보기")
        print("[6] 종료")
        cho = input(">> ")

        while (not cho.isdigit()) or (cho.isdigit() and not (0 <= int(cho) <= 6)):
            print(Fore.RED + "\n0 ~ 7 사이의 숫자만을 입력해야 합니다." + Style.RESET_ALL)
            cho = input(">> ")

        cho = int(cho)
        print()

        if cho == 0:
            if cho == 0:
                while True:
                    print("[0] 전체 보기")
                    print("[1] 카테고리 별로 보기")
                    print("[2] 완료되지 않은 할일 보기")
                    print("[3] 완료된 할일 보기")
                    print("[4] 중요한 할일 보기")
                    print("[5] 취소")
                    cho = input(">> ")

                    while (not cho.isdigit()) or (cho.isdigit() and not (0 <= int(cho) <= 5)):
                        print(Fore.RED + "\n0 ~ 5 사이의 숫자만을 입력해야 합니다." + Style.RESET_ALL)
                        cho = input(">> ")

                    cho = int(cho)

                    if cho == 0:
                        filter_todo('0')
                    elif cho == 1:
                        filter_todo('1')
                    elif cho == 2:
                        filter_todo('2')
                    elif cho == 3:
                        filter_todo('3')
                    elif cho == 4:
                        filter_todo('4')
                    elif cho == 5:
                        break
        elif cho == 1:
            add_todo()
        elif cho == 2:
            while True:
                print("[0] 할일 수정")
                print("[1] 할일 제거")
                print("[2] 취소")
                cho = input(">> ")

                while (not cho.isdigit()) or (cho.isdigit() and not (0 <= int(cho) <= 2)):
                    print(Fore.RED + "\n0 ~ 2 사이의 숫자만을 입력해야 합니다." + Style.RESET_ALL)
                    cho = input(">> ")

                cho = int(cho)
                print()

                if cho == 0:
                    modify_todo()
                elif cho == 1:
                    delete_todo()
                elif cho == 2:
                    break
        elif cho == 3:
            man_category()
            return
        elif cho == 4:
            user_info()
            return
        elif cho == 5:
            program_info()
        elif cho == 6:
            return

def logout():
    global current_id, is_login
    is_login = 0
    current_id = 0
    print(1)
    mainmenu_pre_login()

def user_info():
    while True:
        print("사용자 정보")
        print("현재 사용자 : {0}".format(data[1]))
        print("[0] 로그아웃")
        print("[1] 비밀번호 변경")
        print("[2] 취소")
        cho = input(">> ")

        while (not cho.isdigit()) or (cho.isdigit() and not (0 <= int(cho) <= 2)):
            print(Fore.RED + "\n0 ~ 2 사이의 숫자만을 입력해야 합니다." + Style.RESET_ALL)
            cho = input(">> ")

        cho = int(cho)

        if cho == 0:
            logout()
            return
        elif cho == 1:
            change_pw()
        elif cho == 2:
            mainmenu_aft_login()
            return

def change_pw():
    conn = sqlite3.connect("user_data.db")
    cur = conn.cursor()

    sql = "select * from user_data where 1"
    cur.execute(sql)

    print("\n비밀번호 변경")
    print("[0] 취소\n")

    while True:
        print("현재 비밀번호 입력")
        pw = input("PW >> ")

        if pw == '0':
            conn.close()
            return

        if data[2] == pw:
            break
        else:
            print(Fore.RED + "\n비밀번호를 다시 확인해 주세요\n")
            print("비밀번호가 잘못 입력되었습니다.\n" + Style.RESET_ALL)
            continue

    print("\n변경할 비밀번호 입력")
    ch_pw = input("PW >> ")

    if ch_pw == '0':
        conn.close()
        return

    while not (4 <= len(ch_pw) <= 20):
        print(Fore.RED + "\n4 ~ 20 자 사이로 입력해 주십시오." + Style.RESET_ALL)
        ch_pw = input("PW >> ")

    print("\n비밀번호 확인")
    con_pw = input("PW >> ")

    if con_pw == '0':
        conn.close()
        return

    while ch_pw != con_pw:
        print(Fore.RED + "\n비밀번호를 잘못 입력하셨습니다." + Style.RESET_ALL)
        con_pw = input("PW >> ")

    cur.execute("UPDATE user_data SET pw = ? WHERE id = ? ",
                (ch_pw, current_id))
    conn.commit()

    print()

    conn.close()

def program_info():
    print("프로그램 이름 : Check It!")
    print("깃 허브 주소 : https://github.com/OSS-A-1/SQLiteDB")

def list_user():
    conn = sqlite3.connect("user_data.db")
    cur = conn.cursor()

    sql = "select * from user_data where 1"
    cur.execute(sql)

    rows = cur.fetchall()

    print()
    for row in rows:
        list(row)
        for val in row:
            print(val, end=" ")
        print()
    print()

    conn.close()

def login():
    conn = sqlite3.connect("user_data.db")
    cur = conn.cursor()

    sql = "select * from user_data where 1"
    cur.execute(sql)

    rows = cur.fetchall()

    global data

    cor_id = 0
    data = []

    print("로그인"
          "\n[0] 로그인 취소\n")

    while True:
        id = input("ID >> ")

        if id == '0':
            conn.close()
            return

        for row in rows:
            list(row)
            if row[1] == id:
                data = row
                cor_id = 1
                break

        if cor_id == 0:
            print(Fore.RED + "아이디를 다시 확인하세요.\n"
                  "아이디를 잘못 입력하셨거나 등록되지 않은 아이디 입니다.\n" + Style.RESET_ALL)
            continue
        elif cor_id == 1:
            break

    while True:
        pw = input("PW >> ")

        if pw == '0':
            conn.close()
            return

        if data[2] == pw:
            print("\n로그인 성공")
            global is_login, current_id
            current_id = id
            create_user_db(current_id)
            create_category_db(current_id, 0)
            is_login = 1
            conn.close()
            return
        else:
            print(Fore.RED + "비밀번호를 다시 확인하세요.\n"
                  "비밀번호를 잘못 입력하셨습니다.\n" + Style.RESET_ALL)
            continue

def register():
    conn = sqlite3.connect("user_data.db")
    cur = conn.cursor()

    sql = "select * from user_data where 1"
    cur.execute(sql)

    rows = cur.fetchall()

    cor_id = 0

    print("가입"
          "\n[0] 가입 취소\n")

    while True:
        val_id = input("ID >> ")

        if val_id == '0':
            conn.close()
            return

        while not (4 <= len(val_id) <= 20):
            print(Fore.RED + "\n4 ~ 20 자 사이로 입력해 주십시오." + Style.RESET_ALL)
            val_id = input("ID >> ")

        for row in rows:
            list(row)
            if row[1] == val_id:
                cor_id = 1
                break

        if cor_id == 1:
            print(Fore.RED + "이미 존재하는 아이디 입니다.\n"
                  "다시 입력해 주십시오.\n" + Style.RESET_ALL)
            cor_id = 0
            continue
        elif cor_id == 0:
            break

    val_pw = input("PW >> ")

    if val_pw == '0':
        conn.close()
        return

    while not (4 <= len(val_pw) <= 20):
        print(Fore.RED + "\n4 ~ 20 자 사이로 입력해 주십시오." + Style.RESET_ALL)
        val_pw = input("ID >> ")

    print("비밀번호 확인")
    con_pw = input("PW >> ")

    if con_pw == '0':
        conn.close()
        return

    while val_pw != con_pw:
        print(Fore.RED + "비밀번호를 잘못 입력하셨습니다.\n" + Style.RESET_ALL)
        con_pw = input("PW >> ")

    cur.execute("insert into user_data (id, pw) values (?, ?)",
                (val_id, val_pw))
    conn.commit()

    print("가입 성공!")
    create_user_db(val_id)
    create_category_db(val_id, 1)

    conn.close()

def create_login_db():
    conn = sqlite3.connect("user_data.db")
    cur = conn.cursor()

    table_create_sql = """create table if not exists user_data (
                                num integer primary key autoincrement,
                                id text not null,
                                pw text not null);"""

    cur.execute(table_create_sql)

    cur.close()


def create_category_db(user_id, first):

    conn = sqlite3.connect("{0}_category.db".format(user_id))
    cur = conn.cursor()

    table_create_sql = """Create table IF Not exists cate (
                id integer primary key autoincrement,
                category text not null);"""
    cur.execute(table_create_sql)

    sql = "select * from cate where 1"
    cur.execute(sql)

    if first == 1:
        default_category = ["개인", "일", "쇼핑"]

        for val_category in default_category:
            cur.execute("insert into cate (category) "
                        "values (?)",
                        (val_category,))
            conn.commit()

    conn.close()

def create_user_db(user_id):
    conn = sqlite3.connect("{0}.db".format(user_id))
    cur = conn.cursor()

    table_create_sql = """Create table IF Not exists todo (
                id integer primary key autoincrement,
                importance integer,
                finished integer,
                due date not null,
                category_num integer,
                what text not null);"""
    cur.execute(table_create_sql)

    conn.close()

def man_category():
    while True:
        print("카테고리 관리\n")
        print("[0] 카테고리 보기")
        print("[1] 카테고리 추가")
        print("[2] 카테고리 수정")
        print("[3] 카테고리 제거")
        print("[4] 취소")
        cho = input(">> ")

        while (not cho.isdigit()) or (cho.isdigit() and not (0 <= int(cho) <= 7)):
            print(Fore.RED + "\n0 ~ 3 사이의 숫자만을 입력해야 합니다." + Style.RESET_ALL)
            cho = input(">> ")

        cho = int(cho)

        if cho == 0:
            list_category()
        elif cho == 1:
            add_category()
        elif cho == 2:
            print("카테고리 수정-미구현")
        elif cho == 3:
            print("카테고리 제거-미구현")
        elif cho == 4:
            mainmenu_aft_login()
            return

def list_category():
    conn = sqlite3.connect("{0}_category.db".format(current_id))
    cur = conn.cursor()

    data = []

    sql = "select * from cate where 1"
    cur.execute(sql)

    rows = cur.fetchall()

    print("\nID  CATEGORY  \n"
          "---------------")
    for row in rows:
        data.append(row)

    for row in data:
        print("{0:<4}{1:<10}"
              .format(row[0], row[1]))

    print()
    cur.close()


def add_category():
    conn = sqlite3.connect("{0}_category.db".format(current_id))
    cur = conn.cursor()

    val_cate = input("\n추가할 카테고리 입력 : ")

    while not(0 < len(val_cate) < 21):
        print(Fore.RED + "\n1 ~ 20자 이내로 입력해야 합니다." + Style.RESET_ALL)
        val_cate = input("추가할 카테고리 입력 : ")

    cur.execute("insert into cate (category) values (?)",
                (val_cate,))
    conn.commit()

    print()

    conn.close()

def add_todo():
    conn = sqlite3.connect("{0}.db".format(current_id))
    conn2 = sqlite3.connect("{0}_category.db".format(current_id))
    cur = conn.cursor()
    cur2 = conn2.cursor()

    val_what = input("할일 입력 : ")
    val_due = input("기한 입력 : ")
    sql = "select * from cate where 1"
    cur2.execute(sql)

    rows = cur2.fetchall()

    for no in range(0, len(rows)):
        print("[{0}] {1}".format(rows[no][0], rows[no][1]))

    val_category_num = input("카테고리 선택 : ")

    while (not val_category_num.isdigit()) \
            or (val_category_num.isdigit() and not (1 <= int(val_category_num) <= len(rows))):
        print(Fore.RED + "\n1 ~ {0} 사이의 숫자만을 입력해야 합니다.".format(len(rows)) + Style.RESET_ALL)
        val_category_num = input(">> ")

    val_important = input("중요도\n"
                          "[0] 중요\n"
                          "[1] 보통\n"
                          ">> ")

    while (not val_important.isdigit()) or (val_important.isdigit() and not (0 <= int(val_important) <= 1)):
        print(Fore.RED + "\n0 ~ 1 사이의 숫자만을 입력해야 합니다." + Style.RESET_ALL)
        val_important = input(">> ")

    cur.execute("insert into todo (importance, finished, due, category_num, what) values (?, 0, ?, ?, ?)",
                (val_important, val_due, val_category_num, val_what))
    conn.commit()

    conn.close()
    conn2.close()

def list_todo(data):
    print("ID  IMPORTANCE FINISHED DATE                 CATEGORY    TODO      \n"
          "-------------------------------------------------------------------")
    for val in data:
        print("{0:<4}{1:<10}{2:<8}{3:<21}{4:<12}{5:<10}"
              .format(val[0], val[1], val[2], val[3], val[4], val[5]))
    print()


def filter_todo(filter):
    conn = sqlite3.connect("{0}.db".format(current_id))
    conn2 = sqlite3.connect("{0}_category.db".format(current_id))
    cur = conn.cursor()
    cur2 = conn2.cursor()

    sql = "select * from todo where 1"
    cur.execute(sql)
    sql2 = "select * from cate where 1"
    cur2.execute(sql2)

    rows = cur.fetchall()
    rows2 = cur2.fetchall()

    data = []
    val_data = []
    category = '_'

    if filter == '0':
        for row in rows:
            if row[1] == '0':
                importance = "★"
            else:
                importance = "☆"
            if row[2] == '1':
                finished = "○"
            else:
                finished = "×"
            for row2 in rows2:
                if row[4] == row2[0]:
                    category = row2[1]
            data.append([row[0], importance, finished, row[3], category, row[5]])
    elif filter == '1':
        print()
        for no in range(0, len(rows2)):
            print("[{0}] {1}".format(rows2[no][0], rows2[no][1]))

        category_num = input("카테고리 선택 : ")

        while (not category_num.isdigit()) \
                or (category_num.isdigit() and not (1 <= int(category_num) <= len(rows2))):
            print(Fore.RED + "\n1 ~ {0} 사이의 숫자만을 입력해야 합니다.".format(len(rows2)) + Style.RESET_ALL)
            category_num = input(">> ")

        category_num = int(category_num)

        for row in rows:
            if category_num == row[4]:
                val_data.append(row)

        for row in val_data:
            if row[1] == '0':
                importance = "★"
            else:
                importance = "☆"
            if row[2] == '1':
                finished = "○"
            else:
                finished = "×"
            for row2 in rows2:
                if row[4] == row2[0]:
                    category = row2[1]
            data.append([row[0], importance, finished, row[3], category, row[5]])
    elif filter == '2':
        for row in rows:
            if row[2] == '0':
                val_data.append(row)

        for row in val_data:
            if row[1] == '0':
                importance = "★"
            else:
                importance = "☆"
            if row[2] == '1':
                finished = "○"
            else:
                finished = "×"
            for row2 in rows2:
                if row[4] == row2[0]:
                    category = row2[1]
            data.append([row[0], importance, finished, row[3], category, row[5]])
    elif filter == '3':
        for row in rows:
            if row[2] == '1':
                val_data.append(row)

        for row in val_data:
            if row[1] == '0':
                importance = "★"
            else:
                importance = "☆"
            if row[2] == '1':
                finished = "○"
            else:
                finished = "×"
            for row2 in rows2:
                if row[4] == row2[0]:
                    category = row2[1]
            data.append([row[0], importance, finished, row[3], category, row[5]])
    elif filter == '4':
        for row in rows:
            if row[1] == '0':
                val_data.append(row)

        for row in val_data:
            if row[1] == '0':
                importance = "★"
            else:
                importance = "☆"
            if row[2] == '1':
                finished = "○"
            else:
                finished = "×"
            for row2 in rows2:
                if row[4] == row2[0]:
                    category = row2[1]
            data.append([row[0], importance, finished, row[3], category, row[5]])

    list_todo(data)

def modify_todo():
    conn = sqlite3.connect("{0}.db".format(current_id))
    conn2 = sqlite3.connect("{0}_category.db".format(current_id))
    cur = conn.cursor()
    cur2 = conn2.cursor()

    sql = "select * from todo where 1"
    cur.execute(sql)

    rows2 = cur.fetchall()

    filter_todo('0')

    cho = input("수정할 ID 선택 : ")

    while (not cho.isdigit()) or (cho.isdigit() and not (0 <= int(cho) <= len(rows2))):
        print(Fore.RED + "\n0 ~ {0} 사이의 숫자만을 입력해야 합니다.".format(len(rows2)) + Style.RESET_ALL)
        cho = input(">> ")

    cho = int(cho)

    val_what = input("할일 입력 : ")
    val_due = input("기한 입력 : ")
    sql = "select * from cate where 1"
    cur2.execute(sql)

    rows = cur2.fetchall()

    for no in range(0, len(rows)):
        print("[{0}] {1}".format(rows[no][0], rows[no][1]))

    val_category_num = input("카테고리 선택 : ")

    while (not val_category_num.isdigit()) \
            or (val_category_num.isdigit() and not (1 <= int(val_category_num) <= len(rows))):
        print(Fore.RED + "\n1 ~ {0} 사이의 숫자만을 입력해야 합니다.".format(len(rows)) + Style.RESET_ALL)
        val_category_num = input(">> ")

    val_important = input("중요도\n"
                          "[0] 중요\n"
                          "[1] 보통\n"
                          ">> ")

    while (not val_important.isdigit()) or (val_important.isdigit() and not (0 <= int(val_important) <= 1)):
        print(Fore.RED + "\n0 ~ 1 사이의 숫자만을 입력해야 합니다." + Style.RESET_ALL)
        val_important = input(">> ")

    val_finished = input("완료 여부\n"
                         "[0] 미완료\n"
                         "[1] 완료\n"
                         ">> ")

    while (not val_finished.isdigit()) or (val_finished.isdigit() and not (0 <= int(val_finished) <= 1)):
        print(Fore.RED + "\n0 ~ 1 사이의 숫자만을 입력해야 합니다." + Style.RESET_ALL)
        val_finished = input(">> ")

    cur.execute("UPDATE todo SET importance = ?, finished = ?, due = ?, category_num = ?, what = ? WHERE id = ?",
                (val_important, val_finished, val_due, val_category_num, val_what, cho))
    conn.commit()

def delete_todo():
    print("할일 제거-미구현")

if __name__ == "__main__":
    mainmenu_pre_login()
