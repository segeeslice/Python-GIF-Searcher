import tkinter as tk
from tkinter import messagebox # Not imported by default
from urllib.request import urlopen
import base64, sys, json

API = "QOYhQaZkov0vnRMSRQ2412TPmESK5tmS" # Our public beta Giphy API
DEFAULT_SEARCH = "Cats"    # Default search value
DEFAULT_FPS = 15           # Default animation speed

class GifSearcher():
    def __init__(self):
        self.root = tk.Tk() # Base Tkinter object
        self.root.title("The Python GIF Searcher")
        self.imgData = ""   # Base 64 gif data for displaying

        self.frames = []    # Array of all imgData frames
        self.frameIndex = 0 # Current displayed frame index
        self.frameLen = 0   # Number of frames in the current GIF
        self.frameRate = int(1/DEFAULT_FPS * 1000) # Delay between frames (ms). Must be int. Defaults to 30 fps

        self.searchText = DEFAULT_SEARCH  # Current GIF search
        self.searchData = [] # Json data gathered from GIF search
        self.searchOffset = 0 # Current GIF offset
        self.searchLen = 0 # Current GIF search number of GIFs found

        self.stopFlag = False # Flag for stopping the GIF animation loop

        # ----- TKINTER WIDGETS -----
        # Canvas to hold the GIF
        self.canvas = tk.Canvas(self.root, bg="white", relief="raised")

        # Play / pause button
        self.buttonPlay = tk.Button(self.root, text = "Pause GIF", command=self.toggleLoop)

        # Search box with label and submission button
        self.labelSearch = tk.Label(self.root, text="Search Giphy:")
        self.entrySearch = tk.Entry(self.root)
        self.buttonSearch = tk.Button(self.root, text = "Submit", command=self.search)

        # Buttons to look at different GIFs in search list
        self.buttonPrev = tk.Button(self.root, text="Previous GIF", command=self.prevGIF, state="disabled")
        self.buttonNext = tk.Button(self.root, text="Next GIF", command=self.nextGIF)

        # Animation speed slider with label and submission button
        self.labelSpeed = tk.Label(self.root, text = "GIF Speed (fps):")
        self.scaleSpeed = tk.Scale(self.root, from_ = 1, to = 120, orient = "horizontal")
        self.buttonSpeed = tk.Button(self.root, text = "Submit", command = self.changeSpeed)

        # Section labels
        self.labelSection1 = tk.Label(self.root, text="GIF Searching", font=("Segoi UI", 14))
        self.labelSection2 = tk.Label(self.root, text="GIF Modification", font=("Segoi UI", 14))

        # Random GIF search button
        self.buttonRandom = tk.Button(self.root, text="~ Get Random GIF ~", command=self.randomSearch)

        # ----- GRID SETTINGS -----
        self.canvas.grid       (row = 0, column = 3, padx = 5, pady = 5, rowspan = 1000, sticky="nw")
        self.labelSection1.grid(row = 0, column = 0, padx = 5, pady = 10, columnspan = 3, sticky="w")
        self.labelSearch.grid  (row = 1, column = 0, padx = 5, pady = 5, sticky="nw")
        self.entrySearch.grid  (row = 1, column = 1, padx = 5, pady = 5, sticky="nwes")
        self.buttonSearch.grid (row = 1, column = 2, padx = 5, pady = 5, sticky="nw")
        self.buttonPrev.grid   (row = 2, column = 0, padx = 5, pady = 5, sticky="w")
        self.buttonNext.grid   (row = 2, column = 1, padx = 5, pady = 5, sticky="w")
        self.buttonRandom.grid (row = 3, column = 0, padx = 5, pady = 5, columnspan = 3, sticky="nwes")
        self.labelSection2.grid(row = 4, column = 0, padx = 5, pady = 10, columnspan = 3, sticky="w")
        self.buttonPlay.grid   (row = 5, column = 0, padx = 5, pady = 5, sticky="nw")
        self.labelSpeed.grid   (row = 6, column = 0, padx = 5, pady = 5, sticky="w")
        self.scaleSpeed.grid   (row = 6, column = 1, padx = 5, pady = 5, sticky="nwes")
        self.buttonSpeed.grid  (row = 6, column = 2, padx = 5, pady = 5, sticky="w")

    # Set the image data from the given URL
    def setImgFromURL(self, url):
        # Open the given URL into a data string
        image_string = urlopen(url).read()
        # Parse the data string into base 64 for reading
        self.imgData = base64.encodestring(image_string)

    # Set the frame array using the data from imgData
    # NOTE: frame size and image data must be set prior
    def createFramesArray(self):
        print ("Getting file frames...")
        self.frames = [] # Reset frames variables
        index = 0  # Current frame index

        # Create an array of frames of a gif using preset image data and frame size
        for i in range(0, self.frameLen):
            self.frames.append(tk.PhotoImage(data=self.imgData, format = "gif -index " + str(i)))

        # Change canvas size to be the size of this gif
        w, h = self.frames[0].width(), self.frames[0].height()
        self.canvas.config(width = w, height = h)

        # Reset frame index for gif looping
        self.frameIndex = 0

        # Restart loop
        self.stopFlag = False
        self.root.after(self.frameRate, self.updateImage)

    # Update the image on the canvas with the next frame
    def updateImage(self):
        if self.stopFlag == True: return # Exit if stop flag is set
        if self.frameIndex == 0: self.canvas.delete("all") # Clear the canvas of all images if first frame

        # Display this frame
        # Layers frames on top of each other
        self.canvas.create_image(0, 0, image=self.frames[self.frameIndex], anchor='nw')

        # Cycle frame index and call this again after increment
        self.frameIndex = (self.frameIndex + 1) % self.frameLen
        self.root.after(self.frameRate, self.updateImage)

    # Display a dialog window containing given information
    # Mode can be info, warning, or error
    def displayMessage(self, title, contents, mode):
        if mode == 'info':
            tk.messagebox.showinfo(title, contents)
        elif mode == 'warning':
            tk.messagebox.showwarning(title, contents)
        elif mode == 'error':
            tk.messagebox.showerror(title, contents)
        else:
            print("Could not display message of unknown type: " + mode)

    # ----- WIDGET COMMANDS -----

    def toggleLoop(self):
        # Toggle stop flag to stop the GIF playing if necessary
        self.stopFlag = not self.stopFlag

        # Change button text depending on if the GIF is playing or not
        buttonText = "Play GIF" if self.stopFlag else "Pause GIF"
        self.buttonPlay.config(text = buttonText)

        # Start the animation again if necessary
        if not self.stopFlag: self.updateImage()

    # Search the Giphy server for an image
    def search(self):
        global API

        # Change search text to accomodate URL format and reset offset
        self.searchText = self.entrySearch.get().replace(" ", "+")

        # Get the data given the search text
        url = "http://api.giphy.com/v1/gifs/search?q="+self.searchText+"&api_key="+API
        urlData = urlopen(url).read()
        self.searchData = json.loads(urlData)["data"]

        # Get the number of GIFs found under this search
        self.searchLen = len(self.searchData)

        # Handle error if no data was found under that search
        if self.searchLen is 0:
            self.displayMessage("ERROR", "Found no gifs under that search.", 'error')
            self.stopFlag = True;
            self.root.after(self.frameRate, self.clearGIF)

            self.buttonPrev.config(state="disabled")
            self.buttonNext.config(state="disabled")

        else:
            self.changeSearch(0) # Change the GIF to display the first item in the search list

    def nextGIF(self):
        self.changeSearch(self.searchOffset + 1)

    def prevGIF(self):
        self.changeSearch(self.searchOffset - 1)

    # Change a searched GIF to a new offset
    def changeSearch(self, offset):
        self.searchOffset = offset
        self.frameLen = int(self.searchData[offset]["images"]["original"]["frames"])

        # Current URL we will load
        # "downsized_medium" keyword prevents GIFs from getting too large, but
        # still maintains most smaller images to be their original size
        url = self.searchData[offset]["images"]["downsized_medium"]["url"]
        self.loadImage(url)

        # Change next and previous buttons to be disabled if necessary
        if self.searchOffset is 0: self.buttonPrev.config(state="disabled")
        else: self.buttonPrev.config(state="normal")

        if self.searchOffset >= (self.searchLen-1): self.buttonNext.config(state="disabled")
        else: self.buttonNext.config(state="normal")

    def randomSearch(self):
        global API

        # Get the data from GIPHY's random GIF searcher
        # Can be expanded to use specified search or rating
        url = "http://api.giphy.com/v1/gifs/random?api_key="+API
        urlData = urlopen(url).read()

        # Put data within array because this search only returns one item
        # Keeping in array keeps it consistent with regular searches
        self.searchData = [json.loads(urlData)["data"]]

        # Get the number of GIFs found under this search
        self.searchLen = len(self.searchData)

        # Clear the search box since this is random
        self.entrySearch.delete(0, 'end')

        # Handle error if no data was found under that search
        if self.searchLen is 0:
            self.displayMessage("ERROR", "Found no gifs under that search.", 'error')
            self.stopFlag = True;
            self.root.after(self.frameRate, self.clearGIF)

            self.buttonPrev.config(state="disabled")
            self.buttonNext.config(state="disabled")

        else:
            self.changeSearch(0)

    def changeSpeed(self):
        self.frameRate = int(1/self.scaleSpeed.get() * 1000)

    def clearGIF(self):
        self.imgData = ""
        self.frames = []
        self.frameIndex = 0
        self.frameLen = 0
        self.canvas.delete("all")
        self.canvas.config(width = 0, height = 0)

    # ----- ABSTRACTION -----

    # Load image to app given a url
    def loadImage(self, url):
        self.setImgFromURL(url)
        # Stop current image loop
        self.stopFlag = True

        # Wait until loop is done and create new frame array
        # Loop is started again within createFramesArray
        self.root.after(self.frameRate, self.createFramesArray)

    # Run the application
    def run(self):
        # Set default values in widgets
        self.entrySearch.insert('end', DEFAULT_SEARCH)
        self.scaleSpeed.set(DEFAULT_FPS)

        # Display introductory message
        self.displayMessage(mode='info', title='Welcome!',
            contents='Welcome to the Python GIF searcher!\n\nI went ahead and started you out with a quality search. New GIF searches may take a bit of time to load, and the program may become unresponsive.\n\nBe patient, and enjoy!')

        # Do default search
        # Uses inserted default search from above
        self.search()

        # Animate the image and run the program
        self.root.mainloop()


app = GifSearcher()
app.run()
