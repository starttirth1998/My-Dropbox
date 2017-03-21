import socket
import hashlib
import os
import time
import mimetypes
import re
import signal
import threading

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()
port_1 = 9998
serversocket.bind((host,port_1))
serversocket.listen(5)

port_2 = 9999
timeout = 5
hash_check = ""
hash_check_split = []
hash_dict = {}

class myThread1(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        #self.counter = counter
    def run(self):
        print "Starting " + self.name
        server1()
        print "Exiting " + self.name

class myThread2(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        #self.counter = counter
    def run(self):
        print "Starting " + self.name
        client1()
        print "Exiting " + self.name

def sync():
    hash_check = send_msg("hash checkall",True)
    #print hash_check
    hash_check_split = hash_check.split()

    for k in range(0,len(hash_check_split),7):
        #print hash_check_split[k]
        #print hash_dict
        if hash_check_split[k] not in hash_dict.keys():
            hash_dict[hash_check_split[k]] = hash_check_split[k+1]
            print hash_check_split[k]
            temp = send_msg("download TCP "+hash_check_split[k],False)
            print "File added"
        if hash_dict[hash_check_split[k]] != hash_check_split[k+1]:
            temp = send_msg("download TCP "+hash_check_split[k],False)
            hash_dict[hash_check_split[k]] = hash_check_split[k+1]
            print "File Updated"

def md5(filename):
    hasher = hashlib.md5()
    with open(filename,"rb") as f:
        buf = f.read(1024)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(1024)
    return hasher.hexdigest()

def send_msg(msg,regular):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host,port_2))
    info = ""
    print "Connected"
    client.send(msg)

    if regular:
        info_bit = client.recv(1024).split()
        #print info_bit
        if info_bit[0] == "LEN":
            client.send(("c"))
        else:
            return "Failed to do the task"
        cntr = int(info_bit[1])
        while(cntr > 0):
            current_info = client.recv(1024)
            #print current_info
            cntr -= len(current_info)
            info += current_info
        client.close()
        #print "Client Closed"
        return info
    else:
        info_bit = client.recv(1024).split()
        client.send("done")

        print "File Name:", info_bit[0]
        print "Size:",info_bit[1]
        print "Modified Time:",info_bit[2:7]
        print "MD5 hash:",info_bit[7]

        os.chdir("./shared")
        with open(info_bit[0],"wb") as f:
            print "Start"
            while True:
                #print "Receiving"
                info = client.recv(1024)

                if not info:
                    break
                #print info
                f.write(info)
        f.close()

        #print "File Closed",md5(info_bit[0])
        if md5(info_bit[0]) == info_bit[7]:
            print "Successfully downloaded"
        else:
            print "Downloading failed"

        os.chdir("./..")
        #f.close()
        client.close()
        print "Connection Closed"
        return "Finished"

def client1():
    flag_command = 1
    while True:
        print "prompt>",
        command = raw_input()
        split_command = command.split()
        try:
            while split_command[0] != "exit":
                flag = True
                if split_command[0] == "download":
                    flag = False

                if flag_command == 1:
                    #print command
                    output = send_msg(command,flag)
                    if output != None:
                        print output

                sync()

                #signal.signal(signal.SIGALRM, alarmHandler)
                #print "Check the problem"
                #signal.alarm(timeout)
                try:
                    print "prompt>",
                    command = raw_input()
                    split_command = command.split()
                    signal.alarm(0)
                    flag_command = 1
                except AlarmException:
                    print "Outside Command 2"
                    flag_command = 0
                #signal.signal(signal.SIGALRM, signal.SIG_IGN)
            #thread22.exit()
            break;
        except:
            print("Error Occured")
            #break;

def server1():
    while True:
        try:
            clientsocket, addr = serversocket.accept()
            #print("Got a connection from %s" % str(addr))
            data = clientsocket.recv(1024)
            #print("Recieved",repr(data))

            split_data = data.split()
            #split_data += [""]*5
            if split_data[0] == "index":
                info = ""
                file_list = [f for f in os.listdir('.') if os.path.isfile(f)]
                #print split_data
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
            if split_data[0] == "download":
                info = ""
                file_name = ' '.join(split_data[2:]).strip()
                #print file_name
                if split_data[1] == "TCP":
                    try:
                        if not os.path.isfile(file_name):
                            print "File Not Found"
                            raise(FileNotFoundError)
                        stat = os.stat(file_name)
                        mod_time = time.ctime(stat.st_mtime)
                        size = str(stat.st_size)
                        hash_val = md5(file_name)
                        f = open(file_name,'rb')

                        info += file_name + ' ' + size + ' ' + mod_time + ' ' + hash_val
                        #print info
                        clientsocket.send(info)
                        clientsocket.recv(1024)

                        with open(file_name,"rb") as f:
                            buf = f.read(1024)
                            while len(buf) > 0:
                                #print buf
                                clientsocket.send(buf)
                                buf = f.read(1024)

                        #clientsocket.close()
                    except:
                        print "Invalid command"
                        clientsocket.send("Fail")
                    #clientsocket.send(str(len(info)))

            clientsocket.close()
            #serversocket.close()
        except:
            print "Error Server"
            #clientsocket.close()
            serversocket.close()
            break;

thread11 = myThread1(11,"Thread - 11")
thread12 = myThread2(12,"Thread - 12")

thread11.start()
thread12.start()

#while True:
#    sync()
#    time.sleep(5)
print "Exiting Main Thread"
