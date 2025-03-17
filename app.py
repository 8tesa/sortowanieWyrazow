from flask import Flask, request, render_template_string
import re
import os

app = Flask(__name__)

# Lista skrótów instytucji do odrzucenia
skroty_instytucji = {"PGKIM", "GOPR", "WOSL", "PKP", "ZUS", "NFZ", "PZU"}

def sprawdz_wyraz(wyraz):
    # Odrzucanie skrótów instytucji
    if wyraz in skroty_instytucji:
        return False
    # Odrzucanie słów zawierających cyfry
    if any(char.isdigit() for char in wyraz):
        return False
    # Odrzucanie podwójnych i sklejonych wyrazów (jeśli nie istnieją)
    if " " in wyraz or re.search(r"[A-Z]{2,}", wyraz):
        return False
    return True

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "Brak pliku"
        file = request.files["file"]
        if file.filename == "":
            return "Nie wybrano pliku"

        poprawne = []
        odrzucone = []

        for line in file.read().decode("utf-8").splitlines():
            wyraz = line.strip()
            if sprawdz_wyraz(wyraz):
                poprawne.append(wyraz)
            else:
                odrzucone.append(wyraz)

        # Zapisywanie wyników
        poprawne_file = "poprawne.txt"
        odrzucone_file = "odrzucone.txt"

        with open(poprawne_file, "w", encoding="utf-8") as f:
            f.write("\n".join(poprawne))
        with open(odrzucone_file, "w", encoding="utf-8") as f:
            f.write("\n".join(odrzucone))

        return render_template_string('''
            <!doctype html>
            <title>Wynik</title>
            <h1>Przetwarzanie zakończone!</h1>
            <p><a href="/download/poprawne">Pobierz poprawne słowa</a></p>
            <p><a href="/download/odrzucone">Pobierz odrzucone słowa</a></p>
        ''')

    return render_template_string('''
        <!doctype html>
        <title>Prześlij plik</title>
        <h1>Prześlij plik .txt do sprawdzenia</h1>
        <form method=post enctype=multipart/form-data>
            <input type=file name=file>
            <input type=submit value=Prześlij>
        </form>
    ''')

@app.route("/download/<filename>")
def download_file(filename):
    if filename == "poprawne":
        return open("poprawne.txt", "r", encoding="utf-8").read()
    elif filename == "odrzucone":
        return open("odrzucone.txt", "r", encoding="utf-8").read()
    return "Plik nie istnieje!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

