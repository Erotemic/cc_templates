## Overview: setting up the tools we’ll use

In this course we use three standard tools that work together:

1. **VS Code** — the *editor* where we write and run code.
2. **Python 3.13** — the *runtime* that actually executes our Python programs.
3. **Git** — the *download/update tool* used to copy the starter project onto the computer and track changes.

**Download pages (official links):**
- VS Code: https://code.visualstudio.com/download
- Python 3.13 (Windows): https://www.python.org/downloads/latest/python3.13/
- Git for Windows: https://git-scm.com/install/windows

---

## Tool 1: VS Code (Editor)

### Why we need it

VS Code is where you’ll:

* edit code files,
* see your folder structure,
* run commands in a built-in terminal.

### Get the right download

* Choose the **Windows (x64)** version for most lab computers.

### Windows setup steps (what to click)

1. Download the VS Code installer.
2. Double-click the installer to start.
3. Click through the installer screens:

   * Accept the license agreement
   * Keep the default install location
   * If you see options like “Add to PATH” or “Add ‘Open with Code’”, those are helpful but not strictly required.
4. Finish and launch VS Code.

### How to open VS Code later

Start Menu → type **VS Code** → open **Visual Studio Code**

---

## Tool 2: Python 3.13 (Runtime)

### Why we need it

Python is the thing that runs the program. VS Code is the editor, but **Python executes the code**.

### Get the right download

* Download **Python 3.13.x for Windows (64-bit)**.
* We use **3.13** so everyone gets the same behavior and avoids “too-new” compatibility issues.

### The most important checkbox: “Add to PATH”

During the installer, you will see a checkbox that says something like:

✅ **Add python.exe to PATH**

**Why this matters:**
“PATH” is a list of places Windows looks for programs when you type a command like `python` in the terminal.

* If Python is on PATH, typing `python` works from any folder.
* If it is *not* on PATH, the computer may say “python is not recognized” (or open a store prompt), even though Python is installed.

### Windows setup steps (what to click)

1. Run the Python installer.
2. On the first screen:

   * ✅ Check **Add python.exe to PATH**
3. Accept the rest of the defaults and complete the wizard.

### Quick verification (later)

In a terminal you’ll type:

```bat
python --version
```

You want it to say **Python 3.13.x**.

---

## Tool 3: Git (Download/update tool)

### Why we need it

Git is how we copy the starter project onto the computer using one command, and it’s also how developers keep track of changes.

For students, the first use is simple:

* **download the template project** using `git clone`.

### Windows setup steps

1. Download Git for Windows (x64 for most machines).
2. Run the installer.
3. Accept defaults (that’s fine for beginners).
4. Finish.

### Quick verification (later)

```bat
git --version
```

---

## VS Code basics: opening a folder and the terminal

### Why we “open a folder”

A project is a folder containing code files. Opening the folder in VS Code lets you see everything in one place.

**VS Code:** File → **Open Folder…**
Pick or create a folder like:

* `Documents\coding`
* or `Desktop\coding`

### What is the terminal?

The terminal is a text-based way to tell the computer what to do (like “download this project” or “run this program”). It’s normal in programming to use the terminal because it’s precise and repeatable.

### How to open the terminal in VS Code

* Menu: **View → Terminal**
* Shortcut: **Ctrl + `** (backtick)

---

## Download the starter code (cc_templates)

### Why we do this

Instead of starting from scratch, we copy a working project skeleton and then learn by modifying it.

In the VS Code terminal, run:

```bat
git clone https://github.com/Erotemic/cc_templates.git
```

This creates a new folder named `cc_templates`.

---

## Run the platformer project

### Step 1: go into the platformer folder

```bat
cd cc_templates\platformer
```

**Why:** the file `main.py` is inside this folder. We need to be in the right place to run it easily.

### Step 2: run the program (first run will likely error — that’s expected)

```bat
python main.py
```

**Why you might see an error:**
Many projects depend on extra packages. The starter code expects some packages to be installed first. The error message is the computer’s way of saying “I can’t find that library yet.”

### Step 3: install the required packages

```bat
python -m pip install ubelt pygame Pillow
```

**Why we use `python -m pip` instead of just `pip`:**
On Windows there can be more than one Python installed. `python -m pip` makes sure we install packages into the *same Python* that runs `main.py`.

### Step 4: run again

```bat
python main.py
```

Now the game should launch.

---

## If something doesn’t work (quick, neutral checks)

* If `python` isn’t recognized: Python likely isn’t on PATH (or the terminal needs restarting). Re-run the Python installer and ensure **Add to PATH** is checked.
* If `git` isn’t recognized: Git may not be on PATH yet. Close and reopen VS Code, then try `git --version`.
