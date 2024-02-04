import sys
import tkinter

from url import URL
from browser import Browser

# Main entry point for app
if __name__ == "__main__":
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
