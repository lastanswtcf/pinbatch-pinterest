import os
import threading
import time
import urllib.parse
import webbrowser
from tkinter import filedialog, messagebox
import customtkinter as ctk

from assets import (
    colbg, colfield, colline,
    colbrand, colbrandh, colgreen, colred, colmuted, coltext,
    makelogo, makeicon
)
from engine import Engine, parsecookies
from media import makethumb, getclip


class Authview(ctk.CTkFrame):
    def __init__(self, parent, onauth):
        super().__init__(parent, fg_color=colbg, corner_radius=0)
        self.onauth = onauth
        self.pack_propagate(True)
        self.icon_dev = makeicon("developer", size=(14, 14))
        self.icon_src = makeicon("source", size=(14, 14))
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.place(relx=0.5, rely=0.5, anchor="center")
        self.topbox = ctk.CTkFrame(self.container, fg_color="transparent")
        self.topbox.pack(fill="x", pady=(0, 18))
        brandrow = ctk.CTkFrame(self.topbox, fg_color="transparent")
        brandrow.pack(anchor="center")
        self.logoimg = makelogo(size=(44, 44))
        ctk.CTkLabel(brandrow, image=self.logoimg, text="").pack(side="left", padx=(0, 14))
        titlebox = ctk.CTkFrame(brandrow, fg_color="transparent")
        titlebox.pack(side="left")
        ctk.CTkLabel(titlebox, text="pinbatch", font=("Segoe UI", 26, "bold"),
                     text_color=coltext).pack(anchor="w")
        ctk.CTkLabel(titlebox, text="pinterest batch publishing and automation studio",
                     font=("Segoe UI", 12), text_color=colmuted).pack(anchor="w")
        self.formcard = ctk.CTkFrame(self.container, fg_color=colbg, corner_radius=14,
                                     width=680, border_width=1, border_color=colline)
        self.formcard.pack(fill="x")
        self.formbody = ctk.CTkFrame(self.formcard, fg_color="transparent")
        self.formbody.pack(fill="x", padx=36, pady=28)
        self.fields = {}

        def makeentry(key, title, pholder):
            head = ctk.CTkFrame(self.formbody, fg_color="transparent")
            head.pack(fill="x", pady=(8, 4))
            ctk.CTkLabel(head, text=title, font=("Segoe UI", 12, "bold"),
                         text_color=coltext).pack(side="left")
            status = ctk.CTkLabel(head, text="", font=("Segoe UI", 11), text_color=colmuted)
            status.pack(side="right")
            ent = ctk.CTkEntry(self.formbody, height=42, corner_radius=8, fg_color=colfield,
                               border_width=1, border_color=colline,
                               font=("Consolas", 12), text_color=coltext,
                               placeholder_text=pholder, placeholder_text_color="#636366")
            ent.pack(fill="x", pady=(0, 10))
            ent.bind("<KeyRelease>", lambda e, k=key: self.checkval(k))
            self.fields[key] = (ent, status)

        makeentry("username", "username (required)", "yourhandle")
        makeentry("_pinterest_sess", "cookie: _pinterest_sess (required)", "paste _pinterest_sess cookie value")
        makeentry("csrftoken", "cookie: csrftoken (required)", "paste csrftoken cookie value")

        self.btnconnect = ctk.CTkButton(
            self.formbody,
            text="connect session",
            height=44,
            corner_radius=10,
            fg_color=colbrand,
            hover_color=colbrandh,
            font=("Segoe UI", 14, "bold"),
            text_color="#ffffff",
            command=self.startauth
        )
        self.btnconnect.pack(fill="x", pady=(14, 0))

        self.msgstatus = ctk.CTkLabel(self.formbody, text="", wraplength=640,
                                      justify="center", font=("Segoe UI", 12))
        self.msgstatus.pack(anchor="center", pady=(10, 0))

        self.botbar = ctk.CTkFrame(self.container, fg_color="transparent")
        self.botbar.pack(fill="x", pady=(16, 0))

        ctk.CTkButton(
            self.botbar, text="developer: https://www.lwsg.space/",
            image=self.icon_dev, compound="left", height=28, corner_radius=6,
            fg_color="#141416", hover_color="#222226", font=("Segoe UI", 11),
            text_color="#a1a1aa", cursor="hand2",
            command=lambda: webbrowser.open_new_tab("https://www.lwsg.space/")
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            self.botbar, text="source: https://github.com/lastanswtcf/pinbatch-pinterest",
            image=self.icon_src, compound="left", height=28, corner_radius=6,
            fg_color="#141416", hover_color="#222226", font=("Segoe UI", 11),
            text_color="#a1a1aa", cursor="hand2",
            command=lambda: webbrowser.open_new_tab("https://github.com/lastanswtcf/pinbatch-pinterest")
        ).pack(side="left")

        self.disclaimerbox = None

    def getval(self, key):
        ent = self.fields[key][0]
        val = ent.get().strip()
        if key == "username":
            if "pinterest.com" in val:
                val = val.split("/")[-1]
            return val.lstrip("@").strip("/ ")
        parsed = parsecookies(val)
        if parsed.get(key):
            return parsed[key]
        return "".join(val.split()).strip('"').strip("'")

    def checkval(self, key):
        val = self.getval(key)
        lbl = self.fields[key][1]
        if not val:
            lbl.configure(text="", text_color=colmuted)
        elif key == "username":
            lbl.configure(text="ok", text_color=colgreen)
        else:
            short = key == "_pinterest_sess" and len(val) < 100
            lbl.configure(
                text=f"{'short' if short else 'ok'} ({len(val)} chars)",
                text_color="#f59e0b" if short else colgreen
            )

    def setmsg(self, text, color):
        self.msgstatus.configure(text=text, text_color=color)

    def startauth(self):
        uname = self.getval("username")
        sess = self.getval("_pinterest_sess")
        csrf = self.getval("csrftoken")

        if not uname:
            self.fields["username"][0].focus()
            return self.setmsg("username is required.", colred)
        if not sess:
            self.fields["_pinterest_sess"][0].focus()
            return self.setmsg("please enter your _pinterest_sess cookie.", colred)
        if not csrf:
            self.fields["csrftoken"][0].focus()
            return self.setmsg("please enter your csrftoken cookie.", colred)

        self.btnconnect.configure(state="disabled", text="loading")
        self.setmsg("loading", "#ffffff")

        def worker():
            try:
                engine = Engine({"_pinterest_sess": sess, "csrftoken": csrf})
                info, reason = engine.checkauth(uname)
                boards = engine.loadboards() if info else []
                self.after(0, lambda: self.finishauth(engine, info, reason, boards))
            except Exception as exc:
                self.after(0, lambda e=exc: self.finishauth(None, None, str(e), []))

        threading.Thread(target=worker, daemon=True).start()

    def finishauth(self, engine, info, reason, boards):
        self.btnconnect.configure(state="normal", text="connect session")
        if not info:
            return self.setmsg(f"error: {reason}", colred)
        if not boards:
            return self.setmsg(f"connected as @{info['username']}, but no boards were found.", "#f59e0b")

        self.setmsg("", "#ffffff")
        self.showdisclaimer(engine, info, boards)

    def showdisclaimer(self, engine, info, boards):
        self.formcard.pack_forget()
        self.botbar.pack_forget()
        self.topbox.pack_forget()

        if self.disclaimerbox:
            self.disclaimerbox.destroy()

        self.disclaimerbox = ctk.CTkFrame(self.container, fg_color="transparent")
        self.disclaimerbox.pack(fill="both", expand=True)
        ctk.CTkLabel(self.disclaimerbox, image=self.logoimg, text="").pack(pady=(0, 16))
        ctk.CTkLabel(self.disclaimerbox, text="pinbatch", font=("Segoe UI", 26, "bold"),
                     text_color=coltext).pack(pady=(0, 16))

        msg = (
            "pinbatch is an automated tool that uploads images directly to your pinterest account,\n"
            "and may violate pinterest terms of service.\n\n"
            "use this software at your own risk and responsibility."
        )
        ctk.CTkLabel(self.disclaimerbox, text=msg, font=("Segoe UI", 13),
                     text_color="#d4d4d8", justify="center").pack(pady=(0, 14))

        ctk.CTkButton(
            self.disclaimerbox, text="terms of service (policy.pinterest.com/en/terms-of-service)",
            height=28, corner_radius=6, fg_color="#141416", hover_color="#222226",
            font=("Segoe UI", 11), text_color="#a1a1aa", cursor="hand2",
            command=lambda: webbrowser.open_new_tab("https://policy.pinterest.com/en/terms-of-service")
        ).pack(pady=(0, 24))

        def onaccept():
            self.disclaimerbox.destroy()
            self.disclaimerbox = None
            self.topbox.pack(fill="x", pady=(0, 18))
            self.formcard.pack(fill="x")
            self.botbar.pack(fill="x", pady=(16, 0))
            self.onauth(engine, info, boards)

        ctk.CTkButton(
            self.disclaimerbox, text="accept", width=220, height=44,
            corner_radius=10, fg_color=colbrand, hover_color=colbrandh,
            font=("Segoe UI", 14, "bold"), text_color="#ffffff",
            command=onaccept
        ).pack()


class Dashview(ctk.CTkFrame):
    def __init__(self, parent, onquit):
        super().__init__(parent, fg_color=colbg, corner_radius=0)
        self.onquit = onquit
        self.engine = None
        self.items = []
        self.isbusy = False
        self.abort_requested = False
        self._currentcols = 4

        self.icon_del = makeicon("delete", size=(14, 14))
        self.icon_paste = makeicon("paste", size=(15, 15))
        self.icon_import = makeicon("import", size=(15, 15))
        self.icon_clear = makeicon("clear", size=(15, 15))
        self.icon_send = makeicon("send", size=(15, 15))
        self.icon_down = makeicon("down", size=(12, 12))
        self.icon_dev = makeicon("developer", size=(14, 14))
        self.icon_src = makeicon("source", size=(14, 14))

        self.makeui()

    def makeui(self):
        side = ctk.CTkFrame(self, fg_color=colbg, corner_radius=0,
                            width=320, border_width=1, border_color=colline)
        side.pack(side="left", fill="y", padx=0, pady=0)
        side.pack_propagate(False)
        topbox = ctk.CTkFrame(side, fg_color="#0a0a0c", corner_radius=10,
                              border_width=1, border_color=colline)
        topbox.pack(fill="x", padx=16, pady=16)
        userinfo = ctk.CTkFrame(topbox, fg_color="transparent")
        userinfo.pack(fill="x", padx=10, pady=10)
        badge = ctk.CTkFrame(userinfo, fg_color=colgreen, width=8, height=8, corner_radius=4)
        badge.pack(side="left", padx=(0, 8))
        self.lbluser = ctk.CTkLabel(userinfo, text="@user", font=("Segoe UI", 12, "bold"), text_color=coltext)
        self.lbluser.pack(side="left")

        ctk.CTkButton(
            userinfo, text="disconnect", width=74, height=24,
            corner_radius=6, fg_color="#1e1e22", hover_color="#2c2c32",
            font=("Segoe UI", 10), text_color=coltext, command=self.exitview
        ).pack(side="right")

        credbox = ctk.CTkFrame(side, fg_color="#0a0a0c", corner_radius=8,
                               border_width=1, border_color=colline)
        credbox.pack(fill="x", side="bottom", padx=16, pady=16)

        ctk.CTkButton(
            credbox, text="developer: https://www.lwsg.space/",
            image=self.icon_dev, compound="left", height=26, corner_radius=6,
            fg_color="transparent", hover_color="#1a1a1e", font=("Segoe UI", 10),
            text_color="#a1a1aa", anchor="w", cursor="hand2",
            command=lambda: webbrowser.open_new_tab("https://www.lwsg.space/")
        ).pack(fill="x", padx=6, pady=(6, 2))

        ctk.CTkButton(
            credbox, text="source: https://github.com/lastanswtcf/pinbatch-pinterest",
            image=self.icon_src, compound="left", height=26, corner_radius=6,
            fg_color="transparent", hover_color="#1a1a1e", font=("Segoe UI", 10),
            text_color="#a1a1aa", anchor="w", cursor="hand2",
            command=lambda: webbrowser.open_new_tab("https://github.com/lastanswtcf/pinbatch-pinterest")
        ).pack(fill="x", padx=6, pady=(2, 6))

        def sublbl(txt):
            ctk.CTkLabel(side, text=txt, font=("Segoe UI", 11, "bold"),
                         text_color="#aeaeb2").pack(anchor="w", padx=16, pady=(10, 4))

        sublbl("board")
        self.optboard = ctk.CTkOptionMenu(
            side, values=["select board"], fg_color=colfield,
            button_color="#1c1c20", button_hover_color="#28282e",
            corner_radius=8, height=34, font=("Segoe UI", 11),
            dynamic_resizing=False
        )
        self.optboard.pack(fill="x", padx=16)

        def draw_solid_arrow(x, y, s):
            self.optboard._canvas.delete("dropdown_arrow")
            self.optboard._canvas.create_polygon(
                x - 5, y - 3,
                x + 5, y - 3,
                x, y + 4,
                fill="#ffffff", outline="",
                tags="dropdown_arrow"
            )
            return True

        self.optboard._draw_engine.draw_dropdown_arrow = draw_solid_arrow
        sublbl("pin title ({n} = index)")
        self.enttitle = ctk.CTkEntry(side, fg_color=colfield, border_color=colline,
                                     corner_radius=8, height=34,
                                     placeholder_text="optional title", font=("Segoe UI", 11))
        self.enttitle.pack(fill="x", padx=16)

        sublbl("destination url")
        self.entlink = ctk.CTkEntry(side, fg_color=colfield, border_color=colline,
                                    corner_radius=8, height=34,
                                    placeholder_text="https://", font=("Segoe UI", 11))
        self.entlink.pack(fill="x", padx=16)

        sublbl("description")
        self.txtdesc = ctk.CTkTextbox(side, height=84, fg_color=colfield,
                                      border_width=1, border_color=colline,
                                      corner_radius=8, font=("Segoe UI", 11))
        self.txtdesc.pack(fill="x", padx=16)

        self.btnpub = ctk.CTkButton(
            side, text="publish all", height=40, corner_radius=10,
            image=self.icon_send, compound="left",
            fg_color=colbrand, hover_color=colbrandh,
            font=("Segoe UI", 13, "bold"), text_color="#ffffff",
            command=self.startpub
        )
        self.btnpub.pack(fill="x", padx=16, pady=(16, 0))
        self.progbar = ctk.CTkProgressBar(side, progress_color=colbrand,
                                          fg_color="#1c1c20", corner_radius=4, height=6)
        self.progbar.set(0)
        self.progbar.pack(fill="x", padx=16, pady=(10, 0))
        main = ctk.CTkFrame(self, fg_color=colbg, corner_radius=0)
        main.pack(side="left", fill="both", expand=True)
        bar = ctk.CTkFrame(main, fg_color=colbg, corner_radius=0, height=48,
                           border_width=1, border_color=colline)
        bar.pack(fill="x")
        self.lblcount = ctk.CTkLabel(bar, text="0/30 images queued", font=("Segoe UI", 13, "bold"),
                                     text_color=coltext)
        self.lblcount.pack(side="left", padx=16, pady=10)

        ctk.CTkButton(bar, text="clear", width=74, height=28, corner_radius=7,
                      image=self.icon_clear, compound="left",
                      fg_color="#18181c", hover_color="#242428",
                      font=("Segoe UI", 11), text_color=coltext,
                      command=self.clearitems).pack(side="right", padx=(0, 16))

        ctk.CTkButton(bar, text="import", width=80, height=28, corner_radius=7,
                      image=self.icon_import, compound="left",
                      fg_color="#18181c", hover_color="#242428",
                      font=("Segoe UI", 11), text_color=coltext,
                      command=self.importfiles).pack(side="right", padx=(0, 8))

        ctk.CTkButton(bar, text="paste", width=80, height=28, corner_radius=7,
                      image=self.icon_paste, compound="left",
                      fg_color=colbrand, hover_color=colbrandh,
                      font=("Segoe UI", 11, "bold"), text_color="#ffffff",
                      command=self.pasteitems).pack(side="right", padx=(0, 8))

        self.gridframe = ctk.CTkScrollableFrame(main, fg_color=colbg, corner_radius=0)
        self.gridframe.pack(fill="both", expand=True, padx=16, pady=12)

        def onmainresize(e):
            if e.widget == main and e.width > 100:
                cols = max(2, (e.width - 32) // 190)
                if cols != self._currentcols:
                    self._currentcols = cols
                    if self.items:
                        self.rendergrid()

        main.bind("<Configure>", onmainresize, add="+")
        logcard = ctk.CTkFrame(main, fg_color=colbg, corner_radius=12,
                               border_width=1, border_color=colline)
        logcard.pack(fill="x", padx=16, pady=(0, 12))
        loghead = ctk.CTkFrame(logcard, fg_color="transparent")
        loghead.pack(fill="x", padx=12, pady=(8, 2))
        logdot = ctk.CTkFrame(loghead, fg_color=colgreen, width=8, height=8, corner_radius=4)
        logdot.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(loghead, text="activity log", font=("Segoe UI", 11, "bold"),
                     text_color=coltext).pack(side="left")

        ctk.CTkButton(loghead, text="clear log", width=64, height=20, corner_radius=4,
                      fg_color="#18181c", hover_color="#242428",
                      font=("Segoe UI", 10), text_color=colmuted,
                      command=lambda: self.logbox.delete("1.0", "end")).pack(side="right")

        self.logbox = ctk.CTkTextbox(logcard, height=80, fg_color="#0a0a0c",
                                     border_width=1, border_color=colline,
                                     corner_radius=8, font=("Consolas", 10), text_color="#d4d4d8")
        self.logbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def loadacc(self, engine, info, boards):
        self.engine = engine
        self.lbluser.configure(text=f"@{info['username']}")
        vals = [f"{b['name']} ({b['id']})" for b in boards]
        self.optboard.configure(values=vals)
        if vals:
            self.optboard.set(vals[0])
        self.writelog(f"connected as @{info['username']} with {len(boards)} boards.")

    def writelog(self, txt):
        tstamp = time.strftime("%H:%M:%S")
        self.logbox.insert("end", f"[{tstamp}]  {txt}\n")
        self.logbox.see("end")

    def addpaths(self, paths):
        avail = 30 - len(self.items)
        if avail <= 0:
            self.writelog("queue limit reached: maximum 30 images allowed.")
            messagebox.showinfo("limit reached", "queue limit reached: maximum 30 images allowed.")
            return

        to_add = []
        for p in paths:
            norm = os.path.normcase(os.path.abspath(os.path.realpath(p)))
            if any(os.path.normcase(os.path.abspath(os.path.realpath(it["path"]))) == norm for it in self.items) or norm in to_add:
                continue
            to_add.append(norm)

        if len(to_add) > avail:
            self.writelog(f"queue limit: adding {avail} of {len(to_add)} images (max 30).")
            to_add = to_add[:avail]

        for p in to_add:
            thumb = makethumb(p)
            if not thumb:
                self.writelog(f"skipped non-image: {os.path.basename(p)}")
                continue
            self.items.append({
                "path": p,
                "name": os.path.basename(p),
                "thumb": thumb,
                "status": ""
            })
        self.rendergrid()

    def pasteitems(self):
        paths = getclip()
        if paths:
            self.addpaths(paths)
        else:
            self.writelog("no image found in clipboard.")

    def importfiles(self):
        chosen = filedialog.askopenfilenames(
            filetypes=[("image files", "*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if chosen:
            self.addpaths(list(chosen))

    def clearitems(self):
        if self.isbusy:
            return
        self.items.clear()
        self.rendergrid()

    def delitem(self, item):
        if self.isbusy:
            return
        if item in self.items:
            self.items.remove(item)
            self.rendergrid()

    def rendergrid(self):
        for w in self.gridframe.winfo_children():
            w.destroy()

        count = len(self.items)
        self.lblcount.configure(text=f"{count}/30 images queued")

        cols = self._currentcols
        for c in range(cols):
            self.gridframe.grid_columnconfigure(c, weight=1, uniform="gridcard")

        def scrollwheel(e):
            self.gridframe._parent_canvas.yview_scroll(-int(e.delta / 60), "units")

        if not self.items:
            empty = ctk.CTkFrame(self.gridframe, fg_color="transparent")
            empty.grid(row=0, column=0, columnspan=cols, pady=70)

            ctk.CTkLabel(empty, text="no images queued", font=("Segoe UI", 15, "bold"),
                         text_color=coltext).pack(pady=(0, 4))
            ctk.CTkLabel(empty, text="paste from clipboard (ctrl+v) or import images (max 30)",
                         font=("Segoe UI", 12), text_color=colmuted).pack(pady=(0, 14))

            btnrow = ctk.CTkFrame(empty, fg_color="transparent")
            btnrow.pack()

            ctk.CTkButton(btnrow, text="paste images", width=120, height=32, corner_radius=8,
                          image=self.icon_paste, compound="left",
                          fg_color=colbrand, hover_color=colbrandh, font=("Segoe UI", 11, "bold"),
                          command=self.pasteitems).pack(side="left", padx=6)
            ctk.CTkButton(btnrow, text="import files", width=120, height=32, corner_radius=8,
                          image=self.icon_import, compound="left",
                          fg_color="#18181c", hover_color="#242428", font=("Segoe UI", 11),
                          command=self.importfiles).pack(side="left", padx=6)
            return

        statcolors = {"done": colgreen, "fail": colred, "wait": "#f59e0b"}

        for idx, it in enumerate(self.items):
            card = ctk.CTkFrame(self.gridframe, fg_color="#0a0a0c", corner_radius=12,
                                border_width=1, border_color=colline)
            card.grid(row=idx // cols, column=idx % cols, padx=8, pady=8, sticky="nsew")

            lblimg = ctk.CTkLabel(card, image=it["thumb"], text="")
            lblimg.pack(padx=8, pady=(8, 4))

            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=(0, 8))

            tag = it["status"] or f"#{idx + 1}"
            lbltag = ctk.CTkLabel(row, text=tag, font=("Segoe UI", 10, "bold"),
                                  text_color=statcolors.get(it["status"], colmuted))
            lbltag.pack(side="left")

            btndel = ctk.CTkButton(row, image=self.icon_del, text="", width=24, height=24, corner_radius=6,
                                   fg_color="#1c1c20", hover_color=colred,
                                   command=lambda x=it: self.delitem(x))
            btndel.pack(side="right")

            card.bind("<MouseWheel>", scrollwheel, add="+")
            lblimg.bind("<MouseWheel>", scrollwheel, add="+")
            row.bind("<MouseWheel>", scrollwheel, add="+")
            lbltag.bind("<MouseWheel>", scrollwheel, add="+")

        self.gridframe._parent_canvas.bind("<MouseWheel>", scrollwheel, add="+")

    def startpub(self):
        if self.isbusy:
            return
        if not self.items:
            return messagebox.showinfo("empty queue", "add images before publishing.")

        boardval = self.optboard.get()
        if "(" not in boardval:
            return messagebox.showerror("board", "please select a valid target board.")

        boardid = boardval.rsplit("(", 1)[1].rstrip(")").strip()
        titleval = self.enttitle.get().strip()
        linkval = self.entlink.get().strip()
        descval = self.txtdesc.get("1.0", "end").strip()

        if linkval:
            parsed = urllib.parse.urlparse(linkval)
            if not parsed.scheme or not parsed.netloc or parsed.scheme not in ("http", "https"):
                return messagebox.showerror("invalid link", "url must be a valid link starting with http:// or https://")

        self.isbusy = True
        self.abort_requested = False
        self.progbar.set(0)
        self.btnpub.configure(state="disabled", text="publishing...")
        for it in self.items:
            it["status"] = ""
        itemlist = list(self.items)

        def safe_ui(fn):
            try:
                if self.winfo_exists():
                    self.after(0, fn)
            except Exception:
                pass

        def worker():
            done = 0
            fails = 0
            consecutive_fails = 0

            for idx, it in enumerate(itemlist, 1):
                if self.abort_requested or not self.winfo_exists():
                    safe_ui(lambda: self.writelog("publishing aborted."))
                    break

                it["status"] = "wait"
                safe_ui(self.rendergrid)
                tit = titleval.replace("{n}", str(idx)) if titleval else ""

                try:
                    self.engine.uploadpin(boardid, it["path"], tit, descval, linkval)
                    it["status"] = "done"
                    done += 1
                    consecutive_fails = 0
                    safe_ui(lambda n=idx, t=len(itemlist): self.writelog(f"published {n}/{t}"))
                except Exception as exc:
                    it["status"] = "fail"
                    fails += 1
                    consecutive_fails += 1
                    err_msg = str(exc)
                    safe_ui(lambda n=idx, t=len(itemlist), m=err_msg: self.writelog(f"failed {n}/{t}: {m}"))

                    if "429" in err_msg or "rate limit" in err_msg.lower():
                        safe_ui(lambda: self.writelog("rate limit detected from pinterest. stopping queue."))
                        break

                    if consecutive_fails >= 3:
                        safe_ui(lambda: self.writelog("3 consecutive failures encountered. pausing publishing queue."))
                        break

                frac = idx / len(itemlist)
                safe_ui(lambda v=frac: self.progbar.set(v))
                safe_ui(self.rendergrid)

                if idx < len(itemlist):
                    for _ in range(30):
                        if self.abort_requested or not self.winfo_exists():
                            break
                        time.sleep(0.1)

            safe_ui(lambda d=done, t=len(itemlist): self.writelog(f"finished: {d}/{t} published successfully."))
            self.isbusy = False
            safe_ui(lambda: self.btnpub.configure(state="normal", text="publish all"))

        threading.Thread(target=worker, daemon=True).start()

    def exitview(self):
        if self.isbusy:
            if not messagebox.askyesno("publishing in progress", "uploads are currently running. do you want to abort and disconnect?"):
                return
            self.abort_requested = True
        self.engine = None
        self.items.clear()
        self.progbar.set(0)
        self.rendergrid()
        self.onquit()
