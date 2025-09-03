import customtkinter as ctk

class GitHubStatsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GitHub Stats")
        self.geometry("800x600")

        label = ctk.CTkLabel(self, text="Hello GitHub Stats 👋")
        label.pack(padx=20, pady=20)
