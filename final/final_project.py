import tkinter as tk
import base64
from urllib.request import urlopen
import sys

# Initialize the Tkinter object we will be working with
root = tk.Tk()

# Returns an array of all frames of given base 64 image data
def createFramesArray(imgData):
    print ("Getting file frames...")
    array = [] # Array of frames we will be working with
    index = 0  # Current frame index

    # Create an array of frames
    # Only exits when reaches end of frames (raises exception)
    while True:
        try:
            # Get this gif index's frame
            array.append(tk.PhotoImage(data=imgData, format="gif -index " + str(index)))
            index += 1
        except tk._tkinter.TclError as e:
            # This exception is expected at end of file
            print("Reached end of frames")
            break
        except:
            lastError = sys.exc_info()[0]
            print("Unexpected error: ", lastError)
            break

    return array

# Test image url
url = "https://media1.giphy.com/media/FA8Ox4VeQM8rm/giphy.gif"

# Open the given URL into a data string
image_string = urlopen(url).read()
# Parse the data string into base 64 for reading
image_b64 = base64.encodestring(image_string)


# Gather array of frames in the gif
frames = createFramesArray(image_b64)

# Create canvas to hold image
canvas = tk.Canvas(bg="white", relief="raised")
canvas.pack(side='top', fill='both', expand='yes')

global frame
frame = 0

# Create the image on the canvas
# NOTE: Temporarily just displays the first frame
def updateImage():
    frame += 1
    canvas.create_image(10, 10, image=frames[frame], anchor='nw')


canvas.create_image(10, 10, image=frames[frame], anchor='nw')
root.after(200, updateImage())



root.mainloop()
