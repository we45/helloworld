from flask import Flask,request,Response,render_template,redirect
# from urlparse import urlparse
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.web import FallbackHandler, RequestHandler, Application
from tornado.websocket import WebSocketHandler
import json
import redis
import urllib
import os
app = Flask(__name__, template_folder='templates')

redis_host = os.environ.get('APP_HOST', None)
redis_port = 6379

# rs = redis.Redis(redis_host)
# try:
#     response = rs.client_list()
# except redis.ConnectionError:
#     response = "error"
#

db = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)


@app.route('/',methods = ['GET', 'POST'])
def home():
    if request.method == 'GET':
        if (db.exists('id') == False):
            db.set('id', '0')
        keys = db.keys()
        val = db.mget(keys)
        data = dict(zip(keys, val))
        return render_template('home.html',data=data)
    elif request.method == 'POST':
        todo = request.values.get('todo', None)
        db.set(str(db.get('id')), todo)
        db.incr('id')
        return redirect('/')
    else:
        return 'Page Not Found'


@app.route('/ssrf')
def ssrf():
    if request.method == 'GET':
        if request.args.get('url'):
            url = request.args.get('url')
            # host = urlparse(url).hostname
            # if host:
            #     return 'host is {0}'.format(host)
            # else:
            #     return urllib.urlopen(url).read()
            response  = urllib.urlopen(url)
            html = response.read()
            title = "Request URL is {0}  and below fid the requested URL Response".format(url)
            return Response('{0},{1}'.format(title,html))
        return 'Try SSRF!'
    return 'Try SSRF!'


class WSHandler(WebSocketHandler):
    def open(self):
        print 'new connection'
        self.write_message(json.dumps(dict(output="Hello World")))

    def on_message(self, incoming):
        print 'message received %s' % incoming

        text = json.loads(incoming).get('text', None)
        msg = text if text else 'Sorry could you repeat?'

        response = json.dumps(dict(output='Parrot: {0}'.format(msg)))
        self.write_message(response)

    def on_close(self):
        print 'connection closed'

if __name__ == '__main__':
    wsgi_app = WSGIContainer(app)

    application = Application([
        (r'/websocket', WSHandler),
        (r'.*', FallbackHandler, dict(fallback=wsgi_app))
    ])
    application.listen(80)
    IOLoop.instance().start()
