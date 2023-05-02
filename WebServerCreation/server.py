import socket
import os
import threading
import sys
import argparse
import time
import signal

HOST = "localhost"
PORT = 8080 
DIR = './'
	
def ConnectionThread_HTTP(SOC_REQ, conn):
    print(SOC_REQ)
    if(SOC_REQ[1] == '/'):
        SOC_REQ[1] = '/index.html'
    try:
        if(SOC_REQ[1].find('.html') > 0 or SOC_REQ[1].find('.txt') > 0):
            FLNM = DIR + SOC_REQ[1]
            with open(FLNM,  'r', encoding='latin-1') as FILE:
                content = FILE.read()
            FILE.close()
            SOC_RESP = str.encode("HTTP/1.1 200 OK\n")
            SOC_RESP = SOC_RESP + str.encode('Content-Type: text/html\n')
            SOC_RESP = SOC_RESP + str.encode('\r\n')
            conn.sendall(SOC_RESP)
            conn.sendall(content.encode())
        
        elif(SOC_REQ[1].find('.mp4') > 0):   
            conn.sendall(str.encode("HTTP/1.1 403 Forbidden\r\nForbidden"))
        
        elif(SOC_REQ[1].find('.png') > 0 or SOC_REQ[1].find('.jpg') > 0 or SOC_REQ[1].find('.gif') > 0):
            IMG_EXTN = SOC_REQ[1].split('.')[1]
            FLNM = '.' + SOC_REQ[1]
            image_data = open(FLNM, 'rb')
            SOC_RESP = str.encode("HTTP/1.1 200 OK\n")
            IMG_EXTN = "Content-Type: image/" + IMG_EXTN +"\r\n"
            SOC_RESP = SOC_RESP + str.encode(IMG_EXTN)
            SOC_RESP = SOC_RESP + str.encode("Accept-Ranges: bytes\r\n\r\n")
            conn.sendall(SOC_RESP)
            conn.sendall(image_data.read())
			
        elif(SOC_REQ[1].find('*') > 0 or SOC_REQ[1].find('!') > 0):   
            conn.sendall(str.encode("HTTP/1.1 400 Bad Request\r\nBad Request"))
			
        else:
            conn.sendall(str.encode("HTTP/1.1 404 NOT FOUND\r\nFile Not Found"))
    except FileNotFoundError: 
       conn.sendall(str.encode("HTTP/1.1 404 NOT FOUND\r\nFile Not Found"))
	   
    except Exception:
       conn.sendall(str.encode("HTTP/1.1 500 Internal Server Error\r\nInternal Server Error"))
    
def ConnectionLiveStatus(conn, address):
    size = 1024
    with conn:
        conn.settimeout(3)
        while True:
            try:
                SOC_REQ = conn.recv(size).decode()   
                SOC_HEAD = SOC_REQ.split('\r\n')   
                RESULT  = SOC_HEAD[0].split()
                if RESULT[0] == "GET":
                    ConnectionThread_HTTP(RESULT,conn)
            except Exception as EXP:
                break
    conn.close()
	
def SERLIS():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as SOC_LIST:
        SOC_LIST.bind((HOST, PORT))
        while True:
            SOC_LIST.listen()
            conn, addr = SOC_LIST.accept()
            MULTITHREAD = threading.Thread(target=ConnectionLiveStatus, args=(conn, addr))
            MULTITHREAD.start()
	
if __name__ == "__main__":
    inputArgs = argparse.ArgumentParser()

    inputArgs.add_argument('-document_root', type=str)
    inputArgs.add_argument('-port', type=int)
    parsedArgs = inputArgs.parse_args()
    try:
        PORT = parsedArgs.port
        DIR = parsedArgs.document_root
    except AttributeError:
        print("Arguments are missing or input type is wrong")
        print("Input type = python server.py -document_root './' -port 8080")
        sys.exit(1)
    print("Server host and port" + HOST + ":" + str(PORT))
    print("Server directory:" + DIR)
    SERLIS()
