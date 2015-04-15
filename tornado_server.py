import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
from json import loads
from urllib2 import urlopen
# from nltk_test import find_nouns
import speechrec    # Put speechrec.py in the same folder
import wave
import os
from random import randint
from nltk_test import schedule_meeting
import speechrec
import socket
import json

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'new connection'
        # self.write_message("Hello from the Python Server!")

    def on_message(self, message):
        print 'message received %s' % message
        nouns_list = find_nouns(message)
        for noun in nouns_list:
            self.write_message(noun)

    def on_close(self):
        print 'connection closed'
    def check_origin(self,origin):
        #parsed_origin = urllib.parse.urlparse(origin)
        #print parsed_origin
        return True

# Handle audio data sent to /recognize.
class SpeechWSHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        print "New connection to speech recognizer opened"
        self.recognizer = speechrec.SpeechRecognizer()
        print self.recognizer
        self.recording = False
        self.text = ""

    def on_message(self, message):
        #print "speech-rec received message: %s" % message
        if self.recording == False and message == "start":
            self.recording = True
            return

        if self.recording == True:
            # print "in recording true @@@@@"
            if message == "stop":
                # print "we are about to stop @@@@@"
                self.recording = False
            elif message != "start":
                # print "we are about to write @@@@@"
                outfilename = 'output' + str(randint(0,500)) + '.wav'
                f = open(outfilename , 'w')
                f.write(message)
                f.close()

                print "wrote to file"
                text = self.recognizer.recognize(outfilename).lower()
                
                if schedule_meeting(text):
                    print 'adding to the calender'
                    text = '{"attendees": [{"email": "trevor.frese@gmail.com"},{"email": "britt.k.christy@gmail.com"},{"email": "jtmurphy@gmail.com"}],"api_type": "calendar","start": {"datetime": "2015-04-13T10:00:00","timezone": "America/Los_Angeles"},"end": {"datetime": "2015-04-15T11:00:00","timezone": "America/Los_Angeles"},"location": "House de Gus","summary": "Epic Circle Jerk"}'
                if "search" in text:
                    text = '{"api_type": "wikipedia", "query": "peanut butter"}'
                if "wolfram" in text:
                    text = '{"api_type": "wolfram", "query": "isla vista weather"}' 
                self.write_message(text)
                os.remove(outfilename)
                print "we have finished writing @@@@@"


    def on_close(self):
        print "Connection closed."

    def check_origin(self,origin):
        return True


application = tornado.web.Application([
    (r"/hello", WSHandler),
    (r"/recognize", SpeechWSHandler)
])

if __name__ == "__main__":

    # This line will connect to the website, read its contents
    # and parse the JSON output

    data = loads(urlopen("http://httpbin.org/ip").read())
    '''if "local" or "ubuntu" not in str(socket.gethostname()):

        benny_ssl_options = {
            "certfile": os.path.join("/etc/nginx/ssl/benedictation_io/ssl-bundle.crt"),
            "keyfile": os.path.join("/etc/nginx/ssl/benedictation_io/benedictation-private-key-file.pem")
        }
        http_server = tornado.httpserver.HTTPServer(application,xheaders=True,ssl_options=benny_ssl_options)
    else:'''
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
