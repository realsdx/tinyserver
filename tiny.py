import socket
import sys
import traceback
import signal
import time

#Some color stuffs
white = '\033[1;97m'
green = '\033[1;32m'
blue = '\033[94m'
red = '\033[1;31m'
yellow = '\033[1;33m'
magenta = '\033[1;35m'
end = '\033[1;m'
info = '\033[1;33m[!]\033[1;m'
que =  '\033[1;34m[?]\033[1;m'
bad = '\033[1;31m[-]\033[1;m'
good = '\033[1;32m[+]\033[1;m'
run = '\033[1;97m[~]\033[1;m'

__version__ = '0.1'
__usage__ = "Usage: %s$ python tiny.py <port>%s to run TinyServer on specified port."%(magenta, end)
__banner__= """%s       
 _______           ____                    
/_  __(_)__  __ __/ __/__ _____  _____ ____
 / / / / _ \/ // /\ \/ -_) __/ |/ / -_) __/
/_/ /_/_//_/\_, /___/\__/_/  |___/\__/_/   
           /___/                           
%s"""%(red, end)


def create_response(response_code, html):
    """Only supports html files for now"""
    if response_code == 200:
        status_line = 'HTTP/1.1 200 OK\r\n'
    elif response_code == 404:
        status_line = 'HTTP/1.1 404 NOT FOUND\r\n'

    now = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
    headers = 'Date: {} GMT\r\n'.format(now)
    headers += 'Server: TinyPyServer'+__version__+'\r\n'
    headers += 'Content-Type: text/html\r\n'
    headers += 'Connection: close\r\n\r\n'
    response_header = status_line+headers
    response_data = html
    return response_header, response_data

def get_filename(req):
    """REturns the finename.
    It dosen't support get parameters."""

    get_file = req.split(' ')[1]
    #Removes any ? from get request
    get_file = get_file.split('?')[0]
    #Strips the '/'
    get_file = get_file[1:]
    #Handle empty filename
    if get_file == "":
        get_file = "index.html"

    return get_file

def read_file(filename):
    try:
        file_obj = open(filename,'rb')
        data = file_obj.read()
        file_obj.close()
        filename = None
        #File is found. Set the respone code accordingly
        response_code = 200

    except FileNotFoundError:
        print(bad+"File Not Found. Sending 404 ...")
        response_code = 404
        data = """<!DOCTYPE html>
        <html lang="en" dir="ltr">
          <head>
            <meta charset="utf-8">
            <title>Test apge</title>
          </head>
          <body>
            <center><h1> 404 Page Not Found </h1>
            <small>TinyServer v0.1</small>
            </center>
          </body>
        </html>"""
        #Convert str to bytes
        data = data.encode('utf-8')

    return response_code, data


def main():
    if (len(sys.argv) > 1):
        port = int(sys.argv[1])
    else:
        print(blue+__usage__+end)
        print(info+green+"Running on default port 5000.")
        port = 5000

    print(__banner__)

    socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_obj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_obj.bind(('', port))
    socket_obj.listen(True)
    
    print(good+"Server running...")

    while(True):
        try:           
            client, addr = socket_obj.accept()
            client.settimeout(60)

            print(info+"Client:" , client)
            data = client.recv(1024)
            if not data:
                print(bad+"No data received")
                break

            req = data.decode()
            req_method = req.split(' ')[0]

            if req_method == "GET":
                file_to_open = get_filename(req)
                print(info+"Requested:", file_to_open)
                response_code, data = read_file(file_to_open)

                response_header, response_data = create_response(response_code, data)
                client.send(response_header.encode())
                client.send(response_data)
                #Keep-alive is not supported so connection must be closed
                client.close()
            else:
                print(bad+"Method not Supported")

        except KeyboardInterrupt:
            socket_obj.close()
            sys.exit(0)

        except Exception:
            traceback.print_exc()


main()
