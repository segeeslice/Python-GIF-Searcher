import tkinter as tk
import base64
from urllib.request import urlopen
import sys

class App():
    def __init__(self):
        self.root = tk.Tk() # Base Tkinter object
        self.root.title("The Python GIF Searcher")
        self.imgData = ""   # Base 64 gif data for displaying

        self.frames = []    # Array of imgData frames
        self.frameIndex = 0 # Current displayed frame index
        self.frameSize = 0  # Size of frames
        self.frameRate = int(1/30 * 1000) # Delay between frames (ms). Must be int. Defaults to 30 fps

        # TKinter canvas to hold image
        self.canvas = tk.Canvas(self.root, bg="white", relief="raised")
        self.canvas.grid(row = 0, column = 3, rowspan = 1000, padx = 5, pady = 5)
        # self.canvas.pack(side='right', fill='both', expand='yes')

        self.buttonPlay = tk.Button(self.root, text = "Pause GIF", command=self.toggleLoop)
        self.buttonPlay.grid(row = 0, column = 0, columnspan = 3, sticky="nw", padx = 5, pady = 5)
        # self.buttonPlay.pack(side='left')

        self.labelURL = tk.Label(self.root, text="Image URL:")
        self.labelURL.grid(row = 1, column = 0, sticky="nw", padx = 5, pady = 5)

        self.entryURL = tk.Entry(self.root)
        self.entryURL.grid(row = 1, column = 1, sticky="nw", padx = 5, pady = 5)

        self.buttonURL = tk.Button(self.root, text = "Submit", command=self.changeURL)
        self.buttonURL.grid(row = 1, column = 2, sticky="nw", padx = 5, pady = 5)

        self.stopFlag = False # Flag for stopping the url loop

    # Set the image data from the given URL
    def setImgFromURL(self, url):
        # Open the given URL into a data string
        image_string = urlopen(url).read()
        # Parse the data string into base 64 for reading
        self.imgData = base64.encodestring(image_string)

    # Set the frame array using the data from imgData
    def createFramesArray(self):
        self.stopFlag = True # Stop gif looping if necessary
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
        self.stopFlag = False

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

    # ----- WIDGET COMMANDS -----

    def toggleLoop(self):
        # Toggle stop flag to stop the GIF playing if necessary
        self.stopFlag = not self.stopFlag

        # Change button text depending on if the GIF is playing or not
        buttonText = "Play GIF" if self.stopFlag else "Pause GIF"
        self.buttonPlay.config(text = buttonText)

        # Start the animation again if necessary
        if not self.stopFlag: self.updateImage()

    def changeURL(self):
        url = self.entryURL.get()
        self.loadImage(url)

    # ----- ABSTRACTION -----

    # Load image to app given a url
    def loadImage(self, url):
        self.setImgFromURL(url)
        self.createFramesArray()

    # Run the application
    def run(self):
        self.root.after(500, self.updateImage)
        self.root.mainloop()


# Run the app
testURL = "https://media2.giphy.com/media/57Y0HrGWcu4WYvc6vE/giphy.gif"

ourApp = App()
ourApp.loadImage(testURL)
ourApp.run()
