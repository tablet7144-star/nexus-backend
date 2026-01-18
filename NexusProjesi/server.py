from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# API Anahtarı
REAL_API_KEY = os.environ.get("GOOGLE_API_KEY")

if REAL_API_KEY:
    genai.configure(api_key=REAL_API_KEY)

def generate_with_fallback(prompt):
    """
    Modelleri sırayla dener. Biri hata verirse diğerine geçer.
    Böylece asla 404 hatası almazsın.
    """
    # Denenecek modeller listesi (En iyiden en garantiye doğru)
    models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    
    last_error = None

    for model_name in models_to_try:
        try:
            print(f"Denenen Model: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"{model_name} hata verdi: {e}")
            last_error = e
            continue # Bir sonraki modele geç
    
    # Hiçbiri çalışmazsa hatayı döndür
    raise last_error

@app.route('/', methods=['GET'])
def home():
    return "Nexus Sunucusu Aktif (v2.0 Fix)"

@app.route('/analyze', methods=['POST'])
def analyze_code():
    try:
        if not REAL_API_KEY:
            return jsonify({"error": "Sunucu API anahtarı eksik!"}), 500

        data = request.json
        user_code = data.get("code", "")
        mode = data.get("mode", "DEBUG")

        # Prompt Hazırlığı
        base_prompt = f"Sen Nexus AI Sistemisin. Mod: {mode}. Dil: Türkçe."
        if "DEBUG" in mode: base_prompt += " Hataları düzelt."
        elif "SECURITY" in mode: base_prompt += " Güvenlik analizi yap."
        elif "PERFORMANCE" in mode: base_prompt += " Optimize et."
        elif "AUTO-TEST" in mode: base_prompt += " Unit test yaz."
        elif "DOCS" in mode: base_prompt += " Dokümantasyon ekle."

        full_prompt = f"""
        {base_prompt}
        FORMAT:
        ------------------------------------------
        [DURUM]: (BAŞARILI / RİSKLİ)
        ------------------------------------------
        1. ANALİZ
        2. BULGULAR
        3. SONUÇ
        ------------------------------------------
        KOD:
        {user_code}
        """

        # Akıllı fonksiyonu çağır
        result_text = generate_with_fallback(full_prompt)
        return jsonify({"result": result_text})

    except Exception as e:
        return jsonify({"error": f"Sunucu Hatası: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)

