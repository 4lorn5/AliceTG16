#!/usr/bin/env python3


import hashlib
import os
import sys
import threading
import zlib
import tkinter as tk
from tkinter import filedialog, messagebox

# ── IPS core logic ─────────────────────────────────────────────────────────────

PATCH_HEADER  = b"PATCH"
EOF_MARKER    = b"EOF"

REQUIRED_SHA1  = "C266B05DD367B2973399B8DAFF7C4DC33BEBEDD9"
REQUIRED_CRC32 = "12C4E6FD"


def verify_rom(data: bytes) -> None:
    """Raise ValueError if ROM hashes don't match the expected Alice (PCE) values."""
    sha1  = hashlib.sha1(data).hexdigest().upper()
    crc32 = f"{zlib.crc32(data) & 0xFFFFFFFF:08X}"

    if sha1 != REQUIRED_SHA1 or crc32 != REQUIRED_CRC32:
        raise ValueError(
            f"ROM hash mismatch — wrong or modified ROM.\n\n"
            f"  Expected  SHA-1 : {REQUIRED_SHA1}\n"
            f"  Got       SHA-1 : {sha1}\n\n"
            f"  Expected  CRC32 : {REQUIRED_CRC32}\n"
            f"  Got       CRC32 : {crc32}"
        )


def apply_ips(rom_path: str, ips_path: str, out_path: str, log) -> dict:
    log("Reading ROM…")
    with open(rom_path, "rb") as f:
        rom = bytearray(f.read())

    log("Verifying ROM hashes…")
    verify_rom(bytes(rom))
    log("SHA-1 / CRC32 verified.")

    log("Reading IPS patch…")
    with open(ips_path, "rb") as f:
        ips = f.read()

    if not ips.startswith(PATCH_HEADER):
        raise ValueError("Not a valid IPS file — missing PATCH header.")

    pos = 5
    records = rle_records = bytes_written = 0

    log("Applying patch records…")
    while pos < len(ips):
        raw_offset = ips[pos:pos + 3]
        pos += 3

        if raw_offset == EOF_MARKER:
            break
        if len(raw_offset) < 3:
            raise ValueError(f"Truncated IPS: unexpected end reading offset at pos {pos}.")

        offset = int.from_bytes(raw_offset, "big")

        if pos + 2 > len(ips):
            raise ValueError(f"Truncated IPS: unexpected end reading size at pos {pos}.")
        size = int.from_bytes(ips[pos:pos + 2], "big")
        pos += 2

        if size == 0:
            if pos + 3 > len(ips):
                raise ValueError(f"Truncated IPS: unexpected end reading RLE data at pos {pos}.")
            rle_len  = int.from_bytes(ips[pos:pos + 2], "big")
            rle_byte = ips[pos + 2]
            pos += 3

            needed = offset + rle_len
            if needed > len(rom):
                rom.extend(b"\x00" * (needed - len(rom)))
            rom[offset:offset + rle_len] = bytes([rle_byte]) * rle_len
            bytes_written += rle_len
            rle_records   += 1
        else:
            if pos + size > len(ips):
                raise ValueError(
                    f"Truncated IPS: record at 0x{offset:06X} "
                    f"claims {size} bytes but only {len(ips) - pos} remain."
                )
            data = ips[pos:pos + size]
            pos += size

            needed = offset + size
            if needed > len(rom):
                rom.extend(b"\x00" * (needed - len(rom)))
            rom[offset:offset + size] = data
            bytes_written += size

        records += 1

    log(f"Writing output to {os.path.basename(out_path)}…")
    with open(out_path, "wb") as f:
        f.write(rom)

    return {
        "records":      records,
        "rle_records":  rle_records,
        "bytes_written": bytes_written,
        "output_size":  len(rom),
        "out_path":     out_path,
    }


# ── GUI ────────────────────────────────────────────────────────────────────────

BG          = "#0d0d0d"
BG2         = "#141414"
BORDER      = "#2a2a2a"
GREEN       = "#39ff14"   # neon green — primary accent
GREEN_DIM   = "#1a7a09"
AMBER       = "#ffb300"   # amber — secondary / log text
AMBER_DIM   = "#7a5500"
RED         = "#ff3b3b"
TEXT        = "#d4d4d4"
MONO        = ("Courier", 10)
MONO_SM     = ("Courier", 9)
TITLE_FONT  = ("Courier", 22, "bold")
LABEL_FONT  = ("Courier", 9, "bold")
BTN_FONT    = ("Courier", 10, "bold")


class IPSPatcherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Alice Patcher (PCE)")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.rom_path = tk.StringVar()
        self.ips_path = tk.StringVar()
        self.out_path = tk.StringVar()

        self._build_ui()
        self._center()

    # ── layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = self

        # ── header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(root, bg=BG, pady=14)
        hdr.pack(fill="x")

        tk.Label(hdr, text="ALICE PATCHER (PCE)", font=TITLE_FONT,
                 fg=GREEN, bg=BG).pack()
        tk.Label(hdr, text="ROM • PATCH • APPLY", font=MONO_SM,
                 fg=GREEN_DIM, bg=BG).pack()

        self._divider(root)

        # ── file inputs ───────────────────────────────────────────────────────
        fields = tk.Frame(root, bg=BG, padx=24, pady=10)
        fields.pack(fill="x")

        self._file_row(fields, "ROM FILE",   self.rom_path,
                       [("ROM files", "*.pce *.smc *.md *.nes *.gba *.gb *.gbc *.sfc *.bin *.rom"),
                        ("All files", "*.*")])
        self._file_row(fields, "IPS PATCH",  self.ips_path,
                       [("IPS patch", "*.ips"), ("All files", "*.*")])
        self._file_row(fields, "OUTPUT",     self.out_path,
                       [("All files", "*.*")], save=True)

        self._divider(root)

        # ── apply button ──────────────────────────────────────────────────────
        btn_frame = tk.Frame(root, bg=BG, pady=12)
        btn_frame.pack()

        self.apply_btn = tk.Button(
            btn_frame, text="[ APPLY PATCH ]",
            font=BTN_FONT, fg=BG, bg=GREEN,
            activebackground=GREEN_DIM, activeforeground=BG,
            relief="flat", cursor="hand2",
            padx=24, pady=8,
            command=self._start_patch
        )
        self.apply_btn.pack()

        self._divider(root)

        # ── log window ────────────────────────────────────────────────────────
        log_frame = tk.Frame(root, bg=BG, padx=24, pady=0)
        log_frame.pack(fill="x")

        tk.Label(log_frame, text="LOG", font=LABEL_FONT,
                 fg=GREEN_DIM, bg=BG, anchor="w").pack(fill="x")

        log_inner = tk.Frame(log_frame, bg=BG2,
                             highlightbackground=BORDER, highlightthickness=1)
        log_inner.pack(fill="x", pady=(2, 12))

        self.log_text = tk.Text(
            log_inner, height=9, width=62,
            font=MONO_SM, fg=AMBER, bg=BG2,
            insertbackground=GREEN, relief="flat",
            state="disabled", wrap="word",
            padx=8, pady=6,
            selectbackground=GREEN_DIM
        )
        self.log_text.pack(fill="both", expand=True)

        # colour tags
        self.log_text.tag_config("ok",    foreground=GREEN)
        self.log_text.tag_config("err",   foreground=RED)
        self.log_text.tag_config("stats", foreground=TEXT)

        self._log("Ready. Select a ROM and IPS patch to begin.")

    def _file_row(self, parent, label, var, filetypes, save=False):
        row = tk.Frame(parent, bg=BG, pady=5)
        row.pack(fill="x")

        tk.Label(row, text=label, font=LABEL_FONT,
                 fg=GREEN_DIM, bg=BG, width=10, anchor="w").pack(side="left")

        entry = tk.Entry(
            row, textvariable=var,
            font=MONO_SM, fg=AMBER, bg=BG2,
            insertbackground=GREEN, relief="flat",
            highlightbackground=BORDER, highlightthickness=1,
            width=38
        )
        entry.pack(side="left", padx=(4, 6), ipady=4)

        cmd = (self._browse_save if save else self._browse_open)
        btn = tk.Button(
            row, text="BROWSE",
            font=("Courier", 8, "bold"), fg=GREEN, bg=BG2,
            activebackground=BORDER, activeforeground=GREEN,
            relief="flat", cursor="hand2",
            highlightbackground=BORDER, highlightthickness=1,
            padx=8, pady=3,
            command=lambda v=var, ft=filetypes, s=save: cmd(v, ft)
        )
        btn.pack(side="left")

        # Auto-populate output when ROM is chosen
        if label == "ROM FILE":
            var.trace_add("write", self._auto_output)

    def _divider(self, parent):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=0)

    # ── file dialogs ──────────────────────────────────────────────────────────

    def _browse_open(self, var, filetypes):
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            var.set(path)

    def _browse_save(self, var, filetypes):
        path = filedialog.asksaveasfilename(
            defaultextension="",
            filetypes=filetypes,
            initialfile=os.path.basename(var.get()) if var.get() else ""
        )
        if path:
            var.set(path)

    def _auto_output(self, *_):
        rom = self.rom_path.get()
        if rom and not self.out_path.get():
            base, ext = os.path.splitext(rom)
            self.out_path.set(f"{base}_patched{ext}")

    # ── patching ──────────────────────────────────────────────────────────────

    def _start_patch(self):
        rom = self.rom_path.get().strip()
        ips = self.ips_path.get().strip()
        out = self.out_path.get().strip()

        if not rom or not ips:
            messagebox.showerror("Missing files", "Please select both a ROM and an IPS patch.")
            return
        if not out:
            messagebox.showerror("Missing output", "Please specify an output file path.")
            return
        if not os.path.isfile(rom):
            messagebox.showerror("File not found", f"ROM not found:\n{rom}")
            return
        if not os.path.isfile(ips):
            messagebox.showerror("File not found", f"IPS patch not found:\n{ips}")
            return

        self.apply_btn.configure(state="disabled", text="[ PATCHING… ]", bg=GREEN_DIM)
        self._clear_log()
        threading.Thread(target=self._run_patch, args=(rom, ips, out), daemon=True).start()

    def _run_patch(self, rom, ips, out):
        try:
            result = apply_ips(rom, ips, out, self._log)
            self.after(0, self._on_success, result)
        except Exception as exc:
            self.after(0, self._on_error, str(exc))

    def _on_success(self, r):
        self._log("", tag="ok")
        self._log("✓  PATCH APPLIED SUCCESSFULLY", tag="ok")
        self._log("─" * 44, tag="stats")
        self._log(f"   Records   : {r['records']}  "
                  f"({r['rle_records']} RLE, {r['records']-r['rle_records']} literal)", tag="stats")
        self._log(f"   Modified  : {r['bytes_written']:,} bytes", tag="stats")
        self._log(f"   ROM size  : {r['output_size']:,} bytes", tag="stats")
        self._log(f"   Output    : {os.path.basename(r['out_path'])}", tag="stats")
        self._log("─" * 44, tag="stats")
        self.apply_btn.configure(state="normal", text="[ APPLY PATCH ]", bg=GREEN)

    def _on_error(self, msg):
        self._log("", tag="err")
        self._log(f"✗  ERROR: {msg}", tag="err")
        self.apply_btn.configure(state="normal", text="[ APPLY PATCH ]", bg=GREEN)

    # ── log helpers ───────────────────────────────────────────────────────────

    def _log(self, message, tag=None):
        self.log_text.configure(state="normal")
        prefix = "» " if tag != "stats" and message else ""
        self.log_text.insert("end", prefix + message + "\n", tag or "")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    # ── window centering ──────────────────────────────────────────────────────

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")


# ── entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = IPSPatcherApp()
    app.mainloop()
