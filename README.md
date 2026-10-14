# pinbatch

pinbatch is a minimal desktop application built to upload batches of images directly to pinterest boards in seconds.

no heavy browser automation windows, no selenium popups during upload, and no credentials persisted after exit.

---

### requirements & installation

- **os**: windows 10 / 11
- **python**: python 3.10 or newer

install dependencies using pip:

```bash
pip install -r requirements.txt
```

---

### how it works

1. launch the app via `run_app.bat` or `python app.py`.
2. enter your pinterest username.
3. grab your session cookies from your browser devtools (`f12` > application > cookies > pinterest.com):
   - `_pinterest_sess`
   - `csrftoken`
4. click `connect session`. session tokens are maintained in memory and in an ephemeral process temp folder automatically deleted on exit via `atexit`.
5. review the terms of service disclaimer and click `accept`.
6. paste images directly from your clipboard (`ctrl+v`) or click `import` (maximum 30 images per batch).
7. select your target board, configure optional title templates with `{n}` indexing, set a destination link, and hit `publish all`.

---

### features & safety mechanisms

- **queue safety**: capped at 30 images per run to prevent accidental spam triggers.
- **rate-limit detection**: automatically identifies http 429 responses and pauses the publishing queue.
- **error recovery**: pauses queue if 3 consecutive upload failures occur to prevent account penalties.

---

### important notice & disclaimer

pinbatch connects via internal api endpoints using your browser session cookies.

automated uploading and high-frequency bulk publishing may violate [pinterest terms of service](https://policy.pinterest.com/en/terms-of-service). excessive posting can lead to account restrictions, shadowbans, or rate limits.

use this tool responsibly and entirely at your own risk.

---

### links & license

- developer: [lwsg.space](https://www.lwsg.space/)
- source code: [pinbatch-pinterest](https://github.com/lastanswtcf/pinbatch-pinterest)
- license: custom license (see `LICENSE` file for details)
