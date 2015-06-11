#Author:	Aaron Huber
#Date:		5/2015

#This python script entails a server that the myFTPclient will connect to for the
#purpose of creating and retrieving files.
import socket
import threading
import os
import MySQLdb

ip = "127.0.0.1"			#server ip address
port = 200				#server listening port
db = MySQLdb.connect("localhost", "root", "", "myftp")
cur = db.cursor()

#The listen function listens, receives and validates commands from the client after
# successful authentication has been made.
def listen(ns):
	while True:
		cmd = ns.recv(4096).split(' ', 2)
		if len(cmd) <= 1:
			if cmd[0] == "quit":
				ns.close()
				break
			else:
				ns.send("[*]Invalid Entry: Missing Arguments")
				continue
	
		if cmd[0] == "CREATE":
			create(cmd)
			ns.send("File created!")
		elif cmd[0] == "SHOW":
			show(ns, cmd)
		else:
			ns.send("Invalid command")

#The create function creates a file and writes the data that the client requested to be 
#written to the file.  The file is saved server side.
def create(cmd):	
	fd = open(cmd[1], 'w')
	fd.write(cmd[2])
	fd.close()

#The show function retrieves a file and transfers the file's data to the client.
def show(ns, cmd):
	if os.path.isfile(cmd[1]):
		fd = open(cmd[1], 'r')
		ns.send(fd.read())
		fd.close()
	else:
		ns.send("File does not exist.")

#connhandler handles authentication of all incoming connections; after authentication,
#connhandler dispatches the socket to the listen function
def connhandler(ns, addr):		
	ns.send("myFTP Server 4.0")
	
	#accept and validate the username
	while True:
		data = ns.recv(4096)		#grab the user name
		u_name = data.split(' ', 1)	#split the string for validation
		if u_name[0]!="USER":		#validate the command
			ns.send("[*]Invalid Entry")	#retry entry
			continue
		else:				#the command was correct, query the database for user name
			sql = "SELECT * FROM myftp_user WHERE user_name = '%s'" % u_name[1]
			cur.execute(sql)
			results = cur.fetchone()
			if cur.rowcount == 0:
				ns.send("[*]User name does not exist.")
				continue
			else:
				ns.send("OK")
		break

	#accept and validate the password
	while True:
		data = ns.recv(4096)
		pswd = data.split(' ', 1)
		if pswd[0]!="PASS":
			ns.send("[*]Invalid Entry")
			continue
		else:
			sql = "SELECT * FROM myftp_user WHERE user_name = '%s' AND password = '%s'" % (u_name[1], pswd[1])
			cur.execute(sql)
			if cur.rowcount == 0:
				ns.send("[*]User name does not exist.")
				continue	
			else:
				ns.send("OK")
		break
		
	listen(ns)
	print "%s sent me: %s" % (addr, u_name[1])
	ns.close()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	#create server socket

s.bind((ip, port))					#create the mapping in the OS to forward all traffic destined
							#server's ip and port address to the server application
s.listen(10)						#allow up to 10 simultaneous connections

while True:
	newsocket, addr = s.accept()			#accept incoming connection, saving the socket in newsocket and
							#the client ip and port in addr
	print "**********************************"
	print addr
	print "**********************************"

	c = threading.Thread(target=connhandler, args=(newsocket, addr))	#create a thread to run the new socket
	c.start()					#start the thread