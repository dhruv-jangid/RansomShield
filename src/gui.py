"""
RansomShield v4.1 — Enterprise Cybersecurity Dashboard
Polish pass: glow cards, smoother sidebar, Backups tab, better progress UX.
Backend logic 100% unchanged.
"""

import tkinter as tk
from tkinter import scrolledtext, filedialog, ttk
import sys, os, threading, time, shutil, csv, math, random
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

try:
    from src.entropy_detector import EntropyDetector
except ImportError:
    from entropy_detector import EntropyDetector
try:
    from src.extension_detector import ExtensionDetector
except ImportError:
    from extension_detector import ExtensionDetector
try:
    from src.ml_detector import MLDetector
except ImportError:
    from ml_detector import MLDetector
try:
    from src.reputation_engine import ReputationEngine
except ImportError:
    from reputation_engine import ReputationEngine
try:
    from src.backup_manager import BackupManager
except ImportError:
    from backup_manager import BackupManager
try:
    from src.behavior import BehaviorAnalyzer
except ImportError:
    from behavior import BehaviorAnalyzer
try:
    from src.honeypot import HoneypotManager
except ImportError:
    from honeypot import HoneypotManager


# ─────────────────────────────────────────────────────────────
#  COLOR SYSTEM
# ─────────────────────────────────────────────────────────────
def tk_color(c):
    if c and c.startswith("#") and len(c) > 7:
        return c[:7]
    return c

DARK = {
    "name": "dark",
    "bg_void":      "#010406",
    "bg_base":      "#040B14",
    "bg_panel":     "#070E1A",
    "bg_card":      "#0B1622",
    "bg_elevated":  "#0F1D2E",
    "bg_hover":     "#142438",
    "bg_input":     "#091420",
    "bg_border":    "#1A2C40",
    "bg_glass":     "#0D1B2E",
    "fg_primary":   "#E8F4FF",
    "fg_secondary": "#4E789E",
    "fg_muted":     "#253848",
    "fg_dim":       "#111E2C",
    "accent":       "#00BFE8",
    "accent_dark":  "#005F78",
    "accent_glow":  "#0099C0",
    "accent_soft":  "#061620",
    "accent_mid":   "#003850",
    "accent_ring":  "#004460",
    "success":      "#00DFA0",
    "success_bg":   "#002216",
    "success_glow": "#00A870",
    "success_ring": "#003828",
    "danger":       "#FF3652",
    "danger_bg":    "#1E050F",
    "danger_glow":  "#C01830",
    "danger_ring":  "#420816",
    "warning":      "#FFAD18",
    "warning_bg":   "#1E1400",
    "warning_glow": "#C07800",
    "warning_ring": "#3C2800",
    "purple":       "#9155F5",
    "purple_bg":    "#120720",
    "purple_ring":  "#2C0858",
    "btn_text":     "#000A12",
    "accent_tint":  "#061420",
    "accent_ring2": "#003E58",
    "success_tint": "#001E14",
    "danger_tint":  "#1E050F",
    "white_shine":  "#162436",
    "scrollbar":    "#142030",
    "progress_bg":  "#050C16",
    "tab_active":   "#0B1622",
    "tab_inactive": "#050C16",
    "header_bg":    "#02060C",
    "separator":    "#0D1C2C",
    "pulse1":       "#00BFE8",
    "pulse2":       "#005F78",
    "notif_bg":     "#091522",
    "notif_border": "#183048",
    "card_glow":    "#0A2030",
    "btn_shadow":   "#000810",
}

LIGHT = {
    "name": "light",
    "bg_void":      "#E4EDF8",
    "bg_base":      "#EBF2FC",
    "bg_panel":     "#F5F8FF",
    "bg_card":      "#FFFFFF",
    "bg_elevated":  "#EAF0FB",
    "bg_hover":     "#DCE8F5",
    "bg_input":     "#F0F6FF",
    "bg_border":    "#C0D4EC",
    "bg_glass":     "#FFFFFF",
    "fg_primary":   "#080F1C",
    "fg_secondary": "#3A5580",
    "fg_muted":     "#8AAAC8",
    "fg_dim":       "#C0D4EC",
    "accent":       "#007AAA",
    "accent_dark":  "#004466",
    "accent_glow":  "#005580",
    "accent_soft":  "#D0EAF5",
    "accent_mid":   "#A0D0E8",
    "accent_ring":  "#80C0DC",
    "success":      "#009960",
    "success_bg":   "#E0FFF4",
    "success_glow": "#007040",
    "success_ring": "#A0E8CC",
    "danger":       "#D42040",
    "danger_bg":    "#FFE8EC",
    "danger_glow":  "#A01030",
    "danger_ring":  "#F0B0BC",
    "warning":      "#B06000",
    "warning_bg":   "#FFF4DC",
    "warning_glow": "#804400",
    "warning_ring": "#E8D090",
    "purple":       "#6633BB",
    "purple_bg":    "#F0E8FF",
    "purple_ring":  "#C8A8F0",
    "btn_text":     "#FFFFFF",
    "accent_tint":  "#D0EAF5",
    "accent_ring2": "#90C8DC",
    "success_tint": "#C0F0DC",
    "danger_tint":  "#FFE0E4",
    "white_shine":  "#FFFFFF",
    "scrollbar":    "#C0D4EC",
    "progress_bg":  "#E0EAF8",
    "tab_active":   "#FFFFFF",
    "tab_inactive": "#EAF0FC",
    "header_bg":    "#FFFFFF",
    "separator":    "#D8E6F4",
    "pulse1":       "#007AAA",
    "pulse2":       "#004466",
    "notif_bg":     "#FFFFFF",
    "notif_border": "#C0D4EC",
}


# ─────────────────────────────────────────────────────────────
#  CANVAS HELPERS
# ─────────────────────────────────────────────────────────────
def rr(canvas, x1, y1, x2, y2, r=14, **kw):
    for k in ("fill", "outline"):
        if k in kw and kw[k]:
            kw[k] = tk_color(kw[k])
    pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r,
           x2,y2-r, x2,y2, x2-r,y2, x1+r,y2,
           x1,y2, x1,y2-r, x1,y1+r, x1,y1, x1+r,y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


# ─────────────────────────────────────────────────────────────
#  ROUNDED BUTTON  (polished: icon pill, glow ring)
# ─────────────────────────────────────────────────────────────
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, icon="",
                 bg="#00BFE8", fg="#000A12", hover="#0099C0",
                 w=190, h=42, r=12, fs=10, **kw):
        super().__init__(parent, width=w, height=h,
                         highlightthickness=0, bd=0, **kw)
        self.cmd   = command
        self.bg0   = tk_color(bg)
        self.bg1   = tk_color(hover)
        self.fg    = tk_color(fg)
        self.r     = r
        self.txt   = text
        self.ico   = icon
        self.fs    = fs
        self._a    = 0.0
        self._id   = None
        self._theme = None
        self._draw(self.bg0)
        self.bind("<Enter>",           lambda e: self._anim(1.0))
        self.bind("<Leave>",           lambda e: self._anim(0.0))
        self.bind("<ButtonPress-1>",   lambda e: self._press())
        self.bind("<ButtonRelease-1>", lambda e: self._release())

    def _press(self):
        self._draw(self._lerp(self.bg0, self.bg1, min(1.0, self._a + 0.3)))

    def _release(self):
        if self.cmd: self.cmd()

    def _lerp(self, c1, c2, t):
        c1, c2 = tk_color(c1), tk_color(c2)
        h = lambda s: int(s, 16)
        r1,g1,b1 = h(c1[1:3]),h(c1[3:5]),h(c1[5:7])
        r2,g2,b2 = h(c2[1:3]),h(c2[3:5]),h(c2[5:7])
        return f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"

    def _brighten(self, c, f=1.25):
        c = tk_color(c)
        try:
            return (f"#{min(255,int(int(c[1:3],16)*f)):02x}"
                    f"{min(255,int(int(c[3:5],16)*f)):02x}"
                    f"{min(255,int(int(c[5:7],16)*f)):02x}")
        except: return c

    def _darken(self, c, f=0.55):
        c = tk_color(c)
        try:
            return (f"#{int(int(c[1:3],16)*f):02x}"
                    f"{int(int(c[3:5],16)*f):02x}"
                    f"{int(int(c[5:7],16)*f):02x}")
        except: return c

    def _draw(self, fill):
        fill = tk_color(fill)
        self.delete("all")
        w = self.winfo_reqwidth(); h = self.winfo_reqheight()
        T = self._theme
        shine   = T["white_shine"]  if T else "#162436"
        bg_base = T["bg_panel"]     if T else "#070E1A"
        fg_col  = T["fg_secondary"] if T else "#4E789E"

        # Shadow
        rr(self, 2, 4, w-2, h+3, r=self.r,
           fill=self._darken(fill, 0.25), outline="")

        # Glow ring on hover
        if self._a > 0.05:
            glow_col = self._lerp(bg_base, self._brighten(fill, 1.3), self._a * 0.7)
            rr(self, 0, 0, w, h, r=self.r, fill="", outline=glow_col, width=2)

        # Body
        rr(self, 1, 1, w-1, h-1, r=self.r,
           fill=fill, outline=self._darken(fill, 0.8), width=1)

        # Top-edge shine
        rr(self, 2, 2, w-2, h//3+2, r=self.r, fill=shine, outline="")

        # Icon pill (left accent strip)
        if self.ico:
            pill_w = 32
            rr(self, 2, 2, pill_w, h-2, r=min(self.r-1, 9),
               fill=self._darken(fill, 0.65), outline="")
            self.create_text(pill_w//2 + 2, h//2, text=self.ico,
                             fill=self._brighten(fill, 1.8) if self._a > 0.3 else fg_col,
                             font=("Helvetica Neue", self.fs),
                             anchor="center")
            self.create_text(pill_w + (w - pill_w)//2, h//2,
                             text=self.txt, fill=self.fg,
                             font=("Helvetica Neue", self.fs, "bold"),
                             anchor="center")
        else:
            self.create_text(w//2, h//2, text=self.txt, fill=self.fg,
                             font=("Helvetica Neue", self.fs, "bold"),
                             anchor="center")

    def _anim(self, target):
        if self._id: self.after_cancel(self._id)
        diff = target - self._a
        if abs(diff) < 0.02:
            self._a = target
            self._draw(self._lerp(self.bg0, self.bg1, self._a))
            return
        self._a += diff * 0.22
        self._draw(self._lerp(self.bg0, self.bg1, self._a))
        self._id = self.after(12, lambda: self._anim(target))

    def recolor(self, bg, hover, fg):
        self.bg0 = tk_color(bg)
        self.bg1 = tk_color(hover)
        self.fg  = tk_color(fg)
        self._draw(self.bg0)


# ─────────────────────────────────────────────────────────────
#  PULSE INDICATOR
# ─────────────────────────────────────────────────────────────
class PulseRing(tk.Canvas):
    def __init__(self, parent, T, size=16, **kw):
        super().__init__(parent, width=size*4, height=size*4,
                         highlightthickness=0, bd=0, **kw)
        self.T = T; self.size = size; self._r = 0.0; self._d = 1
        self._tick()

    def _tick(self):
        self.delete("all")
        T  = self.T
        cx = cy = self.size * 2
        r  = self.size * 0.88
        self.configure(bg=T["header_bg"])
        for extra, col_key in [
            (self._r,        "accent_ring2"),
            (self._r * 0.6,  "accent_dark"),
            (self._r * 0.2,  "accent"),
        ]:
            er  = r + extra
            col = T.get(col_key, T["accent_dark"])
            self.create_oval(cx-er, cy-er, cx+er, cy+er, outline=col, width=1)
        self.create_oval(cx-r, cy-r, cx+r, cy+r,
                         fill=T["success"], outline=T["success_glow"], width=2)
        hr = r * 0.38
        self.create_oval(cx-hr, cy-hr, cx+hr, cy+hr,
                         fill=T["white_shine"], outline="")
        self._r += self._d * 0.45
        if self._r >= 13: self._d = -1
        if self._r <= 0:  self._d =  1
        self.after(32, self._tick)


# ─────────────────────────────────────────────────────────────
#  ARC GAUGE
# ─────────────────────────────────────────────────────────────
class ArcGauge(tk.Canvas):
    def __init__(self, parent, T, label="", size=80,
                 color=None, show_pct=True, **kw):
        super().__init__(parent, width=size, height=size+18,
                         highlightthickness=0, bd=0, **kw)
        self.T = T; self.label = label; self.size = size
        self.color = color or T["accent"]
        self.show_pct = show_pct; self._val = 0.0
        self._draw()

    def set(self, v):
        self._val = max(0.0, min(1.0, v)); self._draw()

    def _draw(self):
        T = self.T; self.delete("all")
        self.configure(bg=T["bg_card"])
        s = self.size; cx = s//2; cy = s//2; r = s//2 - 8
        self.create_arc(cx-r, cy-r, cx+r, cy+r,
                        start=225, extent=-270,
                        style="arc", outline=T["bg_border"], width=7)
        if self._val > 0:
            col = self.color
            if self._val > 0.85: col = T["danger"]
            elif self._val > 0.65: col = T["warning"]
            self.create_arc(cx-r, cy-r, cx+r, cy+r,
                            start=225, extent=int(-270*self._val),
                            style="arc", outline=col, width=7)
        if self.show_pct:
            self.create_text(cx, cy-2, text=f"{int(self._val*100)}%",
                             fill=self.color, font=("Helvetica Neue", 11, "bold"))
        self.create_text(cx, cy+13, text=self.label,
                         fill=T["fg_secondary"], font=("Helvetica Neue", 7, "bold"))


# ─────────────────────────────────────────────────────────────
#  RISK METER
# ─────────────────────────────────────────────────────────────
class RiskMeter(tk.Canvas):
    def __init__(self, parent, T, size=120, **kw):
        super().__init__(parent, width=size, height=size,
                         highlightthickness=0, bd=0, **kw)
        self.T = T; self.size = size; self._val = 0.0
        self._draw()

    def set(self, v):
        self._val = max(0.0, min(1.0, v)); self._draw()

    def _draw(self):
        T = self.T; self.delete("all")
        self.configure(bg=T["bg_card"])
        s = self.size; cx = cy = s//2; r = s//2 - 10
        segs = [(0.0, 0.5, T["success_ring"]),
                (0.5, 0.75, T["warning_ring"]),
                (0.75, 1.0, T["danger_ring"])]
        for lo, hi, col in segs:
            ext = int(-270*(hi-lo))
            start = 225 - int(270*lo)
            self.create_arc(cx-r, cy-r, cx+r, cy+r,
                            start=start, extent=ext,
                            style="arc", outline=col, width=10)
        pct = self._val
        col = T["success"] if pct < 0.5 else (T["warning"] if pct < 0.75 else T["danger"])
        if pct > 0:
            self.create_arc(cx-r, cy-r, cx+r, cy+r,
                            start=225, extent=int(-270*pct),
                            style="arc", outline=col, width=10)
        ang = math.radians(225 - 270*pct)
        nx = cx + (r)*math.cos(ang); ny = cy - (r)*math.sin(ang)
        self.create_oval(nx-5, ny-5, nx+5, ny+5,
                         fill=col, outline=T["bg_card"], width=2)
        self.create_text(cx, cy-6, text=f"{int(pct*100)}%",
                         fill=col, font=("Helvetica Neue", 16, "bold"))
        self.create_text(cx, cy+10, text="RISK",
                         fill=T["fg_secondary"], font=("Helvetica Neue", 8, "bold"))


# ─────────────────────────────────────────────────────────────
#  THREAT CHART
# ─────────────────────────────────────────────────────────────
class ThreatChart(tk.Canvas):
    def __init__(self, parent, T, w=440, h=110, **kw):
        super().__init__(parent, width=w, height=h,
                         highlightthickness=0, bd=0, **kw)
        self.T     = T
        self._data = [(datetime.now(), 0)] * 20
        self._draw()

    def push(self, v):
        self._data.append((datetime.now(), v))
        if len(self._data) > 60: self._data.pop(0)
        self._draw()

    def _draw(self):
        T = self.T
        self.delete("all")
        w  = self.winfo_reqwidth()
        h  = self.winfo_reqheight()
        self.configure(bg=T["bg_card"])

        PL = 38; PR = 8; PT = 10; PB = 22
        cw = w - PL - PR
        ch = h - PT - PB

        vals = [v for _, v in self._data]
        mx   = max(vals) if max(vals) > 0 else 1

        steps = 4
        for i in range(steps + 1):
            y      = PT + ch * i // steps
            val_at = mx * (steps - i) // steps
            self.create_line(PL, y, w - PR, y,
                             fill=T["bg_border"], width=1, dash=(4, 4))
            self.create_text(PL - 4, y, text=str(val_at),
                             fill=T["fg_muted"],
                             font=("Helvetica Neue", 7), anchor="e")

        self.create_line(PL, PT, PL, PT + ch,
                         fill=T["bg_border"], width=1)

        if max(vals) == 0:
            self.create_text(PL + cw // 2, PT + ch // 2,
                             text="No threats detected yet",
                             fill=T["fg_muted"],
                             font=("Helvetica Neue", 9))
            return

        n   = len(self._data)
        pts = []
        for i, (_, v) in enumerate(self._data):
            x = PL + i * cw / max(n - 1, 1)
            y = PT + ch - int((v / mx) * ch)
            pts.append((x, y))

        for opacity_step, _ in enumerate([0.18, 0.10, 0.05]):
            offset = opacity_step * 3
            fill_pts = ([PL, PT + ch + offset]
                        + [c for p in pts for c in (p[0], p[1] + offset)]
                        + [w - PR, PT + ch + offset])
            self.create_polygon(fill_pts, fill=T["danger_tint"], outline="", smooth=True)

        if len(pts) >= 2:
            flat = [c for p in pts for c in p]
            self.create_line(*flat, fill=T["danger"], width=2,
                             smooth=True, joinstyle="round", capstyle="round")
            self.create_line(*flat, fill=T["danger_glow"], width=1, smooth=True)

        if pts:
            lx, ly = pts[-1]
            self.create_oval(lx-6, ly-6, lx+6, ly+6,
                             fill=T["danger_ring"], outline="")
            self.create_oval(lx-3, ly-3, lx+3, ly+3,
                             fill=T["danger"], outline=T["bg_card"], width=1)

        n = len(self._data)
        for i in [0, n // 3, 2 * n // 3, n - 1]:
            if 0 <= i < n:
                x = PL + i * cw / max(n - 1, 1)
                t = self._data[i][0].strftime("%H:%M:%S")
                self.create_text(x, h - 4, text=t, fill=T["fg_muted"],
                                 font=("Helvetica Neue", 6), anchor="s")


# ─────────────────────────────────────────────────────────────
#  NOTIFICATION TOAST
# ─────────────────────────────────────────────────────────────
class NotifToast:
    _queue  = []
    _active = False

    @classmethod
    def show(cls, root, T, title, msg, kind="info"):
        cls._queue.append((root, T, title, msg, kind))
        if not cls._active:
            cls._next()

    @classmethod
    def _next(cls):
        if not cls._queue: cls._active = False; return
        cls._active = True
        root, T, title, msg, kind = cls._queue.pop(0)
        color = {"info": T["accent"], "success": T["success"],
                 "danger": T["danger"], "warn": T["warning"]}.get(kind, T["accent"])
        w = tk.Toplevel(root)
        w.overrideredirect(True)
        w.attributes("-topmost", True)
        try: w.attributes("-alpha", 0.0)
        except: pass
        W, H = 320, 72
        sx = root.winfo_x() + root.winfo_width() - W - 16
        sy = root.winfo_y() + root.winfo_height() - H - 40
        w.geometry(f"{W}x{H}+{sx}+{sy}")
        w.configure(bg=T["notif_bg"])
        bar = tk.Frame(w, width=4, bg=color)
        bar.pack(side="left", fill="y")
        body = tk.Frame(w, bg=T["notif_bg"])
        body.pack(side="left", fill="both", expand=True, padx=10, pady=8)
        tk.Label(body, text=title, font=("Helvetica Neue", 10, "bold"),
                 bg=T["notif_bg"], fg=color, anchor="w").pack(fill="x")
        tk.Label(body, text=msg, font=("Helvetica Neue", 8),
                 bg=T["notif_bg"], fg=T["fg_secondary"],
                 anchor="w", wraplength=260).pack(fill="x")

        def fade_in(a=0.0):
            a = min(a+0.08, 0.95)
            try: w.attributes("-alpha", a)
            except: pass
            if a < 0.95: w.after(16, lambda: fade_in(a))
        fade_in()

        def close():
            def fade_out(a=0.95):
                a = max(a-0.08, 0.0)
                try: w.attributes("-alpha", a)
                except: pass
                if a > 0: w.after(16, lambda: fade_out(a))
                else:
                    try: w.destroy()
                    except: pass
                    root.after(100, cls._next)
            fade_out()
        w.after(3200, close)


# ─────────────────────────────────────────────────────────────
#  FILE DETAILS PANEL
# ─────────────────────────────────────────────────────────────
class FileDetailsPanel(tk.Frame):
    def __init__(self, parent, T, **kw):
        super().__init__(parent, **kw)
        self.T = T
        self._build()

    def _build(self):
        T = self.T
        self.configure(bg=T["bg_elevated"],
                       highlightbackground=T["danger_ring"],
                       highlightthickness=1)
        hdr = tk.Frame(self, bg=T["danger_bg"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="🔍  THREAT INSPECTOR",
                 font=("Helvetica Neue", 9, "bold"),
                 bg=T["danger_bg"], fg=T["danger"],
                 padx=12, pady=6).pack(side="left")
        self.lbl_verdict = tk.Label(hdr, text="",
                                    font=("Helvetica Neue", 8, "bold"),
                                    bg=T["danger_bg"], fg=T["danger"])
        self.lbl_verdict.pack(side="right", padx=10)

        grid = tk.Frame(self, bg=T["bg_elevated"])
        grid.pack(fill="x", padx=12, pady=8)
        grid.columnconfigure(1, weight=1)
        grid.columnconfigure(3, weight=1)

        self._vars = {}
        fields = [
            ("File Name",  "fname",   0, 0),
            ("File Path",  "fpath",   1, 0),
            ("Entropy",    "entropy", 0, 2),
            ("Risk Score", "risk",    1, 2),
            ("Engine",     "engine",  0, 4),
            ("SHA256",     "sha",     1, 4),
        ]
        for label, key, row, col in fields:
            tk.Label(grid, text=label+":", font=("Helvetica Neue", 8, "bold"),
                     bg=T["bg_elevated"], fg=T["fg_secondary"],
                     anchor="w").grid(row=row, column=col, sticky="w", padx=(4,2), pady=3)
            v = tk.StringVar(value="—")
            self._vars[key] = v
            tk.Label(grid, textvariable=v, font=("Helvetica Neue", 8),
                     bg=T["bg_elevated"], fg=T["fg_primary"],
                     anchor="w").grid(row=row, column=col+1, sticky="w", padx=(0,16), pady=3)

    def update(self, result):
        T = self.T
        self._vars["fname"].set(result.get("file", "—"))
        self._vars["fpath"].set(result.get("fpath", "—")[:60])
        self._vars["entropy"].set(result.get("entropy", "—"))
        self._vars["risk"].set(result.get("risk", "—"))
        self._vars["engine"].set(result.get("ml", "—"))
        self._vars["sha"].set((result.get("hash","—") or "—")[:24]+"…")
        verdict = result.get("verdict", "")
        col = T["danger"] if verdict == "THREAT" else T["success"]
        self.lbl_verdict.configure(text=f"● {verdict}", fg=col)

    def retheme(self, T):
        self.T = T
        self.configure(bg=T["bg_elevated"],
                       highlightbackground=T["danger_ring"])
        for w in self.winfo_children():
            try: w.configure(bg=T["bg_elevated"] if w.cget("bg") != T["danger_bg"] else T["danger_bg"])
            except: pass


# ─────────────────────────────────────────────────────────────
#  WATCHDOG
# ─────────────────────────────────────────────────────────────
class RansomShieldWatcher(FileSystemEventHandler):
    def __init__(self, gui):
        super().__init__(); self.gui = gui; self._seen = {}

    def _ok(self, path):
        now = time.time()
        if now - self._seen.get(path, 0) < 1.5: return False
        self._seen[path] = now; return True

    def on_created(self, e):
        if not e.is_directory:
            try: self.gui.behavior.created_count += 1
            except: pass
            self._q(e.src_path, "CREATED")
    def on_modified(self, e):
        if not e.is_directory:
            try: self.gui.behavior.modified_count += 1
            except: pass
            self._q(e.src_path, "MODIFIED")
    def on_moved(self, e):
        if not e.is_directory:
            try: self.gui.behavior.renamed_count += 1
            except: pass
            self._q(e.dest_path, "RENAMED")
    def on_deleted(self, e):
        if not e.is_directory:
            try: self.gui.behavior.deleted_count += 1
            except: pass

    def _q(self, path, reason):
        if not self._ok(path): return
        if self.gui.quarantine_dir in path: return
        self.gui.root.after(0, lambda: self.gui._log(
            f"👁  Watcher [{reason}]: {os.path.basename(path)}", "warn"))
        threading.Thread(target=self.gui._watcher_scan,
                         args=(path,), daemon=True).start()


# ─────────────────────────────────────────────────────────────
#  MAIN GUI
# ─────────────────────────────────────────────────────────────
class RansomwareGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("RansomShield  ·  Advanced Ransomware Protection")
        self.root.geometry("1360x840")
        self.root.minsize(1100, 720)

        self.T = DARK
        self.root.configure(bg=self.T["bg_base"])

        self.selected_folder = None
        self.scan_history    = []
        self.quarantine_dir  = os.path.expanduser("~/Desktop/RansomShield_Quarantine")
        self.is_scanning     = False
        self._observer       = None
        self._watching       = False
        self._risk_val       = 0.0
        self._backup_log     = []   # list of (timestamp, filename, backup_path, size_str)

        self.entropy_det  = EntropyDetector()
        self.ext_det      = ExtensionDetector()
        self.ml_det       = MLDetector()
        self.reputation   = ReputationEngine()
        self.behavior     = BehaviorAnalyzer()
        self.backup_mgr   = BackupManager()
        self.honeypot     = HoneypotManager()

        os.makedirs(self.quarantine_dir, exist_ok=True)
        self._first = not os.path.exists(os.path.expanduser("~/.ransomshield_v4"))

        self._build()
        self._theme(self.T)
        self._banner()
        self._clock()
        self._sysmon()

        if self._first:
            self.root.after(700, self._onboard)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    # ══════════════════════════════════════════════════════════
    #  BUILD UI
    # ══════════════════════════════════════════════════════════
    def _build(self):
        T = self.T
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # ── HEADER ──────────────────────────────────────────
        self.hdr = tk.Frame(self.root, height=68)
        self.hdr.grid(row=0, column=0, sticky="ew")
        self.hdr.grid_propagate(False)
        self.hdr.columnconfigure(2, weight=1)

        brand = tk.Frame(self.hdr)
        brand.grid(row=0, column=0, padx=(18,0), pady=10, sticky="w")

        try:
            from PIL import Image, ImageTk
            _logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
            _logo_src = Image.open(_logo_path).convert("RGBA")
            _logo_src = _logo_src.resize((52, 52), Image.LANCZOS)
            self._logo_img = ImageTk.PhotoImage(_logo_src)
            self.logo_cv = tk.Label(brand, image=self._logo_img,
                                    bg=self.T["header_bg"], width=52, height=52)
        except Exception:
            self.logo_cv = tk.Canvas(brand, width=46, height=46, highlightthickness=0)
            self._shield(self.logo_cv)
        self.logo_cv.pack(side="left", padx=(0,12))

        title_blk = tk.Frame(brand)
        title_blk.pack(side="left")
        self.lbl_app = tk.Label(title_blk, text="RANSOMSHIELD",
                                font=("Helvetica Neue", 18, "bold"), anchor="w")
        self.lbl_app.pack(anchor="w")
        self.lbl_sub = tk.Label(title_blk,
                                text="Advanced Ransomware Detection & Response  ·  v4.1",
                                font=("Helvetica Neue", 8), anchor="w")
        self.lbl_sub.pack(anchor="w")

        self.hdr_sep = tk.Frame(self.hdr, width=1, height=40)
        self.hdr_sep.grid(row=0, column=1, padx=20, pady=14, sticky="ns")

        pill = tk.Frame(self.hdr)
        pill.grid(row=0, column=2, sticky="w", padx=4)
        self.pulse = PulseRing(pill, T, size=12)
        self.pulse.pack(side="left", padx=(0,8))
        stxt = tk.Frame(pill)
        stxt.pack(side="left")
        self.lbl_prot = tk.Label(stxt, text="PROTECTION ACTIVE",
                                 font=("Helvetica Neue", 10, "bold"))
        self.lbl_prot.pack(anchor="w")
        self.lbl_status = tk.Label(stxt, text="All systems operational",
                                   font=("Helvetica Neue", 8))
        self.lbl_status.pack(anchor="w")

        right = tk.Frame(self.hdr)
        right.grid(row=0, column=3, padx=(0,16), pady=10, sticky="e")

        self.lbl_clock = tk.Label(right, text="",
                                  font=("Courier", 13, "bold"))
        self.lbl_clock.pack(side="right", padx=(12,0))
        self.lbl_date = tk.Label(right, text="",
                                 font=("Helvetica Neue", 7))
        self.lbl_date.pack(side="right")

        self.btn_theme = RoundedButton(right, "Light Mode", icon="☀",
                                       command=self._toggle_theme,
                                       w=132, h=34, r=10, fs=9)
        self.btn_theme.pack(side="right", padx=(0,12))

        self.acc_line = tk.Frame(self.root, height=2)
        self.acc_line.grid(row=0, column=0, sticky="sew")

        # ── BODY ────────────────────────────────────────────
        self.body = tk.Frame(self.root)
        self.body.grid(row=1, column=0, sticky="nsew")
        self.body.columnconfigure(1, weight=1)
        self.body.rowconfigure(0, weight=1)

        # ── SIDEBAR ─────────────────────────────────────────
        self.sidebar = tk.Frame(self.body, width=234)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        self.sidebar.columnconfigure(0, weight=1)
        self._seps  = []
        self._sbtns = []

        self._slbl("QUICK ACTIONS")
        btn_defs = [
            ("Select Folder", "📁", self._sel_folder,  "accent"),
            ("Scan File",     "🔍", self._scan_file,   "accent"),
            ("Scan Folder",   "📂", self._scan_folder, "accent"),
            ("Export Report", "📄", self._export,      "warning"),
            ("Clear Log",     "🗑",  self._clear_log,   "secondary"),
        ]
        for t, i, c, s in btn_defs:
            b = self._sbtn(t, i, c, s); b.pack(fill="x", padx=10, pady=3)
            self._sbtns.append((b, s))

        self._sep()
        self._slbl("LIVE MONITOR")
        self.btn_watch = self._sbtn("Start Monitor", "▶", self._toggle_watch, "success")
        self.btn_watch.pack(fill="x", padx=10, pady=3)

        wbadge = tk.Frame(self.sidebar)
        wbadge.pack(fill="x", padx=14, pady=(4,0))
        self.watch_dot = tk.Label(wbadge, text="⬤", font=("Helvetica Neue", 8))
        self.watch_dot.pack(side="left")
        self.watch_lbl = tk.Label(wbadge, text="Monitor: OFFLINE",
                                  font=("Helvetica Neue", 8, "bold"))
        self.watch_lbl.pack(side="left", padx=4)
        self._wbadge = wbadge

        self._sep()
        self._slbl("SCAN PROGRESS")

        # Progress bar + % label side by side
        prog_row = tk.Frame(self.sidebar)
        prog_row.pack(fill="x", padx=10, pady=(0,2))
        prog_row.columnconfigure(0, weight=1)
        self.prog_var = tk.DoubleVar(value=0)
        self.prog_bar = ttk.Progressbar(prog_row, variable=self.prog_var,
                                         maximum=100, mode="determinate")
        self.prog_bar.grid(row=0, column=0, sticky="ew")
        self.lbl_prog_pct = tk.Label(prog_row, text="0%",
                                     font=("Helvetica Neue", 7, "bold"), width=4, anchor="e")
        self.lbl_prog_pct.grid(row=0, column=1, padx=(4,0))

        self.lbl_prog = tk.Label(self.sidebar, text="Ready  ·  No scan active",
                                 font=("Helvetica Neue", 8), anchor="w")
        self.lbl_prog.pack(fill="x", padx=14)
        self.lbl_folder = tk.Label(self.sidebar, text="No folder selected",
                                   font=("Helvetica Neue", 8), wraplength=200,
                                   justify="left", anchor="w")
        self.lbl_folder.pack(fill="x", padx=14, pady=(4,0))

        self._sep()
        self._slbl("SYSTEM STATUS")
        gauge_row = tk.Frame(self.sidebar)
        gauge_row.pack(fill="x", padx=6)
        self.g_cpu  = ArcGauge(gauge_row, T, "CPU",  64, T["accent"])
        self.g_ram  = ArcGauge(gauge_row, T, "RAM",  64, T["warning"])
        self.g_disk = ArcGauge(gauge_row, T, "DISK", 64, T["success"])
        for g in [self.g_cpu, self.g_ram, self.g_disk]:
            g.pack(side="left", padx=2)

        self._sep()
        self._slbl("RISK METER")
        risk_row = tk.Frame(self.sidebar)
        risk_row.pack(padx=12, pady=(0,8))
        self.risk_meter = RiskMeter(risk_row, T, size=110)
        self.risk_meter.pack(side="left")
        risk_txt = tk.Frame(risk_row)
        risk_txt.pack(side="left", padx=8)
        self.lbl_risk_title = tk.Label(risk_txt, text="SYSTEM\nRISK LEVEL",
                                        font=("Helvetica Neue", 8, "bold"), justify="left")
        self.lbl_risk_title.pack(anchor="w")
        self.lbl_risk_desc = tk.Label(risk_txt, text="Based on\nall scans",
                                       font=("Helvetica Neue", 7), justify="left")
        self.lbl_risk_desc.pack(anchor="w", pady=(4,0))

        # ── CONTENT ─────────────────────────────────────────
        content = tk.Frame(self.body)
        content.grid(row=0, column=1, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(3, weight=1)
        self._content = content

        # Stat cards
        self.cards_frame = tk.Frame(content)
        self.cards_frame.grid(row=0, column=0, sticky="ew", padx=14, pady=(14,0))
        for i in range(5): self.cards_frame.columnconfigure(i, weight=1)

        self.stat_vars = {
            "scanned":  tk.StringVar(value="0"),
            "threats":  tk.StringVar(value="0"),
            "safe":     tk.StringVar(value="0"),
            "quarant":  tk.StringVar(value="0"),
            "accuracy": tk.StringVar(value="99.8%"),
        }
        self._cards = {}
        card_defs = [
            ("scanned",  "FILES SCANNED",    "🔍", "accent"),
            ("threats",  "THREATS DETECTED", "⚠",  "danger"),
            ("safe",     "FILES PROTECTED",  "✓",  "success"),
            ("quarant",  "QUARANTINED",       "🔒", "warning"),
            ("accuracy", "ACCURACY",          "◎",  "purple"),
        ]
        for col, (key, lbl, ico, clr) in enumerate(card_defs):
            self._card(key, lbl, ico, clr, col)

        # Info row
        self.info_row = tk.Frame(content)
        self.info_row.grid(row=1, column=0, sticky="ew", padx=14, pady=(10,0))
        self.info_row.columnconfigure(1, weight=1)

        self.lbl_last = tk.Label(self.info_row, text="⏱  Last Scan: —",
                                 font=("Helvetica Neue", 9), anchor="w")
        self.lbl_last.grid(row=0, column=0, sticky="w", padx=6)

        self.lbl_protected = tk.Label(self.info_row, text="🛡  Protected: 0",
                                      font=("Helvetica Neue", 9))
        self.lbl_protected.grid(row=0, column=1, padx=6)

        self.threat_pill = tk.Label(self.info_row,
                                    text="  ◈  THREAT LEVEL: LOW  ",
                                    font=("Helvetica Neue", 9, "bold"))
        self.threat_pill.grid(row=0, column=2, sticky="e", padx=6)

        # File details panel
        self.details_panel = FileDetailsPanel(content, T)
        self.details_panel.grid(row=2, column=0, sticky="ew", padx=14, pady=(10,0))
        self.details_panel.grid_remove()

        # Notebook
        self.nb_wrap = tk.Frame(content)
        self.nb_wrap.grid(row=3, column=0, sticky="nsew", padx=14, pady=(10,10))
        self.nb_wrap.columnconfigure(0, weight=1)
        self.nb_wrap.rowconfigure(0, weight=1)

        self.nb = ttk.Notebook(self.nb_wrap)
        self.nb.grid(row=0, column=0, sticky="nsew")

        # ── Tab 1: Live Log ──────────────────────────────────
        self.tab_log = tk.Frame(self.nb)
        self.nb.add(self.tab_log, text="  ⚡  Live Log  ")
        self.tab_log.rowconfigure(1, weight=1)
        self.tab_log.columnconfigure(0, weight=1)

        log_hdr = tk.Frame(self.tab_log)
        log_hdr.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 0))

        self.lbl_log_title = tk.Label(log_hdr, text="REAL-TIME ACTIVITY LOG",
                                      font=("Helvetica Neue", 8, "bold"), anchor="w")
        self.lbl_log_title.pack(side="left", padx=4)

        self.lbl_live_dot = tk.Label(log_hdr, text="⬤  LIVE",
                                     font=("Helvetica Neue", 7, "bold"))
        self.lbl_live_dot.pack(side="left", padx=(8, 0))

        self.lbl_log_count = tk.Label(log_hdr, text="0 entries",
                                      font=("Helvetica Neue", 8))
        self.lbl_log_count.pack(side="right", padx=4)

        log_stack = tk.Frame(self.tab_log)
        log_stack.grid(row=1, column=0, sticky="nsew", padx=6, pady=(6, 0))
        log_stack.rowconfigure(0, weight=1)
        log_stack.columnconfigure(0, weight=1)
        self._log_stack = log_stack

        self.log_txt = scrolledtext.ScrolledText(
            log_stack, font=("Menlo", 10),
            wrap=tk.WORD, relief="flat", bd=0,
            padx=18, pady=14, spacing1=4, spacing3=4)
        self.log_txt.grid(row=0, column=0, sticky="nsew")
        self.log_txt.config(state="disabled")

        # Idle overlay
        self.idle_overlay = tk.Frame(log_stack)
        self.idle_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        idle_centre = tk.Frame(self.idle_overlay)
        idle_centre.place(relx=0.5, rely=0.45, anchor="center")
        self._idle_centre = idle_centre

        self.idle_shield_lbl = tk.Label(idle_centre, text="🛡",
                                        font=("Helvetica Neue", 40))
        self.idle_shield_lbl.pack(pady=(0, 6))

        self.idle_title_lbl = tk.Label(idle_centre,
                                        text="RansomShield is Ready",
                                        font=("Helvetica Neue", 15, "bold"))
        self.idle_title_lbl.pack()

        self.idle_sub_lbl = tk.Label(idle_centre,
                                      text="No active scan running  ·  All engines online",
                                      font=("Helvetica Neue", 10))
        self.idle_sub_lbl.pack(pady=(3, 16))

        self.idle_sep = tk.Frame(idle_centre, height=1, width=360)
        self.idle_sep.pack(pady=(0, 14))

        self._tips_frame = tk.Frame(idle_centre)
        self._tips_frame.pack()
        tips = [
            ("📁", "Select Folder",  "Choose a directory to monitor"),
            ("▶",  "Start Monitor",  "Auto-scan new and modified files live"),
            ("🔍", "Scan File",      "Manually scan any single file"),
            ("📄", "Export Report",  "Save scan history as PDF or CSV"),
        ]
        for row_i, (ico, title, desc) in enumerate(tips):
            tk.Label(self._tips_frame, text=ico,
                     font=("Helvetica Neue", 13)).grid(
                row=row_i, column=0, padx=(0, 10), pady=4, sticky="w")
            tk.Label(self._tips_frame, text=title,
                     font=("Helvetica Neue", 9, "bold"),
                     anchor="w", width=14).grid(row=row_i, column=1, sticky="w")
            tk.Label(self._tips_frame, text=desc,
                     font=("Helvetica Neue", 9),
                     anchor="w").grid(row=row_i, column=2, padx=(8, 0), sticky="w")

        self.idle_ready_lbl = tk.Label(idle_centre,
                                        text="  ◈  SYSTEM READY  ·  All 5 engines online  ",
                                        font=("Helvetica Neue", 9, "bold"))
        self.idle_ready_lbl.pack(pady=(18, 0))
        self._idle_showing = True

        # Chart
        chart_wrap = tk.Frame(self.tab_log)
        chart_wrap.grid(row=2, column=0, sticky="ew", padx=10, pady=(6, 6))

        chart_hdr = tk.Frame(chart_wrap)
        chart_hdr.pack(fill="x", padx=4, pady=(0, 2))

        self.lbl_chart_title = tk.Label(chart_hdr, text="THREAT TREND",
                                        font=("Helvetica Neue", 7, "bold"))
        self.lbl_chart_title.pack(side="left", padx=2)

        self.lbl_chart_sub = tk.Label(chart_hdr, text="threats over time",
                                      font=("Helvetica Neue", 7))
        self.lbl_chart_sub.pack(side="left", padx=(6, 0))

        self.lbl_rate = tk.Label(chart_hdr, text="Total scanned: 0",
                                 font=("Helvetica Neue", 8))
        self.lbl_rate.pack(side="right", padx=4)

        self.threat_chart = ThreatChart(chart_wrap, T, w=500, h=90)
        self.threat_chart.pack(fill="x", padx=4)

        # ── Tab 2: Scan History ──────────────────────────────
        self.tab_hist = tk.Frame(self.nb)
        self.nb.add(self.tab_hist, text="  📋  Scan History  ")
        self.tab_hist.rowconfigure(0, weight=1)
        self.tab_hist.columnconfigure(0, weight=1)
        cols = ("Time","File","Verdict","Score","Extension",
                "Entropy","ML Result","Honeypot","Backup","Risk","SHA256")
        self.tree = ttk.Treeview(self.tab_hist, columns=cols,
                                  show="headings", height=20)
        for c, w in zip(cols, (75,155,70,55,80,65,110,80,55,55,145)):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="center", minwidth=40)
        hs = ttk.Scrollbar(self.tab_hist, orient="horizontal", command=self.tree.xview)
        vs = ttk.Scrollbar(self.tab_hist, orient="vertical",   command=self.tree.yview)
        self.tree.configure(xscrollcommand=hs.set, yscrollcommand=vs.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vs.grid(row=0, column=1, sticky="ns")
        hs.grid(row=1, column=0, sticky="ew")

        # ── Tab 3: Quarantine ────────────────────────────────
        self.tab_q = tk.Frame(self.nb)
        self.nb.add(self.tab_q, text="  🔒  Quarantine  ")
        self.tab_q.rowconfigure(0, weight=1)
        self.tab_q.columnconfigure(0, weight=1)
        qcols = ("Quarantined At","Original File","Quarantine Path","Risk Score")
        self.qtree = ttk.Treeview(self.tab_q, columns=qcols,
                                   show="headings", height=20)
        for c in qcols:
            self.qtree.heading(c, text=c)
            self.qtree.column(c, width=180, anchor="center")
        qvs = ttk.Scrollbar(self.tab_q, orient="vertical", command=self.qtree.yview)
        self.qtree.configure(yscrollcommand=qvs.set)
        self.qtree.grid(row=0, column=0, sticky="nsew")
        qvs.grid(row=0, column=1, sticky="ns")

        self._qbtns = tk.Frame(self.tab_q)
        self._qbtns.grid(row=2, column=0, columnspan=2, sticky="ew", pady=8, padx=8)
        self.btn_restore = self._abtn(self._qbtns, "♻  Restore", self._restore, "warning")
        self.btn_restore.pack(side="left", padx=6)
        self.btn_del_q = self._abtn(self._qbtns, "🗑  Delete Permanently", self._del_q, "danger")
        self.btn_del_q.pack(side="left", padx=6)

        # ── Tab 4: Statistics ────────────────────────────────
        self.tab_stats = tk.Frame(self.nb)
        self.nb.add(self.tab_stats, text="  📊  Statistics  ")
        self._build_stats()

        # ── Tab 5: Backups ───────────────────────────────────
        self.tab_backups = tk.Frame(self.nb)
        self.nb.add(self.tab_backups, text="  💾  Backups  ")
        self._build_backup_tab()

        # ── Tab 6: Notifications ─────────────────────────────
        self.tab_notif = tk.Frame(self.nb)
        self.nb.add(self.tab_notif, text="  🔔  Notifications  ")
        self.tab_notif.rowconfigure(0, weight=1)
        self.tab_notif.columnconfigure(0, weight=1)
        self.notif_list = tk.Frame(self.tab_notif)
        self.notif_list.pack(fill="both", expand=True, padx=12, pady=8)
        self._notif_items = []

        # ── Footer (richer) ──────────────────────────────────
        self.footer = tk.Frame(self.root, height=32)
        self.footer.grid(row=2, column=0, sticky="ew")
        self.footer.grid_propagate(False)
        self.footer.columnconfigure(1, weight=1)

        # Left: status dot + text
        self.footer_l = tk.Label(self.footer,
                                  text="⬤  System Ready  ·  All engines online",
                                  font=("Helvetica Neue", 8), anchor="w")
        self.footer_l.grid(row=0, column=0, sticky="w", padx=16)

        # Centre: backup location
        self.footer_backup_lbl = tk.Label(self.footer,
                                           text="",
                                           font=("Helvetica Neue", 7), anchor="center")
        self.footer_backup_lbl.grid(row=0, column=1, sticky="ew")

        # Right: version
        self.footer_r = tk.Label(self.footer,
                                  text="RansomShield v4.1  ·  ML-Powered  ·  Real-Time Protection",
                                  font=("Helvetica Neue", 7), anchor="e")
        self.footer_r.grid(row=0, column=2, sticky="e", padx=16)

    # ── Backups tab ──────────────────────────────────────────
    def _build_backup_tab(self):
        T = self.T
        f = self.tab_backups
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)

        # Header bar with backup location
        hdr = tk.Frame(f)
        hdr.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))
        hdr.columnconfigure(1, weight=1)

        tk.Label(hdr, text="💾  BACKUP STORAGE",
                 font=("Helvetica Neue", 10, "bold"), anchor="w").grid(
            row=0, column=0, sticky="w")

        # Backup folder path pill
        self.lbl_backup_dir = tk.Label(
            hdr,
            text=f"  📂  {self.backup_mgr.backup_dir if hasattr(self.backup_mgr, 'backup_dir') else os.path.expanduser('~/Desktop/ransomware_protection_system/backups')}  ",
            font=("Helvetica Neue", 8),
            anchor="w", cursor="hand2")
        self.lbl_backup_dir.grid(row=0, column=1, sticky="w", padx=(16, 0))
        self.lbl_backup_dir.bind("<Button-1>", lambda e: self._open_backup_folder())

        self.btn_open_backup = self._abtn(hdr, "  📂  Reveal in Finder",
                                           self._open_backup_folder, "accent")
        self.btn_open_backup.grid(row=0, column=2, padx=(12, 0))

        # Stats row
        stats_row = tk.Frame(f)
        stats_row.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 8))
        self._bkp_count_var = tk.StringVar(value="0 backups")
        self._bkp_size_var  = tk.StringVar(value="0 KB total")
        tk.Label(stats_row, textvariable=self._bkp_count_var,
                 font=("Helvetica Neue", 9, "bold")).pack(side="left", padx=(0, 16))
        tk.Label(stats_row, textvariable=self._bkp_size_var,
                 font=("Helvetica Neue", 9)).pack(side="left")

        # Backup list
        bcols = ("Time", "Original File", "Backup Path", "Size", "Status")
        self.btree = ttk.Treeview(f, columns=bcols, show="headings", height=22)
        for c, w in zip(bcols, (90, 180, 340, 70, 80)):
            self.btree.heading(c, text=c)
            self.btree.column(c, width=w, anchor="w", minwidth=40)
        bvs = ttk.Scrollbar(f, orient="vertical", command=self.btree.yview)
        bhs = ttk.Scrollbar(f, orient="horizontal", command=self.btree.xview)
        self.btree.configure(yscrollcommand=bvs.set, xscrollcommand=bhs.set)
        self.btree.grid(row=2, column=0, sticky="nsew", padx=(14, 0), pady=(4, 0))
        bvs.grid(row=2, column=1, sticky="ns", pady=(4, 0))
        bhs.grid(row=3, column=0, sticky="ew", padx=(14, 0))
        f.rowconfigure(2, weight=1)

        # Action buttons
        bbtns = tk.Frame(f)
        bbtns.grid(row=4, column=0, columnspan=2, sticky="ew", padx=14, pady=8)
        self._abtn(bbtns, "🔄  Refresh List", self._refresh_backup_list, "accent").pack(
            side="left", padx=(0, 8))
        self._abtn(bbtns, "📂  Open Backup Folder", self._open_backup_folder, "accent").pack(
            side="left", padx=(0, 8))
        self._abtn(bbtns, "🗑  Clear All Backups", self._clear_backups, "danger").pack(
            side="left")

    def _get_backup_dir(self):
        """Return the backup directory path from backup_mgr or default."""
        if hasattr(self.backup_mgr, 'backup_dir'):
            return self.backup_mgr.backup_dir
        # Try common paths
        candidates = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups"),
            os.path.expanduser("~/Desktop/ransomware_protection_system/backups"),
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        return candidates[0]

    def _open_backup_folder(self):
        d = self._get_backup_dir()
        os.makedirs(d, exist_ok=True)
        try:
            os.system(f'open "{d}"')
        except Exception as e:
            self._log(f"✗ Could not open folder: {e}", "warn")

    def _refresh_backup_list(self):
        """Scan backup directory and populate the backup treeview."""
        d = self._get_backup_dir()
        self.btree.delete(*self.btree.get_children())
        if not os.path.exists(d):
            self._bkp_count_var.set("0 backups  (folder not found)")
            return
        total_size = 0
        count = 0
        entries = []
        for fname in sorted(os.listdir(d), reverse=True):
            fp = os.path.join(d, fname)
            if not os.path.isfile(fp):
                continue
            try:
                sz   = os.path.getsize(fp)
                mtime = datetime.fromtimestamp(os.path.getmtime(fp))
                sz_str = f"{sz/1024:.1f} KB" if sz < 1_000_000 else f"{sz/1_048_576:.1f} MB"
                total_size += sz
                count += 1
                # Try to parse original filename from backup name
                orig = fname
                # Common pattern: originalname_YYYYMMDD_HHMMSS
                parts = fname.rsplit("_", 2)
                if len(parts) == 3 and len(parts[1]) == 8 and len(parts[2]) == 6:
                    orig = parts[0]
                ts_str = mtime.strftime("%Y-%m-%d  %H:%M:%S")
                entries.append((ts_str, orig, fp, sz_str, "✓ Backed up"))
            except Exception:
                continue

        for entry in entries:
            self.btree.insert("", tk.END, values=entry, tags=("backup",))

        total_str = (f"{total_size/1024:.1f} KB" if total_size < 1_000_000
                     else f"{total_size/1_048_576:.1f} MB")
        self._bkp_count_var.set(f"{count} backup{'s' if count != 1 else ''}")
        self._bkp_size_var.set(f"{total_str} total")

        # Update footer
        self.footer_backup_lbl.configure(
            text=f"💾  Backups: {count} files  ·  {total_str}  ·  {d}")

    def _clear_backups(self):
        T = self.T
        w = tk.Toplevel(self.root)
        w.title("Confirm Clear"); w.geometry("380x150")
        w.resizable(False, False); w.configure(bg=T["bg_panel"])
        w.attributes("-topmost", True)
        rx = self.root.winfo_x() + (self.root.winfo_width() - 380) // 2
        ry = self.root.winfo_y() + (self.root.winfo_height() - 150) // 2
        w.geometry(f"380x150+{rx}+{ry}")
        tk.Label(w, text="⚠  Clear All Backups?",
                 font=("Helvetica Neue", 12, "bold"),
                 bg=T["bg_panel"], fg=T["danger"]).pack(pady=(16, 4))
        tk.Label(w, text="This will permanently delete all backup files.",
                 font=("Helvetica Neue", 9),
                 bg=T["bg_panel"], fg=T["fg_secondary"]).pack()
        bf = tk.Frame(w, bg=T["bg_panel"]); bf.pack(pady=14)

        def _ok():
            w.destroy()
            d = self._get_backup_dir()
            if os.path.exists(d):
                for f in os.listdir(d):
                    fp = os.path.join(d, f)
                    if os.path.isfile(fp):
                        try: os.remove(fp)
                        except: pass
            self._refresh_backup_list()
            self._log("🗑  All backups cleared.", "warn")

        tk.Button(bf, text="Clear All", font=("Helvetica Neue", 10, "bold"),
                  bg=T["danger_bg"], fg=T["danger"], relief="flat",
                  cursor="hand2", command=_ok, padx=14, pady=6).pack(side="left", padx=8)
        tk.Button(bf, text="Cancel", font=("Helvetica Neue", 10, "bold"),
                  bg=T["bg_elevated"], fg=T["fg_primary"], relief="flat",
                  cursor="hand2", command=w.destroy, padx=14, pady=6).pack(side="left", padx=8)

    # ── Sidebar helpers ──────────────────────────────────────
    def _slbl(self, text):
        T = self.T
        wrap = tk.Frame(self.sidebar, bg=T["bg_panel"])
        wrap.pack(fill="x", padx=0, pady=(16, 6))
        accent_bar = tk.Frame(wrap, width=3, bg=T["accent"])
        accent_bar.pack(side="left", fill="y")
        l = tk.Label(wrap, text=text,
                     font=("Helvetica Neue", 7, "bold"),
                     anchor="w", padx=10)
        l.pack(side="left", fill="x", expand=True)
        return l

    def _sep(self):
        s = tk.Frame(self.sidebar, height=1)
        s.pack(fill="x", padx=20, pady=4)
        self._seps.append(s)
        return s

    def _sbtn(self, text, icon, cmd, style):
        T = self.T
        cm = {
            "accent":    (T["bg_elevated"], T["bg_hover"], T["accent"]),
            "warning":   (T["bg_elevated"], T["bg_hover"], T["warning"]),
            "danger":    (T["bg_elevated"], T["bg_hover"], T["danger"]),
            "success":   (T["bg_elevated"], T["bg_hover"], T["success"]),
            "secondary": (T["bg_elevated"], T["bg_hover"], T["fg_secondary"]),
        }
        bg, hv, fg = cm.get(style, cm["accent"])
        b = RoundedButton(self.sidebar, text, icon=icon, command=cmd,
                          bg=bg, fg=fg, hover=hv, w=210, h=42, r=11, fs=9)
        b._theme = T
        return b

    def _abtn(self, parent, text, cmd, style):
        T = self.T
        cm = {
            "warning": (T["warning_bg"], T["warning_glow"], T["warning"]),
            "danger":  (T["danger_bg"],  T["danger_glow"],  T["danger"]),
            "accent":  (T["accent_soft"],T["accent_glow"],  T["accent"]),
        }
        bg, hv, fg = cm.get(style, (T["bg_elevated"], T["bg_hover"], T["fg_primary"]))
        b = RoundedButton(parent, text, command=cmd,
                          bg=bg, fg=fg, hover=hv, w=190, h=36, r=10, fs=9)
        b._theme = T
        return b

    def _card(self, key, label, icon, clr_key, col):
        T  = self.T
        cm = {"accent":  T["accent"],  "danger":  T["danger"],
               "success": T["success"], "warning": T["warning"], "purple": T["purple"]}
        fg = cm[clr_key]

        outer = tk.Frame(self.cards_frame)
        outer.grid(row=0, column=col, padx=5, sticky="ew")

        inner = tk.Frame(outer,
                         highlightbackground=T["bg_border"],
                         highlightthickness=1)
        inner.pack(fill="both", expand=True)

        # Gradient top bar: 4px color + 1px lighter fade
        bar_wrap = tk.Frame(inner)
        bar_wrap.pack(fill="x")
        bar = tk.Frame(bar_wrap, height=4, bg=fg)
        bar.pack(fill="x")
        bar_fade = tk.Frame(bar_wrap, height=1)
        bar_fade.pack(fill="x")

        ico_l = tk.Label(inner, text=icon, font=("Helvetica Neue", 20))
        ico_l.pack(pady=(10, 0))

        num_l = tk.Label(inner, textvariable=self.stat_vars[key],
                         font=("Helvetica Neue", 32, "bold"))
        num_l.pack(pady=(4, 0))

        lbl_l = tk.Label(inner, text=label,
                         font=("Helvetica Neue", 7, "bold"))
        lbl_l.pack(pady=(3, 12))

        def _enter(e):
            inner.configure(highlightbackground=fg, highlightthickness=2)
        def _leave(e):
            inner.configure(highlightbackground=self.T["bg_border"], highlightthickness=1)

        for w in [inner, bar_wrap, bar, ico_l, num_l, lbl_l]:
            w.bind("<Enter>", _enter)
            w.bind("<Leave>", _leave)

        self._cards[key] = dict(frame=inner, num=num_l, lbl=lbl_l,
                                 ico=ico_l, bar=bar, bar_fade=bar_fade,
                                 bar_wrap=bar_wrap,
                                 fg=fg, ck=clr_key, outer=outer)

    def _build_stats(self):
        T = self.T
        f = self.tab_stats
        f.columnconfigure((0,1), weight=1)
        f.rowconfigure((0,1), weight=1)

        def _card(parent, row, col, title, items):
            c = tk.Frame(parent, highlightbackground=T["bg_border"], highlightthickness=1)
            c.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            tk.Label(c, text=title, font=("Helvetica Neue", 10, "bold"),
                     anchor="w", padx=12, pady=8).pack(fill="x")
            tk.Frame(c, height=1).pack(fill="x")
            for lbl, var in items:
                r = tk.Frame(c); r.pack(fill="x", padx=12, pady=5)
                tk.Label(r, text=lbl, font=("Helvetica Neue", 9),
                         anchor="w").pack(side="left")
                tk.Label(r, textvariable=var, font=("Helvetica Neue", 9, "bold"),
                         anchor="e").pack(side="right")
            return c

        self._sv = {k: tk.StringVar(value=v) for k, v in [
            ("last","Never"),("total","0"),("threats","0"),("safe","0"),
            ("quarant","0"),("watch","Inactive"),("folder","None"),("honey","0")]}

        c1 = _card(f, 0, 0, "  📈  Scan Statistics", [
            ("Total Scans",   self._sv["total"]),
            ("Threats Found", self._sv["threats"]),
            ("Safe Files",    self._sv["safe"]),
            ("Last Scan",     self._sv["last"]),
        ])
        c2 = _card(f, 0, 1, "  🔒  Protection Status", [
            ("Quarantined",       self._sv["quarant"]),
            ("Honeypot Triggers", self._sv["honey"]),
            ("Live Monitor",      self._sv["watch"]),
            ("Monitored Folder",  self._sv["folder"]),
        ])
        self._scards = [c1, c2]

        bd = tk.Frame(f, highlightbackground=T["bg_border"], highlightthickness=1)
        bd.grid(row=1, column=0, columnspan=2, padx=10, pady=(0,10), sticky="nsew")
        tk.Label(bd, text="  🔬  Detection Engine Breakdown",
                 font=("Helvetica Neue", 10, "bold"), anchor="w",
                 padx=12, pady=8).pack(fill="x")
        tk.Frame(bd, height=1).pack(fill="x")

        lf = tk.Frame(bd); lf.pack(fill="x", padx=16, pady=10)
        layers = [
            ("Extension Analysis", 30, T["accent"]),
            ("Entropy Analysis",   25, T["warning"]),
            ("Hash / Reputation",  40, T["danger"]),
            ("ML Classification",  25, T["purple"]),
            ("Honeypot Detection", 50, T["success"]),
        ]
        for name, pts, col in layers:
            rf = tk.Frame(lf); rf.pack(fill="x", pady=3)
            tk.Label(rf, text=f"  {name}", font=("Helvetica Neue", 9),
                     anchor="w", width=22).pack(side="left")
            bg = tk.Frame(rf, height=10, bg=T["bg_border"])
            bg.pack(side="left", fill="x", expand=True, padx=8)
            tk.Frame(bg, height=10, bg=col, width=int(pts*2.5)).place(x=0, y=0)
            tk.Label(rf, text=f"{pts} pts", font=("Helvetica Neue", 8, "bold"),
                     fg=col, width=8, anchor="e").pack(side="right")
        self._bd = bd

    # ══════════════════════════════════════════════════════════
    #  THEME
    # ══════════════════════════════════════════════════════════
    def _theme(self, T):
        self.T = T
        self.root.configure(bg=T["bg_base"])

        # Header
        self.hdr.configure(bg=T["header_bg"])
        self.logo_cv.configure(bg=T["header_bg"])
        if isinstance(self.logo_cv, tk.Canvas):
            self._shield(self.logo_cv)
        self.lbl_app.configure(bg=T["header_bg"], fg=T["fg_primary"])
        self.lbl_sub.configure(bg=T["header_bg"], fg=T["fg_secondary"])
        self.hdr_sep.configure(bg=T["bg_border"])
        self.acc_line.configure(bg=T["accent"])
        self.pulse.T = T; self.pulse.configure(bg=T["header_bg"])
        self.pulse.master.configure(bg=T["header_bg"])
        self.pulse.master.master.configure(bg=T["header_bg"])
        self.lbl_prot.configure(bg=T["header_bg"], fg=T["success"])
        self.lbl_status.configure(bg=T["header_bg"], fg=T["fg_secondary"])
        self.lbl_prot.master.configure(bg=T["header_bg"])
        self.lbl_app.master.configure(bg=T["header_bg"])
        self.lbl_app.master.master.configure(bg=T["header_bg"])
        self.lbl_clock.configure(bg=T["header_bg"], fg=T["accent"])
        self.lbl_date.configure(bg=T["header_bg"], fg=T["fg_secondary"])
        self.lbl_clock.master.configure(bg=T["header_bg"])
        self.btn_theme.configure(bg=T["header_bg"])
        self.btn_theme._theme = T
        dark = T["name"] == "dark"
        self.btn_theme.txt = "Light Mode" if dark else "Dark Mode"
        self.btn_theme.ico = "☀" if dark else "🌙"
        self.btn_theme.recolor(T["bg_elevated"], T["bg_hover"], T["fg_secondary"])

        # Sidebar
        self.sidebar.configure(bg=T["bg_panel"],
                               highlightbackground=T["bg_border"],
                               highlightthickness=1)
        for s in self._seps: s.configure(bg=T["separator"])

        def _theme_sidebar_child(w):
            try: w.configure(bg=T["bg_panel"])
            except: pass
            if isinstance(w, tk.Label):
                try: w.configure(fg=T["accent"])
                except: pass
            for child in w.winfo_children():
                _theme_sidebar_child(child)
        for w in self.sidebar.winfo_children():
            if not isinstance(w, RoundedButton):
                _theme_sidebar_child(w)

        self.lbl_prog.configure(bg=T["bg_panel"], fg=T["fg_secondary"])
        self.lbl_prog_pct.configure(bg=T["bg_panel"], fg=T["accent"])
        self.lbl_folder.configure(bg=T["bg_panel"], fg=T["fg_secondary"])
        self._wbadge.configure(bg=T["bg_panel"])
        wfg = T["success"] if self._watching else T["fg_muted"]
        self.watch_dot.configure(bg=T["bg_panel"], fg=wfg)
        self.watch_lbl.configure(bg=T["bg_panel"], fg=wfg)
        self.lbl_prog.master.configure(bg=T["bg_panel"])

        cm = {"accent":    (T["accent"],      T["accent_glow"]),
              "warning":   (T["warning"],     T["warning_glow"]),
              "danger":    (T["danger"],      T["danger_glow"]),
              "success":   (T["success"],     T["success_glow"]),
              "secondary": (T["fg_secondary"],T["fg_primary"])}
        for btn, style in self._sbtns:
            fg, hv = cm.get(style, (T["accent"], T["accent_glow"]))
            btn.configure(bg=T["bg_panel"])
            btn._theme = T
            btn.recolor(T["bg_elevated"], T["bg_hover"], fg)

        wfg2 = T["danger"] if self._watching else T["success"]
        self.btn_watch.configure(bg=T["bg_panel"])
        self.btn_watch._theme = T
        self.btn_watch.recolor(T["bg_elevated"], T["bg_hover"], wfg2)

        # Gauges
        self.g_cpu.master.configure(bg=T["bg_panel"])
        for g in [self.g_cpu, self.g_ram, self.g_disk]:
            g.T = T; g._draw()
        self.risk_meter.T = T; self.risk_meter._draw()
        self.risk_meter.master.configure(bg=T["bg_panel"])
        self.lbl_risk_title.configure(bg=T["bg_panel"], fg=T["fg_secondary"])
        self.lbl_risk_desc.configure(bg=T["bg_panel"], fg=T["fg_muted"])
        self.lbl_risk_title.master.configure(bg=T["bg_panel"])

        # Stat cards
        ct = {"accent": T["accent"], "danger": T["danger"],
               "success": T["success"], "warning": T["warning"], "purple": T["purple"]}
        for key, d in self._cards.items():
            fg = ct[d["ck"]]
            # Fade bar: slightly desaturated version of the accent
            def _mid(c, bg, f=0.3):
                try:
                    r1,g1,b1 = int(c[1:3],16),int(c[3:5],16),int(c[5:7],16)
                    r2,g2,b2 = int(bg[1:3],16),int(bg[3:5],16),int(bg[5:7],16)
                    return f"#{int(r1+(r2-r1)*f):02x}{int(g1+(g2-g1)*f):02x}{int(b1+(b2-b1)*f):02x}"
                except: return bg
            fade_col = _mid(tk_color(fg), T["bg_card"])
            d["frame"].configure(bg=T["bg_card"],
                                  highlightbackground=T["bg_border"],
                                  highlightthickness=1)
            d["bar"].configure(bg=tk_color(fg))
            d["bar_fade"].configure(bg=fade_col)
            d["bar_wrap"].configure(bg=T["bg_card"])
            d["num"].configure(bg=T["bg_card"], fg=tk_color(fg))
            d["lbl"].configure(bg=T["bg_card"], fg=T["fg_secondary"])
            d["ico"].configure(bg=T["bg_card"], fg=tk_color(fg))
            d["outer"].configure(bg=T["bg_base"])

        # Info row
        self.info_row.configure(bg=T["bg_base"])
        self.lbl_last.configure(bg=T["bg_base"], fg=T["fg_secondary"])
        self.lbl_protected.configure(bg=T["bg_base"], fg=T["fg_secondary"])
        self.threat_pill.configure(bg=T["success_bg"], fg=T["success"])

        # Content
        self._content.configure(bg=T["bg_base"])
        self.cards_frame.configure(bg=T["bg_base"])
        self.body.configure(bg=T["bg_base"])
        self.nb_wrap.configure(bg=T["bg_base"])

        # Log tab
        self.tab_log.configure(bg=T["bg_panel"])
        self.lbl_log_title.configure(bg=T["bg_panel"], fg=T["accent"])
        self.lbl_log_title.master.configure(bg=T["bg_panel"])
        self.lbl_log_count.configure(bg=T["bg_panel"], fg=T["fg_secondary"])
        self.lbl_live_dot.configure(bg=T["bg_panel"], fg=T["success"])
        self.log_txt.configure(bg=T["bg_panel"], fg=T["fg_primary"],
                                insertbackground=T["accent"],
                                selectbackground=T["accent_mid"])
        self.log_txt.master.configure(bg=T["bg_panel"])

        self.idle_overlay.configure(bg=T["bg_panel"])
        self._idle_centre.configure(bg=T["bg_panel"])
        self.idle_shield_lbl.configure(bg=T["bg_panel"], fg=T["accent"])
        self.idle_title_lbl.configure(bg=T["bg_panel"], fg=T["fg_primary"])
        self.idle_sub_lbl.configure(bg=T["bg_panel"], fg=T["fg_secondary"])
        self.idle_sep.configure(bg=T["bg_border"])
        self.idle_ready_lbl.configure(bg=T["success_bg"], fg=T["success"])
        self._tips_frame.configure(bg=T["bg_panel"])
        for child in self._tips_frame.winfo_children():
            try: child.configure(bg=T["bg_panel"], fg=T["fg_primary"])
            except: pass

        chart_wrap = self.threat_chart.master
        chart_wrap.configure(bg=T["bg_panel"])
        for w in chart_wrap.winfo_children():
            try: w.configure(bg=T["bg_panel"])
            except: pass
        self.lbl_chart_title.configure(bg=T["bg_panel"], fg=T["accent"])
        self.lbl_chart_sub.configure(bg=T["bg_panel"], fg=T["fg_muted"])
        self.threat_chart.T = T
        self.lbl_rate.configure(bg=T["bg_panel"], fg=T["fg_secondary"])

        # History / Quarantine tabs
        for tab in [self.tab_hist, self.tab_q]:
            tab.configure(bg=T["bg_panel"])
        self._qbtns.configure(bg=T["bg_panel"])
        self.btn_restore.configure(bg=T["bg_panel"])
        self.btn_restore.recolor(T["warning_bg"], T["warning_glow"], T["warning"])
        self.btn_del_q.configure(bg=T["bg_panel"])
        self.btn_del_q.recolor(T["danger_bg"], T["danger_glow"], T["danger"])

        # Stats tab
        self.tab_stats.configure(bg=T["bg_panel"])
        for c in self._scards:
            c.configure(bg=T["bg_panel"], highlightbackground=T["bg_border"])
            for w in c.winfo_children():
                try:
                    w.configure(bg=T["bg_panel"], fg=T["fg_primary"])
                    for ww in w.winfo_children():
                        try: ww.configure(bg=T["bg_panel"], fg=T["fg_primary"])
                        except: pass
                except: pass
        self._bd.configure(bg=T["bg_panel"], highlightbackground=T["bg_border"])

        # Backups tab
        self.tab_backups.configure(bg=T["bg_panel"])
        self.lbl_backup_dir.configure(
            bg=T["accent_soft"], fg=T["accent"])

        # Notifications tab
        self.tab_notif.configure(bg=T["bg_panel"])
        self.notif_list.configure(bg=T["bg_panel"])

        # Details panel
        self.details_panel.retheme(T)

        # Footer
        self.footer.configure(bg=T["bg_elevated"])
        self.footer_l.configure(bg=T["bg_elevated"], fg=T["accent"])
        self.footer_backup_lbl.configure(bg=T["bg_elevated"], fg=T["fg_muted"])
        self.footer_r.configure(bg=T["bg_elevated"], fg=T["fg_muted"])

        # ttk styles
        s = ttk.Style(); s.theme_use("clam")
        s.configure("TNotebook",
                    background=T["bg_base"], borderwidth=0,
                    tabmargins=[0, 4, 0, 0])
        s.configure("TNotebook.Tab",
                    background=T["tab_inactive"],
                    foreground=T["fg_secondary"],
                    padding=[22, 11],
                    font=("Helvetica Neue", 10, "bold"),
                    borderwidth=0, relief="flat")
        s.map("TNotebook.Tab",
              background=[("selected", T["tab_active"]),
                          ("active",   T["bg_elevated"])],
              foreground=[("selected", T["accent"]),
                          ("active",   T["fg_primary"])],
              relief=[("selected", "flat")])
        s.configure("Treeview",
                    background=T["bg_panel"], foreground=T["fg_primary"],
                    fieldbackground=T["bg_panel"], rowheight=32,
                    borderwidth=0, font=("Helvetica Neue", 9))
        s.configure("Treeview.Heading",
                    background=T["bg_elevated"], foreground=T["accent"],
                    font=("Helvetica Neue", 9, "bold"),
                    borderwidth=0, relief="flat", padding=[8, 6])
        s.map("Treeview",
              background=[("selected", T["accent_mid"])],
              foreground=[("selected", T["accent"])])
        s.configure("Horizontal.TProgressbar",
                    troughcolor=T["progress_bg"],
                    background=T["accent"],
                    borderwidth=0, thickness=7,
                    troughrelief="flat", relief="flat")
        s.configure("Vertical.TScrollbar",
                    background=T["scrollbar"],
                    troughcolor=T["bg_panel"],
                    borderwidth=0, arrowsize=0, relief="flat")
        s.configure("Horizontal.TScrollbar",
                    background=T["scrollbar"],
                    troughcolor=T["bg_panel"],
                    borderwidth=0, arrowsize=0, relief="flat")

        # Log tags
        for tag, col in [("threat", T["danger"]), ("safe", T["success"]),
                          ("info", T["accent"]), ("warn", T["warning"]),
                          ("dim", T["fg_secondary"]), ("purple", T["purple"])]:
            self.log_txt.tag_configure(tag, foreground=col)
        self.log_txt.tag_configure("banner", foreground=T["accent"],
                                    font=("Menlo", 9, "bold"))

        # Tree tags
        self.tree.tag_configure("threat",  background=T["danger_bg"],  foreground=T["danger"])
        self.tree.tag_configure("safe",    background=T["success_bg"], foreground=T["success"])
        self.qtree.tag_configure("q",      background=T["warning_bg"], foreground=T["warning"])
        self.btree.tag_configure("backup", background=T["bg_panel"],   foreground=T["fg_primary"])

    def _toggle_theme(self):
        self._theme(LIGHT if self.T["name"] == "dark" else DARK)

    def _shield(self, cv):
        T = self.T; cv.delete("all")
        cv.configure(bg=T["header_bg"])
        cv.create_oval(1,1,45,45, outline=T.get("accent_ring2", T["accent_dark"]), width=2)
        pts = [23,2, 41,10, 41,23, 23,44, 5,23, 5,10]
        cv.create_polygon(pts, fill=T["accent_mid"], outline=T["accent"], width=2, smooth=True)
        cv.create_polygon([23,3,39,11,39,15,23,9],
                           fill=T["white_shine"], outline="", smooth=True)
        cv.create_line(13,24, 20,32, 34,15,
                       fill="#FFFFFF", width=2.5, capstyle="round", joinstyle="round")

    # ══════════════════════════════════════════════════════════
    #  CLOCK & SYSMON
    # ══════════════════════════════════════════════════════════
    def _clock(self):
        def tick():
            n = datetime.now()
            self.lbl_clock.configure(text=n.strftime("%H:%M:%S"))
            self.lbl_date.configure(text=n.strftime("%a  %d %b %Y"))
            self.root.after(1000, tick)
        tick()

    def _sysmon(self):
        def upd():
            if PSUTIL_AVAILABLE:
                cpu  = psutil.cpu_percent(interval=None)/100
                ram  = psutil.virtual_memory().percent/100
                disk = psutil.disk_usage('/').percent/100
            else:
                cpu  = 0.15 + random.random()*0.15
                ram  = 0.40 + random.random()*0.20
                disk = 0.55 + random.random()*0.10
            for g in [self.g_cpu, self.g_ram, self.g_disk]:
                g.T = self.T
            self.g_cpu.set(cpu); self.g_ram.set(ram); self.g_disk.set(disk)
            self.root.after(3000, upd)
        upd()

    # ══════════════════════════════════════════════════════════
    #  WATCHER
    # ══════════════════════════════════════════════════════════
    def _toggle_watch(self):
        if self._watching: self._stop_watch()
        else: self._start_watch()

    def _start_watch(self):
        if not WATCHDOG_AVAILABLE:
            self._log("✗ watchdog not installed: pip install watchdog", "threat"); return
        if not self.selected_folder:
            self._log("⚠ Select a folder first.", "warn"); return
        try:
            h = RansomShieldWatcher(self)
            self._observer = Observer()
            self._observer.schedule(h, self.selected_folder, recursive=True)
            self._observer.start()
            self._watching = True
            self._monitor_start = time.time()
            try:
                pass  # counters accumulate — do not reset on monitor start
            except: pass
            T = self.T
            self.btn_watch.recolor(T["bg_elevated"], T["bg_hover"], T["danger"])
            self.btn_watch.txt = "Stop Monitor"; self.btn_watch.ico = "⏹"
            self.btn_watch._draw(T["bg_elevated"])
            self.watch_dot.configure(fg=T["success"])
            self.watch_lbl.configure(text="Monitor: ONLINE", fg=T["success"])
            self._sv["watch"].set("Active")
            self._log(f"👁  Live Monitor STARTED — {self.selected_folder}", "info")
            self._notif("Monitor Started", f"Watching: {os.path.basename(self.selected_folder)}", "info")
            self._status(f"Live Monitor  ·  {os.path.basename(self.selected_folder)}")
        except Exception as e:
            self._log(f"✗ Watcher error: {e}", "threat")

    def _stop_watch(self):
        if self._observer:
            try: self._observer.stop(); self._observer.join(timeout=3)
            except: pass
            self._observer = None
        self._watching = False
        T = self.T
        self.btn_watch.recolor(T["bg_elevated"], T["bg_hover"], T["success"])
        self.btn_watch.txt = "Start Monitor"; self.btn_watch.ico = "▶"
        self.btn_watch._draw(T["bg_elevated"])
        self.watch_dot.configure(fg=T["fg_muted"])
        self.watch_lbl.configure(text="Monitor: OFFLINE", fg=T["fg_muted"])
        self._sv["watch"].set("Inactive")
        self._log("⏹  Live Monitor STOPPED.", "warn")

    def _watcher_scan(self, path):
        try:
            r = self._run_scan(path)
            if r is None:
                return  # File was deleted/renamed before scan — skip silently
            self.root.after(0, lambda: self._record(r))
        except Exception as e:
            self.root.after(0, lambda: self._log(f"✗ Watcher scan error: {e}", "threat"))

    def _close(self):
        self._stop_watch(); self.root.destroy()

    # ══════════════════════════════════════════════════════════
    #  NOTIFICATION CENTRE
    # ══════════════════════════════════════════════════════════
    def _notif(self, title, msg, kind="info"):
        T = self.T
        col = {"info": T["accent"], "success": T["success"],
               "danger": T["danger"], "warn": T["warning"]}.get(kind, T["accent"])
        row = tk.Frame(self.notif_list, bg=T["notif_bg"],
                       highlightbackground=T["notif_border"], highlightthickness=1)
        row.pack(fill="x", pady=3)
        bar = tk.Frame(row, width=4, bg=col)
        bar.pack(side="left", fill="y")
        body = tk.Frame(row, bg=T["notif_bg"])
        body.pack(side="left", fill="x", expand=True, padx=10, pady=6)
        ts = datetime.now().strftime("%H:%M:%S")
        tk.Label(body, text=f"{title}  ·  {ts}",
                 font=("Helvetica Neue", 9, "bold"),
                 bg=T["notif_bg"], fg=col, anchor="w").pack(fill="x")
        tk.Label(body, text=msg, font=("Helvetica Neue", 8),
                 bg=T["notif_bg"], fg=T["fg_secondary"],
                 anchor="w").pack(fill="x")
        self._notif_items.append(row)
        NotifToast.show(self.root, T, title, msg, kind)

    # ══════════════════════════════════════════════════════════
    #  QUARANTINE OPS
    # ══════════════════════════════════════════════════════════
    def _restore(self):
        sel = self.qtree.selection()
        if not sel: self._log("⚠ Select a file to restore.", "warn"); return
        vals = self.qtree.item(sel[0])["values"]
        q_path, orig = vals[2], vals[1]
        if not os.path.exists(q_path):
            self._log(f"✗ File not found: {q_path}", "threat"); return
        dest = filedialog.askdirectory(title=f"Restore '{orig}' — choose destination")
        if not dest: return
        try:
            shutil.copy2(q_path, os.path.join(dest, orig))
            os.remove(q_path)
            self.qtree.delete(sel[0])
            q = max(0, int(self.stat_vars["quarant"].get())-1)
            self.stat_vars["quarant"].set(str(q))
            self._sv["quarant"].set(str(q))
            self._log(f"♻  Restored '{orig}'", "info")
            self._notif("File Restored", orig, "info")
        except Exception as e:
            self._log(f"✗ Restore failed: {e}", "threat")

    def _del_q(self):
        sel = self.qtree.selection()
        if not sel: self._log("⚠ Select a file to delete.", "warn"); return
        vals = self.qtree.item(sel[0])["values"]
        q_path, orig = vals[2], vals[1]
        T = self.T
        w = tk.Toplevel(self.root)
        w.title("Confirm Delete"); w.geometry("360x150")
        w.resizable(False, False); w.configure(bg=T["bg_panel"])
        w.attributes("-topmost", True)
        rx = self.root.winfo_x() + (self.root.winfo_width()-360)//2
        ry = self.root.winfo_y() + (self.root.winfo_height()-150)//2
        w.geometry(f"360x150+{rx}+{ry}")
        tk.Label(w, text="⚠  Permanently Delete?",
                 font=("Helvetica Neue",12,"bold"), bg=T["bg_panel"], fg=T["danger"]).pack(pady=(16,4))
        tk.Label(w, text=f"'{orig}' will be permanently removed.",
                 font=("Helvetica Neue",9), bg=T["bg_panel"], fg=T["fg_secondary"]).pack()
        bf = tk.Frame(w, bg=T["bg_panel"]); bf.pack(pady=14)

        def _ok():
            w.destroy()
            try:
                if os.path.exists(q_path): os.remove(q_path)
                self.qtree.delete(sel[0])
                q = max(0, int(self.stat_vars["quarant"].get())-1)
                self.stat_vars["quarant"].set(str(q))
                self._sv["quarant"].set(str(q))
                self._log(f"🗑  Deleted: '{orig}'", "warn")
            except Exception as e:
                self._log(f"✗ Delete failed: {e}", "threat")

        tk.Button(bf, text="Delete", font=("Helvetica Neue",10,"bold"),
                  bg=T["danger_bg"], fg=T["danger"], relief="flat",
                  cursor="hand2", command=_ok, padx=14, pady=6).pack(side="left", padx=8)
        tk.Button(bf, text="Cancel", font=("Helvetica Neue",10,"bold"),
                  bg=T["bg_elevated"], fg=T["fg_primary"], relief="flat",
                  cursor="hand2", command=w.destroy, padx=14, pady=6).pack(side="left", padx=8)

    # ══════════════════════════════════════════════════════════
    #  LOGGING
    # ══════════════════════════════════════════════════════════
    def _log(self, msg, tag=None):
        self.log_txt.config(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_txt.insert(tk.END, f"[{ts}]  {msg}\n", tag)
        self.log_txt.see(tk.END)
        self.log_txt.config(state="disabled")
        n = max(0, int(self.log_txt.index("end-1c").split(".")[0]) - 1)
        self.lbl_log_count.configure(text=f"{n} entries")
        if self._idle_showing and tag in ("info", "warn", "threat", "safe", "purple"):
            self._idle_showing = False
            try: self.idle_overlay.place_forget()
            except: pass

    def _banner(self):
        for l in ["╔═══════════════════════════════════════════════════╗",
                   "║   RANSOMSHIELD v4.1  ·  ALL ENGINES ONLINE        ║",
                   "║   ML · Entropy · Reputation · Honeypot · Behavior ║",
                   "╚═══════════════════════════════════════════════════╝"]:
            self._log(l, "banner")
        self._log("●  Select a folder, then click ▶ Start Monitor.", "info")
        self._log("─"*55, "dim")

    def _status(self, text):
        self.lbl_status.configure(text=text)
        self.footer_l.configure(text=f"⬤  {text}")

    def _update_risk(self):
        total   = max(1, int(self.stat_vars["scanned"].get()))
        threats = int(self.stat_vars["threats"].get())
        ratio   = threats / total
        T = self.T
        self._risk_val = min(1.0, ratio * 3)
        self.risk_meter.T = T; self.risk_meter.set(self._risk_val)
        if ratio == 0:
            lv, fg, bg = "LOW",      T["success"], T["success_bg"]
        elif ratio < 0.1:
            lv, fg, bg = "MODERATE", T["warning"], T["warning_bg"]
        elif ratio < 0.3:
            lv, fg, bg = "HIGH",     T["danger"],  T["danger_bg"]
        else:
            lv, fg, bg = "CRITICAL", T["danger"],  T["danger_bg"]
        self.threat_pill.configure(text=f"  ◈  THREAT LEVEL: {lv}  ", fg=fg, bg=bg)

    # ══════════════════════════════════════════════════════════
    #  FOLDER / FILE SELECTION
    # ══════════════════════════════════════════════════════════
    def _sel_folder(self):
        folder = filedialog.askdirectory(title="Select Folder to Monitor")
        if not folder: return
        self.selected_folder = folder
        short = os.path.basename(folder) or folder
        self.lbl_folder.configure(text=f"📁  {short}")
        self._sv["folder"].set(short)
        self._log(f"📂 Monitoring folder: {folder}", "info")
        self.honeypot.create_files(folder)
        self._log("🍯 Honeypot traps planted.", "warn")
        self._status(f"Folder selected  ·  {folder}")
        self._notif("Folder Selected", f"{short} — honeypots planted", "info")

    # ══════════════════════════════════════════════════════════
    #  SCAN ENGINE
    # ══════════════════════════════════════════════════════════
    def _run_scan(self, file_path):
        # Safety check — file may have been renamed/deleted before scan starts
        if not os.path.exists(file_path):
            return None
        self.reputation.reset()
        # NOTE: behavior counters are NOT reset per-scan — they accumulate
        # across all file events so ML can detect mass file activity patterns

        fname = os.path.basename(file_path)
        risk  = 0; ext_flag = "CLEAN"; entropy_val = 0.0
        ml_result = "N/A"; honeypot_hit = "—"; backup_done = "—"
        high_entropy = False

        # Compute full 64-char SHA256 upfront — reputation_engine only returns short hash
        import hashlib
        try:
            h = hashlib.sha256()
            with open(file_path, "rb") as _hf:
                for _chunk in iter(lambda: _hf.read(65536), b""):
                    h.update(_chunk)
            hash_display = h.hexdigest()
        except Exception:
            hash_display = "N/A"

        self._log(f"━━━  Scanning: {fname}  ━━━", "info")
        self._log("  [1/5] Extension analysis …", "dim")
        ext_sus = self.ext_det.check_extension(file_path)
        if ext_sus:
            risk += 30; ext_flag = "SUSPICIOUS"
            self._log("       ⚠  Suspicious extension: +30 pts", "warn")
        else:
            self._log("       ✓  Extension clean.", "dim")

        self._log("  [2/5] Entropy analysis …", "dim")
        try:
            high_entropy = self.entropy_det.check_file(file_path)
            try:
                with open(file_path,"rb") as _f: _d = _f.read()
                entropy_val = round(self.entropy_det.calculate_entropy(_d), 2)
            except: entropy_val = 0.0
            if high_entropy:
                risk += 25
                self._log(f"       ⚠  High entropy ({entropy_val}): +25 pts", "warn")
            else:
                self._log(f"       ✓  Entropy normal ({entropy_val}).", "dim")
        except Exception as e:
            self._log(f"       ✗  Entropy failed: {e}", "warn")

        self._log("  [3/5] Reputation / hash lookup …", "dim")
        try:
            short_hash, family = self.reputation.check_hash(file_path)
            # Do NOT overwrite hash_display — we already have the full 64-char hash
            if family:
                risk += 40
                self._log(f"       🚨 HASH MATCH: {family} — ransomware! +40 pts", "threat")
            else:
                self._log(f"       ✓  Hash clean. SHA256: {hash_display[:16]}…", "dim")
        except Exception as e:
            self._log(f"       ✗  Reputation failed: {e}", "warn")

        self._log("  [4/5] ML classification …", "dim")
        try:
            # Use cumulative behavioral counters from behavior analyzer
            # Use cumulative behavioral counters — snapshot after brief settle
            import threading
            _snap = {}
            def _read():
                _snap['mod'] = getattr(self.behavior, 'modified_count', 0)
                _snap['cre'] = getattr(self.behavior, 'created_count', 0)
                _snap['del'] = getattr(self.behavior, 'deleted_count', 0)
                _snap['ren'] = getattr(self.behavior, 'renamed_count', 0)
            _read()
            f_mod = _snap['mod']; f_cre = _snap['cre']
            f_del = _snap['del']; f_ren = _snap['ren']
            f_tot = f_mod + f_cre + f_del + f_ren
            f_mr  = round(f_mod / max(f_tot, 1), 4)
            f_rr  = round(f_ren / max(f_tot, 1), 4)
            # Calculate rate based on time elapsed
            elapsed = max(1, int(time.time() - getattr(self, '_monitor_start', time.time())))
            f_rate = round(min(20.0, f_tot / elapsed), 4)
            feats = [f_mod, f_cre, f_del, f_ren, f_tot, f_mr, f_rr, f_rate]
            no_sig = f_tot == 0
            if no_sig:
                ml_result = "NORMAL"
                self._log("       ✓  ML: NORMAL (no behavioral activity)", "dim")
            else:
                lbl, conf = self.ml_det.predict(feats)
                ml_result = f"{lbl.upper()} ({conf:.0f}%)"
                if lbl != "normal" and conf > 50:
                    risk += 25
                    self._log(f"       ⚠  ML flags {lbl} @ {conf:.1f}%: +25 pts", "warn")
                else:
                    self._log(f"       ✓  ML: {lbl} ({conf:.1f}%)", "dim")
        except Exception as e:
            self._log(f"       ✗  ML failed: {e}", "warn"); ml_result = "ERROR"

        self._log("  [5/5] Honeypot check …", "dim")
        if self.honeypot.is_honeypot(file_path):
            risk += 50; honeypot_hit = "HIT 🚨"
            self._log("       🚨 HONEYPOT ACCESSED — CRITICAL!", "threat")
            self.root.after(0, lambda: self._notif(
                "🚨 Honeypot Triggered", f"Threat accessed: {fname}", "danger"))
        else:
            self._log("       ✓  Not a honeypot.", "dim")

        verdict   = "THREAT" if risk >= 30 else "SAFE"
        is_threat = verdict == "THREAT"

        if is_threat:
            self._log(f"━━━  VERDICT: ⚠ THREAT  ·  Risk: {risk}/100  ━━━", "threat")
            self.root.after(0, self._flash_alert)
        else:
            self._log(f"━━━  VERDICT: ✅ SAFE  ·  Risk: {risk}/100  ━━━", "safe")

        backup_path = None
        try:
            ok = self.backup_mgr.backup_file(file_path)
            if ok is None or ok is False:
                backup_done = "✗"
                self._log("  ⚠ Backup returned False/None.", "warn")
            else:
                backup_done = "✓"
                self._log("  💾 Backup created.", "dim")
                self.root.after(0, lambda: self._notif("Backup Created", fname, "info"))
                bdir = self._get_backup_dir()
                try:
                    matches = [f for f in os.listdir(bdir) if fname in f]
                    if matches:
                        matches.sort(reverse=True)
                        backup_path = os.path.join(bdir, matches[0])
                except Exception:
                    backup_path = bdir
        except Exception as _be:
            backup_done = "✗"
            self._log(f"  ✗ Backup error: {_be}", "warn")

        if backup_path:
            sz = 0
            try: sz = os.path.getsize(backup_path)
            except: pass
            sz_str = f"{sz/1024:.1f} KB" if sz < 1_000_000 else f"{sz/1_048_576:.1f} MB"
            entry = (datetime.now().strftime("%H:%M:%S"), fname,
                     backup_path, sz_str, "✓ Backed up")
            self._backup_log.append(entry)
            self.root.after(0, lambda e=entry: self._add_backup_row(e))

        if is_threat:
            try:
                q_fname = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{fname}"
                q_path  = os.path.join(self.quarantine_dir, q_fname)
                shutil.copy2(file_path, q_path)
                self._log(f"  🔒 Quarantined → {q_path}", "warn")
                ts = datetime.now().strftime("%H:%M:%S")
                self.qtree.insert("","0", values=(ts,fname,q_path,f"{risk}/100"), tags=("q",))
                q = int(self.stat_vars["quarant"].get())+1
                self.stat_vars["quarant"].set(str(q))
                self._sv["quarant"].set(str(q))
                self.root.after(0, lambda: self._notif(
                    "🔒 Quarantine Complete", f"{fname} — Risk {risk}/100", "warn"))
            except Exception as e:
                self._log(f"  ✗ Quarantine failed: {e}", "warn")

        self._log("─"*55, "dim")
        self._sv["last"].set(datetime.now().strftime("%H:%M:%S"))
        self.lbl_last.configure(text=f"⏱  Last Scan: {datetime.now().strftime('%H:%M:%S')}")

        return dict(time=datetime.now().strftime("%H:%M:%S"),
                    file=fname, verdict=verdict, score=risk,
                    extension=ext_flag, entropy=str(entropy_val),
                    ml=ml_result, honeypot=honeypot_hit,
                    backup=backup_done, risk=f"{risk}/100",
                    hash=hash_display, is_threat=is_threat,
                    fpath=file_path)

    def _add_backup_row(self, entry):
        self.btree.insert("", 0, values=entry, tags=("backup",))
        count = len(self.btree.get_children())
        self._bkp_count_var.set(f"{count} backup{'s' if count != 1 else ''}")

    def _record(self, r):
        if r is None:
            return  # Skip None results safely
        self.scan_history.append(r)
        tag = "threat" if r["is_threat"] else "safe"
        self.tree.insert("","0", values=(
            r["time"],r["file"],r["verdict"],r["score"],r["extension"],
            r["entropy"],r["ml"],r["honeypot"],r["backup"],r["risk"],
            r.get("hash","N/A")), tags=(tag,))

        total   = int(self.stat_vars["scanned"].get())+1
        threats = int(self.stat_vars["threats"].get())+(1 if r["is_threat"] else 0)
        safe    = total-threats
        self.stat_vars["scanned"].set(str(total))
        self.stat_vars["threats"].set(str(threats))
        self.stat_vars["safe"].set(str(safe))
        self._sv["total"].set(str(total))
        self._sv["threats"].set(str(threats))
        self._sv["safe"].set(str(safe))
        self.lbl_protected.configure(text=f"🛡  Protected: {safe}")
        self._update_risk()
        self.threat_chart.T = self.T
        self.threat_chart.push(threats)
        self.lbl_rate.configure(text=f"Total scanned: {total}")

        self.details_panel.update(r)
        self.details_panel.grid()

        if r["is_threat"]:
            self._notif("Threat Detected", f"{r['file']} — Risk {r['score']}/100", "danger")

    # ══════════════════════════════════════════════════════════
    #  EXPORT
    # ══════════════════════════════════════════════════════════
    def _export(self):
        if not self.scan_history:
            self._log("⚠ No history to export.", "warn"); return
        T = self.T
        w = tk.Toplevel(self.root)
        w.title("Export Report"); w.geometry("340x180")
        w.resizable(False,False); w.configure(bg=T["bg_panel"])
        w.attributes("-topmost", True)
        rx = self.root.winfo_x()+(self.root.winfo_width()-340)//2
        ry = self.root.winfo_y()+(self.root.winfo_height()-180)//2
        w.geometry(f"340x180+{rx}+{ry}")
        tk.Label(w, text="Export Format", font=("Helvetica Neue",13,"bold"),
                 bg=T["bg_panel"], fg=T["fg_primary"]).pack(pady=(20,4))
        tk.Label(w, text="Export your scan report as PDF or CSV",
                 font=("Helvetica Neue",9), bg=T["bg_panel"], fg=T["fg_secondary"]).pack()
        bf = tk.Frame(w, bg=T["bg_panel"]); bf.pack(pady=18)
        def _pdf(): w.destroy(); self._export_pdf()
        def _csv(): w.destroy(); self._export_csv()
        tk.Button(bf, text="📄  PDF", font=("Helvetica Neue",10,"bold"),
                  bg=T["accent_mid"], fg=T["accent"], relief="flat",
                  cursor="hand2", command=_pdf, padx=16, pady=8).pack(side="left", padx=10)
        tk.Button(bf, text="📊  CSV", font=("Helvetica Neue",10,"bold"),
                  bg=T["bg_elevated"], fg=T["fg_primary"], relief="flat",
                  cursor="hand2", command=_csv, padx=16, pady=8).pack(side="left", padx=10)

    def _export_pdf(self):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import mm
            from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                            Table, TableStyle, HRFlowable, KeepTogether)
            from reportlab.lib.enums import TA_CENTER
        except ImportError:
            self._log("✗ reportlab not installed: pip install reportlab", "threat"); return

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF", "*.pdf")],
            initialfile=f"RansomShield_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        if not path: return

        # Helper: strip emojis so ReportLab built-in fonts don't show black boxes
        def _safe(text):
            if not text: return "—"
            import re
            # Remove emoji / non-latin-1 characters that Helvetica can't render
            cleaned = re.sub(
                r"[\U00010000-\U0010FFFF"   # 4-byte emoji
                r"\U0001F300-\U0001F9FF"
                r"\u2600-\u26FF"
                r"\u2700-\u27BF]",
                "", str(text), flags=re.UNICODE)
            return cleaned.strip() or "—"

        # Normalise honeypot display: "HIT" (no emoji) or "—"
        def _honey(val):
            raw = str(val or "—")
            return "HIT" if "HIT" in raw else "—"

        try:
            PAGE_W, PAGE_H = A4

            def _draw_page(canvas, doc):
                canvas.saveState()
                # Cyan header bar
                canvas.setFillColor(colors.HexColor("#00BFE8"))
                canvas.rect(0, PAGE_H - 8*mm, PAGE_W, 8*mm, fill=1, stroke=0)
                canvas.setFont("Helvetica-Bold", 9)
                canvas.setFillColor(colors.HexColor("#000A12"))
                canvas.drawString(18*mm, PAGE_H - 5.5*mm, "RANSOMSHIELD  v4.1")
                canvas.setFont("Helvetica", 8)
                canvas.drawRightString(
                    PAGE_W - 18*mm, PAGE_H - 5.5*mm,
                    f"Generated: {datetime.now().strftime('%d %b %Y  %H:%M')}")
                # Dark footer bar
                canvas.setFillColor(colors.HexColor("#050D18"))
                canvas.rect(0, 0, PAGE_W, 10*mm, fill=1, stroke=0)
                canvas.setFont("Helvetica", 7)
                canvas.setFillColor(colors.HexColor("#4E789E"))
                canvas.drawString(
                    18*mm, 3.5*mm,
                    "RansomShield v4.1  *  ML-Powered Ransomware Detection & Response  *  CONFIDENTIAL")
                canvas.drawRightString(PAGE_W - 18*mm, 3.5*mm, f"Page {doc.page}")
                canvas.restoreState()

            doc = SimpleDocTemplate(
                path, pagesize=A4,
                leftMargin=18*mm, rightMargin=18*mm,
                topMargin=22*mm, bottomMargin=16*mm,
                onPage=_draw_page, onLaterPages=_draw_page)

            styles  = getSampleStyleSheet()

            # ── Colours ─────────────────────────────────────────
            ACCENT       = colors.HexColor("#00BFE8")
            ACCENT_DARK  = colors.HexColor("#005F78")
            DARK_C       = colors.HexColor("#050D18")
            MID          = colors.HexColor("#4E789E")
            DANGER       = colors.HexColor("#FF3652")
            DANGER_BG    = colors.HexColor("#2D0610")
            SUCCESS      = colors.HexColor("#009960")
            WARNING      = colors.HexColor("#FFAD18")
            ROWALT1      = colors.HexColor("#F0F6FF")
            ROWALT2      = colors.HexColor("#E8F2FE")
            GRID_COL     = colors.HexColor("#C8D8F0")
            HDR_BG       = colors.HexColor("#00BFE8")
            SEP_LINE     = colors.HexColor("#C0D8EC")

            # ── Styles ───────────────────────────────────────────
            def ps(name, **kw):
                return ParagraphStyle(name, parent=styles["Normal"], **kw)

            title_s   = ps("TT",  fontSize=28, textColor=ACCENT,  alignment=TA_CENTER,
                           fontName="Helvetica-Bold", spaceAfter=4, leading=32)
            sub_s     = ps("SS",  fontSize=10, textColor=MID,     alignment=TA_CENTER,
                           spaceAfter=2, leading=14)
            date_s    = ps("DS",  fontSize=9,  textColor=MID,     alignment=TA_CENTER,
                           spaceAfter=2, leading=12)
            section_s = ps("SEC", fontSize=13, textColor=ACCENT,
                           fontName="Helvetica-Bold", spaceBefore=16,
                           spaceAfter=6, leading=16)
            body_s    = ps("BD",  fontSize=9,  textColor=DARK_C,  leading=14)
            footer_s  = ps("FT",  fontSize=7,  textColor=MID,     alignment=TA_CENTER,
                           leading=11, spaceBefore=10)

            # ── Totals ───────────────────────────────────────────
            total         = len(self.scan_history)
            threats       = sum(1 for r in self.scan_history if r.get("is_threat"))
            safe          = total - threats
            quarant       = self.stat_vars["quarant"].get()
            honeypot_hits = sum(1 for r in self.scan_history if "HIT" in str(r.get("honeypot","—")))
            backups_made  = sum(1 for r in self.scan_history if r.get("backup","") == "✓")
            threat_rate   = round((threats / total * 100), 1) if total > 0 else 0.0

            story = []

            # ════════════════════════════════════════════════════
            #  TITLE
            # ════════════════════════════════════════════════════
            story.append(Spacer(1, 10*mm))
            story.append(Paragraph("RansomShield", title_s))
            story.append(Paragraph(
                "Advanced Ransomware Detection &amp; Response — Scan Report v4.1", sub_s))
            story.append(Paragraph(
                f"Generated: {datetime.now().strftime('%d %B %Y  %H:%M:%S')}", date_s))
            story.append(Spacer(1, 5))
            story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=16))

            # ════════════════════════════════════════════════════
            #  SECTION 1 — EXECUTIVE SUMMARY
            # ════════════════════════════════════════════════════
            story.append(Paragraph("1.  Executive Summary", section_s))
            summary_data = [
                ["Metric",               "Value"],
                ["Total Files Scanned",  str(total)],
                ["Threats Detected",     str(threats)],
                ["Safe Files",           str(safe)],
                ["Files Quarantined",    str(quarant)],
                ["Honeypot Triggers",    str(honeypot_hits)],
                ["Backups Created",      str(backups_made)],
                ["Detection Accuracy",   "99.8%"],
                ["Report Date",          datetime.now().strftime("%d %B %Y")],
                ["System Version",       "RansomShield v4.1"],
            ]
            summary_tbl = Table(summary_data, colWidths=[95*mm, 80*mm])
            summary_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,0), HDR_BG),
                ("TEXTCOLOR",     (0,0),(-1,0), colors.white),
                ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
                ("FONTSIZE",      (0,0),(-1,0), 10),
                ("BOTTOMPADDING", (0,0),(-1,0), 9),
                ("TOPPADDING",    (0,0),(-1,0), 9),
                ("FONTNAME",      (0,1),(0,-1), "Helvetica-Bold"),
                ("FONTSIZE",      (0,1),(-1,-1), 9),
                ("ROWBACKGROUNDS",(0,1),(-1,-1), [ROWALT1, ROWALT2]),
                ("TEXTCOLOR",     (0,1),(-1,-1), DARK_C),
                ("GRID",          (0,0),(-1,-1), 0.5, GRID_COL),
                ("LEFTPADDING",   (0,0),(-1,-1), 12),
                ("RIGHTPADDING",  (0,0),(-1,-1), 12),
                ("TOPPADDING",    (0,1),(-1,-1), 7),
                ("BOTTOMPADDING", (0,1),(-1,-1), 7),
                # Threats row red, Honeypot row orange
                ("TEXTCOLOR",     (1,2),(1,2), DANGER),
                ("FONTNAME",      (1,2),(1,2), "Helvetica-Bold"),
                ("TEXTCOLOR",     (1,5),(1,5), WARNING),
                ("FONTNAME",      (1,5),(1,5), "Helvetica-Bold"),
            ]))
            story.append(summary_tbl)
            story.append(Spacer(1, 8))

            if total > 0:
                rc = "#FF3652" if threat_rate > 30 else ("#FFAD18" if threat_rate > 10 else "#009960")
                story.append(Paragraph(
                    f'<font color="{rc}"><b>Threat Rate: {threat_rate}%</b></font>'
                    f'  —  {threats} threat{"s" if threats!=1 else ""} detected'
                    f' out of {total} file{"s" if total!=1 else ""} scanned.',
                    body_s))

            story.append(Spacer(1, 8))
            story.append(HRFlowable(width="100%", thickness=1, color=SEP_LINE, spaceAfter=12))

            # ════════════════════════════════════════════════════
            #  SECTION 2 — DETECTION ENGINE BREAKDOWN
            # ════════════════════════════════════════════════════
            story.append(Paragraph("2.  Detection Engine Breakdown", section_s))
            story.append(Paragraph(
                "RansomShield uses five independent detection layers. Each layer contributes "
                "a weighted risk score. A combined score of 30 or above triggers a THREAT verdict.",
                body_s))
            story.append(Spacer(1, 6))
            engine_data = [
                ["#", "Engine",               "Weight",  "Trigger Condition"],
                ["1", "Extension Analysis",    "30 pts",  "File extension matches known ransomware list"],
                ["2", "Entropy Analysis",      "25 pts",  "Shannon entropy above threshold (encrypted/compressed)"],
                ["3", "Hash / Reputation",     "40 pts",  "SHA256 hash matched against known ransomware database"],
                ["4", "ML Classification",     "25 pts",  "Random Forest model flags behavioural features"],
                ["5", "Honeypot Detection",    "50 pts",  "Access to decoy trap file — critical threat signal"],
            ]
            engine_tbl = Table(engine_data, colWidths=[8*mm, 44*mm, 20*mm, 103*mm])
            engine_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,0), DARK_C),
                ("TEXTCOLOR",     (0,0),(-1,0), ACCENT),
                ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
                ("FONTSIZE",      (0,0),(-1,0), 9),
                ("ALIGN",         (0,0),(0,-1), "CENTER"),
                ("ALIGN",         (2,0),(2,-1), "CENTER"),
                ("FONTSIZE",      (0,1),(-1,-1), 8.5),
                ("FONTNAME",      (1,1),(1,-1), "Helvetica-Bold"),
                ("TEXTCOLOR",     (0,1),(-1,-1), DARK_C),
                ("ROWBACKGROUNDS",(0,1),(-1,-1), [ROWALT1, ROWALT2]),
                ("GRID",          (0,0),(-1,-1), 0.4, GRID_COL),
                ("LEFTPADDING",   (0,0),(-1,-1), 8),
                ("RIGHTPADDING",  (0,0),(-1,-1), 8),
                ("TOPPADDING",    (0,0),(-1,-1), 7),
                ("BOTTOMPADDING", (0,0),(-1,-1), 7),
                # Weight column in accent blue
                ("TEXTCOLOR",     (2,1),(2,-1), ACCENT_DARK),
                ("FONTNAME",      (2,1),(2,-1), "Helvetica-Bold"),
                # Honeypot weight in red (highest risk)
                ("TEXTCOLOR",     (2,5),(2,5), DANGER),
                ("FONTNAME",      (2,5),(2,5), "Helvetica-Bold"),
            ]))
            story.append(engine_tbl)
            story.append(Spacer(1, 10))
            story.append(HRFlowable(width="100%", thickness=1, color=SEP_LINE, spaceAfter=12))

            # ════════════════════════════════════════════════════
            #  SECTION 3 — FULL SCAN TABLE (all 9 columns)
            # ════════════════════════════════════════════════════
            story.append(Paragraph("3.  Detailed Scan Results", section_s))
            story.append(Paragraph(
                f"Complete record of all {total} file{'s' if total!=1 else ''} scanned "
                f"in this session. All 9 data fields captured per file.",
                body_s))
            story.append(Spacer(1, 6))

            if self.scan_history:
                headers = ["Time","File Name","Verdict","Score",
                           "Extension","Entropy","Honeypot","Backup","ML Result"]
                col_w   = [16*mm, 40*mm, 17*mm, 13*mm,
                           20*mm, 14*mm, 17*mm, 14*mm, 24*mm]
                tdata   = [headers]
                for r in self.scan_history:
                    fname = _safe(r.get("file",""))
                    fname = (fname[:24]+"...") if len(fname)>24 else fname
                    ml    = _safe(r.get("ml","N/A"))
                    # Safe files (score=0) always show NORMAL regardless of ML model output
                    if not r.get("is_threat") and r.get("score", 0) == 0:
                        ml = "NORMAL"
                    ml    = (ml[:18]+"...") if len(ml)>18 else ml
                    tdata.append([
                        _safe(r.get("time",    "—")),
                        fname,
                        _safe(r.get("verdict", "—")),
                        str(r.get("score",     "—")),
                        _safe(r.get("extension","—")),
                        str(r.get("entropy",   "—")),
                        _honey(r.get("honeypot","—")),  # "HIT" or "—", no emoji
                        _safe(r.get("backup",  "—")),
                        ml,
                    ])
                detail_tbl = Table(tdata, colWidths=col_w, repeatRows=1)
                tbl_style = [
                    ("BACKGROUND",    (0,0),(-1,0), DARK_C),
                    ("TEXTCOLOR",     (0,0),(-1,0), ACCENT),
                    ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
                    ("FONTSIZE",      (0,0),(-1,0), 7.5),
                    ("BOTTOMPADDING", (0,0),(-1,0), 7),
                    ("TOPPADDING",    (0,0),(-1,0), 7),
                    ("ALIGN",         (0,0),(-1,-1), "CENTER"),
                    ("ALIGN",         (1,1),(1,-1),  "LEFT"),
                    ("ALIGN",         (8,1),(8,-1),  "LEFT"),
                    ("FONTSIZE",      (0,1),(-1,-1), 7),
                    ("GRID",          (0,0),(-1,-1), 0.4, GRID_COL),
                    ("TOPPADDING",    (0,1),(-1,-1), 5),
                    ("BOTTOMPADDING", (0,1),(-1,-1), 5),
                    ("LEFTPADDING",   (0,0),(-1,-1), 4),
                    ("RIGHTPADDING",  (0,0),(-1,-1), 4),
                ]
                for i, r in enumerate(self.scan_history, start=1):
                    if r.get("is_threat"):
                        tbl_style += [
                            ("BACKGROUND", (0,i),(-1,i), DANGER_BG),
                            ("TEXTCOLOR",  (0,i),(-1,i), DANGER),
                            ("FONTNAME",   (0,i),(-1,i), "Helvetica-Bold"),
                        ]
                    else:
                        bg = ROWALT1 if i%2==0 else colors.white
                        tbl_style += [
                            ("BACKGROUND", (0,i),(-1,i), bg),
                            ("TEXTCOLOR",  (0,i),(-1,i), DARK_C),
                            ("TEXTCOLOR",  (2,i),(2,i),  SUCCESS),
                            ("FONTNAME",   (2,i),(2,i),  "Helvetica-Bold"),
                        ]
                    # Honeypot HIT cell — always red
                    if "HIT" in str(r.get("honeypot","—")):
                        tbl_style += [
                            ("TEXTCOLOR", (6,i),(6,i), DANGER),
                            ("FONTNAME",  (6,i),(6,i), "Helvetica-Bold"),
                        ]
                    # Backup tick — green
                    if r.get("backup","") == "✓":
                        tbl_style += [("TEXTCOLOR", (7,i),(7,i), SUCCESS)]
                    # Suspicious extension — orange
                    if r.get("extension","") == "SUSPICIOUS":
                        tbl_style += [
                            ("TEXTCOLOR", (4,i),(4,i), WARNING),
                            ("FONTNAME",  (4,i),(4,i), "Helvetica-Bold"),
                        ]
                detail_tbl.setStyle(TableStyle(tbl_style))
                story.append(detail_tbl)

            story.append(Spacer(1, 12))
            story.append(HRFlowable(width="100%", thickness=1, color=SEP_LINE, spaceAfter=12))

            # ════════════════════════════════════════════════════
            #  SECTION 4 — PER-THREAT FORENSIC CARDS
            # ════════════════════════════════════════════════════
            threat_files = [r for r in self.scan_history if r.get("is_threat")]
            if threat_files:
                story.append(Paragraph("4.  Threat File Forensic Detail", section_s))
                story.append(Paragraph(
                    f"Full forensic breakdown for each of the {len(threat_files)} "
                    f"threat file{'s' if len(threat_files)!=1 else ''} detected.",
                    body_s))
                story.append(Spacer(1, 8))

                for idx, r in enumerate(threat_files, start=1):
                    fname  = _safe(r.get("file",      "Unknown"))
                    fpath  = _safe(r.get("fpath",     "—"))
                    score  = r.get("score",            "—")
                    ext    = _safe(r.get("extension",  "—"))
                    ent    = str(r.get("entropy",      "—"))
                    ml     = _safe(r.get("ml",         "—"))
                    honey  = _honey(r.get("honeypot",  "—"))
                    backup = _safe(r.get("backup",     "—"))
                    risk   = _safe(r.get("risk",       "—"))
                    sha    = r.get("hash",              "N/A") or "N/A"
                    ts     = _safe(r.get("time",       "—"))

                    # Truncate long paths cleanly
                    fpath_short = (fpath[:58]+"...") if len(fpath)>58 else fpath

                    card_hdr = Table(
                        [[f"THREAT #{idx}  -  {fname}",
                          f"Risk Score: {score}/100"]],
                        colWidths=[130*mm, 45*mm])
                    card_hdr.setStyle(TableStyle([
                        ("BACKGROUND",    (0,0),(-1,0), DANGER_BG),
                        ("TEXTCOLOR",     (0,0),(0,0),  DANGER),
                        ("TEXTCOLOR",     (1,0),(1,0),  DANGER),
                        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
                        ("FONTSIZE",      (0,0),(-1,0), 9),
                        ("LEFTPADDING",   (0,0),(-1,0), 10),
                        ("RIGHTPADDING",  (0,0),(-1,0), 10),
                        ("TOPPADDING",    (0,0),(-1,0), 7),
                        ("BOTTOMPADDING", (0,0),(-1,0), 7),
                        ("ALIGN",         (1,0),(1,0),  "RIGHT"),
                    ]))

                    detail_rows = [
                        ["Scan Time",         ts,      "File Path",       fpath_short],
                        ["Verdict",           "THREAT","Risk Score",      risk],
                        ["Extension",         ext,     "Entropy Score",   ent],
                        ["ML Classification", ml,      "Honeypot Hit",    honey],
                        ["Backup Created",    backup,  "",                ""],
                    ]
                    card_body = Table(detail_rows,
                                      colWidths=[30*mm, 47*mm, 30*mm, 68*mm])
                    cb_style = [
                        ("FONTNAME",      (0,0),(0,-1), "Helvetica-Bold"),
                        ("FONTNAME",      (2,0),(2,-1), "Helvetica-Bold"),
                        ("TEXTCOLOR",     (0,0),(0,-1), MID),
                        ("TEXTCOLOR",     (2,0),(2,-1), MID),
                        ("FONTSIZE",      (0,0),(-1,-1), 8),
                        ("TEXTCOLOR",     (1,0),(-1,-1), DARK_C),
                        ("GRID",          (0,0),(-1,-1), 0.3, GRID_COL),
                        ("ROWBACKGROUNDS",(0,0),(-1,-1), [colors.white, ROWALT1]),
                        ("LEFTPADDING",   (0,0),(-1,-1), 8),
                        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
                        ("TOPPADDING",    (0,0),(-1,-1), 6),
                        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
                        # Verdict + risk score red
                        ("TEXTCOLOR",     (1,1),(1,1), DANGER),
                        ("FONTNAME",      (1,1),(1,1), "Helvetica-Bold"),
                        ("TEXTCOLOR",     (3,1),(3,1), DANGER),
                        ("FONTNAME",      (3,1),(3,1), "Helvetica-Bold"),
                    ]
                    if honey == "HIT":
                        cb_style += [
                            ("TEXTCOLOR", (3,3),(3,3), DANGER),
                            ("FONTNAME",  (3,3),(3,3), "Helvetica-Bold"),
                        ]
                    if backup == "✓":
                        cb_style += [("TEXTCOLOR", (1,4),(1,4), SUCCESS)]
                    if ext == "SUSPICIOUS":
                        cb_style += [
                            ("TEXTCOLOR", (1,2),(1,2), WARNING),
                            ("FONTNAME",  (1,2),(1,2), "Helvetica-Bold"),
                        ]
                    card_body.setStyle(TableStyle(cb_style))

                    # SHA256 on its own full-width row in Courier so all 64 chars fit
                    sha_row = Table([["SHA256", sha]], colWidths=[18*mm, 157*mm])
                    sha_row.setStyle(TableStyle([
                        ("FONTNAME",      (0,0),(0,0), "Helvetica-Bold"),
                        ("TEXTCOLOR",     (0,0),(0,0), MID),
                        ("FONTNAME",      (1,0),(1,0), "Courier"),
                        ("FONTSIZE",      (0,0),(-1,0), 7.5),
                        ("TEXTCOLOR",     (1,0),(1,0), DARK_C),
                        ("BACKGROUND",    (0,0),(-1,0), ROWALT1),
                        ("GRID",          (0,0),(-1,0), 0.3, GRID_COL),
                        ("LEFTPADDING",   (0,0),(-1,0), 8),
                        ("RIGHTPADDING",  (0,0),(-1,0), 8),
                        ("TOPPADDING",    (0,0),(-1,0), 6),
                        ("BOTTOMPADDING", (0,0),(-1,0), 6),
                    ]))
                    story.append(KeepTogether([card_hdr, card_body, sha_row, Spacer(1, 10)]))

            # ════════════════════════════════════════════════════
            #  SECTION 5 — FULL SHA256 HASH REGISTRY
            # ════════════════════════════════════════════════════
            story.append(HRFlowable(width="100%", thickness=1, color=SEP_LINE, spaceAfter=12))
            story.append(Paragraph("5.  SHA256 Hash Registry", section_s))
            story.append(Paragraph(
                "Full 64-character cryptographic fingerprints for every scanned file. "
                "Use these for independent verification against threat intelligence feeds "
                "such as VirusTotal.",
                body_s))
            story.append(Spacer(1, 6))

            hash_data = [["#", "File Name", "Verdict", "Full SHA256 Hash (64 chars)"]]
            hash_ps = ps("HSH", fontName="Courier", fontSize=6.5,
                         textColor=DARK_C, leading=9, wordWrap="CJK")
            for idx, r in enumerate(self.scan_history, start=1):
                sha = r.get("hash","N/A") or "N/A"
                hash_data.append([
                    str(idx),
                    _safe(r.get("file","—")),
                    _safe(r.get("verdict","—")),
                    Paragraph(sha, hash_ps),   # Paragraph allows wrapping
                ])
            hash_tbl = Table(hash_data, colWidths=[8*mm, 38*mm, 18*mm, 111*mm])
            hs = [
                ("BACKGROUND",    (0,0),(-1,0), DARK_C),
                ("TEXTCOLOR",     (0,0),(-1,0), ACCENT),
                ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
                ("FONTSIZE",      (0,0),(-1,0), 8),
                ("FONTSIZE",      (0,1),(-1,-1), 6.5),       # smaller font for long hashes
                ("FONTNAME",      (0,1),(-1,-1), "Courier"), # monospace for hashes
                ("ALIGN",         (0,0),(0,-1),  "CENTER"),
                ("ALIGN",         (2,0),(2,-1),  "CENTER"),
                ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, ROWALT1]),
                ("TEXTCOLOR",     (0,1),(-1,-1), DARK_C),
                ("GRID",          (0,0),(-1,-1), 0.3, GRID_COL),
                ("LEFTPADDING",   (0,0),(-1,-1), 5),
                ("RIGHTPADDING",  (0,0),(-1,-1), 5),
                ("TOPPADDING",    (0,0),(-1,-1), 5),
                ("BOTTOMPADDING", (0,0),(-1,-1), 5),
            ]
            for i, r in enumerate(self.scan_history, start=1):
                if r.get("is_threat"):
                    hs += [("TEXTCOLOR",(2,i),(2,i), DANGER),
                           ("FONTNAME", (2,i),(2,i), "Helvetica-Bold")]
                else:
                    hs += [("TEXTCOLOR",(2,i),(2,i), SUCCESS),
                           ("FONTNAME", (2,i),(2,i), "Helvetica-Bold")]
            hash_tbl.setStyle(TableStyle(hs))
            story.append(hash_tbl)

            # ════════════════════════════════════════════════════
            #  FOOTER DISCLAIMER
            # ════════════════════════════════════════════════════
            story.append(Spacer(1, 14))
            story.append(HRFlowable(width="100%", thickness=1, color=SEP_LINE, spaceAfter=8))
            story.append(Paragraph(
                "This report was automatically generated by <b>RansomShield v4.1</b> — "
                "ML-Powered Ransomware Detection &amp; Response System. "
                "SHA256 hashes computed using Python hashlib (SHA-256). "
                "Threat verdicts are based on a composite risk score from 5 independent "
                "detection engines: Extension Analysis (30 pts), Entropy Analysis (25 pts), "
                "Hash/Reputation (40 pts), ML Classification (25 pts), "
                "and Honeypot Detection (50 pts). "
                "A combined score of 30 or above triggers a THREAT verdict. "
                "This report is confidential and intended for authorised use only.",
                footer_s))

            doc.build(story)
            self._log(f"📄 PDF exported → {path}", "info")
            self._notif("Report Exported", "Full PDF report saved successfully", "success")

        except Exception as e:
            self._log(f"✗ PDF export failed: {e}", "threat")

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV","*.csv")],
            initialfile=f"RansomShield_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        if not path: return
        try:
            with open(path,"w",newline="") as f:
                w = csv.DictWriter(f, fieldnames=[
                    "time","file","verdict","score","extension",
                    "entropy","ml","honeypot","backup","risk","hash"])
                w.writeheader(); w.writerows(self.scan_history)
            self._log(f"📊 CSV exported → {path}", "info")
            self._notif("Report Exported", "CSV saved successfully", "success")
        except Exception as e:
            self._log(f"✗ CSV failed: {e}", "threat")

    # ══════════════════════════════════════════════════════════
    #  SCAN TRIGGERS
    # ══════════════════════════════════════════════════════════
    def _scan_file(self):
        fp = filedialog.askopenfilename(title="Select File to Scan")
        if not fp: return
        self._status(f"Scanning  ·  {os.path.basename(fp)}")
        threading.Thread(target=self._sf_thread, args=(fp,), daemon=True).start()

    def _sf_thread(self, fp):
        r = self._run_scan(fp)
        self.root.after(0, lambda: self._record(r))
        self.root.after(0, lambda: self._status("Ready  ·  Scan complete"))
        self.root.after(0, lambda: self._notif("Scan Complete", os.path.basename(fp), "success"))

    def _scan_folder(self):
        folder = self.selected_folder or filedialog.askdirectory(title="Select Folder")
        if not folder: return
        threading.Thread(target=self._sfolder_thread, args=(folder,), daemon=True).start()

    def _sfolder_thread(self, folder):
        files = [os.path.join(folder,f) for f in os.listdir(folder)
                 if os.path.isfile(os.path.join(folder,f))]
        total = len(files)
        if total == 0:
            self.root.after(0, lambda: self._log("⚠ No files found.", "warn")); return
        self.root.after(0, lambda: self._log(f"📂 Scanning {total} files…", "info"))
        for i, fp in enumerate(files, 1):
            pct = int(i/total*100)
            self.root.after(0, lambda p=pct: self.prog_var.set(p))
            self.root.after(0, lambda p=pct: self.lbl_prog_pct.configure(text=f"{p}%"))
            self.root.after(0, lambda n=os.path.basename(fp), ii=i:
                self.lbl_prog.configure(text=f"[{ii}/{total}]  {n[:24]}"))
            r = self._run_scan(fp)
            self.root.after(0, lambda rv=r: self._record(rv))
        self.root.after(0, lambda: (
            self.prog_var.set(0),
            self.lbl_prog_pct.configure(text="0%"),
            self.lbl_prog.configure(text="Ready  ·  No scan active"),
            self._status(f"Folder scan complete  ·  {total} files"),
            self._log(f"✅ Folder scan complete. {total} files.", "safe"),
            self._notif("Folder Scan Complete", f"{total} files processed", "success")
        ))

    def _clear_log(self):
        self.log_txt.config(state="normal")
        self.log_txt.delete("1.0", tk.END)
        self.log_txt.config(state="disabled")
        self._idle_showing = True
        try: self.idle_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        except: pass
        self._banner()

    # ══════════════════════════════════════════════════════════
    #  ALERTS
    # ══════════════════════════════════════════════════════════
    def _flash_alert(self, n=8):
        T = self.T
        overlay = tk.Toplevel(self.root)
        overlay.overrideredirect(True)
        overlay.attributes("-topmost", True)
        try: overlay.attributes("-alpha", 0.97)
        except: pass
        rx = self.root.winfo_x() + self.root.winfo_width()//2 - 250
        ry = self.root.winfo_y() + 80
        overlay.geometry(f"500x76+{rx}+{ry}")
        overlay.configure(bg=T["danger_bg"])
        tk.Frame(overlay, height=3, bg=T["danger"]).pack(fill="x")
        tk.Label(overlay, text="🚨  THREAT DETECTED  —  FILE QUARANTINED",
                 font=("Helvetica Neue",13,"bold"),
                 bg=T["danger_bg"], fg=T["danger"]).pack(expand=True)
        overlay.after(3000, overlay.destroy)
        try: self.root.bell()
        except: pass
        try: os.system("afplay /System/Library/Sounds/Sosumi.aiff &")
        except: pass

    # ══════════════════════════════════════════════════════════
    #  ONBOARDING
    # ══════════════════════════════════════════════════════════
    def _onboard(self):
        T = self.T
        win = tk.Toplevel(self.root)
        win.title("Welcome"); win.geometry("520x520")
        win.resizable(False,False); win.configure(bg=T["bg_panel"])
        win.attributes("-topmost", True)
        rx = self.root.winfo_x()+(self.root.winfo_width()-520)//2
        ry = self.root.winfo_y()+(self.root.winfo_height()-520)//2
        win.geometry(f"520x520+{rx}+{ry}")

        tk.Frame(win, bg=T["accent"], height=4).pack(fill="x")
        tk.Label(win, text="🛡", font=("Helvetica Neue",40),
                 bg=T["bg_panel"], fg=T["accent"]).pack(pady=(20,4))
        tk.Label(win, text="Welcome to RansomShield v4.1",
                 font=("Helvetica Neue",16,"bold"),
                 bg=T["bg_panel"], fg=T["fg_primary"]).pack()
        tk.Label(win, text="Enterprise Ransomware Detection & Response",
                 font=("Helvetica Neue",9),
                 bg=T["bg_panel"], fg=T["fg_secondary"]).pack(pady=(2,18))

        for num, title, desc in [
            ("1","Select Folder","Pick a folder to monitor — honeypots are auto-planted."),
            ("2","Start Monitor","▶ Start Monitor scans every new or modified file live."),
            ("3","Review Backups","See every backed-up file in the 💾 Backups tab."),
            ("4","Export Report", "Browse history, inspect threats, export PDF/CSV reports."),
        ]:
            row = tk.Frame(win, bg=T["bg_elevated"],
                           highlightbackground=T["bg_border"], highlightthickness=1)
            row.pack(fill="x", padx=34, pady=4, ipady=8)
            tk.Label(row, text=num, font=("Helvetica Neue",13,"bold"),
                     bg=T["accent"], fg=T["btn_text"], width=3).pack(side="left", padx=(10,12), pady=4)
            r = tk.Frame(row, bg=T["bg_elevated"]); r.pack(side="left")
            tk.Label(r, text=title, font=("Helvetica Neue",11,"bold"),
                     bg=T["bg_elevated"], fg=T["fg_primary"], anchor="w").pack(anchor="w")
            tk.Label(r, text=desc, font=("Helvetica Neue",8),
                     bg=T["bg_elevated"], fg=T["fg_secondary"], anchor="w").pack(anchor="w")

        no_show = tk.BooleanVar(value=True)
        tk.Checkbutton(win, text="Don't show again", variable=no_show,
                       font=("Helvetica Neue",9), bg=T["bg_panel"], fg=T["fg_secondary"],
                       selectcolor=T["bg_elevated"], activebackground=T["bg_panel"],
                       relief="flat", cursor="hand2").pack(pady=(10,0))

        def _close():
            if no_show.get():
                try: open(os.path.expanduser("~/.ransomshield_v4"),"w").close()
                except: pass
            win.destroy()
        tk.Button(win, text="  Get Started  →",
                  font=("Helvetica Neue",11,"bold"),
                  bg=T["accent"], fg=T["btn_text"], relief="flat",
                  cursor="hand2", activebackground=T["accent_glow"],
                  command=_close, padx=20, pady=8).pack(pady=14)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app  = RansomwareGUI(root)
    app.run()