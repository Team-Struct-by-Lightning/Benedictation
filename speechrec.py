# speechrec.py -- interface to the server-side speech recognizer
# Should primarily expose one method, recognize(input), which takes the name of a wav file and returns text.
# Implementation details should be hidden, and in seperate functions, allowing for easy switching of the backend implementation if necessary.

import audiotools
import httplib
import json
import os

class SpeechRecognizer():
    def __init__(self):
        self.host = "www.google.com"
        self.port = 80
        self.connection = httplib.HTTPConnection("www.google.com:80")        # self.connection.connect()
        self.jdecode = json.JSONDecoder()
    
    # Recognize a piece of audio.
    # Input: a .wav filename, string
    # Return: recognition output, string
    def recognize(self, input):
        return self._rec_googleapi(input)
        
    def _rec_googleapi(self, input):
        APIKEY = "AIzaSyD9JtT_kVZ0S0vKsskgxrK_WtIE1G7FAjY"
        audiotools.open(input).convert("32bittest.flac", audiotools.FlacAudio)
        headers = {"Content-Type": "audio/x-flac;rate=44100"}
        speechfile = open("32bittest.flac","r")
        target = "/speech-api/v2/recognize?output=json&lang=en-us&key=" + APIKEY
        request = self.connection.request("POST",target,speechfile,headers)
        
        hyp = ""
        response = self.connection.getresponse()
        if response.status == 200:
            jdata = str(response.read()) 
            print "raw response: ",jdata

            # Should return a string of JSON, in the form of a bytes literal (in Python 3), which is then converted to string
            # data = self.jdecode.raw_decode(jdata)
            # print data
            # hyp = data.hypotheses[0].utterance
        
        speechfile.close()
        # os.remove("speech.flac")
        return hyp

if __name__ == "__main__":
    sr = SpeechRecognizer()
    text = sr.recognize("32bittest.wav")
    print text        