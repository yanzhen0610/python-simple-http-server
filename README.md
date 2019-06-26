# python-simple-http-server

This is made for some simple cases. For example, mock API.

default listening on `0.0.0.0:1234`

no extra packages required, just run with `python3 server.py`

compatible with python 3.7 and later versions (since the `http.server.ThreadingHTTPServer` only appears after python 3.7)

## run

```shell
python3 server.py
```

## example

### GET

#### code

```python
class ExampleHTTPRequestHandler(BaseHTTPRequestHandler):
    def get_example(self):
        self.append_response('Hello World!\n')
        self.append_response('It\'s a GET example.\n')
        self.append_response('Request Header:\n')
        self.append_response(self.headers)
        self.set_status(200)

class ExampleHTTPRequestHandlerPool(BaseHTTPRequestHandlerPool):
    def __init__(self, *args, **kwargs):
        super().__init__(handler_class=ExampleHTTPRequestHandler, *args, **kwargs)

    def _setup_handlers(self):
        self.set_GET_handler('/', ExampleHTTPRequestHandler.get_example)
```

#### curl

```shell
curl localhost:1234 -v
```

#### output

```plain
* Rebuilt URL to: localhost:1234/
*   Trying ::1...
* TCP_NODELAY set
* Connection failed
* connect to ::1 port 1234 failed: Connection refused
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 1234 (#0)
> GET / HTTP/1.1
> Host: localhost:1234
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
Host: localhost:1234
User-Agent: curl/7.54.0
Accept: */*

* Closing connection 0
```

### POST

#### code

```python
class ExampleHTTPRequestHandler(BaseHTTPRequestHandler):
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
        self.set_POST_handler('/', ExampleHTTPRequestHandler.post_example)
```

#### curl

```shell
curl localhost:1234 -X POST -H 'Content-Type: application/json' -d '{"key": "value"}' -v
```

#### output

```plain
Note: Unnecessary use of -X or --request, POST is already inferred.
* Rebuilt URL to: localhost:1234/
*   Trying ::1...
* TCP_NODELAY set
* Connection failed
* connect to ::1 port 1234 failed: Connection refused
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 1234 (#0)
> POST / HTTP/1.1
> Host: localhost:1234
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
Host: localhost:1234
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
class ExampleHTTPRequestHandler(BaseHTTPRequestHandler):
    def params_example(self):
        self.append_response('Parameters:\n')
        self.append_response(self.params) # self.params is type of dict

class ExampleHTTPRequestHandlerPool(BaseHTTPRequestHandlerPool):
    def __init__(self, *args, **kwargs):
        super().__init__(handler_class=ExampleHTTPRequestHandler, *args, **kwargs)

    def _setup_handlers(self):
        self.set_GET_handler('/params', ExampleHTTPRequestHandler.params_example)
        self.set_POST_handler('/params', ExampleHTTPRequestHandler.params_example)
```

#### curl

```shell
curl 'localhost:1234/params?a=b&c=d&url=https%3A//github.com/yanzhen0610/python-simple-http-server' -X POST -H 'Content-Type: application/json' -d '{"key": "value"}' -v
```

#### output

```plain
Note: Unnecessary use of -X or --request, POST is already inferred.
*   Trying ::1...
* TCP_NODELAY set
* Connection failed
* connect to ::1 port 1234 failed: Connection refused
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 1234 (#0)
> POST /params?a=b&c=d&url=https%3A//github.com/yanzhen0610/python-simple-http-server HTTP/1.1
> Host: localhost:1234
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

### with session

#### code

```python
class ExampleHTTPRequestHandler(BaseHTTPRequestHandler):
    def session_example(self):
        self.session_start() # start new session if client didn't provide session ID
        self.session.update(self.params) # self.session is type of dict
        self.append_response('session data:\n')
        self.append_response(self.session)
        self.set_status(200)

class ExampleHTTPRequestHandlerPool(BaseHTTPRequestHandlerPool):
    def __init__(self, *args, **kwargs):
        super().__init__(handler_class=ExampleHTTPRequestHandler, *args, **kwargs)

    def _setup_handlers(self):
        self.set_GET_handler('/session', ExampleHTTPRequestHandler.session_example)
        self.set_POST_handler('/session', ExampleHTTPRequestHandler.session_example)
```

#### interactive steps

##### step 1

###### curl

```shell
curl 'localhost:1234/session?a=b' -v
```

###### output

```plain
*   Trying ::1...
* TCP_NODELAY set
* Connection failed
* connect to ::1 port 1234 failed: Connection refused
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 1234 (#0)
> GET /session?a=b HTTP/1.1
> Host: localhost:1234
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
curl 'localhost:1234/session?c=d' -H 'Cookie: session=P4G4vqN11RfJIXjrmPX0QEQpxppOvYPA' -v
```

###### output

```plain
*   Trying ::1...
* TCP_NODELAY set
* Connection failed
* connect to ::1 port 1234 failed: Connection refused
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to localhost (127.0.0.1) port 1234 (#0)
> GET /session?c=d HTTP/1.1
> Host: localhost:1234
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
