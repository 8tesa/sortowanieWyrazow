from flask import Flask, request, render_template
import openai

app = Flask(__name__)

# Upewnij się, że Twój klucz API OpenAI jest ustawiony jako zmienna środowiskowa.
openai.api_key = "TWÓJ_KLUCZ_API"  # Zastąp właściwym kluczem lub skorzystaj z zmiennej środowiskowej.

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

def sprawdz_w_openai(slowo):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # lub gpt-4, jeśli masz dostęp
            messages=[
                {"role": "system", "content": "Czy to poprawne polskie słowo? Odpowiedz tylko 'TAK' lub 'NIE'!"},
                {"role": "user", "content": slowo}
            ]
        )
        # Drukowanie odpowiedzi do debugowania
        print("Odpowiedź z OpenAI:", response)
        odpowiedz = response["choices"][0]["message"]["content"].strip()
        return odpowiedz == "TAK"
    except Exception as e:
        print("Błąd podczas komunikacji z OpenAI:", e)
        return False

if __name__ == '__main__':
    app.run(debug=True)





