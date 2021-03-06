import tornado.ioloop
import tornado.web
import tornado.websocket
import time
import struct

def start(ws):
    f = open("spreedmovie.hevc", "rb")
    while True:
        data = f.read(ws.chunk_size)
        if not data:
            print("Done!")
            ws.send_message("flush")
            break
        ws.send_message(data)
        time.sleep(1 / ws.fps)

class VideoStreamWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")
        self.chunk_size = 4096
        self.fps = 30.0
        tag = 'wsh264'
        self.send_message(struct.pack('!6s2H', tag.encode('utf-8'), 320, 160))

    # @tornado.web.asynchronous
    def on_message(self, message):
        cmd = message.split()
        if len(cmd) > 0:
            if cmd[0] == "v_002":
                start(self)
            if cmd[0] == "chunk_size":
                self.chunk_size = int(cmd[1])
            if cmd[0] == "fps":
                self.fps = float(cmd[1])

    # @tornado.web.asynchronous
    def send_message(self, data):
        self.write_message(data, binary=True)

    def check_origin(self, origin):
        return True

    def on_close(self):
        print("WebSocket closed")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        import os
        f = open("libde265_websocket.html")
        self.write(f.read())
        self.finish()

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/websocket", VideoStreamWebSocket),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': '../lib'}),
            ]
        tornado.web.Application.__init__(self, handlers)
        print("Waiting for WebSocket...")

application = Application()
application.listen(8080)
tornado.ioloop.IOLoop.instance().start()
