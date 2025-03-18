from flask import Flask, request, render_template
import openai

app = Flask(__name__)

# API OpenAI (upewnij się, że masz poprawny klucz)
openai.api_key = "TWÓJ_KLUCZ_API"

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
        
        # Dodaj logowanie:
        with open("log_responses.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"{slowo} -> {odpowiedz}\n")
        
        return odpowiedz == "TAK"
    except Exception as e:
        # Również zapisujemy wyjątek, jeśli coś pójdzie nie tak
        with open("log_responses.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"{slowo} -> ERROR: {str(e)}\n")
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




