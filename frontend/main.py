import tkinter as tk
from tkinter import ttk
import requests

class PipimApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("pipim")
        self.geometry("600x400")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.view_packages_frame = ttk.Frame(notebook)
        self.install_package_frame = ttk.Frame(notebook)

        notebook.add(self.view_packages_frame, text="View Installed Packages")
        notebook.add(self.install_package_frame, text="Install Package")

        self.create_view_packages_ui(self.view_packages_frame)
        self.create_install_package_ui(self.install_package_frame)

        install_python_button = ttk.Button(
            self,
            text="Install Python",
            command=self.open_install_python_popup
        )
        install_python_button.pack(pady=10)

    def create_view_packages_ui(self, parent):
        title_label = tk.Label(parent, text="View Installed Packages", font=("Arial", 16))
        title_label.pack(pady=10)

        for pkg in requests.get("http://127.0.0.1:5000/get_modules").json():
            pkg_name = pkg["name"]
            pkg_version = pkg["version"]
            pkg = f"{pkg_name}\t{pkg_version}"
            pkg_frame = ttk.Frame(parent)
            pkg_frame.pack(fill="x", pady=5, padx=20)

            pkg_label = tk.Label(pkg_frame, text=pkg, font=("Arial", 12))
            pkg_label.pack(side="left")

            remove_button = ttk.Button(pkg_frame, text="Remove")
            remove_button.pack(side="right")

    def create_install_package_ui(self, parent):
        title_label = tk.Label(parent, text="Install Package", font=("Arial", 16))
        title_label.pack(pady=10)

        package_label = tk.Label(parent, text="Package Name:")
        package_label.pack(pady=5)

        package_entry = ttk.Entry(parent)
        package_entry.pack(pady=5)

        install_button = ttk.Button(parent, text="Install")
        install_button.pack(pady=10)

    def open_install_python_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Install Python")
        popup.geometry("300x150")

        label = tk.Label(popup, text="Install Python", font=("Arial", 14))
        label.pack(pady=20)

        close_button = ttk.Button(popup, text="Close", command=popup.destroy)
        close_button.pack(pady=10)


if __name__ == "__main__":
    app = PipimApp()
    app.mainloop()