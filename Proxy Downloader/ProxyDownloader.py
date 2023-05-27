'''
subject: CS421 Programming Assignment
author: Gokberk Keskinkilic
date: 31.03.2023
'''

import socket
import os
import sys

# Setting up a socket to listen to incoming requests
HOST = 'localhost'
PORT = int(sys.argv[1])

#while True:
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Listening on {HOST}:{PORT}...")

    while True:
        # Parsing the incoming request to extract information. Printing the request on the console.
        conn, addr = s.accept()
        with conn:
            # print('Connected using adress:', addr)
            response = b""
            data = conn.recv(4096)
            request = data.decode('utf-8')

            # Without this part, the code gives out of bound error in parsing segment
            if(len(request) == 0):
                print("Request is empty, Firefox error. Please resend the request. Clearing cache might help as well...")
                continue

            # Blocking unnecessary contents
            if("firefox" in request or "ipv4" in request or "favicon" in request or "CONNECT" in request or "mozilla" in request or "GET" not in request):
                continue

            print("Retrieved request from Firefox:\n")
            print(request)

            # Extracting the server name and file name from the request
            datastr = data.decode()
            my = datastr.split("\r\n")
            server_name = my[1][6:] 

            get = my[0]                             # GET http HTTP/1.1
            getList = get.split(" ") 
            file_name = getList[1].split('/')[-1]   # parsing the file name from address

            print(f"Server name: {server_name}")
            print(f"  File name: {file_name}")
            
            # Sending an HTTP request to the server and retrieving its content. Receiving in a loop until no data left.
            print("Sending an HTTP request...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy:
                proxy.connect((server_name, 80))
                proxy.sendall(data)
                response = b''
                while True:
                    recv_data = proxy.recv(1024)
                    if not recv_data:
                        break
                    response += recv_data

            # Sending it back to browser
            conn.sendall(response)

            # Printing the status code of the response
            response_str = response.decode()
            response_first_line = response_str.split("\r\n")[0]
            first = response_first_line.split()[0]          # first = "HTTP/1.1", used to replace from response
            status_code = response_first_line.split()[1]

            # Replacing the rest to reach the response phrase
            response_first_line = response_first_line.replace(" ", "", 2)
            response_first_line = response_first_line.replace(first, "")
            response_phrase = response_first_line.replace(status_code, "")
            
            print(f"Retrieved: {status_code} {response_phrase}")

            # Saving the downloaded file with its name.
            print(f"Saving \"{file_name}\"")
            with open(file_name, 'wb') as f:
                f.write(response)
            print("File Saved.")
            print("You may continue with the next webpage...\n")

            # To repeat the same procedure as long as the user keeps connecting to the websites, disconnecting from the previous one
            conn.close()