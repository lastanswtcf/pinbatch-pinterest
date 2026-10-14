# <img src="images/logo.png" width="36" height="36" alt="pinbatch logo" valign="middle"> pinbatch

pinbatch is a minimal desktop tool to upload batches of images directly to pinterest boards in seconds.

no browser automation popups, no selenium windows during upload, and no credentials saved after closing the app.

> [!NOTE]
> your credentials stay in memory and in an ephemeral temp folder that is automatically deleted when the app closes or restarts.

---

### requirements & installation

| requirement | version |
| :--- | :--- |
| **operating system** | windows 10 / 11 |
| **python** | python 3.10+ |

install the required dependencies:

```bash
pip install -r requirements.txt
```

start the tool:

```bash
run_app.bat
```

> [!TIP]
> you can paste images directly from your clipboard anywhere in the dashboard using <kbd>Ctrl</kbd> + <kbd>V</kbd>.

---

### how to use

1. run `run_app.bat` or `python app.py`.
2. enter your pinterest username.
3. get your session cookies from browser devtools (<kbd>F12</kbd> > application > cookies > pinterest.com):
   - `_pinterest_sess`
   - `csrftoken`
4. click `connect`.
5. read and accept the disclaimer prompt.
6. import images with `import files` or paste them with <kbd>Ctrl</kbd> + <kbd>V</kbd> (up to 30 images).
7. pick your target board, set an optional title template (e.g. `pin #{n}`), add a link if needed, and click `publish all`.

---

### built-in safety limits

- **30 images limit**: batches are capped at 30 images to prevent triggering automated spam blocks.
- **duplicate protection**: prevents uploading identical images already present in the current queue.
- **rate-limit stop**: automatically halts the queue if pinterest returns an `http 429` (rate limit).
- **auto-pause on errors**: pauses publishing if 3 consecutive uploads fail to protect your account.

---

### important disclaimer

pinbatch uses internal pinterest endpoints via your browser session cookies.

> [!WARNING]
> automated uploading may violate [pinterest terms of service](https://policy.pinterest.com/en/terms-of-service). excessive posting can lead to account restrictions, shadowbans, or rate limits. use this tool responsibly and at your own risk.

---

### links & license

- **developer**: [lwsg.space](https://www.lwsg.space/)
- **repository**: [pinbatch-pinterest](https://github.com/lastanswtcf/pinbatch-pinterest)
- **license**: custom license (see `LICENSE` file)
