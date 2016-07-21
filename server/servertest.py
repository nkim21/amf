from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import sys
from fleet import Fleet
import simplejson
import threading

fleet = Fleet()
app_dict = {}

def connect_and_run(id):
    fleet.connect(id)
    # fleet.run(id)

class Handler(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.end_headers()

        app_id = ''
        drone_id = app_dict[app_id]
        lat, lon = fleet.get_location(drone_id)

        message = "{}, {}".format(lat, lon)

        self.wfile.write(message)
        self.wfile.write('\n')
        return

    def do_POST(self):
        self._set_headers()
        print "@@@@@ start POST"
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))

        self.send_response(200)
        self.end_headers()
        
        data = simplejson.loads(self.data_string)

        print "{}".format(data)
        lat = data['latitude']
        lon = data['longitude']

        droneid = fleet.request(lat, lon)
        if droneid is not -1:
            app_dict[data['instanceID']] = droneid
            # fleet.connect(droneid)
            message =  "{}".format(data['address'])

            t = threading.Thread(target=connect_and_run, args=(droneid,))
            t.start()
        else:
            message = "-1"

        self.wfile.write(message)
        self.wfile.write('\n')
        print "@@@@@ end POST"
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':
    if sys.argv[1:]:
        port = int(sys.argv[1])
    else:
        port = 8080
    # server = ThreadedHTTPServer(('localhost', port), Handler)
    # server = ThreadedHTTPServer(('104.194.103.165', port), Handler)
    server = ThreadedHTTPServer(('', port), Handler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()