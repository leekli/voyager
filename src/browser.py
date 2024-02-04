import tkinter

# Browser Constants
WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18


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

    def scrolldown(self):
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
