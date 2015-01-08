#!/usr/bin/env python3
#
import sqlite3
import os

try:
	os.remove('quip.db')
except OSError:
	pass

con = sqlite3.connect('quip.db')
con.executescript(open('create_database.sql', 'r').read())
con.close()
