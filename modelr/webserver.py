'''
Created on Apr 30, 2012

@author: sean
'''
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from argparse import ArgumentParser
from os import curdir, sep, listdir
from os.path import isfile, join, dirname
import string
import cgi
import time
from urlparse import urlparse, parse_qs
from modelr.urlargparse import SendHelp, ArgumentError


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        uri = urlparse(self.path)
        
        parameters = parse_qs(uri.query)
        
        if uri.path != '/plot':
            self.send_error(404, 'File Not Found: %s' % self.path)
            return
        
        script = parameters.pop('script', None)
        
        if not script or len(script) != 1:
            self.send_script_error("argument 'script' was ommitted or malformed (got %r)" % (script))
            return
        
        dirn = dirname(__file__)
        script_path = join(dirn, 'scripts', script[0])
        
        if not isfile(script_path):
            self.send_script_error("argument 'script' '%r' was is not a valid script " % (script[0],))
            return
        
        namespace = {}
        with open(script_path, 'r') as fd:
            exec fd.read() in namespace
            
        parser = namespace['create_parser']()
        
        try:
            args = parser.parse_params(parameters)
        except SendHelp as helper:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
                
            self.wfile.write(helper.html)
            return
        except ArgumentError as err:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
                
            self.wfile.write('<p><b>Error:</b> %s</p>' % (err.args[0],))
            self.wfile.write(parser.help_html)
            return
        
        run_script = namespace['run_script']
        jpeg_data = run_script(args) 
        
        self.send_response(200)
        self.send_header('Content-type', 'image/jpeg')
        self.end_headers()
            
        self.wfile.write(jpeg_data)
        
    def send_script_error(self, msg):
        
        scripts_dir = join(dirname(__file__), 'scripts')
        
        available_scripts = '<ul>\n'
        for script in listdir(scripts_dir):
            if script == '__init__.py':
                continue
            elif not script.endswith('.py'):
                continue
            
            namespace = {}
            with open(join(scripts_dir, script), 'r') as fd:
                exec fd.read() in namespace
            short_doc = namespace.get('short_description', 'No doc')
            available_scripts += '<li><b>%s</b> -- %s</li>\n' % (script, short_doc)
            
        available_scripts += '</ul>\n'
        
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
            

        self.wfile.write('<p><b>Error:</b> %s </p> %s' % (msg, available_scripts))
        
        
        
    def do_POST(self):
        self.send_error(404, 'Post request not supportd yet: %s' % self.path)


def main():
    
    parser = ArgumentParser(description=__doc__)
    
    parser.add_argument('--host', type=str, default='')
    parser.add_argument('-p', '--port', type=int, default=80)

    args = parser.parse_args()
    
    try:
        server = HTTPServer((args.host, args.port), MyHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()


if __name__ == '__main__':
    main()
    
