import socket
import hashlib
import os
import time
import mimetypes

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()
port = 9998
serversocket.bind((host,port))
serversocket.listen(5)

while True:
    try:
        clientsocket, addr = serversocket.accept()
        print("Got a connection from %s" % str(addr))
        data = clientsocket.recv(1024)
        #print("Recieved",repr(data))

        split_data = data.split()
        #split_data += [""]*5
        if split_data[0] == "index":
            if split_data[1] == "longlist":
                #print "in"
                info = ""
                file_list = [f for f in os.listdir('.') if os.path.isfile(f)]
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
                clientsocket.send("PASS " + str(len(info)))
                clientsocket.recv(1)
                while len(info):
                    sent = clientsocket.send(info)
                    info = info[sent:]
            elif split_data[1] == "shortlist":
                info = ""
                file_list = [f for f in os.listdir('.') if os.path.isfile(f)]
                try:
                    start_time = time.mktime(time.strptime(' '.join(split_data[2:6]), '%d %m %Y %H:%M:%S'))
                    end_time = time.mktime(time.strptime(' '.join(split_data[6:10]), '%d %m %Y %H:%M:%S'))
                    #print file_list
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
                    clientsocket.send("PASS " + str(len(info)))
                    clientsocket.recv(1)
                    while len(info):
                        sent = clientsocket.send(info)
                        info = info[sent:]
                except:
                    #clientsocket.send("PASS " + str(0))
                    #clientscoket.recv(1)
                    print "Invalid command"
                    clientsocket.send('Fail')
            clientsocket.close()
    except:
        print "Error Server"
        #clientsocket.close()
        #serversocket.close()
        #break;
