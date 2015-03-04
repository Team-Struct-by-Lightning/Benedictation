import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
# from nltk_test import find_nouns
import speechrec    # Put speechrec.py in the same folder
import wave
import os

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
        
    def on_message(self, message):
        print "speech-rec received message: %s" % message
        if self.recording == False and message == "start":
            self.recording = True
        if self.recording == True:
            if message == "stop":
                self.recording = False
                #self.write_message("test response %s" % message)
            else:
                # message is a wav file, fully encoded, *with headers*.
                # is it a file-like object? can Python read it? or is it a raw binary array which I must index into past the headers and use?
                #msg_wav = wave.open(message, "rb")
                #print type(message)
                message_data = str(message)[44:]    # this skips the 44-byte header and gets the data
                # write this to an open wavfile object
                
        
    def on_close(self):
        print "Connection closed."
        os.remove("speech.wav")
    
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