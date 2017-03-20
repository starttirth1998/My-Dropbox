import socket
import hashlib
import signal

class AlarmException(Exception):
    pass

def alarmHandler(signum, frame):
    raise AlarmException

host = socket.gethostname()
port = 9998
timeout = 5
flag_command = 1
hash_check = ""
hash_check_split = []
hash_dict = {}

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
    client.connect((host,port))
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

        #f.close()
        client.close()
        print "Connection Closed"
        return "Finished"

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
                output = send_msg(command,flag)
                if output != None:
                    print output

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

            signal.signal(signal.SIGALRM, alarmHandler)
            signal.alarm(timeout)
            try:
                print "prompt>",
                command = raw_input()
                split_command = command.split()
                signal.alarm(0)
                flag_command = 1
            except AlarmException:
                print "Outside Command 2"
                flag_command = 0
            signal.signal(signal.SIGALRM, signal.SIG_IGN)
        break;
    except:
        print("Error Occured")
        #break;
