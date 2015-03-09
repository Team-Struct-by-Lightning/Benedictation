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
        print "in googleapi func @@@@@@@@"
        APIKEY = "AIzaSyD9JtT_kVZ0S0vKsskgxrK_WtIE1G7FAjY"
        audiotools.open(input).convert("output.flac", audiotools.FlacAudio)
        headers = {"Content-Type": "audio/x-flac;rate=44100"}
        speechfile = open("output.flac","r")
        target = "/speech-api/v2/recognize?output=json&lang=en-us&key=" + APIKEY
        request = self.connection.request("POST",target,speechfile,headers)
        
        hyp = ""
        json_result = ""
        response = self.connection.getresponse()
        if response.status == 200:
            jdata = response.read()

            lines = str(jdata).splitlines()
            if(len(lines) > 1):
                json_result = lines[1]
                try:
                    decoded = json.loads(json_result)
                    # pretty printing of json-formatted string
                    # print json.dumps(decoded, sort_keys=True, indent=4)
                    hyp = decoded['result'][0]['alternative'][0]['transcript']
                    print "speech rec result: ", hyp
                except (ValueError, KeyError, TypeError):
                    print "JSON format error"
        
        speechfile.close()
        os.remove("output.flac")
        return hyp


if __name__ == "__main__":
    sr = SpeechRecognizer()
    text = sr.recognize("output219.wav")
    print text        
