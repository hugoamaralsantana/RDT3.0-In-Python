from socket import *
import time
import sys
from datetime import datetime

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

print("[STARTING] Name: Victor Santana | Date and Time: " + str(datetime.now()) + "\n")

serverName = "gaia.cs.umass.edu" #SERVER ADDRESS FOR RELAY SERVER
serverPort = 20000 #SERVER PORT FOR RELAY SERVER

connect_id = sys.argv[1]
loss_rate = sys.argv[2]
corrupt_rate = sys.argv[3]
max_delay = sys.argv[4]
in_timeout = sys.argv[5]

in_timeout = int(in_timeout)

declar_txt = "When in the Course of human events, it becomes necessary for one people to dissolve the political bands which have connected them with another, and to assume among the powers of the earth, the separat"

client_exit = 0

total_pkt_rcvd = 0
total_pkt_corrupt = 0
total_pkt_sent = 0
total_timeout = 0
total_checksum = checksum(declar_txt)

while (client_exit == 0):

    hello_msgtag = "HELLO S "

    hello_msg = hello_msgtag + str(loss_rate) + " " + str(corrupt_rate) + " " + str(max_delay) + " " + str(connect_id)

    #SENDER SOCKET CREATION
    sendersocket = socket(AF_INET, SOCK_STREAM)

    #CONNECT SOCKET TO GAIA
    sendersocket.connect((serverName, serverPort))

    #SEND HELLO MESSAGE TO GAIA SERVER
    sendersocket.send((hello_msg.encode()))

    while True:
        #RECEIVE RESPONSE FROM GAIA
        print("[GAIA] Awaiting response from Gaia Server...\n")
        gaia_response = sendersocket.recv(1024).decode()

        #CHECK FOR ERROR
        if(gaia_response[:5] == "ERROR"):
            print(gaia_response[5:] + "\n")
            print("[ERROR] \"" + gaia_response[5:] + "\"\n") #SERVER ERROR RESPONSE HANDLING
            break
        
        elif(gaia_response == "WAITING"):
            time.sleep(3)
            print("[WAIT] Awaiting Receiver Connection...\n") #WAITING FOR RECEIVER CONNECTION AND RECHECKING EVERY 10 SECONDS
            continue
        elif(gaia_response[:2] != "OK"):
            print("[UNKNOWN] Unknown Server Response >>> \"" + gaia_response + "\"\n") #CHECKING FOR ANY POSSIBLE OUTLIER RESPONSES FOR LATER DEBUGGING
        else:
            print("[OK] \"" + gaia_response[3:] + "\"\n")
            print("[CONNECTED] Client Connected To Gaia | Date and Time: " + str(datetime.now()) + "\n")
            
            seq_num = 0
            expected_ack = 0

            while True:

                #SET SOCKET TIMEOUT
                sendersocket.settimeout(in_timeout)

                print("[TEXT] Extracting Text from Document...\n")
                payload = declar_txt[:20]
                declar_txt = declar_txt[20:]

                if(declar_txt == ""):
                    client_exit = 1

                rdt_msg = str(seq_num) + " " + str(seq_num) + " " + payload + " "

                print("[CHECKSUM] Generating Checksum...\n")
                checksum_num = checksum(rdt_msg)

                rdt_msg = rdt_msg + str(checksum_num)

                while True:
                    print("[TRANSMIT] Transmitting to Receiver...\n")

                    sendersocket.send(rdt_msg.encode())

                    total_pkt_sent += 1

                    try:
                        recv_response = sendersocket.recv(1024).decode()

                    except timeout:
                        print("[TIMEOUT] No response received from Receiver in time. Retransmitting...\n")
                        total_timeout += 1
                        continue

                    total_pkt_rcvd += 1

                    sum_check = checksum_verifier(recv_response)

                    if(sum_check):

                        if(int(recv_response[2]) == expected_ack):

                            print("[OK] Receiver received packet correctly. Preparing next packet...\n")

                            expected_ack += 1
                            seq_num += 1

                            if(expected_ack == 2):
                                expected_ack = 0
                            if(seq_num == 2):
                                seq_num = 0
                            break

                        else:
                            print("[ACK] Incorrect ACK received. Retransmitting Packet\n")
                            total_pkt_corrupt += 1
                            continue
                    
                    else:
                        print("[CHECKSUM] Incorrect Checksum received. Retransmitting Packet\n")
                        total_pkt_corrupt += 1
                        continue

                if(client_exit == 1):
                    print("[DONE] Client now shutting down...\n")
                    print("----------------------------------------\n")
                    print("[CHECKSUM] Final Checksum: " + str(total_checksum) + "\n")
                    print("[RECEIVED] " + str(total_pkt_rcvd) + " packets were received.\n")
                    print("[CORRUPT] " + str(total_pkt_corrupt) + " packets were corrupt.\n")
                    print("[TIMEOUTS] " + str(total_timeout) + " timeouts occurred.\n")
                    print("[SENT] " + str(total_pkt_sent) + " packets were sent.\n")
                    break

            if(client_exit == 1):
                break
        
        if(client_exit == 1):
            break

    #CLOSE SOCKET
    print("[CLOSE] Closing the socket...\n")
    sendersocket.close()

    if(client_exit == 0):
        print("[REATTEMPT] Error Connecting to Gaia. Attempting to reconnect...\n")
        print("----------------------------------------------------------------\n")
        time.sleep(3)

print("[EXIT] Client now exiting...")