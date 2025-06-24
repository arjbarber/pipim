# pipim
GUI Package Manager for Python

## Download (Coming Soon)
Downloadable executables are coming soon. For now, follow the steps below to run the program.

---

## Run Instructions:

### 1. Install Git
- On macOS, this can be done through `brew install git`.
- On Windows, download and install Git from the [official website](https://git-scm.com/).

### 2. Install Python
- Download and install Python from the [official website](https://www.python.org/) or the Microsoft Store.

### 3. Clone the Repository
Run the following command in your terminal or command prompt:
```
git clone https://github.com/arjbarber/pipim.git
```
This will copy all the files from this repository to a folder on your computer.

### 4. Install Dependencies
Navigate to the project folder and install the required dependencies:
```
cd pipim
pip install -r requirements.txt
```

### 5. Run the Application
Run the following command to start the application:

#### Windows:
```
python runner.py
```

#### macOS/Linux:
```
python runner.py
```

---

## Features
- View installed Python packages.
- Search for packages on PyPI.
- Install and uninstall packages.
- Save package information locally.
- Open package documentation directly from the app.

---

## Notes
- Ensure Python is added to your system's PATH during installation.
- The app runs a backend server on `http://127.0.0.1:5050/` and launches a GUI frontend.
- If you encounter issues, ensure no other process is using port `5050`.

---

Congrats! The app is now running! An executable will be made soon to automate this process.