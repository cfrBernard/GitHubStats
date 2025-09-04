# gui/app.py
import datetime
import webbrowser
from io import BytesIO

import customtkinter as ctk
import requests
from PIL import Image, ImageTk

from GitHubStats.core.config import load_config
from GitHubStats.core.github_api import GitHubClient
from GitHubStats.core.utils import start_auto_refresh


class GitHubStatsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GitHub Stats")
        self.geometry("600x230")
        self.resizable(False, False)

        # config
        cfg = load_config()
        self.username = cfg["GITHUB_USERNAME"]
        self.client = GitHubClient(cfg["GITHUB_TOKEN"], self.username)

        # === Layout principal : 2 colonnes ===
        self.grid_columnconfigure(0, weight=0)  # sidebar
        self.grid_columnconfigure(1, weight=1)  # main content
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)  # request stats

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=220)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nswe", padx=(10, 0), pady=10)
        self.sidebar.grid_propagate(False)

        # Bloc haut : 2 colonnes
        self.sidebar.grid_columnconfigure(0, weight=0)  # col gauche
        self.sidebar.grid_columnconfigure(1, weight=1)  # col droite

        # Colonne gauche : avatar + bouton Visit
        url = f"https://github.com/{self.username}.png"
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        self.avatar_image = ImageTk.PhotoImage(img)

        self.label_avatar = ctk.CTkLabel(self.sidebar, image=None, text="")
        self.label_avatar.grid(row=0, column=0, pady=(10, 5), padx=(0, 85), sticky="n")

        self.btn_visit = ctk.CTkButton(
            self.sidebar,
            text="Visit GitHub",
            width=100,
            command=lambda: webbrowser.open(f"https://github.com/{self.username}"),
        )
        self.btn_visit.grid(row=0, column=0, pady=(115, 5), padx=(0, 84), sticky="s")

        # Colonne droite : nom + bio
        self.label_name = ctk.CTkLabel(
            self.sidebar, text="", font=("Arial", 18, "bold"), anchor="w"
        )
        self.label_name.place(x=115, y=5)

        self.label_bio = ctk.CTkLabel(
            self.sidebar, text="", wraplength=100, anchor="w", justify="left"
        )
        self.label_bio.place(x=115, y=35)

        # Ligne suivante : on repasse en 1 colonne
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_columnconfigure(1, weight=1)

        # Bouton Refresh
        self.btn_refresh = ctk.CTkButton(self.sidebar, text="Refresh", command=self.refresh)
        self.btn_refresh.grid(row=2, column=0, columnspan=2, pady=(0, 0), padx=9, sticky="ew")

        # Checkbox Auto Refresh
        self.auto_update_var = ctk.BooleanVar()
        self.chk_auto_update = ctk.CTkCheckBox(
            self.sidebar,
            text="Auto Refresh",
            variable=self.auto_update_var,
            command=self.toggle_auto_refresh,
            checkbox_width=16,
            checkbox_height=16,
            font=("Arial", 12),
        )
        self.chk_auto_update.grid(row=3, column=0, columnspan=2, pady=5, padx=5, sticky="e")

        # --- Main Stats ---
        self.main_stats = ctk.CTkFrame(self)
        self.main_stats.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.stats_labels = {}

        positions = {
            "Followers": (0, 0),
            "Following": (1, 0),
            "Stars": (0, 1),
            "Forks": (1, 1),
            "Public Repos": (0, 2),
            "Private Repos": (1, 2),
            "Public Gists": (0, 3),
            "Private Gists": (1, 3),
        }

        for field, (r, c) in positions.items():
            frame = ctk.CTkFrame(self.main_stats)
            frame.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

            lbl = ctk.CTkLabel(frame, text=f"{field}")
            lbl.pack(anchor="center", padx=9, pady=7)

            val = ctk.CTkLabel(frame, text="0", font=("TkDefaultFont", 14, "bold"))
            val.pack(anchor="center")

            self.stats_labels[field.lower()] = val

        # --- Request Stats ---
        self.request_stats = ctk.CTkFrame(self, height=40)
        self.request_stats.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 10))
        self.request_stats.grid_propagate(False)

        self.label_rate = ctk.CTkLabel(self.request_stats, text="")
        self.label_rate.pack(pady=5)

        # Initial refresh
        self.refresh()

    def toggle_auto_refresh(self):
        if self.auto_update_var.get():
            start_auto_refresh(self.refresh)

    def truncate(self, text, max_len=100):
        return text if not text or len(text) <= max_len else text[:max_len] + "..."

    def load_avatar(self, url, size=(100, 100)):
        try:
            response = requests.get(url)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        except Exception as e:
            print("Erreur chargement avatar:", e)
            return None

    def refresh(self):
        rate = self.client.rate_limit()
        stats = self.client.user_overview()

        # Avatar
        avatar_img = self.load_avatar(stats["avatar_url"], size=(100, 100))
        if avatar_img:
            self.label_avatar.configure(image=avatar_img)
            self.label_avatar.image = avatar_img

        # Name & Bio
        self.label_name.configure(text=self.truncate(stats["name"], 10))
        self.label_bio.configure(text=self.truncate(stats["bio"], 100))

        # Stats
        for key in self.stats_labels:
            self.stats_labels[key].configure(text=str(stats.get(key, 0)))

        # Rate limit
        reset_time = datetime.datetime.fromtimestamp(rate["reset"])
        reset_str = reset_time.strftime("%H:%M:%S")
        self.label_rate.configure(
            text=f"Requests left: {rate['remaining']} / {rate['limit']} | Reset at {reset_str}"
        )
