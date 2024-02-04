import socket
import ssl
import subprocess


class URL:
    """
    Class: URL

    This class deals with the parsing of a URL string given as an argument, and initiating the request.

    Methods:
        request: Creates a socket connection and sends the request.
        file_uri_open: Opens a file in line with file schema.
    """

    def __init__(self, url):
        """
        The constructor for URL Class.

        Parameters:
            url (str): Given as only argument.
        """

        # Separate scheme (http/https/file) from url
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https", "file"]

        # Set correct port number depending on HTTP/HTTPS scheme provided
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        # Separate host and path (add trailing / if no path)
        if "/" not in url:
            url = url + "/"

        self.host, url = url.split("/", 1)
        self.path = "/" + url

        # Deal with any custom port numbers given in the URL request
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

        # Set HTTP Headers
        self.connection = "close"
        self.user_agent = "Voyager/0.1 (X11; Linux x86_64)"

    def request(self):
        # Create socket & wrap in SSL
        request_socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
        )

        # Create socket connection
        request_socket.connect((self.host, self.port))

        # Wrap socket in SSL if HTTPS scheme requested
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            request_socket = ctx.wrap_socket(request_socket, server_hostname=self.host)

        # Send the request through the socket as per HTTP/1.0 Protocol incl. two newlines at end of request
        request_socket.send(
            (
                "GET {} HTTP/1.1\r\n".format(self.path)
                + "Host: {}\r\n".format(self.host)
                + "Connection: {}\r\n".format(self.connection)
                + "User-Agent: {}\r\n\r\n".format(self.user_agent)
            ).encode("utf8")
        )

        # Obtain response from request
        response = request_socket.makefile("r", encoding="utf8", newline="\r\n")

        # Extract the Response HTTP Status Code, then the HTTP Version/Code/Reason
        status_line = response.readline()
        version, status_code, status_reason = status_line.split(" ", 2)

        # Extract the Response Headers and Collect into a Dictionary
        response_headers = {}

        while True:
            current_line = response.readline()

            # This means it's the end of the response
            if current_line == "\r\n":
                break

            header, value = current_line.split(":", 1)
            response_headers[header.lower()] = value.strip()

        # Extract the rest of the 'body' (html)
        body = response.read()

        # Close the socket once all Response information is extracted and saved
        request_socket.close()

        return body

    def file_uri_open(self, url):
        # Gets the file path
        file_path = url.path

        # If not file path given, a default HTML file loads locally.
        if file_path == "" or file_path == "/":
            try:
                subprocess.run(["open", "./var/fileUrlDefault.html"])
            except:
                print("There was an error opening the file.")
        else:
            try:
                subprocess.run(["open", f"{file_path}"])
            except:
                print("There was an error opening the file.")

        return None
