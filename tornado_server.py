import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver
from nltk_test import find_nouns
#class MainHandler(tornado.web.RequestHandler):
#	def get(self):
#		print 'yo im a get request my niggah'
#		self.write("Hello, world")

#hey = find_nouns("this is the sentence")
#print hey

class WSHandler(tornado.websocket.WebSocketHandler):
	def open(self):
		print 'new connection'
		self.write_message("Hello Evan")

	def on_message(self, message):
		print 'message received %s' % message
		nouns_list = find_nouns(message)
		for noun in nouns_list:
			self.write_message(noun)

	def on_close(self):
		print 'connection closed'
	def check_origin(self, origin):
		#parsed_origin = urllib.parse.urlparse(origin)
		#print parsed_origin
		return True

application = tornado.web.Application([
	(r"/hello", WSHandler),
])

if __name__ == "__main__":
	#application.listen(8888)
	#tornado.ioloop.IOLoop.instance().start()
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(8888)
	tornado.ioloop.IOLoop.instance().start()