import threading
import thread
import socket 
import sys
from base64 import b64encode
import time
import os 


class ProxyServer :
    
    def __init__(self) : 
        self.NoConnections = 20
        self.bufferSize = 1000
        self.authfilePath = 'auth.txt' 
        self.blacklistfilePath = 'blacklist.txt'
        self.allowedURL = ['127.0.0.1']
        self.iiitports = range(20000,20100) 
        self.allowedServers = range(20000,20201)
        self.requestCount = {}
        self.nextCacheSlot = 0
        self.cacheFileNames = {0: 'cache1.txt', 1:'cache2.txt', 2:'cache3.txt'}
        self.cachedResponse = {}
        self.requestTime = {}
        self.cachedTime = {}

    def addModtimeHeadrer(self,client_dict, mtime):   

        lines = client_dict["data"].splitlines()
        print "lines !!! = ", lines
        while lines[len(lines)-1] == '':
            lines.remove('')

        print "Empty lines removed"

        header =  mtime
        header = "If-Modified-Since: " + header
        lines.append(header)

        client_dict["data"] = "\r\n".join(lines) + "\r\n\r\n"
        print "header adding funtiotn done", client_dict['data']
        return client_dict

    def getRequest(self, client_socket, address, client_dict) :
        responseData = ""

        request_tuple = (client_dict["port"], client_dict["file"])

        try:
            if request_tuple in self.cachedTime.keys():
                print "inside iifff"
                client_dict = self.addModtimeHeadrer(client_dict, self.cachedTime[request_tuple]) 
                print "after adding header"


            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((client_dict['url'], int(client_dict['port'])))
            server_socket.send(client_dict['data']) 

            response = server_socket.recv(self.bufferSize)
            print "RESPONSE OF SERVER", response
            # print 'MOD : ',"304 Not Modified" in response
            if self.isCached(request_tuple) and '530' not in response :
                responseData += response
                while len(response)>0 and response!=' ':
                    response = server_socket.recv(self.bufferSize)
                    responseData += response
                print "Cached version being returned"
                cacheFilename = self.cachedResponse[request_tuple]
                f = open(cacheFilename, 'r') 
                cacheFileContent = f.read()
                responseData = cacheFileContent
            else: 
                print "Live version being returned"
                responseData += response
                while len(response)>0 and response!=' ':
                    response = server_socket.recv(self.bufferSize)
                    responseData += response
                print "Requestu tuple", request_tuple
                self.doCache(request_tuple, responseData)
        
            server_socket.close() 

        except Exception as e:
            print "Error ", e
            client_socket.close()

        print "Returned:"
        print responseData
        return responseData

    def postRequest(self, client_socket, address, client_dict) :
        responseData = ""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((client_dict['url'], int(client_dict['port'])))
            server_socket.send(client_dict['data']) 

            response = server_socket.recv(self.bufferSize)
            responseData += response
            while len(response)>0 and response!=' ':
                response = server_socket.recv(self.bufferSize)
                responseData += response
            
            server_socket.close() 

        except Exception as e:
            print "Error ", e
            server_socket.close()
            client_socket.close()

        print "Returned:"
        return responseData
        
    def auth(self, key) :
        """ Checking if the server is aurthorized or not """ 
        auth_file = open(self.authfilePath, "r")
        lines = auth_file.readlines()
        lines = map(lambda x: x.replace('\n',''), lines)
        lines = map(lambda x: b64encode(x), lines)
        if key in lines:
            return True
        else:
            return False

    def isCached(self, request_tuple) :
        print "in iscached", self.cachedResponse.keys()
        print 'checll'
        if request_tuple in self.cachedResponse.keys():
            print 'truuuu'
            return True
        else:
            print 'false ::(('
            return False
    
    def doCache(self, request_tuple, response_cache):
        milis = int(round(time.time() * 1000))
        print "overall count" , self.requestCount
        # print "check if already refered", self.requestCount[request_tuple] 
        if request_tuple in self.requestCount.keys():
            if milis-self.requestTime[request_tuple]<30000:
                self.requestCount[request_tuple] += 1
            else:
                if self.requestCount[request_tuple] > 0:
                    self.requestCount[request_tuple] = 1
                    self.requestTime[request_tuple] = milis
        else:
            self.requestCount[request_tuple] = 1
            self.requestTime[request_tuple] = milis

        if self.requestCount[request_tuple] == 3:
            if len(self.cachedResponse.keys()) == 3:
                self.cachedResponse = {key:val for key, val in self.cachedResponse.items() if val != self.cacheFileNames[self.nextCacheSlot]}
            
            # response cache is the varianble to be written 
            f = open(self.cacheFileNames[self.nextCacheSlot], 'w') 
            f.write(response_cache)
            f.close()            
            
            self.cachedResponse[request_tuple] = self.cacheFileNames[self.nextCacheSlot] 
            self.cachedTime[request_tuple] = time.ctime(os.path.getmtime(self.cacheFileNames[self.nextCacheSlot]))
            self.nextCacheSlot += 1 
            self.nextCacheSlot = self.nextCacheSlot % 3 

            #write response_cache in one of the files and store it's value in cachedResponse
            self.requestCount = {key:val for key, val in self.requestCount.items() if key != request_tuple}

            return

    def parse(self, data):
        """ Parsing Client Data """ 
        datalines = data.splitlines()
        client_dict = {}
        client_dict["method"] = datalines[0].split(' ')[0]
        client_dict["host"] = datalines[0].split('/')[2]
        client_dict["url"] = client_dict["host"].split(':')[0]
        client_dict["port"] = client_dict["host"].split(':')[1]
        client_dict["file"] =  datalines[0].split('/')[3].split(' ')[0]
        auth_str = 'Basic'
        if auth_str in datalines[2] and len(datalines[2].split(': Basic ')) > 0:
            client_dict["auth"] = datalines[2].split(': Basic ')[1]
        return client_dict

    def isBlocked(self, host):
        """ Checking if the server is blocked or not """ 
        blacklist_file = open(self.blacklistfilePath, "r")
        lines = blacklist_file.readlines()
        lines = map(lambda x: x.replace('\n',''), lines)
        if host in lines:
            return True
        else:
            return False

    def oneRequest(self, socket, address, data):
        """ Handling one request """ 
        client_dict = self.parse(data)
        client_dict["data"] = data

        if int(address[1]) not in self.iiitports or address[0] not in self.allowedURL :
            socket.send("You are outside IIIT\nYou can not access IIIT files\n")
            return 

        if int(client_dict["port"]) not in self.allowedServers:
            socket.send("You can only access server inside IIIT(20000-20099) or outside IIIT(20101-20200) ")
            return

        if client_dict["method"] == 'POST':
            if self.isBlocked(client_dict['host']):
                if self.auth(client_dict["auth"]):
                    responseData = self.postRequest(socket, address, client_dict)
                    socket.send(responseData)         
                else:
                    socket.send("You are not authorized to access this server\n")
            else:
                responseData = self.postRequest(socket, address, client_dict)   
                socket.send(responseData)         
                print responseData         

        elif client_dict["method"] == 'GET':
            if self.isBlocked(client_dict['host']):
                if self.auth(client_dict["auth"]):
                    responseData = self.getRequest(socket, address, client_dict)         
                    socket.send(responseData)         
                else:
                    socket.send("You are not authorized to access this server\n")
            else:
                responseData = self.getRequest(socket, address, client_dict)         
                socket.send(responseData)         

        socket.close() 

        return 

    def runningServer(self):
        """ Running loop looking at all requests and addressing them all """ 

        try:
            proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            proxy_socket.bind(('', self.proxy_port))
            proxy_socket.listen(self.NoConnections)

        except:
            print "Error in starting server"

        while True:
            client_socket, client_addr, client_data = 0, 0, 0
            try:
                client_socket, client_addr = proxy_socket.accept()
                client_data = client_socket.recv(self.bufferSize)
                print "Proxy Server listened", client_data

                t1 = threading.Thread(target=self.oneRequest, args=(client_socket, client_addr, client_data))
                t1.start()

            except KeyboardInterrupt:
                proxy_socket.close() 
                if client_socket != 0:
                    client_socket.close() 
                print "\nShutting down"
                sys.exit()


if __name__ == '__main__':
    P = ProxyServer()
    P.proxy_port = int(sys.argv[1]) 
    P.runningServer() 






    