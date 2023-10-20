from jinja2 import Environment, PackageLoader
from http.server import BaseHTTPRequestHandler, HTTPServer
from argparse import ArgumentParser
from os import listdir
from os.path import isfile, join, dirname

import os

from urllib.parse import urlparse, parse_qs
from modelr.web.urlargparse import SendHelp, ArgumentError, \
    URLArgumentParser
import traceback
import json
import multiprocessing as mp
import ssl
import socket
from socketserver import ThreadingMixIn

from modelr.EarthModel import EarthModel
from modelr.SeismicModel import SeismicModel
from modelr.ModelrPlot import ModelrPlot
from modelr.ForwardModel import ForwardModel
from modelr.ModelrScript import ModelrScript

import base64

# import cProfile as prof

# -*- coding: utf-8 -*-
'''
===================
modelr.web.server
===================

Main program to start a web server.

Created on Apr 30, 2012

@author: sean
'''

socket.setdefaulttimeout(6)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ This class allows to handle requests in separated threads.
        No further content needed, don't touch this. """


class MyHandler(BaseHTTPRequestHandler):
    '''
    Handles a single request.
    '''

    def terminate(self):
        '''
        shut down the application
        '''
        # "terminate requested"

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("Shutting down...".encode())

        self.server._BaseServer__shutdown_request = True

    def eval_script(self, script, script_type):
        '''
        Get the the namespace for a script.
        '''
        # If no script was passed, then tell the user
        if not script or len(script) != 1:
            # "++++++++++++++++++++++++++++++++++++"
            self.send_script_error("argument 'script' was omitted " +
                                   "or malformed (got %r)" % (script))
            return

        if script_type is None:
            # "++++++++++++++++++++++++++++++++++++"
            self.send_script_error("argument 'script_type' was omitted "
                                   "or malformed (got %r)" % (script))
            return

        # Otherwise, run the script
        dirn = dirname(__file__)
        script_path = join(dirn, 'scripts', script_type[0], script[0])

        if not isfile(script_path):
            self.send_script_error("argument 'script' '%r' was is not a "
                                   "valid script " % (script[0],))
            return

        namespace = {}
        with open(script_path, 'r') as fd:
            exec(fd.read(), namespace)

        return namespace

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Allow', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers',
                         'X-Request, X-Requested-With')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def do_GET(self):
        '''
        handle a get request.
        '''
        # "my do GET"
        try:
            uri = urlparse(self.path)
            parameters = parse_qs(uri.query)

            # super dangerous. commenting out
            # if uri.path == '/terminate':
            #    self.terminate()
            #    return

            # returns the script help
            if uri.path == '/script_help.json':

                script = parameters.pop('script', None)
                script_type = parameters.pop('type', None)

                namespace = self.eval_script(script, script_type)
                if namespace is None:
                    self.send_response(400)
                    self.end_headers()

                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Headers',
                                 'X-Request, X-Requested-With')
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                script_main = namespace['run_script']
                add_arguments = namespace['add_arguments']
                short_description = namespace.get('short_description',
                                                  'No description')

                parser = URLArgumentParser(short_description)
                add_arguments(parser)

                self.wfile.write(parser.json_data)

                return

            # list the available scripts
            if uri.path == '/available_scripts.json':
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Headers',
                                 'X-Request, X-Requested-With')
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                script_type = parameters.pop('type', None)

                all_scripts = self.get_available_scripts(script_type)

                data = json.dumps(all_scripts)

                self.wfile.write(data.encode())
                return

            # Outputs a base64 image and an auxillary json structure
            elif uri.path == '/plot.json':

                parameters = parse_qs(uri.query)
                script = parameters.pop("script", None)
                script_type = parameters.pop("type", None)

                # Get the namespace
                namespace = self.eval_script(script, script_type)
                if namespace is None:
                    return

                plot_generator = ModelrScript(parameters, namespace)

                # Run in sub-process to prevent memory hogging
                # p = mp.Process(target=self.run_script_jpg_json,
                #                args=(plot_generator,))
                # p.start()
                # p.join()
                self.run_script_jpg_json(plot_generator)

            # Outputs json data
            elif uri.path == '/data.json':
                parameters = parse_qs(uri.query)
                script = parameters.pop("script", None)
                script_type = parameters.pop("type", None)

                print("running", script, script_type)
                payload = json.loads(parameters.pop("payload")[0])

                # Get the namespace
                namespace = self.eval_script(script, script_type)
                if namespace is None:
                    return

                # payload = json.parse(parameters["payload"])
                script_main = namespace["run_script"]

                # Run in sub-process to prevent memory hogging
                # p = mp.Process(target=self.run_script_json,
                #                args=(script_main, payload))
                # p.start()
                # p.join()
                self.run_script_json(script_main, payload)

            # Output only an image
            elif uri.path == '/plot.jpeg':
                script = parameters.pop('script', None)
                script_type = parameters.pop('type', None)
                namespace = self.eval_script(script, script_type)
                if namespace is None:
                    return

                script_main = namespace['run_script']
                add_arguments = namespace['add_arguments']
                short_description = namespace.get('short_description',
                                                  'No description')
                # "parameters", parameters
                # p = mp.Process(target=self.run_script_jpg,
                #                args=(script[0], script_main,
                #                      add_arguments, short_description,
                #                      parameters))
                # p.start()
                # p.join()
                self.run_script_jpg(script[0], script_main,
                                     add_arguments, short_description,
                                     parameters)

            else:
                self.send_error(404, 'File Not Found: %s' % self.path)
                return

        except Exception:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            tb = traceback.format_exc().splitlines()

            tb = '</br>\n'.join(tb)

            self.wfile.write('<b>Python Error</b></br>'.encode())
            self.wfile.write('<div>'.encode())
            self.wfile.write(tb.encode())
            self.wfile.write('</div>'.encode())
            raise

    def run_script_jpg(self, script, script_main, add_arguments,
                       short_description, parameters):
        '''
        Run a script that returns a jpeg

        :param script_main: the main method of the script
        :param add_arguments: poplate an argument parser
        :param short_description: a short description of the script
        :param parameters: the parameters from the get request
        '''
        parser = URLArgumentParser(short_description)
        add_arguments(parser)
        try:
            args = parser.parse_params(parameters)
        except SendHelp:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            template = self.server.jenv.get_template('ScriptHelp.html')

            # parameters
            html = template.render(script=script, parser=parser,
                                   parameters=parameters)
            self.wfile.write(html.encode())
            return
        except ArgumentError as err:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(('<p><b>Error:</b> %s</p>'
                             % (err.args[0],)).encode())
            self.wfile.write(parser.help_html.encode())
            return

        jpeg_data = script_main(args)[0]

        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()

        self.wfile.write(jpeg_data)

        del jpeg_data

    def run_script_json(self, script, payload):

        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers',
                         'X-Request, X-Requested-With')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        data = script(payload)

        # Write response
        self.wfile.write(json.dumps(data).encode())

    def run_script_jpg_json(self, plot_generator):
        """
        Runs a script and writes out a JSON response with
        a base64 encoded jpeg and json metadata
        """

        # Run the script
        image_data, metadata = plot_generator.go()

        # Encode for http send
        encoded_image = base64.b64encode(image_data)

        # convert to json
        data = json.dumps({'data': encoded_image,
                           'metadata': metadata})

        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers',
                         'X-Request, X-Requested-With')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Write response
        self.wfile.write(data.encode())

    def get_available_scripts(self, script_type=None):
        '''
        Returns a list of all the scripts in the scripts directory.
        '''

        if script_type is None:
            # "++++++++++++++++++++++++++++++++++++"
            return

        scripts_dir = join(dirname(__file__), 'scripts',
                           script_type[0])

        available_scripts = []
        for script in listdir(scripts_dir):
            try:
                if script == '__init__.py':
                    continue
                elif not script.endswith('.py'):
                    continue

                namespace = {}
                with open(join(scripts_dir, script), 'r') as fd:
                    exec(fd.read(), namespace)


                short_doc = namespace.get('short_description',
                                          'No doc')
                # script, namespace
                available_scripts.append((script, short_doc))
            except Exception as e:
                print(script, e)

        return available_scripts

    def send_script_error(self, msg):
        '''
        Send an error related to the script.
        '''

        template = self.server.jenv.get_template('ScriptError.html')

        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        scripts = self.get_available_scripts(['scenario'])
        html = template.render(msg=msg, available_scripts=scripts)
        self.wfile.write(html.encode())

    def do_POST(self):
        """
        Calls that access datafiles
        """
        uri = urlparse(self.path)

        if uri.path == '/forward_model.json':

            content_len = int(self.headers.getheader('content-length'))
            raw_json = self.rfile.read(content_len)

            parameters = json.loads(raw_json)

            earth_script = parameters["earth_model"].pop("script",
                                                         None)
            earth_namespace = self.eval_script([earth_script],
                                               ['earth'])

            earth_model = EarthModel(parameters["earth_model"],
                                     earth_namespace)

            seismic_script = parameters["seismic_model"].pop("script",
                                                             None)

            seismic_namespace = self.eval_script([seismic_script],
                                                 ['seismic'])

            seismic_model = SeismicModel(parameters["seismic_model"]["args"],
                                         seismic_namespace)

            plot_script = parameters["plots"].pop("script", None)
            plot_namespace = self.eval_script([plot_script],
                                              ['plots'])

            plots = ModelrPlot(parameters["plots"]["args"],
                               plot_namespace)

            forward_model = ForwardModel(earth_model, seismic_model,
                                         plots)

            # prof.runctx('self.run_json(forward_model)',
            #            {'self': self, 'forward_model':forward_model},
            #            {},
            #            'profile.test')

            # p = mp.Process(target=self.run_script_jpg_json,
            #                args=(forward_model,))

            # p.start()
            # p.join()
            self.run_script_jpg_json(forward_model)

            return

        elif (uri.path == '/delete_model'):

            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            content_len = int(self.headers.getheader('content-length'))
            raw_json = self.rfile.read(content_len)

            parameters = json.loads(raw_json)
            os.remove(str(parameters["filename"]))

            return

        self.send_error(404, 'Post request not supportd yet: %s'
                        % self.path)

# Locations of the PEM files for SSL
# If this doesn't work, an alternative would be to store the
# full chain including the private key, as described here:
# http://www.digicert.com/ssl-support/pem-ssl-creation.htm
# CERTFILE = '/etc/ssl/modelr/public.pem'
# KEYFILE = '/etc/ssl/private/private.pem'
CERTFILE = 'cert.pem'
KEYFILE = 'key.pem'


def main():
    '''
    Main method starts a server and exits on
    '''
    parser = ArgumentParser(description=__doc__)

    parser.add_argument('--host', type=str, default='')
    parser.add_argument('-p', '--port', type=int, default=80)

    parser.add_argument('--local', type=bool, default=False)
    args = parser.parse_args()
    try:
        # This provides SSL, serving over HTTPS.
        # This approach will not allow service over HTTP.
        # I think we should allow both, since there is no
        # real reason for modelr-server to be secure.
        # I don't know if we need to check the certificate
        # on the client side too, or if doing it this way
        # will satisfy the browser and that's enough.

        if not args.local:
            server = ThreadedHTTPServer((args.host, args.port), MyHandler)

            # Force TLS v1.2. Not important per se, but the
            # main point is to disallow SSL v3, which is insecure.
            # I think we're supposed to load certs to the context,
            # but if this doesn't work we can put that bit back
            # in the socket wrapping part.
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            context.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE)

            server.socket = context.wrap_socket(server.socket,
                                                server_side=True)
            server.socket.settimeout(0.0)

        else:
            server = HTTPServer((args.host, args.port), MyHandler)

        server.jenv = Environment(loader=PackageLoader('modelr',
                                                       'web/templates'))

        print('started httpserver...')
        server.serve_forever()

    except KeyboardInterrupt:
        print('^C received, shutting down server')
        server.socket.close()


if __name__ == '__main__':
    main()
