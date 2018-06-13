# -*- coding: utf-8 -*- 
import sqlite3
try:
	from . import duecheck as dc
except:
	import duecheck as dc
from pathlib import Path

def auto_fin():
	home_dir = str(Path.home())
	conn = sqlite3.connect(home_dir + "/task.db")
	cur = conn.cursor()

	slct_data = "select * from todo where finished = ?"
	cur.execute(slct_data,['n'])
	records = cur.fetchall()
	for row in records:
		if not (dc.istime(row[2]) or row[2] == '0000-00-00 00:00:00'):
			sql = "update todo set finished = ? where id = ?"
			cur.execute(sql,['y',row[0]])
			conn.commit()
