from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# API Anahtarı
REAL_API_KEY = os.environ.get("GOOGLE_API_KEY")

if REAL_API_KEY:
    genai.configure(api_key=REAL_API_KEY)

@app.route('/', methods=['GET'])
def home():
    return "Nexus Sunucusu (Flash v1.5) Aktif!"

@app.route('/analyze', methods=['POST'])
def analyze_code():
    try:
        if not REAL_API_KEY:
            return jsonify({"error": "Sunucu API anahtarı eksik!"}), 500

        data = request.json
        user_code = data.get("code", "")
        mode = data.get("mode", "DEBUG")

        # --- MODEL SEÇİMİ (EN YENİ VE HIZLI MODEL) ---
        # Artık döngü yok, direkt hedefi vuruyoruz.
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Prompt
        prompt = f"""
        Sen Nexus AI Asistanısın.
        Görev: {mode}
        Dil: Türkçe
        
        KOD:
        {user_code}
        
        Lütfen detaylı analiz yap ve sonucu düzgün formatta ver.
        """

        response = model.generate_content(prompt)
        return jsonify({"result": response.text})

    except Exception as e:
        # Hatayı gizlemeden direkt gösterelim ki ne olduğunu bilelim
        return jsonify({"error": f"Google Hatası: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
