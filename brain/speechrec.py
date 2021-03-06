# speechrec.py -- interface to the server-side speech recognizer
# Should primarily expose one method, recognize(input), which takes the name of a wav file and returns text.
# Implementation details should be hidden, and in seperate functions, allowing for easy switching of the backend implementation if necessary.

import audiotools
import httplib
import json
import os
import yaml


class SpeechRecognizer():
    def __init__(self):
        self.host = "www.google.com"
        self.port = 80
        self.jdecode = json.JSONDecoder()

    # Recognize a piece of audio.
    # Input:  name of a .wav file: string
    # Return: hypotheses: list of strings
    def recognize(self, input):
        try:
            self.connection = httplib.HTTPConnection("www.google.com:80")        # self.connection.connect()
            return self._rec_googleapi(input)
        except Exception as e:  # Catch any errors not caught in the recognize function
            print "Error in speech recognizer: ", e.message
            return [""]         # Return an empty hypothesis list


    def _rec_googleapi(self, input):
        print "in googleapi func @@@@@@@@"
        f = open('python_api.yml')
        yml_dict_speech = yaml.safe_load(f)
        f.close()
        APIKEY = yml_dict_speech['google_speech']['api_key']
        audiotools.open(input).convert("output.flac", audiotools.FlacAudio)
        headers = {"Content-Type": "audio/x-flac;rate=44100"}
        speechfile = open("output.flac","r")
        target = "/speech-api/v2/recognize?output=json&lang=en-us&key=" + str(APIKEY)
        target = target.strip() # just in case there are leading or trailing whitespace or newlines
        request = self.connection.request("POST",target,speechfile,headers)

        hyp = ""
        json_result = ""
        try:
            response = self.connection.getresponse()
            if response.status == 200:
                lines = str(response.read()).splitlines()
                if(len(lines) > 1):
                    json_result = lines[1]

                    decoded = json.loads(json_result)
                    # pretty printing of json-formatted string
                    print json.dumps(decoded, sort_keys=True, indent=4)
                    # hyp = decoded['result'][0]['alternative'] # [0]['transcript']
                    hyp = [str(x["transcript"]) for x in decoded['result'][0]['alternative']]
                    print "speech rec result: ", hyp

            else:
                print "got this response status from google: ",response.status
                hyp = ["error, got this response status from google: " + response.status]

            return hyp
        except httplib.BadStatusLine:
            print "got bad status line error, trying to make google request again";
            self.recognize(input) # call again
        finally:
            speechfile.close()
            os.remove("output.flac")
            self.connection.close()


if __name__ == "__main__":
    sr = SpeechRecognizer()
    text = sr.recognize("output219.wav")
    print text
