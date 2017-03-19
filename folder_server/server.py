import socket
import hashlib
import os
import time
import mimetypes
import re

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()
port = 9990
serversocket.bind((host,port))
serversocket.listen(5)

def md5(filename):
    hasher = hashlib.md5()
    with open(filename,"rb") as f:
        buf = f.read(1024)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(1024)
    return hasher.hexdigest()

while True:
    try:
        clientsocket, addr = serversocket.accept()
        print("Got a connection from %s" % str(addr))
        data = clientsocket.recv(1024)
        #print("Recieved",repr(data))

        split_data = data.split()
        #split_data += [""]*5
        if split_data[0] == "index":
            info = ""
            file_list = [f for f in os.listdir('.') if os.path.isfile(f)]
            if split_data[1] == "longlist":
                #print "in"
                #print file_list
                for f in file_list:
                    #print f
                    stat = os.stat(f)
                    mod_time = time.ctime(stat.st_mtime)
                    size = str(stat.st_size)
                    file_type = mimetypes.guess_type(f,False)
                    if not file_type:
                        file_type = "Unknown"
                    info+='\t'.join([f,size,mod_time,str(file_type[0])])+'\n'
                    #print info
                clientsocket.send("LEN " + str(len(info)))
                clientsocket.recv(1)
                while len(info):
                    sent = clientsocket.send(info)
                    info = info[sent:]
            elif split_data[1] == "shortlist":
                try:
                    start_time = time.mktime(time.strptime(' '.join(split_data[2:6]), '%d %m %Y %H:%M:%S'))
                    end_time = time.mktime(time.strptime(' '.join(split_data[6:10]), '%d %m %Y %H:%M:%S'))
                    #print start_time
                    for f in file_list:
                        #print f
                        stat = os.stat(f)
                        mod_time = time.ctime(stat.st_mtime)
                        size = str(stat.st_size)
                        file_type = mimetypes.guess_type(f,False)
                        if not file_type:
                            file_type = "Unknown"
                        if start_time < os.path.getmtime(f) < end_time:
                            info+='\t'.join([f,size,mod_time,str(file_type[0])])+'\n'
                        #print info
                    clientsocket.send("LEN " + str(len(info)))
                    clientsocket.recv(1)
                    while len(info):
                        sent = clientsocket.send(info)
                        info = info[sent:]
                except:
                    #clientsocket.send("LEN " + str(0))
                    #clientscoket.recv(1)
                    print "Invalid command"
                    clientsocket.send("Fail")
            elif split_data[1] == "regex":
                #print "in"
                #print file_list
                try:
                    reg = re.compile(' '.join(split_data[2:]).strip())
                    #print reg
                    for f in file_list:
                        #print f
                        stat = os.stat(f)
                        mod_time = time.ctime(stat.st_mtime)
                        size = str(stat.st_size)
                        file_type = mimetypes.guess_type(f,False)
                        if not file_type:
                            file_type = "Unknown"
                        print reg.search(f)
                        if reg.search(f):
                            info+='\t'.join([f,size,mod_time,str(file_type[0])])+'\n'
                        #print info
                    clientsocket.send("LEN " + str(len(info)))
                    clientsocket.recv(1)
                    while len(info):
                        sent = clientsocket.send(info)
                        info = info[sent:]
                except:
                    print "Invalid command"
                    clientsocket.send("Fail")
        if split_data[0] == "hash":
            info = ""
            file_list = [f for f in os.listdir('.') if os.path.isfile(f)]
            if split_data[1] == "verify":
                try:
                    file_name = ' '.join(split_data[2:]).strip()
                    #print file_name
                    if os.path.isfile(file_name):
                        hash_val = md5(file_name)
                        mod_time = time.ctime(os.path.getmtime(file_name))
                        info += '\t'.join([hash_val,mod_time])+'\n'
                    clientsocket.send("LEN " + str(len(info)))
                    clientsocket.recv(1)
                    clientsocket.send(info)
                except:
                    print "Invalid " + file_name
                    clientsocket.send("Fail")
            elif split_data[1] == "checkall":
                for f in file_list:
                    hash_val = md5(f)
                    mod_time = time.ctime(os.path.getmtime(f))
                    info += '\t'.join([f, hash_val, mod_time])+'\n'
                    #print info
                clientsocket.send("LEN "+str(len(info)))
                clientsocket.recv(1)
                while len(info):
                    sent = clientsocket.send(info)
                    info = info[sent:]
            else:
                print "Invalid command"
                clientsocket.send("Fail")
        clientsocket.close()
        #serversocket.close()
    except:
        print "Error Server"
        #clientsocket.close()
        serversocket.close()
        break;
