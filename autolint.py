#!/usr/bin/env python3
"""
Dieses Modul durchsucht rekursiv das Projekt nach Python-Dateien, führt pylint aus,
zeigt die gefundenen Linter-Fehler an und ermöglicht (mit Hilfe eines GPT-Modells)
einen automatischen Code-Fix.
"""

import os
import sys
import subprocess
from openai import OpenAI

# Initialisiere den OpenAI-Client.
# Setze den API-Schlüssel über die Umgebungsvariable OPENAI_API_KEY.
client = OpenAI()

STEP_FILENAME = "lintstep.txt"

EXCLUDE_PATHS = [
    os.sep + ".git" + os.sep,
    os.sep + "__pycache__" + os.sep,
    os.sep + "build" + os.sep,
    os.sep + "dist" + os.sep,
    os.sep + "docs" + os.sep,
    os.sep + "venv" + os.sep,
    os.sep + "ops" + os.sep,
]


def list_python_files(root="."):
    """
    Durchsuche rekursiv das Verzeichnis `root` nach allen Python-Dateien,
    die nicht in ausgeschlossenen Unterverzeichnissen liegen.
    """
    py_files = []
    for dirpath, _dirnames, filenames in os.walk(root):
        if any(exclude in dirpath for exclude in EXCLUDE_PATHS):
            continue
        for filename in filenames:
            if filename.endswith(".py"):
                full_path = os.path.join(dirpath, filename)
                if not any(exclude in full_path for exclude in EXCLUDE_PATHS):
                    py_files.append(full_path)
    py_files.sort()
    return py_files


def load_last_processed_file() -> str:
    """Lade den zuletzt verarbeiteten Dateipfad aus STEP_FILENAME, falls vorhanden."""
    if os.path.exists(STEP_FILENAME):
        with open(STEP_FILENAME, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def save_current_file(file_path: str) -> None:
    """Speichere den aktuell verarbeiteten Dateipfad in STEP_FILENAME."""
    with open(STEP_FILENAME, "w", encoding="utf-8") as f:
        f.write(file_path)


def run_pylint(file_path: str) -> str:
    """
    Führt pylint für die angegebene Datei aus und liefert die Ausgabe
    als String zurück.
    """
    try:
        result = subprocess.run(
            ["pylint", file_path],
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout + "\n" + result.stderr
    except FileNotFoundError:
        print(
            "pylint wurde nicht gefunden. Bitte installiere pylint "
            "und stelle sicher, dass es im PATH ist."
        )
        return ""


def filter_lint_messages(lint_output: str) -> str:
    """
    Filtert aus der pylint-Ausgabe alle Zeilen, die 'duplicate-code'
    enthalten und gibt den Rest als zusammengefassten String zurück.
    """
    filtered_lines = []
    for line in lint_output.splitlines():
        if "duplicate-code" not in line:
            filtered_lines.append(line)
    return "\n".join(filtered_lines)


def get_code_from_file(file_path: str) -> str:
    """Lese den kompletten Inhalt der Datei ein."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def ensure_ends_with_empty_line(code: str) -> str:
    """Stellt sicher, dass der Code mit einer leeren Zeile endet."""
    if not code.endswith("\n"):
        code += "\n"
    lines = code.splitlines()
    if lines and lines[-1].strip() != "":
        code += "\n"
    return code


def call_gpt_model(code: str, lint_message: str) -> str:
    """
    Ruft das GPT-Modell auf mit dem gesamten Code und den Linter-Fehlern,
    und liefert den (verbesserten) Code als Antwort zurück.
    """
    content = (
        "Hier ist der komplette Code:\n\n" + code + "\n\n" +
        "Folgende Linter-Fehler wurden festgestellt:\n\n" + lint_message +
        "\n\nBitte aktualisiere den Code basierend darauf. Achte darauf, dass "
        "die letzte Zeile des Codes leer ist."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "developer",
                "content": (
                    "You are a pythoncode linter and fixer. You will fix the linter "
                    "problems and return the code with the last line empty. Do not add "
                    "any additional characters or explanations or backticks - just "
                    "return the fixed code."
                )
            },
            {"role": "user", "content": content}
        ],
        response_format={"type": "text"},
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        store=False
    )
    return response.choices[0].message.content.strip()


def process_file(file_path: str) -> bool:
    """
    Lintert die Datei, zeigt die Linter-Fehler an und fragt interaktiv:
      1: Autofix via GPT-Modell
      2: Datei überspringen
      3: Script beenden

    Falls die Datei bereits mit „Your code has been rated at 10.00/10“
    gewertet wurde, wird sie automatisch übersprungen.
    Gibt True zurück, wenn die Verarbeitung fortgesetzt werden soll,
    oder False, wenn das Script beendet wird.
    """
    print(f"\nDatei: {file_path}")
    save_current_file(file_path)
    lint_output = run_pylint(file_path)

    # Prüfe, ob der perfekte Rating-String vorhanden ist.
    if "Your code has been rated at 10.00/10" in lint_output:
        print("Diese Datei wurde bereits mit 10.00/10 bewertet. Überspringe sie automatisch.")
        return True

    lint_messages = filter_lint_messages(lint_output)
    if not lint_messages.strip():
        print("Keine relevanten Linter-Fehler gefunden.")
        return True

    print(f"Die Datei '{file_path}' enthält folgende Linter-Fehler:\n{lint_messages}\n")
    user_choice = input("Drücke 1 für Autofix, 2 zum Überspringen und 3 zum Beenden: ").strip()
    while user_choice not in ("1", "2", "3"):
        user_choice = input(
            "Ungültige Eingabe. Drücke 1 für Autofix, 2 zum Überspringen "
            "und 3 zum Beenden: "
        ).strip()

    if user_choice == "1":
        print("Rufe das GPT-Modell auf...")
        original_code = get_code_from_file(file_path)
        updated_code = call_gpt_model(original_code, lint_messages)
        updated_code = ensure_ends_with_empty_line(updated_code)
        if updated_code.strip() == "":
            print("Das GPT-Modell hat keinen aktualisierten Code geliefert.")
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_code)
            print(f"Datei '{file_path}' wurde geupgradet.")
        return True
    elif user_choice == "2":
        print("Überspringe diese Datei.")
        return True
    elif user_choice == "3":
        print("Script wird beendet.")
        return False


def main():
    py_files = list_python_files(".")
    if not py_files:
        print("Keine Python-Dateien gefunden.")
        sys.exit(0)
    last_processed = load_last_processed_file()
    start_processing = (last_processed == "")
    for file_path in py_files:
        if not start_processing:
            if file_path == last_processed:
                start_processing = True
            continue
        continue_processing = process_file(file_path)
        if not continue_processing:
            break


if __name__ == "__main__":
    main()
