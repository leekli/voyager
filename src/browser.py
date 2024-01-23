import socket
import sys
import ssl
import subprocess
import tkinter

# Browser Constants
WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18


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


class Browser:
    """
    Class: Browser

    This class deals with creating the Browser GUI Window & Canvas, and drawing the text to the screen.

    Methods:
        load: Depending on the scheme used, it will initate the request, parse the text and draw it to the screen. If file URI then it will open the file path.
        draw: Draws the text from self.display_list to the screen, handles the x/y co-ordinates of the screen.
        scrolldown: Handles the user event 'scroll down' and re-drawing the screen in line with new text positions.
    """

    def __init__(self):
        # Initalise Tk window
        self.scroll = 0
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.window.title("🚀 Voyager")
        self.canvas.pack()
        self.window.bind("<Down>", self.scrolldown)

    def load(self, url):
        # Deals with loading the content depending on scheme supplied.
        # Supported schemes: HTTTP, HTTPS, File

        if url.scheme == "http" or url.scheme == "https":
            body = url.request()
            text = lex(body)
            self.display_list = layout(text)
            self.draw()

        if url.scheme == "file":
            url.file_uri_open(url)

    def draw(self):
        # On each re-draw, clear the current content and re-render based on x and y co-ordinates.
        self.canvas.delete("all")

        for x, y, char in self.display_list:
            if y > self.scroll + HEIGHT:
                continue
            if y + VSTEP < self.scroll:
                continue
            self.canvas.create_text(x, y - self.scroll, text=char)

    SCROLL_STEP = 100

    def scrolldown(self, event):
        # Handle the user clicking scroll down, adjust the scroll step and re-draw the screen
        self.scroll += self.SCROLL_STEP
        self.draw()


def lex(body):
    # Parses the response body, removing opening and closing tags <> and returning the remaining text content.
    text = ""
    in_tag = False

    for char in body:
        if char == "<":
            in_tag = True
        elif char == ">":
            in_tag = False
        elif not in_tag:
            text += char

    return text


def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP

    for char in text:
        display_list.append((cursor_x, cursor_y, char))
        cursor_x += HSTEP

        if cursor_x >= WIDTH - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP

    return display_list


if __name__ == "__main__":
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
