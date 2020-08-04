from tinyserver.httpserver import HTTPServer

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

__banner__= """%s       
 _______           ____                    
/_  __(_)__  __ __/ __/__ _____  _____ ____
 / / / / _ \/ // /\ \/ -_) __/ |/ / -_) __/
/_/ /_/_//_/\_, /___/\__/_/  |___/\__/_/   
           /___/                           
%s"""%(red, end)

print(__banner__)

server = HTTPServer()
server.start_server()
