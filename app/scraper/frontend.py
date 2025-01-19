"""
This module contain the code for frontend
"""

from scraper.communicator import Communicator
import tkinter as tk
from tkinter import ttk,  WORD
from scraper.scraper import Backend
from scraper.common  import Common
import threading



class Frontend:
    def __init__(self):
        """Initializing frontend layout"""

        self.root = tk.Tk()
        icon = tk.PhotoImage(file="app\images\GMS.png")

        self.root.iconphoto(True, icon)
        self.root.geometry("850x650")
        self.root.resizable(False, False)
        self.root.title("Google maps scraper")

        self.style = ttk.Style()
        self.style.map(
            "my.TButton",  # making style for our buttons
            foreground=[("active", "green")],
            background=[("active", "white")],
        )

        bgimage = tk.PhotoImage(file="app\images\Home.png")

        self.imglabel = tk.Label(self.root, image=bgimage)
        self.imglabel.place(x=0, y=0, relwidth=1, relheight=1)
        self.imglabel.image = bgimage

        """For search entry"""
        self.search_label = ttk.Label(
            self.root,
            text="Search:",
            font=("Franklin Gothic Medium", 17),
            foreground="green",
            background="white",
        )
        self.search_label.place(x=255, y=175)

        self.search_box = ttk.Entry(self.root, width=30, font=("Arial", 15))
        self.search_box.place(x=355, y=180)

        """For submit button"""
        self.submit_button = ttk.Button(
            self.root,
            text="Submit",
            width=15,
            command=self.getinput,
            style="my.TButton",
        )
        self.submit_button.place(x=355, y=320)

        """for output format entry"""
        self.outputFormatButtonLabel = ttk.Label(
            self.root,
            text="Format:",
            font=("Franklin Gothic Medium", 17),
            foreground="green",
            background="white",
        )
        self.outputFormatButtonLabel.place(x=255, y=230)

        self.outputFormatButton = ttk.Combobox(
            self.root, values=["Excel", "Json", "Csv"], state="readonly"
        )
        self.outputFormatButton.place(x=355, y=240)

        """for message box"""
        self.show_text = tk.Text(
            self.root,
            font=("arial", 13),
            height=10,
            width=35,
            state="disabled",
            border=False,
            wrap=WORD,
            highlightbackground="black",
            highlightthickness=2,
        )
        self.show_text.place(x=295, y=440)

        """For healdess checkbox"""

        self.healdessCheckBoxVar = tk.IntVar()
        self.healdessCheckBox = tk.Checkbutton(
            self.root, text="Headless mode", variable=self.healdessCheckBoxVar)
        self.healdessCheckBox.place(x=700, y=45)

        self.__replacingtext(
            "Welcome to Google Maps Scraper!\n\nLet's start scraping..."
        )

        self.init_communicator()
    
    def init_communicator(self):
        Communicator.set_frontend_object(self)

    def __replacingtext(self, text):
        """This function will insert the text in text showing box"""

        self.show_text.config(state="normal")
        self.show_text.insert(tk.END, "• " + text)
        self.show_text.insert(tk.END, "\n\n")
        self.show_text.see(tk.END)
        self.show_text.config(state="disabled")

    def getinput(self):
        self.searchQuery = self.search_box.get()
        self.outputFormatValue = self.outputFormatButton.get()

        if len(self.searchQuery) == 0 and len(self.outputFormatValue) == 0:
            self.__replacingtext(text="Oops! Your query is not valid")

        elif len(self.searchQuery) == 0:
            self.__replacingtext(text="Oops! You did empty search")
        elif len(self.outputFormatValue) == 0:
            self.__replacingtext(text="Oops! You did not select output format")

        else:
            self.submit_button.config(state="disabled")

            self.searchQuery = self.searchQuery.lower()
            self.outputFormatValue = self.outputFormatValue.lower()
            self.headlessMode = self.healdessCheckBoxVar.get()

            self.threadToStartBackend = threading.Thread(
                target=self.startscraping)
            self.threadToStartBackend.start()

    def closingbrowser(self):
        """It will close the browser when the app is closed"""

        try:
            # super().closeThread.set()
            Common.set_close_thread()
            self.root.destroy()
        except:
            pass

    def startscraping(self):
        backend = Backend(
            self.searchQuery,
            self.outputFormatValue,
            healdessmode=self.headlessMode
        )

        backend.mainscraping()
    
    def end_processing(self):
        self.submit_button.config(state="normal")
        try:
            if self.threadToStartBackend.is_alive():
                self.threadToStartBackend.join()
        except:
            pass

    def messageshowing(
        self,
        message):

        self.__replacingtext(message)


if __name__ == "__main__":
    app = Frontend()
    app.root.protocol("WM_DELETE_WINDOW", app.closingbrowser)
    app.root.mainloop()
