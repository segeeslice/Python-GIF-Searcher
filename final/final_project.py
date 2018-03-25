import tkinter as tk
from tkinter import messagebox
from urllib.request import urlopen
import base64, sys, json

API = "dc6zaTOxFJmzC"      # Public beta Giphy API
DEFAULT_SEARCH = "welcome" # Default search value
DEFAULT_FPS = 15           # Default animation speed

class App():
    def __init__(self):
        self.root = tk.Tk() # Base Tkinter object
        self.root.title("The Python GIF Searcher")
        self.imgData = ""   # Base 64 gif data for displaying

        self.frames = []    # Array of imgData frames
        self.frameIndex = 0 # Current displayed frame index
        self.frameSize = 0  # Size of frames
        self.frameRate = int(1/DEFAULT_FPS * 1000) # Delay between frames (ms). Must be int. Defaults to 30 fps

        self.searchText = DEFAULT_SEARCH  # Current GIF search
        self.searchOffset = 0 # Current GIF offset

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

        # Look at different GIFs in search list
        self.buttonPrev = tk.Button(self.root, text="Previous GIF", command=self.prevGIF, state="disabled")
        self.buttonNext = tk.Button(self.root, text="Next GIF", command=self.nextGIF)

        # Speed slider with label and submission button
        self.labelSpeed = tk.Label(self.root, text = "GIF Speed (fps):")
        self.scaleSpeed = tk.Scale(self.root, from_ = 1, to = 120, orient = "horizontal")
        self.buttonSpeed = tk.Button(self.root, text = "Submit", command = self.changeSpeed)

        # ----- GRID SETTINGS -----
        self.canvas.grid      (row = 0, column = 3, padx = 5, pady = 5, rowspan = 1000)
        self.buttonPlay.grid  (row = 0, column = 0, padx = 5, pady = 5, sticky="nw")
        self.labelSearch.grid (row = 1, column = 0, padx = 5, pady = 5, sticky="nw")
        self.entrySearch.grid (row = 1, column = 1, padx = 5, pady = 5, sticky="nw")
        self.buttonSearch.grid(row = 1, column = 2, padx = 5, pady = 5, sticky="nw")
        self.buttonPrev.grid  (row = 2, column = 0, padx = 5, pady = 5, sticky="w")
        self.buttonNext.grid  (row = 2, column = 1, padx = 5, pady = 5, sticky="w")
        self.labelSpeed.grid  (row = 3, column = 0, padx = 5, pady = 5, sticky="w")
        self.scaleSpeed.grid  (row = 3, column = 1, padx = 5, pady = 5, sticky="nw")
        self.buttonSpeed.grid (row = 3, column = 2, padx = 5, pady = 5, sticky="w")

    # Set the image data from the given URL
    def setImgFromURL(self, url):
        # Open the given URL into a data string
        image_string = urlopen(url).read()
        # Parse the data string into base 64 for reading
        self.imgData = base64.encodestring(image_string)

    # Set the frame array using the data from imgData
    def createFramesArray(self):
        print ("Getting file frames...")
        self.frames = [] # Reset frames variables
        index = 0  # Current frame index

        # Create an array of frames of a gif
        # Only exits when reaches end of frames (raises exception)
        while True:
            try:
                # Get this gif index's frame
                self.frames.append(tk.PhotoImage(data=self.imgData, format="gif -index " + str(index)))
                index += 1
            except tk._tkinter.TclError as e:
                # This exception is expected at end of file
                print("Reached end of frames")
                break
            except:
                lastError = sys.exc_info()[0]
                print("Unexpected error: ", lastError)
                break

        # Change canvas size to be the size of this gif
        w, h = self.frames[0].width(), self.frames[0].height()
        self.canvas.config(width = w, height = h)

        # Reset gif looping variables
        self.frameSize = len(self.frames)
        self.frameIndex = 0

        # Restart loop
        self.stopFlag = False
        self.updateImage()

    # Update the image on the canvas with the next frame
    def updateImage(self):
        if self.stopFlag == True: return # Exit if stop flag is set
        if self.frameIndex == 0: self.canvas.delete("all") # Clear the canvas of all images if first frame

        # Display this frame
        # Layers frames on top of each other
        self.canvas.create_image(0, 0, image=self.frames[self.frameIndex], anchor='nw')

        # Increment frame index and call this again after increment
        self.frameIndex = self.frameIndex + 1 if self.frameIndex < self.frameSize-1 else 0
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

    def search(self, oldSearch = False):
        global API

        if not oldSearch:
            self.searchText = self.entrySearch.get().replace(" ", "+")
            self.searchOffset = 0

        url = "http://api.giphy.com/v1/gifs/search?q="+self.searchText+"&api_key="+API+"&limit=1&offset="+str(self.searchOffset)
        urlData = urlopen(url).read()
        jsonData = json.loads(urlData)

        # Error out with message to user if no data was found in the search
        if len(jsonData["data"]) is 0:
            self.displayMessage("ERROR", "Found no gifs under that search.", 'error')
            return
        else:
            urlGif = jsonData["data"][0]["images"]["original"]["url"]
            self.loadImage(urlGif)

    def nextGIF(self):
        self.searchOffset += 1
        self.search(oldSearch = True)
        self.buttonPrev.config(state="normal")

    def prevGIF(self):
        self.searchOffset -= 1
        self.search(oldSearch = True)
        if self.searchOffset is 0: self.buttonPrev.config(state="disabled")

    def changeSpeed(self):
        self.frameRate = int(1/self.scaleSpeed.get() * 1000)

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

        # Do default search
        # Uses inserted default search from above
        self.search()

        # Animate the image and run the program
        self.root.mainloop()

# Run the app
testURL = "https://media2.giphy.com/media/57Y0HrGWcu4WYvc6vE/giphy.gif"

ourApp = App()
ourApp.run()
