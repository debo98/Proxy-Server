                                       HTTP Proxy Server

Roll Number : 20171092
Roll Number : 20171088


Proxy Server Default Port : 20100
IIIT Ports (Allowed) : 20000-20099
Outside Server Ports : 20101-20200

1. Request(GET) server without proxy server
-> python server.py {PORT}
-> curl 127.0.0.1:{PORT}/


                                        GET Request Handling
--->Get Requests Allow Caching
--->Get Requests do not allow binary files
1. Request(GET) from server through proxy server
-> python server/server.py {PORT}
-> python proxy/proxy_server.py {PROXY_PORT}
-> `curl --request GET --proxy 127.0.0.1:{PROXY_PORT} --local-port 20000-20099 127.0.0.1:{PORT}/`

2. Request(GET) from server through proxy server - Access Blocked server through Authentication
-> python server.py {PORT}
-> python proxy/proxy_server.py {PROXY_PORT}
-> `curl --request GET -u {username}:{password} --proxy 127.0.0.1:{PROXY_PORT} --local-port 20000-20099 127.0.0.1:{PORT}/sampledata`

                                        POST Request Handling
--->Post Requests are not supposed to do caching
--->Post Requests allow both binary and ascii files


1. Request(POST) from server through proxy server
-> python server.py {PORT}
-> python proxy/proxy_server.py {PROXY_PORT}
-> `curl --request POST --proxy 127.0.0.1:{PROXY_PORT} --local-port 20000-20099 127.0.0.1:{PORT}/sampledata`

2. Request(POST) from server through proxy server - Access Blocked server through Authentication
-> python server.py {PORT}
-> python proxy/proxy_server.py {PROXY_PORT}
-> `curl --request POST -u {username}:{password} --proxy 127.0.0.1:{PROXY_PORT} --local-port 20000-20099 127.0.0.1:{PORT}/sampledata`

3. Getting binary file using POST 
-> `curl --request POST --proxy 127.0.0.1:20100 --local-port 20000-20099 127.0.0.1:20008/2.data --output temp.txt`
