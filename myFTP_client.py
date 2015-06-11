#Author:	Aaron Huber
#Date:		5/2015

#This python code is a client program that connects to a myFTP server for the purpose of
#creating, storing, and retrieving file data.
import socket
import sys
import hashlib

ip = sys.argv[1]		#take ip address from command arguments
port = int(sys.argv[2])		#take port from command arguments

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	#create a socket
s.settimeout(60)			
s.connect((ip, port))		#connect to ex_server
banner = s.recv(4096)		#grab the server banner
print banner			#print banner to terminal

data = "[*]Invalid Entry"

#send over user credentials
while True: 
	user_name = ' '.join(["USER", raw_input()])		#take in client input
	s.send(user_name)		#send client data to server
	data = s.recv(4096)
	print data
	if data =="[*]Invalid Entry" or data =="[*]User name does not exist.":
		continue	

	break
	
#send over password credentials
while True:
	pswd = raw_input()		#take in client input
	hash_pswd = hashlib.sha256(pswd.encode()).hexdigest()		#the password is hashed to be compared with the 
																#hash that is stored in the MySQL database
	final_pswd = ' '.join(["PASS", hash_pswd])
	s.send(final_pswd)		#send client data to server
	data = s.recv(4096)
	print data
	if data =="[*]User name does not exist.":
		continue	

	break

#client access	
while True:
	cmd = raw_input("Enter a command: \n")
	s.send(cmd)
	if cmd == "quit":
		break
	msg = s.recv(4096)
	print msg

s.close()			#close the connection