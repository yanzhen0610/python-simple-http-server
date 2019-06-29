# python-simple-http-server

This is made for some simple cases. For example, mocking third party API for testing.

The default listening address is `0.0.0.0:8000`, modify the main function to change.

**no extra packages required**, just run with `python3 http_server.py [-h] [--bind ADDRESS] [port]` or `python3 example.py [-h] [--bind ADDRESS] [port]` to run example

`HTTPServer` is conditionally inherit from `http.server.ThreadingHTTPServer` if your python version is >= `3.7`

**Note:** python3 also provided file based HTTP server, start with `python3 -m http.server <port>`

## How to use?

### steps

1. inherit `http_server.BaseHTTPRequestHandler` and write your handlers
2. inherit `http_server.BaseHTTPRequestHandlerPool` and override method `_setup_handlers()`
3. make an instance of your class which inherited from `http_server.BaseHTTPRequestHandlerPool`
4. pass the instance to `http_server.HTTPServer` as `request_handler_class` and make an instance
5. call the method `serve_forever()` from your `http_server.HTTPServer` instance

### variables and methods

#### variables

- `self.requestline`

- `self.command`

- `self.path`

- `self.fragment`

- `self.request_version`

- `self.headers`
  
    returned from `http.client.parse_headers`
    
    **common methods**
    
    - `get()`
    
    - `get_all()`

    - `__get_item__()`
    
- `self.cookies`
  
    read from headers `Cookie` and parse into key value dictionary
    
- `self.request_payload`
  
    read from POST payload if client has valid content length
    
- `self.params`
  
    parse from request query(url after `?` and before `#`) and parse from POST payload if the content type is `application/json` or `application/x-www-form-urlencoded`

#### methods

- `self.append_content(content)`

    append the content that will responses to client

    the header `Content-Length` is depends on appended contents

    type `bytes` will be appended directly

    type `str` will be encoded to `utf8`

    other types will use `str(obj)` to convert to str then encoded to `utf8`

- `self.append_header(keyword, value)`
  
    append the header that will responses to client
    
- `self.set_status(code)`
  
    set the response status code

## `HTTPServer` conditionally inherit

```python
BaseHTTPServer = http.server.HTTPServer
if hasattr(http.server, 'ThreadingHTTPServer'):
    BaseHTTPServer = http.server.ThreadingHTTPServer

class HTTPServer(BaseHTTPServer):
    def __init__(self, server_address, request_handler_class=BaseHTTPRequestHandlerPool):
        super().__init__(server_address, request_handler_class)
```

## run

```shell
python3 server.py
```

## example

### GET

#### code

```python
class ExampleHTTPRequestHandler(http_server.BaseHTTPRequestHandler):
    def get_example(self):
        self.append_response('Hello World!\n')
        self.append_response('It\'s a GET example.\n')
        self.append_response('Request Header:\n')
        self.append_response(self.headers)
        self.set_status(200)

class ExampleHTTPRequestHandlerPool(http_server.BaseHTTPRequestHandlerPool):
    def __init__(self, *args, **kwargs):
        super().__init__(handler_class=ExampleHTTPRequestHandler, *args, **kwargs)

    def _setup_handlers(self):
        self.set_handler('GET', '/', ExampleHTTPRequestHandler.get_example)
```

#### curl

```shell
curl localhost:8000 -v
```

#### output

```plain
* Rebuilt URL to: localhost:8000/
*   Trying ::1...
* TCP_NODELAY set
* Connection failed
* connect to ::1 port 8000 failed: Connection refused
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 8000 (#0)
> GET / HTTP/1.1
> Host: localhost:8000
> User-Agent: curl/7.54.0
> Accept: */*
> 
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Content-Length: 107
< 
Hello World!
It's a GET example.
Request Header:
Host: localhost:8000
User-Agent: curl/7.54.0
Accept: */*

* Closing connection 0
```

### POST

#### code

```python
class ExampleHTTPRequestHandler(http_server.BaseHTTPRequestHandler):
    def post_example(self):
        self.append_response('Hello World!\n')
        self.append_response('It\'s a POST example.\n')
        self.append_response('Request Header:\n')
        self.append_response(self.headers)
        self.append_response('Request Payload:\n')
        self.append_response(self.request_payload)
        self.set_status(200)

class ExampleHTTPRequestHandlerPool(http_server.BaseHTTPRequestHandlerPool):
    def __init__(self, *args, **kwargs):
        super().__init__(handler_class=ExampleHTTPRequestHandler, *args, **kwargs)

    def _setup_handlers(self):
        self.set_handler('POST', '/', ExampleHTTPRequestHandler.post_example)
```

#### curl

```shell
curl localhost:8000 -X POST -H 'Content-Type: application/json' -d '{"key": "value"}' -v
```

#### output

```plain
Note: Unnecessary use of -X or --request, POST is already inferred.
* Rebuilt URL to: localhost:8000/
*   Trying ::1...
* TCP_NODELAY set
* Connection failed
* connect to ::1 port 8000 failed: Connection refused
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 8000 (#0)
> POST / HTTP/1.1
> Host: localhost:8000
> User-Agent: curl/7.54.0
> Accept: */*
> Content-Type: application/json
> Content-Length: 16
> 
* upload completely sent off: 16 out of 16 bytes
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Content-Length: 191
< 
Hello World!
It's a POST example.
Request Header:
Host: localhost:8000
User-Agent: curl/7.54.0
Accept: */*
Content-Type: application/json
Content-Length: 16

Request Payload:
* Closing connection 0
{"key": "value"}
```

### with parameters

#### code

```python
class ExampleHTTPRequestHandler(http_server.BaseHTTPRequestHandler):
    def params_example(self):
        self.append_response('Parameters:\n')
        self.append_response(self.params) # self.params is type of dict

class ExampleHTTPRequestHandlerPool(http_server.BaseHTTPRequestHandlerPool):
    def __init__(self, *args, **kwargs):
        super().__init__(handler_class=ExampleHTTPRequestHandler, *args, **kwargs)

    def _setup_handlers(self):
        self.set_handler('GET', '/params', ExampleHTTPRequestHandler.params_example)
        self.set_handler('POST', '/params', ExampleHTTPRequestHandler.params_example)
```

#### curl

```shell
curl 'localhost:8000/params?a=b&c=d&url=https%3A//github.com/yanzhen0610/python-simple-http-server' -X POST -H 'Content-Type: application/json' -d '{"key": "value"}' -v
```

#### output

```plain
Note: Unnecessary use of -X or --request, POST is already inferred.
*   Trying ::1...
* TCP_NODELAY set
* Connection failed
* connect to ::1 port 8000 failed: Connection refused
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 8000 (#0)
> POST /params?a=b&c=d&url=https%3A//github.com/yanzhen0610/python-simple-http-server HTTP/1.1
> Host: localhost:8000
> User-Agent: curl/7.54.0
> Accept: */*
> Content-Type: application/json
> Content-Length: 16
> 
* upload completely sent off: 16 out of 16 bytes
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Content-Length: 115
< 
Parameters:
* Closing connection 0
{'a': 'b', 'c': 'd', 'url': 'https://github.com/yanzhen0610/python-simple-http-server', 'key': 'value'}
```

### with cookies

#### code

```python
class ExampleHTTPRequestHandler(http_server.BaseHTTPRequestHandler):
    def cookies_example(self):
        self.append_response('Cookies:\n')
        self.append_response(self.cookies)
        self.append_headers('Content-Type', 'text/plain')
        self.set_status(200)

class ExampleHTTPRequestHandlerPool(http_server.BaseHTTPRequestHandlerPool):
    def __init__(self, *args, **kwargs):
        super().__init__(handler_class=ExampleHTTPRequestHandler, *args, **kwargs)

    def _setup_handlers(self):
        self.set_handler('GET', '/cookies', ExampleHTTPRequestHandler.cookies_example)
        self.set_handler('POST', '/cookies', ExampleHTTPRequestHandler.cookies_example)
```

#### curl

```shell
curl 'localhost:8000/cookies?c=d' -H 'Cookie: session=P4G4vqN11RfJIXjrmPX0QEQpxppOvYPA;a=;b' -v
```

#### output

```plain
*   Trying ::1...
* TCP_NODELAY set
* Connection failed
* connect to ::1 port 8000 failed: Connection refused
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 8000 (#0)
> GET /cookies?c=d HTTP/1.1
> Host: localhost:8000
> User-Agent: curl/7.54.0
> Accept: */*
> Cookie: session=P4G4vqN11RfJIXjrmPX0QEQpxppOvYPA;a=;b
> 
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Content-Type: text/plain
< Content-Length: 76
< 
Cookies:
* Closing connection 0
{'session': 'P4G4vqN11RfJIXjrmPX0QEQpxppOvYPA', 'a': '', 'b': None}
```

### with session

#### code

```python
class ExampleHTTPRequestHandler(http_server.BaseHTTPRequestHandler):
    def session_example(self):
        self.session_start() # start new session if client didn't provide session ID
        self.session.update(self.params) # self.session is type of dict
        self.append_response('session data:\n')
        self.append_response(self.session)
        self.set_status(200)

class ExampleHTTPRequestHandlerPool(http_server.BaseHTTPRequestHandlerPool):
    def __init__(self, *args, **kwargs):
        super().__init__(handler_class=ExampleHTTPRequestHandler, *args, **kwargs)

    def _setup_handlers(self):
        self.set_handler('GET', '/session', ExampleHTTPRequestHandler.session_example)
        self.set_handler('POST', '/session', ExampleHTTPRequestHandler.session_example)
```

#### interactive steps

##### step 1

###### curl

```shell
curl 'localhost:8000/session?a=b' -v
```

###### output

```plain
*   Trying ::1...
* TCP_NODELAY set
* Connection failed
* connect to ::1 port 8000 failed: Connection refused
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 8000 (#0)
> GET /session?a=b HTTP/1.1
> Host: localhost:8000
> User-Agent: curl/7.54.0
> Accept: */*
> 
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Set-Cookie: session=P4G4vqN11RfJIXjrmPX0QEQpxppOvYPA;
< Content-Length: 24
< 
session data:
* Closing connection 0
{'a': 'b'}
```

##### step 2

###### curl

```shell
curl 'localhost:8000/session?c=d' -H 'Cookie: session=P4G4vqN11RfJIXjrmPX0QEQpxppOvYPA' -v
```

###### output

```plain
*   Trying ::1...
* TCP_NODELAY set
* Connection failed
* connect to ::1 port 8000 failed: Connection refused
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 8000 (#0)
> GET /session?c=d HTTP/1.1
> Host: localhost:8000
> User-Agent: curl/7.54.0
> Accept: */*
> Cookie: session=P4G4vqN11RfJIXjrmPX0QEQpxppOvYPA
> 
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Content-Length: 34
< 
session data:
* Closing connection 0
{'a': 'b', 'c': 'd'}
```
