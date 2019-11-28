import http.server
import urllib.parse
import json
import random
import string
import functools
import traceback

BaseHTTPServer = http.server.HTTPServer
if hasattr(http.server, 'ThreadingHTTPServer'):
    BaseHTTPServer = http.server.ThreadingHTTPServer


def random_string(length, character_set=string.ascii_letters+string.digits):
    return ''.join(random.choice(character_set) for _ in range(length))


class BaseHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    SESSION_ID_LENGTH = 32
    PUBLIC_SESSION_STORE = dict()

    def __init__(self, *args, **kwargs):
        if 'handlers' in kwargs:
            self.__handlers = kwargs['handlers']
            del kwargs['handlers']
        else:
            self.__handlers = dict()
        if 'session_store' in kwargs:
            self.__session_store = kwargs['session_store']
            del kwargs['session_store']
        else:
            self.__session_store = BaseHTTPRequestHandler.PUBLIC_SESSION_STORE
        self.__response_status_code = 500
        self.__response_headers = list()
        self.__response = bytes()
        self.request_payload = None
        self.session = None
        super().__init__(*args, **kwargs)

    def __parse_path(self):
        url = urllib.parse.urlparse(self.path)
        self.path = url.path
        self.params = {k: v for k, v in urllib.parse.parse_qsl(url.query)}
        self.fragment = url.fragment

    def __parse_cookies(self):
        all_cookies_header = self.headers.get_all('Cookie')
        if all_cookies_header is None:
            all_cookies_header = []

        cookies_str_iter = (cookie_str.strip() for cookies_str in all_cookies_header for cookie_str in cookies_str.split(';'))
        cookies_kv_iter = (cookie_str.split('=', 1) for cookie_str in cookies_str_iter)
        cookies_kv_iter = filter(lambda x: len(x) > 0 and len(x[0]) > 0, cookies_kv_iter)
        cookies_normalized_kv_iter = (cookie_kv + [None] for cookie_kv in cookies_kv_iter)
        cookies = {urllib.parse.unquote(k): (
            urllib.parse.unquote(v) if v is not None else None) for k, v, *_ in cookies_normalized_kv_iter}

        self.cookies = cookies

    def __read_request_payload(self):
        try:
            content_length = int(self.headers.get('Content-Length'))
        except (TypeError, ValueError):
            self.set_status(411)
            return False
        self.request_payload = self.rfile.read(content_length)
        return True

    def __parse_request_payload(self):
        if self.request_payload is None:
            return

        content_type = self.headers.get('Content-Type')
        params = None

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
        self.log_request(code=code, size=len(self.__response))
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

        # reset session
        self.session = None
        # reset request_payload
        self.request_payload = None

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
        if 'GET' not in self.__handlers:
            self.set_status(405)
        elif self.path in self.__handlers['GET']:
            try:
                self.__handlers['GET'][self.path].__get__(self, self.__class__)()
            except:
                traceback.print_exc()
        else:
            self.set_status(404)
        self.__send_response()

    def do_POST(self):
        self.__parse_path()
        self.__parse_cookies()
        
        if self.__read_request_payload():
            self.__parse_request_payload()
            if 'POST' not in self.__handlers:
                self.set_status(405)
            elif self.path in self.__handlers['POST']:
                try:
                    self.__handlers['POST'][self.path].__get__(self, self.__class__)()
                except:
                    traceback.print_exc()
            else:
                self.set_status(404)

        self.__send_response()

    def dump_info(self):
        self.append_response(json.dumps({
            'requestline': self.requestline,
            'command': self.command,
            'path': self.path,
            'fragment': self.fragment,
            'request_version': self.request_version,
            'headers': list(self.headers.raw_items()),
            'cookies': self.cookies,
            'request_payload': str(self.request_payload) if self.request_payload is not None else None,
            'params': self.params,
        }, indent='  '))
        self.append_headers('Content-Type', 'application/json')
        self.set_status(501)

class BaseHTTPRequestHandlerPool:
    def __init__(self, handler_class=BaseHTTPRequestHandler):
        self.handlers = dict()
        self.session_store = dict()
        self.handler_class = handler_class
        self._setup_handlers()

    def __call__(self, *args, **kwargs):
        kwargs['handlers'] = self.handlers
        kwargs['session_store'] = self.session_store
        return self.handler_class(*args, **kwargs)

    def _setup_handlers(self):
        self.set_handler('GET', '/', BaseHTTPRequestHandler.dump_info)
        self.set_handler('POST', '/', BaseHTTPRequestHandler.dump_info)

    def set_handler(self, command, path, callable_handler):
        if command not in self.handlers:
            self.handlers[command] = dict()
        self.handlers[command][path] = callable_handler

class HTTPServer(BaseHTTPServer):
    def __init__(self, server_address, request_handler_class=BaseHTTPRequestHandlerPool):
        super().__init__(server_address, request_handler_class)


def main(bind_address, port, handler_pool_class=BaseHTTPRequestHandlerPool):
    listening_address = bind_address, port
    handler_pool = handler_pool_class()
    http_server = HTTPServer(listening_address, handler_pool)
    http_server.serve_forever()
