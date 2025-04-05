import customtkinter
import requests

class PipimApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x400")

        self.button = customtkinter.CTkButton(self, text="my button", command=self.button_callbck)
        self.button.pack(padx = 10, pady = 10, side="top")

    def button_callbck(self):
        print("button press")

while __name__ == "__main__":
    app = PipimApp()
    app.mainloop()