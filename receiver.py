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

client_exit = 0

rcvd_txt = ""

total_pkt_rcvd = 0
total_pkt_corrupt = 0
total_ack_sent = 0
total_pkt_duplicate = 0

while (client_exit == 0):

    hello_msgtag = "HELLO R "

    hello_msg = hello_msgtag + str(loss_rate) + " " + str(corrupt_rate) + " " + str(max_delay) + " " + str(connect_id)

    #SENDER SOCKET CREATION
    receiversocket = socket(AF_INET, SOCK_STREAM)

    #CONNECT SOCKET TO GAIA
    receiversocket.connect((serverName, serverPort))

    #SEND HELLO MESSAGE TO GAIA SERVER
    receiversocket.send(hello_msg.encode())

    while (client_exit == 0):
        #RECEIVE RESPONSE FROM GAIA
        print("[GAIA] Awaiting response from Gaia Server...\n")
        gaia_response = receiversocket.recv(1024).decode()

        #CHECK FOR ERROR
        if(gaia_response[:5] == "ERROR"):
            print(gaia_response[5:] + "\n")
            print("[ERROR] \"" + gaia_response + "\"\n") #SERVER ERROR RESPONSE HANDLING
            break
        
        elif(gaia_response == "WAITING"):
            time.sleep(10)
            print("[WAIT] Awaiting Receiver Connection...") #WAITING FOR RECEIVER CONNECTION AND RECHECKING EVERY 10 SECONDS
            continue
        elif(gaia_response[:2] != "OK"):
            print("[UNKNOWN] Unknown Server Response >>> \"" + gaia_response + "\"") #CHECKING FOR ANY POSSIBLE OUTLIER RESPONSES FOR LATER DEBUGGING
        else:
            print("[OK] \"" + gaia_response[3:] + "\"\n")
            print("[CONNECTED] Client Connected To Gaia | Date and Time: " + str(datetime.now()) + "\n")
            ack_num = 1
            expected_seq = 0

            while True:
                print("Current ACK: " + str(ack_num) + "\n")
                print("Expected Sequence: " + str(expected_seq) + "\n")

                recv_msg = receiversocket.recv(1024).decode()

                if(recv_msg == ""):
                    client_exit = 1
                    break
                
                total_pkt_rcvd += 1

                sum_check = checksum_verifier(recv_msg)

                if(sum_check): #IF PACKET IS NOT CORRUPT

                    if(int(recv_msg[0]) == expected_seq): #IF PACKET IS NOT DUPLICATE DUE TO LOST ACK IN PREVIOUS TRANSMIT

                        rcvd_txt = rcvd_txt + recv_msg[4:-6]
                        print("[OK] Received Packet Correctly. Transmitting Correct ACK...\n")
                        print("Received Text: " + rcvd_txt + "\n")

                        ack_num += 1

                        if(ack_num == 2):
                            ack_num = 0
                        
                        rdt_ack = "  " + str(ack_num) + " " + "                    " + " "
                        
                        checksum_num = checksum(rdt_ack)

                        rdt_ack = rdt_ack + str(checksum_num)

                        receiversocket.send(rdt_ack.encode())

                        total_ack_sent += 1

                        expected_seq += 1

                        if(expected_seq == 2):
                            expected_seq = 0
                    
                    else: #PACKET IS A DUPLICATE; RETURN INCORRECT ACK_NUM
                        
                        print("[DUPLICATE] Duplicate Packet Detected. Sending Wrong ACK...\n")
                        total_pkt_duplicate += 1

                        rdt_ack = "  " + str(ack_num) + " " + "                    " + " "
                        
                        checksum_num = checksum(rdt_ack)

                        rdt_ack = rdt_ack + str(checksum_num)

                        receiversocket.send(rdt_ack.encode())

                        total_ack_sent += 1

                else: #PACKET IS CORRUPT; RETURN INCORRECT ACK_NUM
                    print("[CORRUPT] Corrupt Packet Detected. Sending Wrong ACK...\n")
                    total_pkt_corrupt += 1

                    rdt_ack = "  " + str(ack_num) + " " + "                    " + " "

                    checksum_num = checksum(rdt_ack)

                    rdt_ack = rdt_ack + str(checksum_num)

                    receiversocket.send(rdt_ack.encode())

                    total_ack_sent += 1

    print("----------------------------------------\n")
    print("[CHECKSUM] Final Checksum: " + str(checksum(rcvd_txt)) + "\n")
    print("[RECEIVED] " + str(total_pkt_rcvd) + " packets were received.\n")
    print("[DUPLICATE] " + str(total_pkt_duplicate) + " packets were duplicates.\n")
    print("[CORRUPT] " + str(total_pkt_corrupt) + " received packets were corrupt.\n")
    print("[SENT] " + str(total_ack_sent) + " packets were sent.\n")

    #CLOSE SOCKET
    print("[CLOSE] Closing the socket...\n")
    receiversocket.close()

    if(client_exit == 0):
        print("[REATTEMPT] Error Connecting to Gaia. Attempting to reconnect...")
        time.sleep(3)

print("[EXIT] Client now exiting...")