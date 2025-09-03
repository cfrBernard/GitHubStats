import customtkinter as ctk

from GitHubStats.gui.app import GitHubStatsApp


def main():
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    app = GitHubStatsApp()
    app.mainloop()


if __name__ == "__main__":
    main()
