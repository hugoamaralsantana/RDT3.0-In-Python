from socket import *
import time

serverName = "gaia.cs.umass.edu" #SERVER ADDRESS FOR RELAY SERVER
serverPort = 20000 #SERVER PORT FOR RELAY SERVER

exit = 0

while (exit == 0):
    loss_rate = input("Please input the loss rate (Between 0.0 and 1.0) >>> ")              #USER INPUTS LOSS RATE FOR CONNECTION
    corrupt_rate = input("Please input the corruption rate (Between 0.0 and 1.0) >>> ")     #USER INPUTS CORRUPTION RATE FOR CONNECTION
    max_delay = input("Please input the max_delay (Between 0 and 5) >>> ")                  #USER INPUTS MAX DELAY FOR CONNECTION
    connect_id = input("Please input the connection ID (4 digits) >>> ")                    #USER INPUTS CONNECTION ID USED BY RELAY SERVER FOR CONNECTING RECEIVER AND SENDER

    hello_msgtag = "HELLO S "

    hello_msg = hello_msgtag + str(loss_rate) + str(corrupt_rate) + str(max_delay) + str(connect_id)

    #SENDER SOCKET CREATION
    sendersocket = socket(AF_INET, SOCK_STREAM)

    #CONNECT SOCKET TO GAIA
    sendersocket.connect((serverName, serverPort))

    #SEND HELLO MESSAGE TO GAIA SERVER
    sendersocket.send(hello_msg)

    while True:
        #RECEIVE RESPONSE FROM GAIA
        gaia_response = sendersocket.recv(1024).decode()

        #CHECK FOR ERROR
        if(gaia_response[:5] == "ERROR"):
            print(gaia_response[5:] + "\n")
            print("[ERROR] Please try connecting again...\n") #SERVER ERROR RESPONSE HANDLING
            break
        
        elif(gaia_response == "WAITING"):
            time.sleep(10)
            print("[WAIT] Awaiting Receiver Connection...") #WAITING FOR RECEIVER CONNECTION AND RECHECKING EVERY 10 SECONDS
            continue
        elif(gaia_response != "OK"):
            print("[UNKNOWN] Unknown Server Response >>> \"" + gaia_response + "\"") #CHECKING FOR ANY POSSIBLE OUTLIER RESPONSES FOR LATER DEBUGGING
        else:
            #RDT PROTOCOL AND FILE SENDING
            check = 0 #PLACEHOLDER TO REMOVE REDLINE ERROR

    #CLOSE SOCKET
    sendersocket.close()

print("[EXIT] Client now exiting...")