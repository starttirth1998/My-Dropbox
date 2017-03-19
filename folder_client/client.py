import socket
import hashlib

host = socket.gethostname()
port = 9994

def send_msg(msg,regular):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host,port))
    info = ""
    print "Connected"
    client.send(msg)
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

while True:
    command = raw_input()
    split_command = command.split()
    try:
        while split_command[0] != "Close":
            arg = True
            if split_command[0] == "download":
                arg = False

            output = send_msg(command,arg)
            if output != None:
                print output

            command = raw_input()
            split_command = command.split()
        break;
    except:
        print("Error Occured")
        #break;
