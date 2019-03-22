import SimpleHTTPServer
import SocketServer
import sys
import mimetypes
import os
import time

PORT = int(sys.argv[1])


class IsFileBinary:
	READ_BYTES = 512
	CHAR_THRESHOLD = 0.3
	TEXT_CHARACTERS = ''.join(
		[chr(code) for code in range(32,127)] +
		list('\b\f\n\r\t')
	)

	def test(self,file_path):
		# read chunk of file
		fh = open(file_path,'r')
		file_data = fh.read(IsFileBinary.READ_BYTES)
		fh.close()

		# store chunk length read
		data_length = len(file_data)
		if (not data_length):
			# empty files considered text
			return False

		if ('\x00' in file_data):
			# file containing null bytes is binary
			return True

		# remove all text characters from file chunk, get remaining length
		binary_length = len(file_data.translate(None,IsFileBinary.TEXT_CHARACTERS))

		# if percentage of binary characters above threshold, binary file
		return (
			(float(binary_length) / data_length) >=
			IsFileBinary.CHAR_THRESHOLD
)

class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    # def send_head(self):
    #     print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    #     if self.command != "POST" and self.headers.get('If-Modified-Since', None):
    #         filename = self.path.strip("/")
    #         if os.path.isfile(filename):
    #             a = time.strptime(time.ctime(os.path.getmtime(filename)), "%a %b %d %H:%M:%S %Y")
    #             b = 0
    #             # b = time.strptime(self.headers.get('If-Modified-Since', None), "%a %b %d %H:%M:%S %Y")
    #             print 'a', a, 'b', b
    #             if a < b:
    #                 self.send_response(304)
    #                 self.send_header('Cache-control', 'must-revalidate')
    #                 self.end_headers()
    #                 return None
    #     SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)
    #     return

    def do_POST(self):
        filename = self.path.split('/')
        try:
            fp = open(filename[-1],'r')
            fileContents = fp.read()
            print fileContents
            self.send_response(200)
            self.end_headers()
            self.wfile.write(fileContents)
            fp.close()
        except:
            self.send_error(404)            
            self.end_headers()
            self.wfile.write("File not found\n\n")

        SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)
        return

    def do_GET(self):
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        filename = self.path.split('/')
        try:
            fp = open(filename[-1],'r')
        except:
            self.send_error(404)            
            self.end_headers()
            self.wfile.write("File not found\n\n")  
            SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)
            return 

        print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", self.headers.get('If-Modified-Since')
        if self.headers.get('If-Modified-Since', None): 
            if os.path.isfile(filename[-1]):
                print "inside"
                a = time.ctime(os.path.getmtime(filename[-1]))
                b = self.headers.get('If-Modified-Since', None)
                # b > a means b is older
                print 'a:', a, 'b:', b, 'a<b', a<b
                if a > b:
                    print "INSIDE SECONF IF IN PROXY SERVER"
                    self.send_response(530)
                    fileContents = fp.read()
                    self.send_header('Cache-control', 'must-revalidate')
                    self.end_headers()
                    self.wfile.write(fileContents)
                    fp.close()
                    return None

        is_file_binary = IsFileBinary()

        if is_file_binary.test(filename[-1]) == False :
            fileContents = fp.read()
            print fileContents
            self.send_response(200)
            self.end_headers()
            self.wfile.write(fileContents)
            fp.close()
        else :
            self.send_error(404)            
            self.end_headers()
            self.wfile.write("Binary file cannot be sent\n\n")

        SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)
        return

httpd = SocketServer.TCPServer(("", PORT), Handler)
httpd.allow_reuse_address = True
print "serving at port", PORT
httpd.serve_forever()