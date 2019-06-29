import http_server

class ExampleHTTPRequestHandler(http_server.BaseHTTPRequestHandler):
    def get_example(self):
        self.append_response('Hello World!\n')
        self.append_response('It\'s a GET example.\n')
        self.append_response('Request Header:\n')
        self.append_response(self.headers)
        self.set_status(200)

    def post_example(self):
        self.append_response('Hello World!\n')
        self.append_response('It\'s a POST example.\n')
        self.append_response('Request Header:\n')
        self.append_response(self.headers)
        self.append_response('Request Payload:\n')
        self.append_response(self.request_payload)
        self.append_headers('Content-Type', 'text/plain')
        self.set_status(200)

    def params_example(self):
        self.append_response('Parameters:\n')
        self.append_response(self.params) # self.params is type of dict
        self.append_headers('Content-Type', 'text/plain')
        self.set_status(200)

    def cookies_example(self):
        self.append_response('Cookies:\n')
        self.append_response(self.cookies)
        self.append_headers('Content-Type', 'text/plain')
        self.set_status(200)

    def session_example(self):
        self.session_start() # start new session if client didn't provide session ID
        self.session.update(self.params) # self.session is type of dict
        self.append_response('session data:\n')
        self.append_response(self.session)
        self.append_headers('Content-Type', 'text/plain')
        self.set_status(200)

class ExampleHTTPRequestHandlerPool(http_server.BaseHTTPRequestHandlerPool):
    def __init__(self, *args, **kwargs):
        super().__init__(handler_class=ExampleHTTPRequestHandler, *args, **kwargs)

    def _setup_handlers(self):
        self.set_handler('GET', '/', ExampleHTTPRequestHandler.get_example)

        self.set_handler('POST', '/', ExampleHTTPRequestHandler.post_example)

        self.set_handler('GET', '/params', ExampleHTTPRequestHandler.params_example)
        self.set_handler('POST', '/params', ExampleHTTPRequestHandler.params_example)

        self.set_handler('GET', '/cookies', ExampleHTTPRequestHandler.cookies_example)
        self.set_handler('POST', '/cookies', ExampleHTTPRequestHandler.cookies_example)

        self.set_handler('GET', '/session', ExampleHTTPRequestHandler.session_example)
        self.set_handler('POST', '/session', ExampleHTTPRequestHandler.session_example)


def main(bind_address=None, port=None):
    http_server.main(bind_address=bind_address, port=port, handler_pool_class=ExampleHTTPRequestHandlerPool)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', '-b', default='', metavar='ADDRESS',
                        help='Specify alternate bind address '
                             '[default: all interfaces]')
    parser.add_argument('port', action='store',
                        default=8000, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
    args = parser.parse_args()

    main(bind_address=args.bind, port=args.port)
