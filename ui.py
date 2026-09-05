"""Francabel desktop window. Dark desk, no social login passwords."""

from __future__ import annotations

import os
import webbrowser
from tkinter import (
    BOTH,
    END,
    LEFT,
    RIGHT,
    WORD,
    BooleanVar,
    StringVar,
    Tk,
    Toplevel,
    filedialog,
    messagebox,
    ttk,
)
from tkinter import Text
from tkinter import Canvas
import tkinter as tk

from desk import (
    COMPOSE_URLS,
    FORMAT_SPECS,
    PLATFORMS,
    compose_from_template,
    export_post,
    import_pack_file,
    latest_pack,
    load_queue,
    run_desk,
    save_post,
    set_status,
)
from publish import publish_facebook_page, publish_linkedin
from shop import HONESTY_LOCK, all_services, load_shop, save_shop
from visuals import load_thumbnail

BG = "#ffffff"
PANEL = "#f3f3f3"
INK = "#111111"
MUTED = "#333333"
RUST = "#111111"
BRASS = "#111111"
LINE = "#d0d0d0"
BTN_FG = "#ffffff"


def start_gui() -> None:
    root = Tk()
    root.title("Francabel Enterprise")
    root.geometry("1100x720")
    root.minsize(900, 600)
    root.configure(bg=BG)
    _style(root)
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")
    try:
        icon = tk.PhotoImage(file=icon_path)
        root.iconphoto(True, icon)
        root._icon = icon
    except Exception:
        pass
    App(root)
    root.mainloop()


def _style(root: Tk) -> None:
    s = ttk.Style(root)
    s.theme_use("clam")
    s.configure(".", background=BG, foreground=INK, fieldbackground=PANEL, bordercolor=LINE)
    s.configure("TFrame", background=BG)
    s.configure("Panel.TFrame", background=PANEL)
    s.configure("TLabel", background=BG, foreground=INK, font=("Georgia", 11))
    s.configure("Muted.TLabel", background=BG, foreground=MUTED, font=("Georgia", 10))
    s.configure("Title.TLabel", background=BG, foreground=BRASS, font=("Georgia", 18, "bold"))
    s.configure("Head.TLabel", background=BG, foreground=INK, font=("Georgia", 14, "bold"))
    s.configure("Panel.TLabel", background=PANEL, foreground=INK, font=("Georgia", 11))
    s.configure("TButton", background=RUST, foreground=BTN_FG, padding=8, font=("Georgia", 10))
    s.map("TButton", background=[("active", "#333333")], foreground=[("active", BTN_FG)])
    s.configure("Ghost.TButton", background=PANEL, foreground=INK, padding=8)
    s.configure("Nav.TButton", background=BG, foreground=MUTED, padding=10, font=("Georgia", 11))
    s.configure("NavOn.TButton", background=PANEL, foreground=BRASS, padding=10, font=("Georgia", 11, "bold"))
    s.configure("TNotebook", background=BG, borderwidth=0)
    s.configure("TNotebook.Tab", background=PANEL, foreground=MUTED, padding=(12, 6))
    s.map("TNotebook.Tab", background=[("selected", "#111111")], foreground=[("selected", "#ffffff")])
    s.configure("TEntry", fieldbackground="#ffffff", foreground=INK, insertcolor=INK)
    s.configure("TCombobox", fieldbackground=PANEL, foreground=INK, background=PANEL)


class App:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.page = StringVar(value="desk")
        self._thumbs: list = []
        shell = ttk.Frame(root)
        shell.pack(fill=BOTH, expand=True)
        nav = ttk.Frame(shell, width=230)
        nav.pack(side=LEFT, fill="y")
        nav.pack_propagate(False)
        ttk.Label(nav, text="FRANCABEL", style="Title.TLabel").pack(padx=16, pady=(24, 0), anchor="w")
        ttk.Label(nav, text="ENTERPRISE", style="Muted.TLabel").pack(padx=16, pady=(0, 4), anchor="w")
        ttk.Label(nav, text="Overnight desk", style="Muted.TLabel").pack(padx=16, pady=(0, 20), anchor="w")
        self.nav_btns = {}
        for key, label in (("desk", "Desk"), ("studio", "Studio"), ("shop", "Shop"), ("about", "About")):
            b = ttk.Button(nav, text=label, style="Nav.TButton", command=lambda k=key: self.show(k))
            b.pack(fill="x", padx=12, pady=2)
            self.nav_btns[key] = b
        ttk.Label(nav, text=HONESTY_LOCK, style="Muted.TLabel", wraplength=198).pack(
            side="bottom", padx=16, pady=16, anchor="w"
        )
        self.body = ttk.Frame(shell)
        self.body.pack(side=LEFT, fill=BOTH, expand=True)
        self.frames = {name: ttk.Frame(self.body) for name in ("desk", "studio", "shop", "about")}
        self._build_desk()
        self._build_studio()
        self._build_shop()
        self._build_about()
        self.show("desk")

    def show(self, name: str) -> None:
        self.page.set(name)
        for key, fr in self.frames.items():
            fr.pack_forget()
        self.frames[name].pack(fill=BOTH, expand=True)
        for key, b in self.nav_btns.items():
            b.configure(style="NavOn.TButton" if key == name else "Nav.TButton")
        if name == "desk":
            self.refresh_desk()
        if name == "studio":
            self.refresh_studio()
        if name == "shop":
            self.refresh_shop()

    def _clear(self, frame: ttk.Frame) -> None:
        for child in frame.winfo_children():
            child.destroy()

    def _build_desk(self) -> None:
        f = self.frames["desk"]
        top = ttk.Frame(f)
        top.pack(fill="x", padx=24, pady=20)
        ttk.Label(top, text="Desk", style="Title.TLabel").pack(side=LEFT)
        ttk.Button(top, text="Run desk", command=self.on_run_desk).pack(side=RIGHT, padx=6)
        self.story = ttk.Label(f, text="", style="Muted.TLabel", wraplength=820, justify=LEFT)
        self.story.pack(fill="x", padx=24, pady=(0, 12))
        self.queue_host = ttk.Frame(f)
        self.queue_host.pack(fill=BOTH, expand=True, padx=24, pady=(0, 24))

    def refresh_desk(self) -> None:
        pack = latest_pack()
        story = (pack or {}).get("story_of_the_day") or "No pack yet. Run the desk."
        self.story.configure(text=story)
        for child in self.queue_host.winfo_children():
            child.destroy()
        self._thumbs = []
        canvas = Canvas(self.queue_host, bg=BG, highlightthickness=0)
        scroll = ttk.Scrollbar(self.queue_host, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scroll.pack(side=RIGHT, fill="y")
        queue = list(reversed(load_queue()))
        if not queue:
            ttk.Label(inner, text="Queue is empty.", style="Muted.TLabel").pack(anchor="w")
            return
        for post in queue:
            self._post_card(inner, post)

    def _post_card(self, parent: ttk.Frame, post: dict) -> None:
        card = tk.Frame(parent, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
        card.pack(fill="x", pady=6)
        thumb = load_thumbnail(tk, post.get("visual") or "", 96)
        if thumb:
            self._thumbs.append(thumb)
            lbl = tk.Label(card, image=thumb, bg=PANEL)
            lbl.pack(side=LEFT, padx=10, pady=10)
        info = tk.Frame(card, bg=PANEL)
        info.pack(side=LEFT, fill="x", expand=True, padx=8, pady=10)
        title = f"{post.get('service') or 'Post'}  ·  {post.get('ratio') or post.get('format') or '1:1'}  ·  {post.get('status') or 'queued'}"
        tk.Label(info, text=title, bg=PANEL, fg=BRASS, font=("Georgia", 12, "bold"), anchor="w").pack(fill="x")
        tk.Label(
            info,
            text=post.get("hook") or "",
            bg=PANEL,
            fg=INK,
            wraplength=640,
            justify=LEFT,
            anchor="w",
            font=("Georgia", 11),
        ).pack(fill="x")
        ttk.Button(card, text="Open", command=lambda p=post: self.open_post(p)).pack(side=RIGHT, padx=12, pady=12)

    def on_run_desk(self) -> None:
        path = run_desk()
        messagebox.showinfo("Francabel", f"Pack written.\n{path}")
        self.refresh_desk()

    def open_post(self, post: dict) -> None:
        win = Toplevel(self.root)
        win.title(post.get("service") or "Post")
        win.configure(bg=BG)
        win.geometry("760x640")
        ttk.Label(win, text=post.get("service") or "Post", style="Head.TLabel").pack(anchor="w", padx=16, pady=(16, 4))
        ttk.Label(win, text=post.get("hook") or "", style="Muted.TLabel", wraplength=700).pack(anchor="w", padx=16)
        nb = ttk.Notebook(win)
        nb.pack(fill=BOTH, expand=True, padx=16, pady=12)
        texts = {}
        captions = dict(post.get("captions") or {})
        for plat in PLATFORMS:
            tab = ttk.Frame(nb)
            nb.add(tab, text="X" if plat == "x" else plat.title())
            box = Text(tab, wrap=WORD, bg=PANEL, fg=INK, insertbackground=INK, relief="flat", font=("Georgia", 11), height=10)
            box.insert("1.0", captions.get(plat) or "")
            box.pack(fill=BOTH, expand=True, padx=8, pady=8)
            texts[plat] = box
        shots = post.get("shot_list") or {}
        shot_txt = "\n".join(shots.get("shots") or [])
        shot_txt += f"\nOn-screen: {shots.get('on_screen_question') or ''}\nVoice: {shots.get('voice_line') or ''}"
        ttk.Label(win, text=shot_txt, style="Muted.TLabel", wraplength=700, justify=LEFT).pack(anchor="w", padx=16)

        def current_caption() -> str:
            plat = PLATFORMS[nb.index("current")]
            return texts[plat].get("1.0", END).strip()

        def save_caps() -> None:
            for plat, box in texts.items():
                captions[plat] = box.get("1.0", END).strip()
            post["captions"] = captions
            save_post(post)

        def copy_cap() -> None:
            save_caps()
            self.root.clipboard_clear()
            self.root.clipboard_append(current_caption())
            messagebox.showinfo("Francabel", "Caption copied.")

        def open_app() -> None:
            plat = PLATFORMS[nb.index("current")]
            webbrowser.open(COMPOSE_URLS[plat])

        def do_export() -> None:
            save_caps()
            folder = export_post(post)
            set_status(post["id"], "exported")
            post["status"] = "exported"
            messagebox.showinfo("Francabel", f"Exported to\n{folder}")
            self.refresh_desk()

        def mark_posted() -> None:
            set_status(post["id"], "posted")
            post["status"] = "posted"
            messagebox.showinfo("Francabel", "Marked posted. Instagram and TikTok still need the tap in their own app.")
            self.refresh_desk()

        def fb_publish() -> None:
            save_caps()
            shop = load_shop()
            ok, msg = publish_facebook_page(shop.get("facebook_page_token") or "", captions.get("facebook") or "")
            messagebox.showinfo("Facebook Page", msg)
            if ok:
                set_status(post["id"], "posted")
                self.refresh_desk()

        def li_publish() -> None:
            save_caps()
            shop = load_shop()
            ok, msg = publish_linkedin(shop.get("linkedin_token") or "", captions.get("linkedin") or "")
            messagebox.showinfo("LinkedIn", msg)
            if ok:
                set_status(post["id"], "posted")
                self.refresh_desk()

        bar = ttk.Frame(win)
        bar.pack(fill="x", padx=16, pady=(0, 16))
        ttk.Button(bar, text="Copy caption", command=copy_cap).pack(side=LEFT, padx=4)
        ttk.Button(bar, text="Open app", command=open_app).pack(side=LEFT, padx=4)
        ttk.Button(bar, text="Export", command=do_export).pack(side=LEFT, padx=4)
        ttk.Button(bar, text="Mark posted", command=mark_posted).pack(side=LEFT, padx=4)
        ttk.Button(bar, text="Publish to Page", command=fb_publish).pack(side=LEFT, padx=4)
        ttk.Button(bar, text="LinkedIn token post", command=li_publish).pack(side=LEFT, padx=4)

    def _build_studio(self) -> None:
        f = self.frames["studio"]
        ttk.Label(f, text="Studio", style="Title.TLabel").pack(anchor="w", padx=24, pady=(20, 8))
        how = (
            "You pick the service and the picture size. Then click Compose. "
            "I write the captions, the 12-second shot list, and attach the poster. "
            "The new post appears on Desk, ready to copy. This is not a fake customer interview."
        )
        ttk.Label(f, text=how, style="Muted.TLabel", wraplength=820, justify=LEFT).pack(anchor="w", padx=24, pady=(0, 12))
        spec = (
            "Still image: JPEG or PNG.\n"
            "1:1 square is 1080×1080 for feed posts.\n"
            "9:16 portrait is 1080×1920 for Stories, Reels, and TikTok.\n"
            "16:9 landscape is 1280×720 for YouTube, LinkedIn, and Facebook video stills."
        )
        ttk.Label(f, text=spec, style="Muted.TLabel", wraplength=820, justify=LEFT).pack(anchor="w", padx=24, pady=(0, 16))
        row = ttk.Frame(f)
        row.pack(anchor="w", padx=24, pady=4)
        ttk.Label(row, text="Service", width=12).pack(side=LEFT)
        self.studio_service = StringVar()
        self.studio_combo = ttk.Combobox(row, textvariable=self.studio_service, state="readonly", width=42)
        self.studio_combo.pack(side=LEFT)
        row2 = ttk.Frame(f)
        row2.pack(anchor="w", padx=24, pady=8)
        ttk.Label(row2, text="Picture size", width=12).pack(side=LEFT)
        self.studio_fmt = StringVar()
        labels = [FORMAT_SPECS[k]["label"] for k in ("square", "story", "landscape")]
        self.studio_fmt_combo = ttk.Combobox(row2, textvariable=self.studio_fmt, values=labels, state="readonly", width=72)
        self.studio_fmt_combo.pack(side=LEFT)
        self.studio_fmt.set(FORMAT_SPECS["square"]["label"])
        ttk.Button(f, text="Compose — I write it and put it on Desk", command=self.on_compose).pack(anchor="w", padx=24, pady=16)
        self.studio_status = ttk.Label(f, text="", style="Head.TLabel", wraplength=820)
        self.studio_status.pack(anchor="w", padx=24, pady=(0, 12))

    def refresh_studio(self) -> None:
        services = all_services()
        self.studio_combo["values"] = services
        if services and self.studio_service.get() not in services:
            self.studio_service.set(services[0])
        if not self.studio_fmt.get():
            self.studio_fmt.set(FORMAT_SPECS["square"]["label"])

    def on_compose(self) -> None:
        shop = load_shop()
        svc = self.studio_service.get().strip()
        if not svc:
            self.studio_status.configure(text="Pick a service first.")
            return
        self.studio_status.configure(text="Writing…")
        self.root.update_idletasks()
        try:
            post = compose_from_template(shop, svc, self.studio_fmt.get() or "square")
            from desk import add_to_queue
            add_to_queue(post)
        except Exception as exc:
            self.studio_status.configure(text=f"Compose failed: {exc}")
            return
        spec = post.get("format_label") or post.get("format")
        self.studio_status.configure(
            text=f"Added to Desk: {post.get('service')} · {spec}. Open Desk to copy the caption."
        )
        self.root.after(600, lambda: self.show("desk"))

    def _build_shop(self) -> None:
        f = self.frames["shop"]
        ttk.Label(f, text="Shop", style="Title.TLabel").pack(anchor="w", padx=24, pady=(20, 8))
        form = ttk.Frame(f)
        form.pack(fill="x", padx=24)
        self.shop_vars = {
            "name": StringVar(),
            "website": StringVar(),
            "cities": StringVar(),
            "desk_hour": StringVar(),
            "posts_per_night": StringVar(),
            "extra_services": StringVar(),
            "extra_platforms": StringVar(),
            "facebook_page_token": StringVar(),
            "linkedin_token": StringVar(),
        }
        labels = [
            ("name", "Shop name"),
            ("website", "Website"),
            ("cities", "Cities (comma separated)"),
            ("desk_hour", "Desk hour (3:00 = 3am Eastern overnight)"),
            ("posts_per_night", "Posts per night (1–3)"),
            ("extra_services", "Extra services"),
            ("extra_platforms", "Extra platforms"),
            ("facebook_page_token", "Facebook Page token (not your password)"),
            ("linkedin_token", "LinkedIn token (not your password)"),
        ]
        for key, label in labels:
            row = ttk.Frame(form)
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=label, width=42).pack(side=LEFT)
            ttk.Entry(row, textvariable=self.shop_vars[key], width=48, show="*" if "token" in key else "").pack(side=LEFT)
        ttk.Label(f, text=HONESTY_LOCK, style="Muted.TLabel", wraplength=800).pack(anchor="w", padx=24, pady=16)
        bar = ttk.Frame(f)
        bar.pack(anchor="w", padx=24, pady=8)
        ttk.Button(bar, text="Save shop", command=self.on_save_shop).pack(side=LEFT, padx=4)
        ttk.Button(bar, text="Import pack JSON", command=self.on_import).pack(side=LEFT, padx=4)
        ttk.Button(bar, text="Open LinkedIn token page", command=lambda: webbrowser.open("https://www.linkedin.com/developers/apps")).pack(side=LEFT, padx=4)
        ttk.Button(bar, text="Open Facebook token page", command=lambda: webbrowser.open("https://developers.facebook.com/tools/explorer/")).pack(side=LEFT, padx=4)

    def refresh_shop(self) -> None:
        shop = load_shop()
        self.shop_vars["name"].set(shop.get("name") or "Francabel")
        self.shop_vars["website"].set(shop.get("website") or "https://francabel.com")
        self.shop_vars["cities"].set(", ".join(shop.get("cities") or []))
        self.shop_vars["desk_hour"].set(shop.get("desk_hour") or "3:00")
        self.shop_vars["posts_per_night"].set(str(shop.get("posts_per_night") or 2))
        self.shop_vars["extra_services"].set(", ".join(shop.get("extra_services") or []))
        self.shop_vars["extra_platforms"].set(", ".join(shop.get("extra_platforms") or []))
        self.shop_vars["facebook_page_token"].set(shop.get("facebook_page_token") or "")
        self.shop_vars["linkedin_token"].set(shop.get("linkedin_token") or "")

    def on_save_shop(self) -> None:
        save_shop({k: v.get() for k, v in self.shop_vars.items()})
        messagebox.showinfo("Francabel", "Shop saved.")

    def on_import(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("All", "*.*")])
        if not path:
            return
        n, msg = import_pack_file(path)
        messagebox.showinfo("Francabel", msg)
        if n:
            self.show("desk")

    def _build_about(self) -> None:
        f = self.frames["about"]
        ttk.Label(f, text="About", style="Title.TLabel").pack(anchor="w", padx=24, pady=(20, 8))
        text = (
            "Francabel Enterprise overnight desk for francabel.com. "
            "At 3:00am Eastern I write the day's posts. You open Desk, copy, tap Post.\n\n"
            "Studio: you pick a service and a picture size. I compose. It lands on Desk.\n"
            "Run desk: I pick the mix for the night.\n\n"
            "Tokens in Shop are official Page / LinkedIn API keys, never Gmail or Facebook login passwords.\n"
            "Instagram and TikTok still post from their own apps or Meta Business Suite.\n"
            "https://business.facebook.com/latest/composer"
        )
        ttk.Label(f, text=text, style="Muted.TLabel", wraplength=800, justify=LEFT).pack(anchor="w", padx=24, pady=8)
