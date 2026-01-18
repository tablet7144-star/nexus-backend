from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# API Anahtarını Render'ın gizli kasasından çekeceğiz (Kodun içinde yazmayacak!)
REAL_API_KEY = os.environ.get("GOOGLE_API_KEY")

if REAL_API_KEY:
    genai.configure(api_key=REAL_API_KEY)

@app.route('/', methods=['GET'])
def home():
    return "Nexus Sunucusu Aktif!"

@app.route('/analyze', methods=['POST'])
def analyze_code():
    try:
        # Anahtar yoksa işlem yapma
        if not REAL_API_KEY:
            return jsonify({"error": "Sunucu API anahtarı ayarlanmamış!"}), 500

        data = request.json
        user_code = data.get("code", "")
        mode = data.get("mode", "DEBUG")
        
        # En iyi modeli seç
        model = genai.GenerativeModel("gemini-1.5-pro")

        # Prompt hazırlığı
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

        response = model.generate_content(full_prompt)
        return jsonify({"result": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)