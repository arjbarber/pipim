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

        # Create a container for the canvas and scrollbar
        container = ttk.Frame(parent)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Get the background color from the top-level widget
        default_bg = parent.winfo_toplevel().cget("bg")
        canvas = tk.Canvas(container, borderwidth=0, bg=default_bg)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a scrollable frame inside the canvas
        scrollable_frame = ttk.Frame(canvas)
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Update scroll region when the frame's size changes
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", on_frame_configure)

        # Update the frame width to match the canvas width
        def on_canvas_configure(event):
            canvas.itemconfig(window_id, width=event.width)

        canvas.bind("<Configure>", on_canvas_configure)

        # Enable mouse wheel scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # For Linux
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # For Linux

        def refresh_packages():
            # Clear current content
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            r = requests.get(BACKEND_URL + "get_modules")
            if r.status_code == 200:
                data = r.json()  # Parse the JSON response
            else:
                pkg_frame = ttk.Frame(scrollable_frame)
                pkg_frame.pack(fill="x", pady=5, padx=20)
                pkg_label = ttk.Label(pkg_frame, text="No modules installed.", font=("Arial", 12))
                pkg_label.pack(side="left", padx=100)
                return

            # Create a frame for each package and use grid for alignment
            for pkg in data:
                pkg_name = pkg["name"]
                pkg_version = pkg["version"]

                pkg_frame = ttk.Frame(scrollable_frame)
                pkg_frame.pack(fill="x", pady=5, padx=20)

                # Package name
                pkg_label = ttk.Label(pkg_frame, text=pkg_name, font=("Arial", 12))
                pkg_label.grid(row=0, column=0, sticky="w")

                # Version aligned next to the package name
                pkg_version_label = ttk.Label(pkg_frame, text=f"Version: {pkg_version}", font=("Arial", 12))
                pkg_version_label.grid(row=0, column=1, sticky="e", padx=20)

                # Documentation button on the right side
                doc_button = ttk.Button(pkg_frame, text="Documentation",
                                        command=lambda name=pkg_name: open_documentation(name))
                doc_button.grid(row=0, column=2, sticky="e", padx=5)

                # Remove button on the far right
                remove_button = ttk.Button(pkg_frame, text="Remove",
                                        command=lambda name=pkg_name, version=pkg_version: remove_button_popup(name, version))
                remove_button.grid(row=0, column=3, sticky="e", padx=5)

                # Let the name and version columns expand to use available space
                pkg_frame.columnconfigure(0, weight=1)
                pkg_frame.columnconfigure(1, weight=1)

        # Bind the refresh_packages function to the tab being selected
        parent.bind("<Visibility>", lambda event: refresh_packages())

        def open_documentation(name):
            r = requests.post(BACKEND_URL + "package_documentation", json={"package_name": name})
            if r.status_code != 200:
                raise Exception("Failed to fetch documentation")

        def remove_package(name, popup):
            r = requests.post(BACKEND_URL + "uninstall_package", json={"package_name": name})
            if r.status_code == 200:
                refresh_packages()  # Refresh the package list after removal

            popup.destroy()

        def remove_button_popup(package_name, package_version):

            default_bg = self.winfo_toplevel().cget("bg")

            popup = tk.Toplevel(self)
            popup.title("Remove Package")
            popup.geometry("300x150")
            popup.configure(bg="#f0f0f0")  

            # Display popup content
            label = ttk.Label(popup, text=f"You are attempting to remove package {package_name} with version {package_version}.\nDo you wish to proceed?", font=("Arial", 14), background="#f0f0f0")
            label.pack(pady=20)

            close_button = ttk.Button(popup, text="Remove", command=lambda name=package_name: remove_package(name, popup))
            close_button.pack(pady=10)

            # Close button for the popup
            close_button = ttk.Button(popup, text="Cancel", command=popup.destroy)
            close_button.pack(pady=10)

        # Initial load of packages
        refresh_packages()

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
        def search_package():
            query = package_entry.get()
            if not query:
                result_label.config(text="Please enter a package name.")
                return

            try:
                response = requests.get(BACKEND_URL + "search_for_packages", params={"q": query})
                response.raise_for_status()
                packages = response.json()

                result_text.delete("1.0", tk.END)
                if isinstance(packages, list) and packages:
                    for pkg in packages:
                        result_text.insert(tk.END, f"{pkg['name']} ({pkg['version']}): {pkg['description']}\n\n")
                else:
                    result_text.insert(tk.END, "No packages found.")
            except Exception as e:
                result_label.config(text=f"Error: {str(e)}")

        # UI Components
        title_label = ttk.Label(parent, text="Search For Package", font=("Arial", 16))
        title_label.pack(pady=10)

        package_label = ttk.Label(parent, text="Package Name:")
        package_label.pack(pady=5)

        package_entry = ttk.Entry(parent, width=40)
        package_entry.pack(pady=5)

        install_button = ttk.Button(parent, text="Search", command=search_package)
        install_button.pack(pady=10)

        result_label = ttk.Label(parent, text="", foreground="red")
        result_label.pack()

        result_text = tk.Text(parent, height=15, width=60, wrap="word")
        result_text.pack(pady=10)

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