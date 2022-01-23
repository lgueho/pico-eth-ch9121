import gc
CONTENT_TYPE = {
    "text": "text/html; charset=utf-8",
    "html": "text/html; charset=utf-8",
    "json": "application/json; charset=utf-8"
}
HTTP = {
    200: "OK",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error"
}


async def _parse_headers(request):
    """Parse the stream to add headers of the http request.

    Args:
        request (StreamReader): With arguments, path, method, query

    Returns:
        dict: headers of the request.
    """
    headers = {}
    while True:
        line = await request.readline()
        try:
            key, value = line.decode().split(':', 1)
            headers[key.lower()] = value.strip()
        except Exception:
            break
    return headers


async def _parse_request(request):
    """Parse the stream to add path, methode, query and header of the http request.

    Args:
        request (StreamReader): With arguments, path, method, query and headers
    """
    try:
        line = await request.readline()
        request.method, request.path, _ = line.decode().split()
        try:
            request.path, request.query = request.path.split('?', 1)
        except Exception:
            request.query = None
        request.headers = await _parse_headers(request)
    except Exception as ex:
        print(ex)


def reponse(http_code=500, body="", content_type='text', header={}):
    """Format the http(1.0) response in binary.

    Args:
        http_code (int, optional): Http code of the response . Defaults to 500.
        body (str, optional): Body of the response. Defaults to "".
        content_type (str, optional): The body type (json, html). Defaults to 'text'.
        header (dict, optional): extra header. Defaults to {}.

    Returns:
        bytes: response formated in bytes.
    """
    body = body.encode("utf-8") if body else HTTP[http_code].encode("utf-8")
    header["Content-Type"] = CONTENT_TYPE.get(content_type)
    header["Content-Length"] = len(body)
    reponse = f"HTTP/1.0 {http_code} {HTTP.get(http_code)}\r\n".encode("utf-8")
    reponse += "Connection: close\r\n".encode("utf-8")
    for k, v in header.items():
        reponse += f"{k}:{v}\r\n".encode("utf-8")
    reponse += "\r\n".encode("utf-8")
    reponse += body
    return reponse


class App:

    def __init__(self, server, token='', host='0.0.0.0', port=80):
        self.server = server
        self._token = token
        self.host = host
        self.port = port
        self.handlers = {}

    def route(self, path, methods=['GET'], security=False):
        """Route manager. Only simple route with query are managed.

        Args:
            path (str): Route for the function
            methods (list, optional): Route methods allowed.
                Defaults to ['GET'].
            security (boolean, optional): Check if the request as correct
                token. Default to False.
        """
        def wrapper(handler):
            self.handlers[path] = (methods, handler, security)
            return handler
        return wrapper

    async def _dispatch(self, reader, writer):
        """Dispatch methode to read the request, dispatch to the route function and write the response.

        Args:
            reader (StreamReader): Stream Reader (uasyncio).
            writer (StreamWriter): Stream Writer (uasyncio).
        """
        byte_reponse = b""
        try:
            # Set the request header.
            reader.headers = {}
            # Parse the request.
            await _parse_request(reader)
            # Get the route information.
            methods, handler, security = self.handlers[reader.path]
            if security and self._token != reader.headers.get("token"):
                # Token for the route do not match.
                byte_reponse = reponse(http_code=403)
            elif reader.method not in methods:
                # Method for the route is not set.
                byte_reponse = reponse(http_code=405)
            else:
                try:
                    # if everything is ok, then process the request.
                    byte_reponse = handler(reader)
                except Exception as ex:
                    # If error during the handling of the request.
                    byte_reponse = reponse(http_code=400, body=str(ex))
        except KeyError:
            # If the route is not set.
            byte_reponse = reponse(http_code=404)
        except Exception as ex:
            # Any internal server error.
            byte_reponse = reponse(http_code=500, body=str(ex))
        finally:
            # Write the response.
            await writer.awrite(byte_reponse)
            # Flush the stream.
            await writer.drain()
            # Memory clean
            gc.collect()

    async def serve(self):
        await self.server.serve(self._dispatch, self.host, self.port)
