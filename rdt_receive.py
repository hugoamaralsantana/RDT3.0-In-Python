from socket import *
import time

serverName = "localhost" #SERVER ADDRESS FOR RELAY SERVER
serverPort = 169420 #SERVER PORT FOR RELAY SERVER

#SENDER SOCKET CREATION
rdtsocket = socket(AF_INET, SOCK_STREAM)

#CONNECT SOCKET TO GAIA
rdtsocket.connect((serverName, serverPort))

ack_num = 1
expected_seq = 0

rcvd_txt = ""

while True:

    recv_msg = rdtsocket.recv(1024).decode()

    sum_check = checksum_verifier(recv_msg)

    if(sum_check): #IF PACKET IS NOT CORRUPT

        if(recv_msg[0] == expected_seq): #IF PACKET IS NOT DUPLICATE DUE TO LOST ACK IN PREVIOUS TRANSMIT

            rcvd_txt = rcvd_txt + recv_msg[5:-6]

            ack_num += 1

            if(ack_num == 2):
                ack_num = 0
            
            rdt_ack = "  " + str(ack_num) + " " + "                    " + " "
            
            checksum_num = checksum(rdt_ack)

            rdt_ack = rdt_ack + str(checksum_num)

            rdtsocket.send(rdt_ack)

            expected_seq += 1

            if(expected_seq == 2):
                expected_seq = 0
        
        else: #PACKET IS A DUPLICATE; RETURN INCORRECT ACK_NUM
            rdt_ack = "  " + str(ack_num) + " " + "                    " + " "
            
            checksum_num = checksum(rdt_ack)

            rdt_ack = rdt_ack + str(checksum_num)

            rdtsocket.send(rdt_ack)

    else: #PACKET IS CORRUPT; RETURN INCORRECT ACK_NUM
        rdt_ack = "  " + str(ack_num) + " " + "                    " + " "

        checksum_num = checksum(rdt_ack)

        rdt_ack = rdt_ack + str(checksum_num)

        rdtsocket.send(rdt_ack)

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