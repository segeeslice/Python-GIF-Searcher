import tkinter as tk
import base64
from urllib.request import urlopen
import sys

class App():
    def __init__(self):
        self.root = tk.Tk() # Base Tkinter object
        self.imgData = ""   # Base 64 gif data for displaying

        self.frames = []    # Array of imgData frames
        self.frameIndex = 0 # Current displayed frame index
        self.frameSize = 0  # Size of frames
        self.frameRate = int(1/30 * 1000) # Delay between frames (ms). Must be int. Defaults to 30 fps

        # TKinter canvas to hold image
        self.canvas = tk.Canvas(bg="white", relief="raised")
        self.canvas.pack(side='top', fill='both', expand='yes')

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
