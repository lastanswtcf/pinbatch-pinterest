import atexit
import ctypes
import json
import os
import re
import shutil
import tempfile
import urllib.parse
import requests
from py3pin.Pinterest import Pinterest

baseurl = "https://www.pinterest.com"
reqcookies = ("_pinterest_sess", "csrftoken")
optcookies = ("_auth", "_b", "_routing_id", "sessionFunnelEventLogged")
agenthdr = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
browserhdrs = {
    "User-Agent": agenthdr,
    "Accept": "application/json, text/javascript, */*, q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Referer": baseurl + "/",
    "Origin": baseurl,
    "X-Requested-With": "XMLHttpRequest",
    "X-Pinterest-PWS-Handler": "www/[username].js",
    "X-Pinterest-Source-Url": "/",
    "X-App-Version": "c0a8f2b",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


def cleanstr(val):
    return str(val).strip().strip('"').strip("'").strip()

def parsecookies(text):
    text = (text or "").strip()
    res = {}
    if not text:
        return res
    if text[0] in "{[":
        try:
            raw = json.loads(text)
            if isinstance(raw, dict):
                for k, v in raw.items():
                    if isinstance(v, (str, int)):
                        res[k] = cleanstr(v)
            elif isinstance(raw, list):
                for item in raw:
                    if isinstance(item, dict) and "name" in item and "value" in item:
                        res[item["name"]] = cleanstr(item["value"])
            if res:
                return res
        except ValueError:
            pass

    text = re.sub(r"^\s*cookie\s*:\s*", "", text, flags=re.I)
    wanted = set(reqcookies) | set(optcookies)

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = re.split(r"\t+", line)
        if len(parts) >= 2 and parts[0].strip() in wanted:
            res[parts[0].strip()] = cleanstr(parts[1])
            continue
        m = re.match(r"^([A-Za-z0-9_\-]+)\s*:\s*(.+)$", line)
        if m and m.group(1) in wanted:
            res[m.group(1)] = cleanstr(m.group(2))

    for chunk in text.replace("\n", ";").split(";"):
        if "=" in chunk:
            k, _, v = chunk.partition("=")
            k = k.strip()
            if k and re.fullmatch(r"[A-Za-z0-9_\-]+", k):
                res.setdefault(k, cleanstr(v))

    if not res and "\n" not in text and " " not in text and len(text) > 40:
        res["_pinterest_sess"] = cleanstr(text)

    return res

def is_pid_running(pid):
    if pid <= 0:
        return False
    if os.name == "nt":
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(0x1000 | 0x00100000, False, pid)
        if not handle:
            return False
        exit_code = ctypes.c_ulong()
        kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
        kernel32.CloseHandle(handle)
        return exit_code.value == 259
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def clean_orphans():
    try:
        td = tempfile.gettempdir()
        current_pid = os.getpid()
        for item in os.listdir(td):
            if item.startswith(("pinbatch_", "pinbatch_img_")):
                parts = item.split("_")
                is_active = False
                if len(parts) >= 3 and parts[1] == "img" and parts[2].isdigit():
                    pid = int(parts[2])
                    if pid == current_pid or is_pid_running(pid):
                        is_active = True
                elif len(parts) >= 2 and parts[1].isdigit():
                    pid = int(parts[1])
                    if pid == current_pid or is_pid_running(pid):
                        is_active = True
                if not is_active:
                    full = os.path.join(td, item)
                    shutil.rmtree(full, ignore_errors=True)
    except Exception:
        pass

clean_orphans()

class Engine:
    def __init__(self, cookies):
        self.cookies = {k: v for k, v in cookies.items() if v}
        self.username = None
        self.userid = None
        self.session = requests.Session()
        for k, v in self.cookies.items():
            self.session.cookies.set(k, v, domain=".pinterest.com", path="/")
        self.session.headers.update(browserhdrs)
        if self.cookies.get("csrftoken"):
            self.session.headers["X-CSRFToken"] = self.cookies["csrftoken"]
        self.tmpdir = tempfile.mkdtemp(prefix=f"pinbatch_{os.getpid()}_")
        atexit.register(shutil.rmtree, self.tmpdir, True)
        self.api = Pinterest(cred_root=self.tmpdir, user_agent=agenthdr)
        self.api.http.headers.update(browserhdrs)
        for k, v in self.cookies.items():
            self.api.http.cookies.set(k, v, domain=".pinterest.com", path="/")

    def __del__(self):
        if hasattr(self, "tmpdir") and os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir, ignore_errors=True)

    def resget(self, name, opts, srcurl="/"):
        payload = json.dumps({"options": opts, "context": {}})
        url = "{}/resource/{}/get/?source_url={}&data={}".format(
            baseurl, name, urllib.parse.quote(srcurl, safe=""),
            urllib.parse.quote(payload, safe="")
        )
        return self.session.get(url, timeout=20)

    def checkauth(self, uname):
        uname = (uname or "").strip().lstrip("@").strip("/ ")
        if "pinterest.com" in uname:
            uname = uname.split("/")[-1].strip()

        if not uname:
            return None, "username is required to verify your boards!"

        if not self.cookies.get("_pinterest_sess"):
            return None, "missing _pinterest_sess cookie!"
        if not self.cookies.get("csrftoken"):
            return None, "missing csrftoken cookie!"

        opts = {
            "username": uname,
            "page_size": 1,
            "field_set_key": "profile_grid_item"
        }

        try:
            resp = self.resget("BoardsResource", opts, f"/{uname}/boards/")
        except requests.RequestException as exc:
            return None, f"network error: {exc}"

        try:
            body = resp.json()
        except ValueError:
            return None, f"pinterest returned non-json answer (code {resp.status_code})"

        ctx = body.get("client_context", {})
        authed = bool(ctx.get("is_authenticated"))
        diag = f"[code {resp.status_code} | authed={authed} | bot={ctx.get('is_bot')}]"

        if not authed:
            return None, f"session rejected {diag}. check if _pinterest_sess is valid!"

        user = ctx.get("user") or {}
        self.userid = user.get("id")
        self.username = uname
        self.api.username = uname

        return {
            "username": self.username,
            "fullname": user.get("full_name") or self.username
        }, f"connected {diag}"

    def loadboards(self):
        boards = []
        seen = set()

        def addlist(items):
            for b in items or []:
                bid = b.get("id")
                name = b.get("name")
                if bid and name and str(bid) not in seen:
                    seen.add(str(bid))
                    boards.append({"id": str(bid), "name": name})

        try:
            self.api.username = self.username
            addlist(self.api.boards_all(username=self.username))
        except Exception:
            pass

        if not boards and self.username:
            bookmark = None
            for _ in range(20):
                opts = {
                    "username": self.username,
                    "page_size": 50,
                    "privacy_filter": "all",
                    "sort": "custom",
                    "field_set_key": "profile_grid_item",
                    "group_by": "visibility",
                    "include_archived": True,
                }
                if bookmark:
                    opts["bookmarks"] = [bookmark]
                try:
                    r = self.resget("BoardsResource", opts, f"/{self.username}/boards/").json()
                except Exception:
                    break
                addlist(r.get("resource_response", {}).get("data"))
                bms = r.get("resource", {}).get("options", {}).get("bookmarks") or []
                bookmark = bms[0] if bms else None
                if not bookmark or bookmark == "-end-":
                    break

        return boards
    def uploadpin(self, boardid, imgpath, title="", desc="", link=""):
        resp = self.api.upload_pin(
            board_id=str(boardid),
            image_file=imgpath,
            title=title or "",
            description=desc or "",
            link=link or ""
        )
        try:
            body = resp.json().get("resource_response", {})
        except Exception:
            return {}
        if body.get("error"):
            msg = body["error"].get("message") or "pinterest rejected the pin!"
            raise RuntimeError(msg)
        return body.get("data", {})
