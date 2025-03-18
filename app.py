from flask import Flask, request, render_template
import openai

app = Flask(__name__)

# Ustawienie klucza API OpenAI z Twoich zmiennych środowiskowych
openai.api_key = "TWÓJ_KLUCZ_API"

# Funkcja sprawdzająca poprawność słowa w języku polskim za pomocą OpenAI
def sprawdz_w_openai(slowo):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Wersja dostępna w darmowym planie
            messages=[
                {"role": "system", "content": "Czy to poprawne polskie słowo? Odpowiedz tylko 'TAK' lub 'NIE'!"},
                {"role": "user", "content": slowo}
            ]
        )
        odpowiedz = response["choices"][0]["message"]["content"].strip()
        return odpowiedz == "TAK"
    except Exception as e:
        print(f"Błąd podczas komunikacji z OpenAI: {e}")
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
        if sprawdz_w_openai(slowo):
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



