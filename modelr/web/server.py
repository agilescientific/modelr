'''
===================
modelr.web.server
===================

Main program to strat a web server.

Created on Apr 30, 2012

@author: sean
'''

from jinja2 import Environment, PackageLoader
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from argparse import ArgumentParser
from os import listdir
from os.path import isfile, join, dirname
from urlparse import urlparse, parse_qs
from modelr.web.urlargparse import SendHelp, ArgumentError, URLArgumentParser
import traceback
import json

class MyHandler(BaseHTTPRequestHandler):
    '''
    Handles a single request.
    '''
    
    def terminate(self):
        '''
        shut down the application
        '''
        print "terminate requested"
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("Shutting down...")

        self.server._BaseServer__shutdown_request = True
        
    def eval_script(self, script):
        '''
        Evaluate a script in the scripts directory.
        '''
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
            
        return namespace

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Allow', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'X-Request, X-Requested-With')
        self.send_header('Content-Length', '0')
        self.end_headers()

    
    def do_GET(self):
        '''
        handle a get request.
        '''
        print "my do GET"
        try:
            uri = urlparse(self.path)
            
            parameters = parse_qs(uri.query)
            
            if uri.path == '/terminate':
                self.terminate()
                return
            
            if uri.path == '/script_help.json':
                
                script = parameters.pop('script', None)
                namespace = self.eval_script(script)
                if namespace is None:
                    self.send_response(400)
                    self.end_headers()

                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Headers', 'X-Request, X-Requested-With')
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                script_main = namespace['run_script']
                add_arguments = namespace['add_arguments']
                short_description = namespace.get('short_description', 'No description')

                parser = URLArgumentParser(short_description)
                add_arguments(parser)
                
                self.wfile.write(parser.json_data)
                
                return
            
            if uri.path == '/available_scripts.json':
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Headers', 'X-Request, X-Requested-With')
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                all_scripts = self.get_available_scripts()
                
                data = json.dumps(all_scripts)
                
                self.wfile.write(data)
                
                return
            
            if uri.path != '/plot.jpeg':
                self.send_error(404, 'File Not Found: %s' % self.path)
                return
            
            script = parameters.pop('script', None)
            
            namespace = self.eval_script(script)
            if namespace is None:
                return
                
            script_main = namespace['run_script']
            add_arguments = namespace['add_arguments']
            short_description = namespace.get('short_description', 'No description')
            
            print "parameters", parameters
            self.run_script(script[0], script_main, add_arguments, short_description, parameters)
            
        except Exception as err:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            tb = traceback.format_exc().splitlines()
            
            tb = '</br>\n'.join(tb)
            
            self.wfile.write('<b>Python Error</b></br>')
            self.wfile.write('<div>')
            self.wfile.write(tb)
            self.wfile.write('</div>')
            
            raise
        
    def run_script(self, script, script_main, add_arguments, short_description, parameters):
        '''
        Run a script 
        
        :param script_main: the main method of the script
        :param add_arguments: poplate an argument parser
        :param short_description: a short description of the script
        :param parameters: the parameters from the get request
        '''
        parser = URLArgumentParser(short_description)
        add_arguments(parser)
        try:
            args = parser.parse_params(parameters)
        except SendHelp as helper:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            template = self.server.jenv.get_template('ScriptHelp.html')
            
            print parameters
            html = template.render(script=script, parser=parser, parameters=parameters)
            self.wfile.write(html)
            return
        except ArgumentError as err:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
                
            self.wfile.write('<p><b>Error:</b> %s</p>' % (err.args[0],))
            self.wfile.write(parser.help_html)
            return
        
        jpeg_data = script_main(args) 
        
        self.send_response(200)
        self.send_header('Content-type', 'image/jpeg')
        self.end_headers()
            
        self.wfile.write(jpeg_data)
    
    def get_available_scripts(self):
        scripts_dir = join(dirname(__file__), 'scripts')

        available_scripts = []
        for script in listdir(scripts_dir):
            try:
                if script == '__init__.py':
                    continue
                elif not script.endswith('.py'):
                    continue
                
                namespace = {}
                with open(join(scripts_dir, script), 'r') as fd:
                    exec fd.read() in namespace
                short_doc = namespace.get('short_description', 'No doc')
                
                available_scripts.append((script, short_doc))
            except:
                pass
            
        return available_scripts
            
    def send_script_error(self, msg):
        '''
        Send an error related to the script.
        '''
        
        template = self.server.jenv.get_template('ScriptError.html')
        
            
        
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = template.render(msg=msg, available_scripts=self.get_available_scripts())
        self.wfile.write(html)
        
        
    def do_POST(self):
        self.send_error(404, 'Post request not supportd yet: %s' % self.path)


def main():
    '''
    Main method starts a server and exits on 
    '''
    parser = ArgumentParser(description=__doc__)
    
    parser.add_argument('--host', type=str, default='')
    parser.add_argument('-p', '--port', type=int, default=80)

    args = parser.parse_args()
    try:
        server = HTTPServer((args.host, args.port), MyHandler)
        server.jenv = Environment(loader=PackageLoader('modelr', 'web/templates'))
        
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()


if __name__ == '__main__':
    main()
    
