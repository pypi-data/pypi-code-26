import os
import shutil
import sys
from collections import defaultdict


#----------------------------------------------------------------------
def create_project(cmd, project, project_name, app_name, compilestatic=True, collectstatic=True):
    """"""


    # if len(sys.argv) <= 1:
        # print('Run:')
        # print('For django: radiant startproject django MyProject \'My APP Name\'')
        # print('For brython: radiant startproject brython MyProject \'My APP Name\'')
        # sys.exit()

    if cmd != 'startproject':
        sys.exit()

    try:
        TEMPLATE = project
    except:
        print('Missing template mame, available: \'django\', \'brython\'')

        print('Example (for django): startproject django MyProject \'My APP Name\'')
        print('Example (for brython): startproject brython MyProject \'My APP Name\'')

        sys.exit()

    try:
        PROJECT = project_name
    except:
        print('Missing project mame')
        sys.exit()

    try:
        APPNAME = app_name
        PACKAGENAME = str(APPNAME).lower().replace(' ', '')
    except:
        print('Missing app name')
        sys.exit()

    SRC = os.path.join(os.path.abspath(os.path.dirname(__file__)), TEMPLATE)
    TRG = os.path.join(os.getcwd(), PROJECT)


    #----------------------------------------------------------------------
    def parcefile(filename, kwargs):
        """"""
        #for filename in editfiles:
        if not os.path.exists(filename):
            return
        file = open(filename, "r")
        lines = file.readlines()
        file.close()
        new_lines = "".join(lines)
        new_lines = new_lines.replace("{{", "#&<<").replace("}}", ">>&#")
        new_lines = new_lines.replace("{", "{{").replace("}", "}}")
        new_lines = new_lines.replace("#&<<", "{").replace(">>&#", "}")

        #new_lines = new_lines.format(**kwargs)
        d = defaultdict(lambda: 'UNKNOWN')
        d.update(kwargs)

        new_lines = new_lines.format_map(d)

        file = open(filename, "w")
        file.write(new_lines)
        file.close()


    try:
        shutil.copytree(SRC, TRG)
    except FileExistsError as e:
        print(e)
        sys.exit()


    ignore = ('migrations',
              '__pycache__',
              )


    for root, dirs, files in os.walk(TRG):
        [dirs.remove(dir_) for dir_ in ignore if dir_ in dirs]

        for f in files:
            if f.endswith(".png"):
                continue
            file = os.path.join(root, f)
            parcefile(file, {'PROJECT': PROJECT, 'APPNAME': APPNAME, 'PACKAGENAME': PACKAGENAME,})


    if os.path.exists(os.path.join(TRG, TEMPLATE)):
        os.rename(os.path.join(TRG, TEMPLATE), os.path.join(TRG, PROJECT))

    if os.path.exists(os.path.join(TRG, 'DjangoApp')):
        os.rename(os.path.join(TRG, 'DjangoApp'), os.path.join(TRG, PROJECT))

    os.chdir(TRG)
    os.system("python manage.py migrate")
    if compilestatic:
        os.system("python manage.py compilestatic")
    if collectstatic:
        os.system("python manage.py collectstatic --noinput")



if __name__ == '__main__':

    create_project(*sys.argv[1:])