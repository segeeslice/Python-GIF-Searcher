import tkinter as tk
from tkinter import messagebox # Not imported by default
from urllib.request import urlopen, urlretrieve
import base64, sys, json, os

API = "QOYhQaZkov0vnRMSRQ2412TPmESK5tmS" # Our public GIPHY API app key
DEFAULT_SEARCH = "Cats"    # Default search value
DEFAULT_FPS = 15           # Default animation speed

class GifSearcher():
    def __init__(self):
        self.root = tk.Tk() # Base Tkinter object
        self.root.title("Python GIF Searcher") # Set window title
        self.root.resizable(False,False) # Disable window resizing

        self.imgData = ""   # Base 64 gif data for displaying

        self.frames = []    # Array of all imgData frames
        self.frameIndex = 0 # Current displayed frame index
        self.frameLen = 0   # Number of frames in the current GIF
        self.frameRate = int(1/DEFAULT_FPS * 1000) # Delay between frames (ms). Must be int. Defaults to 30 fps

        self.searchData = [] # Json data gathered from GIF search
        self.searchOffset = 0 # Current GIF offset
        self.searchLen = 0 # Current GIF search number of GIFs found

        self.stopFlag = False # Flag for stopping the GIF animation loop

        # ----- TKINTER WIDGETS -----
        # Canvas to hold the GIF
        self.canvas = tk.Canvas(self.root, bg="white", relief="raised", width = 0, height = 0)

        # Play / pause button
        self.buttonPlay = tk.Button(self.root, text = "Pause GIF", command=self.toggleLoop, state="disabled")

        # Search box with label and submission button
        self.labelSearch = tk.Label(self.root, text="Search Giphy:")
        self.entrySearch = tk.Entry(self.root)
        self.buttonSearch = tk.Button(self.root, text = "Submit", command=self.search)

        # Buttons to look at different GIFs in search list
        self.buttonPrev = tk.Button(self.root, text="Previous GIF", command=self.prevGIF, state="disabled")
        self.buttonNext = tk.Button(self.root, text="Next GIF", command=self.nextGIF, state="disabled")

        # Animation speed slider with label and submission button
        self.labelSpeed = tk.Label(self.root, text = "GIF Speed (fps):")
        self.scaleSpeed = tk.Scale(self.root, from_ = 1, to = 120, orient = "horizontal")
        self.buttonSpeed = tk.Button(self.root, text = "Submit", command = self.changeSpeed)

        # Section labels
        self.labelSection1 = tk.Label(self.root, text="GIF Searching", font=("Segoi UI", 14))
        self.labelSection2 = tk.Label(self.root, text="GIF Modification", font=("Segoi UI", 14))

        # Trending GIFs search button
        self.buttonTrending = tk.Button(self.root, text="~ Get Trending GIFs ~", command=self.trendingSearch)

        # Random GIF search button
        self.buttonRandom = tk.Button(self.root, text="~ Get Random GIF ~", command=self.randomSearch)

        # Download current GIF button
        self.buttonDownload = tk.Button(self.root, text="Download GIF", command=self.downloadGIF, state="disabled")

        # ----- GRID SETTINGS -----
        self.canvas.grid        (row = 0, column = 3, padx = 5, pady = 5, rowspan = 1000, sticky="nw")
        self.labelSection1.grid (row = 0, column = 0, padx = 5, pady = 10, columnspan = 3, sticky="w")
        self.buttonPrev.grid    (row = 1, column = 0, padx = 5, pady = 5, sticky="w")
        self.buttonNext.grid    (row = 1, column = 1, padx = 5, pady = 5, sticky="w")
        self.labelSearch.grid   (row = 2, column = 0, padx = 5, pady = 5, sticky="nw")
        self.entrySearch.grid   (row = 2, column = 1, padx = 5, pady = 5, sticky="nwes")
        self.buttonSearch.grid  (row = 2, column = 2, padx = 5, pady = 5, sticky="nw")
        self.buttonTrending.grid(row = 3, column = 0, padx = 5, pady = 5, columnspan = 3, sticky="nwes")
        self.buttonRandom.grid  (row = 4, column = 0, padx = 5, pady = 5, columnspan = 3, sticky="nwes")
        self.labelSection2.grid (row = 5, column = 0, padx = 5, pady = 10, columnspan = 3, sticky="w")
        self.buttonPlay.grid    (row = 6, column = 0, padx = 5, pady = 5, sticky="nw")
        self.buttonDownload.grid(row = 6, column = 1, padx = 5, pady = 5, sticky="nw")
        self.labelSpeed.grid    (row = 7, column = 0, padx = 5, pady = 5, sticky="w")
        self.scaleSpeed.grid    (row = 7, column = 1, padx = 5, pady = 5, sticky="nwes")
        self.buttonSpeed.grid   (row = 7, column = 2, padx = 5, pady = 5, sticky="w")

    # ----- UTILITY FUNCTIONS -----

    # Set the frame array using the data from imgData
    # NOTE: frame size and image data must be set prior
    def createFramesArray(self):
        print ("Processing file frames...")
        self.frames = [] # Reset frames variables
        tempLen = 0  # Current frame length count

        # Create an array of frames of a gif using preset image data and frame size
        try:
            for i in range(0, self.frameLen):
                self.frames.append(tk.PhotoImage(data=self.imgData, format = "gif -index " + str(i)))
                tempLen += 1 # Keep count of how many frames we're at

        # Catch TKinter exception and simply continue to display if issue
        # Done this way because occasionally GIPHY data is invalid
        except Exception as e:
            print("Unexpected error while processing GIF: " + str(e))
            self.frameLen = tempLen

        # Change canvas size to be the size of this gif
        w, h = self.frames[0].width(), self.frames[0].height()
        self.canvas.config(width = w, height = h)

        # Reset frame index for gif looping
        self.frameIndex = 0

        # Restart loop
        self.buttonPlay.config(text = "Pause GIF")
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
            messagebox.showinfo(title, contents)
        elif mode == 'warning':
            messagebox.showwarning(title, contents)
        elif mode == 'error':
            messagebox.showerror(title, contents)
        else:
            print("Could not display message of unknown type: " + mode)

    def displayWelcomeMessage(self):
        # Display introductory message
        self.displayMessage(mode='info', title='Welcome!',
            contents='Welcome to the Python GIF searcher!\n\nNew GIF searches may take a bit of time to load, and the program may become unresponsive.\n\nBe patient, and enjoy!')

    # Load searchData from giphy API using given mode
    # Modes are 'search', 'random', and 'trending'
    def loadSearchData(self, mode):
        global API
        print("Fetching GIF data...")

        base="http://api.giphy.com/v1/gifs/" # Base url
        endpoint = "" # Modal endpoint

        # Generate GIPHY API endpoint depending on given mode
        endpoint = mode + "?api_key="+API

        # Get and add search text to endpoint if search mode
        if mode is "search":
            # Modify search to accomodate URL format
            searchText = self.entrySearch.get().replace(" ", "+")
            endpoint += "&q=" + searchText

        # If not search mode, clear search to indicate this
        else:
            self.entrySearch.delete(0, 'end')

        # Retrieve search data
        try:
            url = base + endpoint
            urlData = urlopen(url).read()
            self.searchData = json.loads(urlData)["data"]

        # Handle any urllib error and exit
        # Done in this way to envelop multiple error possibilities
        # (HTTP error, URL connection error, etc)
        except:
            errorString = "Unexpected error while fetching search data:\n" + str(sys.exc_info()[0]) + "\n\n(Are you connected to the internet?)"
            self.displayMessage("ERROR", errorString, 'error')
            self.handleError()
            return

        # Convert search data to list in the case that we only retrieve one item
        if type(self.searchData) != list:
            self.searchData = [self.searchData]

        # Get the number of GIFs found under this search
        self.searchLen = len(self.searchData)

        # Handle error if no data was found under that search
        if self.searchLen is 0:
            self.displayMessage("ERROR", "Found no gifs under that search.", 'error')
            self.handleError()

        else:
            self.changeSearch(0) # Change the GIF to display the first item in the search list

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

    # Clear all GIF data in case of error
    # Stops GIF first to prevent animation errors
    def handleError(self):
        self.stopFlag = True;
        self.root.after(self.frameRate, self.clearGIF)

    # Clear all GIF data
    def clearGIF(self):
        self.imgData = ""
        self.frames = []
        self.frameIndex = 0
        self.frameLen = 0
        self.searchOffset = 0
        self.canvas.delete("all")
        self.canvas.config(width = 0, height = 0)

        self.buttonPrev.config(state="disabled")
        self.buttonNext.config(state="disabled")
        self.buttonPlay.config(state="disabled")
        self.buttonDownload.config(state="disabled")

    # ----- WIDGET COMMANDS -----

    def toggleLoop(self):
        # Toggle stop flag to stop the GIF playing if necessary
        self.stopFlag = not self.stopFlag

        # Change button text depending on if the GIF is playing or not
        buttonText = "Play GIF" if self.stopFlag else "Pause GIF"
        self.buttonPlay.config(text = buttonText)

        # Start the animation again if necessary
        if not self.stopFlag: self.updateImage()

    # Search given text
    def search(self):
        self.loadSearchData("search")

    def trendingSearch(self):
        self.loadSearchData("trending")

    # Get random GIF
    def randomSearch(self):
        self.loadSearchData("random")

    # Get next GIF in search
    def nextGIF(self):
        self.changeSearch(self.searchOffset + 1)

    # Get previous GIF in search
    def prevGIF(self):
        self.changeSearch(self.searchOffset - 1)

    # Modify GIF animation speed
    def changeSpeed(self):
        self.frameRate = int(1/self.scaleSpeed.get() * 1000)

    # Download a GIF to the local directory
    def downloadGIF(self):
        print("Downloading GIF...")

        # Get the URL of the currently displayed image
        # Uses the original instead of the displayed, downsized one
        url = self.searchData[self.searchOffset]["images"]["original"]["url"]

        # Get the filepath of the current working directory
        filepath = os.path.join(os.getcwd(), self.searchData[self.searchOffset]["title"] + ".gif")

        # Download the GIF to the program's file location using its GIPHY title
        # If a file with that name already exists, it simply overwrites it
        # This shouldn't be too detrimental, but could be revised if necessary
        try:
            urlretrieve(url, filepath)
        except Exception as e:
            # Display file save error
            self.displayMessage(title="ERROR", mode="error",
                contents = "Unexpected error downloading: " + str(e) + "\n\n(Are you connected to the internet?)")

            return # Return early as to not display success message

        self.displayMessage(title="Success!", mode="info",
            contents="GIF successfully downloaded to '{}'".format(filepath))

    # ----- ABSTRACTION / USER FUNCTIONS -----

    # Load image to app given a url
    # Can be used manually or with widgets
    def loadImage(self, url):
        try:
            # Open the given URL into a data string
            image_string = urlopen(url).read()
            # Parse the data string into base 64 for reading
            self.imgData = base64.encodestring(image_string)

        # Catch and handle any possible urllib errors
        except:
            errorString = "Unexpected error while fetching GIF data:\n" + str(sys.exc_info()[0]) + "\n\n(Are you connected to the internet?)"
            self.displayMessage("ERROR", errorString, 'error')
            self.handleError()
            return

        # Enable play and download buttons
        self.buttonPlay.config(state="normal")
        self.buttonDownload.config(state="normal")

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

        # After slight delay, display a welcome message
        # NOTE: Needs the delay because entry becomes disabled if messagebox
        #       is used outside of the root.mainloop
        self.root.after(200, self.displayWelcomeMessage)

        # Run the program
        self.root.mainloop()

app = GifSearcher()
app.run()
