#!/usr/bin/env python3

import subprocess
import sys
import os
import re

OUTPUT_FILE = "project.txt"
SPECFILE_OUTPUT = "specfile.txt"
SPECFOL_OUTPUT = "specfol.txt"

EXCLUDE_PATTERNS = re.compile(
    r"(__pycache__|migrations|tests|static|staticfiles|media|venv|env|wallet_backups)"
)

EXCLUDE_FILES = re.compile(
    r"(admin\.py|apps\.py|__init__\.py)"
)

BINARY_EXTENSIONS = (
    ".pyc", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".zip", ".pdf", ".db", ".sqlite3", ".key", ".css", ".min.js"
)


def git_ls_files():
    try:
        result = subprocess.check_output(["git", "ls-files"], text=True)
        return result.strip().splitlines()
    except subprocess.CalledProcessError:
        print("❌ Not a git repository")
        sys.exit(1)


def is_relevant_file(path):
    if EXCLUDE_PATTERNS.search(path):
        return False
    if EXCLUDE_FILES.search(path):
        return False
    if path.endswith(BINARY_EXTENSIONS):
        return False
    if not (path.endswith(".py") or path.endswith(".html")):
        return False
    return True


def is_dynamic_html(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            return "{{" in content or "{%" in content
    except Exception:
        return False


def strip_python_noise(content):
    lines = []
    in_docstring = False

    for line in content.splitlines():
        stripped = line.strip()

        if stripped.startswith(('"""', "'''")):
            in_docstring = not in_docstring
            continue

        if in_docstring:
            continue

        if stripped.startswith("#") or not stripped:
            continue

        lines.append(line)

    return "\n".join(lines)


def write_files(file_list, filename=OUTPUT_FILE, append=False):
    mode = "a" if append else "w"
    with open(filename, mode, encoding="utf-8") as out:
        for path in file_list:
            if not os.path.exists(path):
                continue

            out.write(f"\n===== FILE: {path} =====\n")

            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if path.endswith(".py"):
                        content = strip_python_noise(content)
                    out.write(content + "\n")
            except Exception as e:
                out.write(f"[ERROR READING FILE: {e}]\n")

    print(f"\n✅ Output written to {filename}\n")


# Option 1: Relevant Django logic
def option_relevant_django_files(files):
    selected = []
    for f in files:
        if is_relevant_file(f):
            if f.endswith(".html") and not is_dynamic_html(f):
                continue
            selected.append(f)
    write_files(selected, OUTPUT_FILE)


# Option 2: Specific files manually
def option_select_files(files):
    print("\nAvailable files:\n")
    for i, f in enumerate(files):
        print(f"{i}: {f}")

    picks = input("\nEnter file numbers (comma separated): ").strip()
    indexes = [int(i) for i in picks.split(",") if i.isdigit()]
    selected = [files[i] for i in indexes if i < len(files)]
    write_files(selected, SPECFILE_OUTPUT)


# Option 3: Specific HTML templates
def option_select_html(files):
    html_files = [f for f in files if f.endswith(".html")]

    for i, f in enumerate(html_files):
        print(f"{i}: {f}")

    picks = input("\nSelect HTML file numbers (comma separated): ").strip()
    indexes = [int(i) for i in picks.split(",") if i.isdigit()]
    selected = [html_files[i] for i in indexes if i < len(html_files)]
    write_files(selected, SPECFILE_OUTPUT)


# Option 4: Specific folder(s) → specfol.txt
def option_select_folders(files):
    # Find all unique top-level folders
    folders = sorted(set(f.split("/")[0] for f in files if "/" in f))

    print("\nAvailable folders:\n")
    for i, f in enumerate(folders):
        print(f"{i}: {f}")

    picks = input("\nEnter folder numbers (comma separated): ").strip()
    indexes = [int(i) for i in picks.split(",") if i.isdigit()]
    selected_folders = [folders[i] for i in indexes if i < len(folders)]

    # Gather all relevant files in the selected folders
    selected_files = []
    for f in files:
        for folder in selected_folders:
            if f.startswith(folder + "/") and is_relevant_file(f):
                if f.endswith(".html") and not is_dynamic_html(f):
                    continue
                selected_files.append(f)

    if not selected_files:
        print("❌ No relevant files found in selected folder(s)")
        return

    write_files(selected_files, SPECFOL_OUTPUT, append=True)


def menu():
    files = git_ls_files()

    while True:
        print("""
==============================
 Git Project Scanner CLI
==============================
1) Print relevant Django app files (logic only)
2) Print specific files (manual selection)
3) Print specific HTML templates
4) Print specific folder(s)
5) Exit
""")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            option_relevant_django_files(files)
        elif choice == "2":
            option_select_files(files)
        elif choice == "3":
            option_select_html(files)
        elif choice == "4":
            option_select_folders(files)
        elif choice == "5":
            print("Bye 👋")
            break
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    menu()