import tkinter as tk
from tkinter import ttk
import requests

BACKEND_URL = 'http://127.0.0.1:5000/'

# Main application class
class PipimApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("pipim")  # Set the window title
        self.geometry("600x400")  # Set the window size

        # Apply a consistent theme
        style = ttk.Style(self)
        style.theme_use("clam")  # Use a cross-platform theme like "clam"

        # Create a notebook (tabbed interface)
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # Create frames for each tab
        self.view_packages_frame = ttk.Frame(notebook)
        self.install_package_frame = ttk.Frame(notebook)
        self.search_package_frame = ttk.Frame(notebook)

        # Add frames to the notebook
        notebook.add(self.view_packages_frame, text="View Installed Packages")
        notebook.add(self.install_package_frame, text="Install Package")
        notebook.add(self.search_package_frame, text="Search For Packages")

        # Initialize the UI for each tab
        self.create_view_packages_ui(self.view_packages_frame)
        self.create_install_package_ui(self.install_package_frame)
        self.create_search_package_ui(self.search_package_frame)

        # Add a button to install Python
        install_python_button = ttk.Button(
            self,
            text="Install Python",
            command=self.open_install_python_popup
        )
        install_python_button.pack(pady=10)

    # Create the UI for the "View Installed Packages" tab
    def create_view_packages_ui(self, parent):
        title_label = ttk.Label(parent, text="View Installed Packages", font=("Arial", 16))
        title_label.pack(pady=10)

        # Create a canvas and a scrollbar for scrolling
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Configure the canvas to update the scroll region
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Enable scrolling with the mouse wheel
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # For Linux
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # For Linux

        def refresh_packages():
            # Clear the current content in the scrollable frame
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            # Fetch installed packages from the server
            r = requests.get(BACKEND_URL + "get_modules")
            if r.status_code == 200:
                data = r.json()  # Parse the JSON response
            else:
                # Display a message if no modules are installed
                pkg_frame = ttk.Frame(scrollable_frame)
                pkg_frame.pack(fill="x", pady=5, padx=20)
                pkg_label = ttk.Label(pkg_frame, text="No modules installed.", font=("Arial", 12))
                pkg_label.pack(side="left", padx=100)
                return

            # Create a frame for each package
            for pkg in data:
                pkg_name = pkg["name"]
                pkg_version = pkg["version"]
                pkg_frame = ttk.Frame(scrollable_frame, width=canvas.winfo_width())
                pkg_frame.pack(fill="x", pady=5, padx=20)

                # Display package name and version
                pkg_label = ttk.Label(pkg_frame, text=pkg_name, font=("Arial", 12))
                pkg_label.pack(side="left")
                pkg_version_label = ttk.Label(pkg_frame, text=f"Version: {pkg_version}", font=("Arial", 12))
                pkg_version_label.pack(side="left", padx=40, anchor="center")

                # Add a "Remove" button for each package
                remove_button = ttk.Button(
                    pkg_frame,
                    text="Remove",
                    command=lambda name=pkg_name: remove_package(name)
                )
                remove_button.pack(side="right")

        def remove_package(name):
            # Send a request to remove the package
            r = requests.post(BACKEND_URL + "uninstall_package", json={"package_name": name})
            if r.status_code == 200:
                refresh_packages()  # Refresh the package list after removal

        # Initial load of packages
        refresh_packages()

        # Adjust canvas and scrollbar spacing
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10))

    # Create the UI for the "Install Package" tab
    def create_install_package_ui(self, parent):
        title_label = ttk.Label(parent, text="Install Package", font=("Arial", 16))
        title_label.pack(pady=10)

        # Input field for package name
        package_label = ttk.Label(parent, text="Package Name:")
        package_label.pack(pady=5)
        package_entry = ttk.Entry(parent)
        package_entry.pack(pady=5)

        # Create a frame to display the log dynamically
        log_frame = ttk.Frame(parent)
        log_frame.pack(fill="both", expand=True, pady=10)

        # Create a canvas and a scrollbar for scrolling
        canvas = tk.Canvas(log_frame)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=canvas.yview)
        scrollable_log_frame = ttk.Frame(canvas)

        # Configure the canvas to update the scroll region
        scrollable_log_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_log_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Function to dynamically update the log
        def update_log(message: str, success: bool):
            log_label = ttk.Label(
                scrollable_log_frame,
                text=message,
                font=("Arial", 12),
                foreground="green" if success else "red"
            )
            log_label.pack(anchor="w", pady=2)

        # Function to handle package installation
        def install_package(name: str) -> None:
            data = {"package_name": name}
            r = requests.post(BACKEND_URL + 'install_package', json=data)
            if r.status_code == 200:
                response_data = r.json()
                update_log(response_data["message"], success=True)
            else:
                response_data = r.json()
                update_log(response_data.get("error", "An error occurred"), success=False)

        # Button to trigger package installation
        install_button = ttk.Button(parent, text="Install", command=lambda: install_package(package_entry.get()))
        install_button.pack(pady=10)

    # Create the UI for the "Search For Package" tab
    def create_search_package_ui(self, parent):
        title_label = ttk.Label(parent, text="Search For Package", font=("Arial", 16))
        title_label.pack(pady=10)

        # Input field for package name
        package_label = ttk.Label(parent, text="Package Name:")
        package_label.pack(pady=5)
        package_entry = ttk.Entry(parent)
        package_entry.pack(pady=5)

        # Button to trigger package search
        install_button = ttk.Button(parent, text="Install")
        install_button.pack(pady=10)

    # Open a popup window for installing Python
    def open_install_python_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Install Python")
        popup.geometry("300x150")

        # Display popup content
        label = ttk.Label(popup, text="Install Python", font=("Arial", 14))
        label.pack(pady=20)

        # Close button for the popup
        close_button = ttk.Button(popup, text="Close", command=popup.destroy)
        close_button.pack(pady=10)

# Run the application
if __name__ == "__main__":
    app = PipimApp()
    app.mainloop()