#!/usr/bin/env python

# TODO: Add some argparse stuff later
#import argparse
import ldap
import mysql.connector

import sys

################################################################
# !! BEGIN: user configuration
################################################################

# Exclusion List: local accounts, do not check for updates
# -------------------------------------------------------------
exclusion = ['admin', 'administrator']

# LDAP Credentials
# --------------------------------------------------------------
ldapserver = "ldap://<server>:<port>"
binddn = "CN=<bind user>,CN=Users,dc=<domain>,dc=<tld>"
bindpw = "<bind user pass>"
basedn = "CN=Users,DC=<domain>,DC=<tld>"

# MySQL Credentials
# --------------------------------------------------------------
mysqlsvr = "localhost"
mysql_db = "<rundeck mysql database>"
mysqlusr = "<rundeck mysql username>"
mysqlpwd = "<rundeck mysql password>"

################################################################
# !! END: user configuration
################################################################

def ldap_search(username):
	# LDAP Search
	searchFilter = "(&(objectclass=User)(sAMAccountName=%s))" % username
	searchAttribute = ["givenName","sn","mail"]

	l = ldap.initialize(ldapserver)		# Initialize LDAP
	searchScope = ldap.SCOPE_SUBTREE	# this will scope the entire subtree under UserUnits

	# Bind to the server
	try:
		l.protocol_version = ldap.VERSION3
		l.simple_bind_s(binddn, bindpw) 
	except ldap.INVALID_CREDENTIALS:
		sys.exit(0)
	except ldap.LDAPError, e:
		if type(e.message) == dict and e.message.has_key('desc'):
			sys.exit(0)
		else: 
			sys.exit(0)
	try:    
		ldap_result_id = l.search(basedn, searchScope, searchFilter, searchAttribute)
		result_set = []
		result_type, result_data = l.result(ldap_result_id, 0)
		if (result_data == []):
			# aww, no data found
			data = None
		else:
			# yay, we found some data
			if result_type == ldap.RES_SEARCH_ENTRY:
				result_set.append(result_data)
				cn = result_data[0][0]		# cn Returned first
				data = result_data[0][1]	# searchAttributes second

				# Clean up the data items for easy access
				for (i, j) in data.items():
					if len(j) == 1:
						data[i] = j[0]
		return data
	except ldap.LDAPError, e:
		sys.exit(0)
	finally:
		l.unbind_s()
	return 0

def mysql_update(cursor, username, userdata):
	query = "UPDATE rduser SET first_name='{}', last_name='{}', email='{}' WHERE login='{}'".format(
		userdata["givenName"], userdata["sn"], userdata["mail"], username)
	cursor.execute(query)	

def mysql_search():
	cnx = mysql.connector.connect(host=mysqlsvr, user=mysqlusr, password=mysqlpwd, database=mysql_db)
	cur = cnx.cursor()

	query = "SELECT login from rduser where email is NULL and login <> 'admin'"

	for login in exclusion:
		query += " and login <> '{}'".format(login)

	print query

	cur.execute(query)
	result = cur.fetchall()

	print result
	sys.exit(0)

	for login in result:
		userdata = ldap_search(login[0])
		mysql_update(cur, login[0], userdata)

	cur.close()
	cnx.commit()
	cnx.close()

def main():
	# TODO: Add some argparse
	# --full-update ?
	mysql_search()


if __name__ == "__main__":
	main()

