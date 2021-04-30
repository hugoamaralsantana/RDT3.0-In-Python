# RDT3.0-In-Python
This is an implementation of the RDT3.0 Protocol.

Project Basis:
I'm currently a student at UMass Amherst and am working on a project for my Computer Networks course and decided to complete my project with regular commits on GitHub in order to document my progress and to share my work with those interested in seeing my code.

Project Updates:

4/26/2021:
Implemented Gaia Server Connectivity so that the program can communicate properly with Gaia Server and to handle the connection process as the server attempts to find a matching
ID user to form a connection between

I added some preventative measures for possible Server Response Outliers in order for the system output to alert the user of any Unknown responses that the server might possibly 
send. Outside of that, I implemented the WAITING, ERROR, and OK server response handling. All that's needed is to fill up the OK if statement with the RDT3.0 Protocol of data 
loss, corruption, and delays.

4/28/2021:
Implemented Rough Structure of RDT3.0 Protocol for Receiver and Sender

4/29/2021:
Finished implementing incorrect ACK and duplicate handling for receiver and timeouts for the sender.

Implemented RDT3.0 Protocol into Gaia Communication and worked out bugs

Added summary of transmission of packets lost, packets corrupt, and timeouts for easier user access.

DISCLAIMER:
NOT ALLOWED TO COPY IN ANY WAY SHAPE OR FORM FOR USE IN CS453 Computer Networks at UMass Amherst!
