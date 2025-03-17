from flask import Flask, request, render_template
import re
import openai

app = Flask(__name__)

# API OpenAI (upewnij się, że masz poprawny klucz)
openai.api_key = "TWOJ_KLUCZ_API"

# Lista skrótów instytucji do odrzucenia
SKROTY_INSTYTUCJI = {"PGKIM", "GOPR", "WOSL", "PKP", "ZUS", "NFZ", "PZU"}

# Funkcja sprawdzająca, czy słowo zawiera cyfry
def zawiera_cyfry(slowo):
    return any(char.isdigit() for char in slowo)

# Funkcja sprawdzająca, czy słowo jest podwójne
def podwojne_slowo(slowo):
    return " " in slowo

# Funkcja sprawdzająca, czy słowo jest sklejone (np. "domszafa")
def sklejone_slowo(slowo):
    return not re.match(r'^[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+$', slowo)

# Funkcja sprawdzająca poprawność słowa w języku polskim za pomocą OpenAI
def sprawdz_w_openai(slowo):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Czy to poprawne polskie słowo? Odpowiedz tylko 'TAK' lub 'NIE'!"},
                {"role": "user", "content": slowo}
            ]
        )
        odpowiedz = response["choices"][0]["message"]["content"].strip()
        return odpowiedz == "TAK"
    except:
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "Nie przesłano pliku."
    
    file = request.files['file']
    if file.filename == '':
        return "Nie wybrano pliku."
    
    poprawne_slowa = []
    odrzucone_slowa = []
    
    for line in file:
        slowo = line.decode('utf-8').strip()
        if (slowo in SKROTY_INSTYTUCJI or 
            zawiera_cyfry(slowo) or 
            podwojne_slowo(slowo) or 
            sklejone_slowo(slowo)):
            odrzucone_slowa.append(slowo)
        elif sprawdz_w_openai(slowo):
            poprawne_slowa.append(slowo)
        else:
            odrzucone_slowa.append(slowo)
    
    # Zapis wyników do plików
    with open('poprawne.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(poprawne_slowa))
    
    with open('odrzucone.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(odrzucone_slowa))
    
    return "Przetwarzanie zakończone! <a href='/download/poprawne'>Pobierz poprawne słowa</a> | <a href='/download/odrzucone'>Pobierz odrzucone słowa</a>"

@app.route('/download/<file>')
def download(file):
    if file == "poprawne":
        return open('poprawne.txt', 'r', encoding='utf-8').read()
    elif file == "odrzucone":
        return open('odrzucone.txt', 'r', encoding='utf-8').read()
    return "Nie znaleziono pliku."

if __name__ == '__main__':
    app.run(debug=True)


