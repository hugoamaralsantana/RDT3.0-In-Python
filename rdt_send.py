from socket import *
import time

serverName = "localhost" #SERVER ADDRESS FOR RELAY SERVER
serverPort = 169420 #SERVER PORT FOR RELAY SERVER

#SENDER SOCKET CREATION
rdtsocket = socket(AF_INET, SOCK_STREAM)

#CONNECT SOCKET TO GAIA
rdtsocket.connect((serverName, serverPort))

rdtsocket.settimeout(1)

seq_num = 0
expected_ack = 0
client_exit = 0

declar_txt = "When in the Course of human events, it becomes necessary for one people to dissolve the political bands which have connected them with another, and to assume among the powers of the earth, the separat"

while True:

    payload = declar_txt[:20]
    declar_txt = declar_txt[20:]

    if(declar_txt == ""):
        client_exit = 1

    rdt_msg = str(seq_num) + " " + str(seq_num) + " " + payload + " "

    checksum_num = checksum(rdt_msg)

    rdt_msg = rdt_msg + str(checksum_num)

    while True:

        rdtsocket.send(rdt_msg)

        try:
            recv_response = rdtsocket.recv(1024).decode()

        except timeout:
            continue

        sum_check = checksum_verifier(recv_response)

        if(sum_check):

            if(recv_response[3] == expected_ack):
                expected_ack += 1
                seq_num += 1

                if(expected_ack == 2):
                    expected_ack = 0
                if(seq_num == 2):
                    seq_num = 0
                break

            else:
                continue
        
        else:
            continue

    if(client_exit == 1):
        rdtsocket.close()
        break


def checksum(msg):
    """
     This function calculates checksum of an input string
     Note that this checksum is not Internet checksum.
    
     Input: msg - String
     Output: String with length of five
     Example Input: "1 0 That was the time fo "
     Expected Output: "02018"
    """

    # step1: covert msg (string) to bytes
    msg = msg.encode("utf-8")
    s = 0
    # step2: sum all bytes
    for i in range(0, len(msg), 1):
        s += msg[i]
    # step3: return the checksum string with fixed length of five 
    #        (zero-padding in front if needed)
    return format(s, '05d')

def checksum_verifier(msg):
    """
     This function compares packet checksum with expected checksum
    
     Input: msg - String
     Output: Boolean - True if they are the same, Otherwise False.
     Example Input: "1 0 That was the time fo 02018"
     Expected Output: True
    """

    expected_packet_length = 30
    # step 1: make sure the checksum range is 30
    if len(msg) < expected_packet_length:
        return False
    # step 2: calculate the packet checksum
    content = msg[:-5]
    calc_checksum = checksum(content)
    expected_checksum = msg[-5:]
    # step 3: compare with expected checksum
    if calc_checksum == expected_checksum:
        return True
    return False