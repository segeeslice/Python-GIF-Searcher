class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")
        self.hi_there.grid(row=0, column=0, columnspan=200, padx=200)

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=root.destroy)
        self.quit.grid(row = 1, column = 0, columnspan=200)

        # Image setup
        url = "https://media1.giphy.com/media/FA8Ox4VeQM8rm/giphy.gif"

        image_byt = urlopen(url).read()
        image_b64 = base64.encodestring(image_byt)
        photo = tk.PhotoImage(data = image_b64)

        canvas = tk.Canvas(bg="white", relief="raised")
        canvas.pack(side='top', fill='both', expand='yes')

        canvas.create_image(10, 10, image=photo, anchor='nw')

    def say_hi(self):
        print("hi there, everyone!")

        this_color = self.hi_there.cget('fg')
        new_color = "purple" if this_color != "purple" else "green"
        self.hi_there.config(fg=new_color)
