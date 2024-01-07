import socket


class URL:
    """
    Class: URL.

    This class deals with the parsing of a URL string given as an argument.

    Attributes:
        url (str): Given as only argument to Class.
        scheme (str): Extracts the scheme from the URL string (e.g. 'http')
        host (str): Extracts the host from the URL string (e.g. example.org)
        path (str): Extracts the path from the URL string (e.g. /index.html)

    Methods:
        request: Creates a socket connection and sends the request.

    Example:
        >>> url = URL("http://example.org")
        >>> url.request()
    """

    def __init__(self, url):
        """
        The constructor for URL Class.

        Parameters:
            url (str): Given as only argument to Class.
        """

        # Seperate scheme (http) from url
        self.scheme, url = url.split("://", 1)
        assert self.scheme == "http"

        # Separate host and path
        if "/" not in url:
            url = url + "/"

        self.host, url = url.split("/", 1)
        self.path = "/" + url

    def request(self):
        # Create socket
        request_socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
        )

        # Create socket connection
        request_socket.connect((self.host, 80))

        # Send the request through the socket as per HTTP/1.0 Protocol incl. two newlines at end of request
        request_socket.send(
            (
                "GET {} HTTP/1.0\r\n".format(self.path)
                + "Host: {}\r\n\r\n".format(self.host)
            ).encode("utf8")
        )

        # Obtain response from request
        response = request_socket.makefile("r", encoding="utf8", newline="\r\n")

        # Extract the Response HTTP Status Code, then the HTTP Version/Code/Reason
        status_line = response.readline()
        version, status_code, status_reason = status_line.split(" ", 2)

        # Extract the Response Headers and Collect into a Dictionary
        # Ensure 'transfer-encoding' & 'content-encoding' are not in Response Headers
        response_headers = {}

        while True:
            current_line = response.readline()

            # This means it's the end of the response
            if current_line == "\r\n":
                break

            header, value = current_line.split(":", 1)
            response_headers[header.lower()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        # Extract the rest of the 'body' (html)
        body = response.read()

        # Close the socket once all Response information is extracted and saved
        request_socket.close()

        return body


url = URL("http://example.org")
url.request()