import sys
import customtkinter as ctk

from assets import colbg, colgreen, colred
from views import Authview, Dashview

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


class Mainapp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PinBatch")
        self.geometry("1160x740")
        self.minsize(960, 600)
        self.configure(fg_color=colbg)
        self.makebar()
        self.body = ctk.CTkFrame(self, fg_color=colbg, corner_radius=0)
        self.body.pack(fill="both", expand=True)
        self.dash = Dashview(self.body, onquit=self.showauth)
        self.auth = Authview(self.body, onauth=self.showdash)
        self.bind_all("<Control-v>", lambda e: self.dash.pasteitems() if self.dash.winfo_ismapped() else None)
        self.protocol("WM_DELETE_WINDOW", self.onclose)
        self.showauth()

    def makebar(self):
        self.lblstat = ctk.CTkLabel(self, text="")

    def onclose(self):
        if hasattr(self, "dash") and self.dash.isbusy:
            self.dash.abort_requested = True
        self.destroy()

    def showauth(self):
        self.dash.pack_forget()
        self.auth.pack(fill="both", expand=True)
        self.lblstat.configure(text="offline", text_color=colred)

    def showdash(self, engine, info, boards):
        self.auth.pack_forget()
        self.dash.pack(fill="both", expand=True)
        self.dash.loadacc(engine, info, boards)
        self.lblstat.configure(text=f"online (@{info['username']})", text_color=colgreen)


def main():
    try:
        app = Mainapp()
        app.mainloop()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)


if __name__ == "__main__":
    main()
