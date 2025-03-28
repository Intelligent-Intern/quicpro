import sys
import subprocess
from openai import OpenAI

client = OpenAI()

def get_lint_messages(lint_file: str) -> list[str]:
    """
    Lese die Linternachrichten aus der Datei ein und filtere alle,
    die den String "duplicate-code" enthalten.
    """
    messages = []
    with open(lint_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and "duplicate-code" not in line:
                messages.append(line)
    return messages

def get_code_from_file(code_file: str) -> str:
    """
    Lese den gesamten Inhalt der Code-Datei ein.
    """
    with open(code_file, "r", encoding="utf-8") as f:
        return f.read()

def call_gpt_model(code: str, lint_message: str) -> str:
    """
    Ruft das GPT-Modell auf und gibt die Antwort zurück.
    Die Eingabe besteht aus dem Code und der jeweiligen Linternachricht.
    """
    content = f"{code}\n\n{lint_message}\n\n"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": content
            }
        ],
        response_format={
            "type": "text"
        },
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        store=False
    )
    
    return response.choices[0].text.strip()

def run_linter(code_file: str) -> None:
    """
    Führt pylint für die angegebene Code-Datei aus und zeigt die Ausgabe an.
    """
    try:
        print("\nLinter wird ausgeführt...")
        # subprocess.run führt den Befehl aus und kann die Ausgabe zurückliefern.
        result = subprocess.run(
            ["pylint", code_file],
            capture_output=True,
            text=True,
            check=False  # Überspringt einen Fehlerabbruch, falls pylint einen Exit-Code != 0 liefert.
        )
        print(result.stdout)
        print(result.stderr)
    except FileNotFoundError:
        print("pylint wurde nicht gefunden. Bitte stelle sicher, dass pylint installiert ist und im PATH liegt.")

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <lint_message_file> <code_file>")
        sys.exit(1)

    lint_file = sys.argv[1]
    code_file = sys.argv[2]

    code = get_code_from_file(code_file)
    lint_messages = get_lint_messages(lint_file)

    if not lint_messages:
        print("Keine Linternachrichten gefunden, die verarbeitet werden sollen.")
        sys.exit(0)

    for lint in lint_messages:
        print(f"\n>>> Verarbeite Linternachricht:\n{lint}")
        gpt_response = call_gpt_model(code, lint)
        print("\nAntwort vom GPT-Modell:")
        print(gpt_response)
        print("-" * 40)
        
        # Auf Benutzereingabe warten, bevor zur nächsten Nachricht übergegangen wird
        user_input = input("Drücke 1, um zur nächsten Nachricht zu gelangen: ")
        while user_input.strip() != "1":
            user_input = input("Bitte drücke 1, um fortzufahren: ")

    # Linter tatsächlich für die gegebene Code-Datei ausführen:
    run_linter(code_file)

if __name__ == "__main__":
    main()