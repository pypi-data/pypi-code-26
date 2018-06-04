from qlib.file import ensure_path
import os, sys


J = os.path.join

PORT = 59999
HOME = os.path.join(os.path.join(os.getenv('HOME'), '.config'), 'treatbook')
TREAT_DESKTOP = J(J(os.getenv("HOME"), 'Desktop'), 'TreaShare')
DOWNLOAD_PATH = J(J(os.getenv('HOME'), 'Desktop'), 'TreatDown')
DB_PATH =  J(HOME, "database.sql")
WEB_PATH = J(os.path.dirname(__file__), "Editor")
STATIC_PATH = J(WEB_PATH,'static')
DOCS_PATH = J(HOME, "Docs")
EXCEL_PATH = J(TREAT_DESKTOP, 'Xlsx')

ensure_path(HOME)
ensure_path(TREAT_DESKTOP)
ensure_path(STATIC_PATH)
ensure_path(DOWNLOAD_PATH)
ensure_path(DOCS_PATH)
ensure_path(WEB_PATH)
