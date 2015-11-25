# scripts
Generic scripts for miscellaneous projects.
===========================================

 update_rundeck_ldap_info.py :

 	Rundeck out of box does not support pulling LDAP credentials into Rundeck. Missing
	items are First Name, Last Name, and E-Mail address. This script is designed to be
	run as a cron job against a mysql database configuration for a Rundeck configuration
	using LDAP authentication. The script will iterate through all users that do not
	have an e-mail address sent and attempt to pull their name and 	e-mail address into
	the Rundeck 'rdusers' table.
