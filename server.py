import http.server
import urllib.parse
import json
import random
import string
import functools
import traceback


def random_string(length, character_set=string.ascii_letters+string.digits):
    return ''.join(random.choice(character_set) for _ in range(length))


class BaseHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    SESSION_ID_LENGTH = 32

    def __init__(self, *args, get_handlers, post_handlers, session_store, **kwargs):
        self.__get_handlers = get_handlers
        self.__post_handlers = post_handlers
        self.__session_store = session_store
        self.__response_status_code = 500
        self.__response_headers = list()
        self.__response = bytes()
        super().__init__(*args, **kwargs)

    def __parse_path(self):
        url = urllib.parse.urlparse(self.path)
        self.path = url.path
        self.params = {k: v for k, v in urllib.parse.parse_qsl(url.query)}

    def __parse_cookies(self):
        all_cookies_header = self.headers.get_all('Cookie')
        if all_cookies_header is None:
            all_cookies_header = []

        cookies_str_iter = (cookie_str.strip() for cookies_str in all_cookies_header for cookie_str in cookies_str.split(';'))
        cookies_kv_iter = (cookie_str.split('=') for cookie_str in cookies_str_iter)
        cookies = {urllib.parse.unquote(k): urllib.parse.unquote(v) for k, v in cookies_kv_iter}

        self.cookies = cookies

    def __read_request_payload(self):
        try:
            content_length = int(self.headers.get('Content-Length'))
        except (TypeError, ValueError):
            content_length = -1
        self.request_payload = self.rfile.read(content_length)

    def __parse_request_payload(self):
        if self.request_payload is None:
            return

        content_type = self.headers.get('Content-Type')

        if content_type == 'application/json':
            try:
                params = json.loads(self.request_payload)
            except json.decoder.JSONDecodeError:
                params = None

        elif content_type == 'application/x-www-form-urlencoded':
            params = dict()
            for key, value in urllib.parse.parse_qsl(self.request_payload.decode()):
                params[key] = value
        
        if params is not None:
            self.params.update(params)

    # override
    def send_response(self, code, message=None):
        self.log_request(code)
        self.send_response_only(code, message=message)

    def __send_response(self):
        # send status code
        self.send_response(self.__response_status_code)
        # reset
        self.__response_status_code = 500

        # send headers
        for key, value in self.__response_headers:
            self.send_header(key, value)
        self.send_header('Content-Length', len(self.__response))
        self.end_headers()
        # reset
        self.__response_headers.clear()

        # send content
        self.wfile.write(self.__response)
        # reset
        self.__response = bytes()

    def set_status(self, status_code):
        self.__response_status_code = status_code

    def append_headers(self, key, value):
        self.__response_headers.append((key, value))

    def append_response(self, content):
        if content is None:
            return
        if isinstance(content, (bytes, bytearray)):
            pass
        elif not isinstance(content, str):
            content = str(content)
        if isinstance(content, str):
            content = content.encode()
        self.__response += content

    def new_session(self):
        session_id = random_string(BaseHTTPRequestHandler.SESSION_ID_LENGTH)
        self.__session_store[session_id] = dict()
        self.append_headers('Set-Cookie', 'session={};'.format(session_id))
        return session_id

    def session_start(self):
        if 'session' not in self.cookies:
            session_id = self.new_session()
            session_exist = False
        else:
            session_id = self.cookies['session']
            session_exist = True
            if session_id not in self.__session_store:
                session_id = self.new_session()
                session_exist = False
        self.session = self.__session_store[session_id]
        return session_exist

    def do_GET(self):
        self.__parse_path()
        self.__parse_cookies()
        if self.path in self.__get_handlers:
            try:
                self.__get_handlers[self.path].__get__(self, self.__class__)()
            except:
                traceback.print_exc()
        else:
            self.set_status(404)
        self.__send_response()

    def do_POST(self):
        self.__parse_path()
        self.__parse_cookies()
        self.__read_request_payload()
        self.__parse_request_payload()
        if self.path in self.__post_handlers:
            try:
                self.__post_handlers[self.path].__get__(self, self.__class__)()
            except:
                traceback.print_exc()
        else:
            self.set_status(404)
        self.__send_response()

class BaseHTTPRequestHandlerPool:
    def __init__(self, handler_class=BaseHTTPRequestHandler):
        self.get_handlers = dict()
        self.post_handlers = dict()
        self.session_store = dict()
        self.handler_class = handler_class
        self._setup_handlers()

    def __call__(self, *args, **kwargs):
        return self.handler_class(
            get_handlers=self.get_handlers,
            post_handlers=self.post_handlers,
            session_store=self.session_store,
            *args,
            **kwargs
        )

    def _setup_handlers(self):
        return

    def set_GET_handler(self, path, callable_handler):
        self.get_handlers[path] = callable_handler

    def set_POST_handler(self, path, callable_handler):
        self.post_handlers[path] = callable_handler

class HTTPServer(http.server.ThreadingHTTPServer):
    def __init__(self, server_address, request_handler_class=BaseHTTPRequestHandlerPool):
        super().__init__(server_address, request_handler_class)

class ExampleHTTPRequestHandler(BaseHTTPRequestHandler):
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
        self.set_status(200)

class ExampleHTTPRequestHandlerPool(BaseHTTPRequestHandlerPool):
    def __init__(self, *args, **kwargs):
        super().__init__(handler_class=ExampleHTTPRequestHandler, *args, **kwargs)

    def _setup_handlers(self):
        self.set_GET_handler('/', ExampleHTTPRequestHandler.get_example)
        self.set_POST_handler('/', ExampleHTTPRequestHandler.post_example)


def main(bind_address='0.0.0.0', port=1234):
    listening_address = bind_address, port
    handler = ExampleHTTPRequestHandlerPool()
    http_server = HTTPServer(listening_address, handler)
    http_server.serve_forever()


if __name__ == '__main__':
    main()
