import tkinter as tk
from tkinter import ttk
import requests

class PipimApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("pipim")
        self.geometry("600x400")

        # Apply a consistent theme
        style = ttk.Style(self)
        style.theme_use("clam")  # Use a cross-platform theme like "clam"

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.view_packages_frame = ttk.Frame(notebook)
        self.install_package_frame = ttk.Frame(notebook)
        self.search_package_frame = ttk.Frame(notebook)

        notebook.add(self.view_packages_frame, text="View Installed Packages")
        notebook.add(self.install_package_frame, text="Install Package")
        notebook.add(self.search_package_frame, text="Search For Packages")

        self.create_view_packages_ui(self.view_packages_frame)
        self.create_install_package_ui(self.install_package_frame)
        self.create_search_package_ui(self.search_package_frame)

        install_python_button = ttk.Button(
            self,
            text="Install Python",
            command=self.open_install_python_popup
        )
        install_python_button.pack(pady=10)

    def create_view_packages_ui(self, parent):
        title_label = ttk.Label(parent, text="View Installed Packages", font=("Arial", 16))
        title_label.pack(pady=10)

        # Create a canvas and a scrollbar
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Configure the canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Enable scrolling with the trackpad or mouse wheel
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # For Linux
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # For Linux

        # Populate the scrollable frame with package information
        r = requests.get("http://127.0.0.1:5000/get_modules")
        if r.status_code == 200:
            data = r.json()
        else:
            pkg_frame = ttk.Frame(scrollable_frame)
            pkg_frame.pack(fill="x", pady=5, padx=20)
            pkg_label = ttk.Label(pkg_frame, text="No modules installed.", font=("Arial", 12))
            pkg_label.pack(side="left", padx=100)
            return

        for pkg in data:
            pkg_name = pkg["name"]
            pkg_version = pkg["version"]
            pkg_frame = ttk.Frame(scrollable_frame, width=canvas.winfo_width())
            pkg_frame.pack(fill="x", pady=5, padx=20)

            pkg_label = ttk.Label(pkg_frame, text=pkg_name, font=("Arial", 12))
            pkg_label.pack(side="left")

            pkg_version_label = ttk.Label(pkg_frame, text=f"Version: {pkg_version}", font=("Arial", 12))
            pkg_version_label.pack(side="left", padx=20, anchor="center")

            remove_button = ttk.Button(pkg_frame, text="Remove")
            remove_button.pack(side="right")

        # Adjust canvas and scrollbar spacing
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10))

    def create_install_package_ui(self, parent):
        title_label = ttk.Label(parent, text="Install Package", font=("Arial", 16))
        title_label.pack(pady=10)

        package_label = ttk.Label(parent, text="Package Name:")
        package_label.pack(pady=5)

        package_entry = ttk.Entry(parent)
        package_entry.pack(pady=5)

        install_button = ttk.Button(parent, text="Install")
        install_button.pack(pady=10)

    def create_search_package_ui(self, parent):
        title_label = ttk.Label(parent, text="Search For Package", font=("Arial", 16))
        title_label.pack(pady=10)

        package_label = ttk.Label(parent, text="Package Name:")
        package_label.pack(pady=5)

        package_entry = ttk.Entry(parent)
        package_entry.pack(pady=5)
        
        install_button = ttk.Button(parent, text="Install")
        install_button.pack(pady=10)


    def open_install_python_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Install Python")
        popup.geometry("300x150")

        label = ttk.Label(popup, text="Install Python", font=("Arial", 14))
        label.pack(pady=20)

        close_button = ttk.Button(popup, text="Close", command=popup.destroy)
        close_button.pack(pady=10)


if __name__ == "__main__":
    app = PipimApp()
    app.mainloop()