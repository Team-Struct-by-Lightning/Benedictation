import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
# from nltk_test import find_nouns
import speechrec    # Put speechrec.py in the same folder
import wave
import os
from random import randint
from speechrec import recognize

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
        self.recording = False
        self.text = ""
        
    def on_message(self, message):
        #print "speech-rec received message: %s" % message
        if self.recording == False and message == "start":
            self.recording = True
            return

        if self.recording == True:
            if message == "stop":
                self.recording = False
            else:
                outfilename = 'output' + str(randint(0,500)) + '.wav'
                f = open(outfilename , 'w')
                f.write(message)
                
                print "wrote to file"
                text = recognize(outfilename)
                self.write_message(text)
                os.remove(outfilename)
     
                
    def on_close(self):
        print "Connection closed."
        # os.remove("speech.wav")
    
    def check_origin(self,origin):
        return True
    
    
application = tornado.web.Application([
    (r"/hello", WSHandler),
    (r"/recognize", SpeechWSHandler)
])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()