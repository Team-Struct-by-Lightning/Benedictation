import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
import json
from json import loads
from urllib2 import urlopen
import httplib
import email_class
import wave
import os
import random
import socket


#SciKit Learn Library Imports/Dependencies
import numpy as np
import random
from sklearn.naive_bayes import BernoulliNB
from brain.nlp import *
from query_training_set import *

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path


# Import the brain!
import brain.speechrec as speechrec
from brain.nlp import *

from brain.query_categorization import *

class EmailWSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print "new connection to email recognizer opened"
        self.email = email_class.email_sender()

    def on_message(self, message):
        try:
            json_email = json.loads(message)
            # pretty printing of json-formatted string
            print json.dumps(message, sort_keys=True, indent=4)
            # hyp = decoded['result'][0]['alternative'][0]['transcript']
            self.email.send_email(json_email['send_name'], json_email['send_email'], json_email['recipient_email'], json_email['email_type'])
        except Exception as e:
            print e.message

    def on_close(self):
        print "Connection closed."

    def check_origin(self,origin):
        return True

# Handle audio data sent to /recognize.
class SpeechWSHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        print "New connection to speech recognizer opened"
        self.recognizer = speechrec.SpeechRecognizer()

    def on_message(self, message):
        text = None
        try:
            outfilename = 'output' + hex(random.getrandbits(128))[2:-1] + '.wav'
            f = open(outfilename , 'w')
            f.write(message)
            f.close()

            print "wrote to file"
            text = self.recognizer.recognize(outfilename)   # This should always return something
            os.remove(outfilename)                          # an empty hyp [""] if nothing found

            print text
            if text:
                for x in text:
                    if x != "":
                        text = predict_api_type(api_predictor, x)
                        break
                    else:
                        text = '{"api_type": "google", "query": "", "noun_phrase": ""}'
            else:
                text = '{"api_type": "google", "query": "", "noun_phrase": ""}'

        except Exception as e:
            print e.message
            text = '{"api_type": "google", "query": "", "noun_phrase": ""}'

        if not text:
            text = '{"api_type": "google", "query": "", "noun_phrase": ""}'
        self.write_message(text)
        print "we have finished writing @@@@@"

    def on_close(self):
        print "Connection closed."

    def check_origin(self,origin):
        return True

# Handle audio data sent to /recognize_test.
class SpeechWSHandler_Test(tornado.websocket.WebSocketHandler):

    def open(self):
        print "New connection to speech recognizer opened"
        self.recognizer = speechrec.SpeechRecognizer()

    def on_message(self, message):
        text = None
        try:
            text = [message]
            if text:
                for x in text:
                    if x != "":
                        text = predict_api_type(api_predictor, x)
                        break
                    else:
                        text = '{"api_type": "google", "query": "", "noun_phrase": ""}'
            else:
                text = '{"api_type": "google", "query": "", "noun_phrase": ""}'

        except Exception as e:
            print e.message
            text = '{"api_type": "google", "query": "", "noun_phrase": ""}'

        if not text:
            text = '{"api_type": "google", "query": "", "noun_phrase": ""}'
        self.write_message(text)
        print "we have finished writing @@@@@"

    def on_close(self):
        print "Connection closed."

    def check_origin(self,origin):
        return True

application = tornado.web.Application([
    (r"/recognize", SpeechWSHandler),
    (r"/email", EmailWSHandler),
    (r"/recognize_test",SpeechWSHandler_Test)
])

if __name__ == "__main__":

    # This line will connect to the website, read its contents
    # and parse the JSON output

    data = loads(urlopen("http://httpbin.org/ip ").read())

    api_predictor = BernoulliNB()

    train_predictor_for_brain(api_predictor, training_set_calendar, training_set_schedule_suggest, training_set_google_calendar_show, training_set_google_docs, training_set_google_drawings, training_set_wolfram, training_set_wikipedia)

    print "predictor has been trained"
    if 'ip-172-31-10-207' in str(socket.gethostname()):   # If on AWS

        benny_ssl_options = {
            "certfile": os.path.join("/etc/nginx/ssl/benedictation_io/ssl-bundle.crt"),
            "keyfile": os.path.join("/etc/nginx/ssl/benedictation_io/benedictation-private-key-file.pem")
        }
        http_server = tornado.httpserver.HTTPServer(application,xheaders=True,ssl_options=benny_ssl_options)
    else:
        http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()