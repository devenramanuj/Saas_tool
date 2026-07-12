import json
import os
import requests
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Render ના Environment Variables માંથી કી રીડ કરશે
API_KEY = os.environ.get("GEMINI_API_KEY")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="gu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ContentFlip AI - Micro SaaS</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-slate-50 text-slate-800 font-sans antialiased">

    <header class="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-2">
                <div class="bg-indigo-600 text-white p-2 rounded-lg">
                    <i class="fa-solid fa-arrows-spin text-xl"></i>
                </div>
                <span class="text-xl font-bold tracking-tight bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">ContentFlip AI</span>
            </div>
            <div class="flex items-center space-x-4">
                <span class="text-sm font-medium bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full border border-indigo-100">Free Tier</span>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            <!-- Left Side -->
            <div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
                <div>
                    <h2 class="text-lg font-bold text-slate-900 mb-2">૧. તમારું મૂળ કન્ટેન્ટ અહીં નાખો</h2>
                    <textarea id="sourceContent" rows="8" class="w-full p-4 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-slate-700 placeholder-slate-400 resize-none mb-6" placeholder="તમારું લાંબુ કન્ટેન્ટ અહીં લખો અથવા પેસ્ટ કરો..."></textarea>

                    <h2 class="text-lg font-bold text-slate-900 mb-2">૨. પ્લેટફોર્મ સિલેક્ટ કરો</h2>
                    <div class="grid grid-cols-3 gap-3 mb-6">
                        <label class="cursor-pointer">
                            <input type="radio" name="platform" value="linkedin" checked class="peer sr-only">
                            <div class="flex flex-col items-center justify-center p-3 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50 peer-checked:border-indigo-600 peer-checked:bg-indigo-50 peer-checked:text-indigo-600 transition-all">
                                <i class="fa-brands fa-linkedin text-xl mb-1"></i>
                                <span class="text-xs font-semibold">LinkedIn</span>
                            </div>
                        </label>
                        <label class="cursor-pointer">
                            <input type="radio" name="platform" value="twitter" class="peer sr-only">
                            <div class="flex flex-col items-center justify-center p-3 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50 peer-checked:border-indigo-600 peer-checked:bg-indigo-50 peer-checked:text-indigo-600 transition-all">
                                <i class="fa-brands fa-x-twitter text-xl mb-1"></i>
                                <span class="text-xs font-semibold">Twitter (X)</span>
                            </div>
                        </label>
                        <label class="cursor-pointer">
                            <input type="radio" name="platform" value="reels" class="peer sr-only">
                            <div class="flex flex-col items-center justify-center p-3 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50 peer-checked:border-indigo-600 peer-checked:bg-indigo-50 peer-checked:text-indigo-600 transition-all">
                                <i class="fa-brands fa-instagram text-xl mb-1"></i>
                                <span class="text-xs font-semibold">Reels Hook</span>
                            </div>
                        </label>
                    </div>
                </div>

                <button onclick="generateContent()" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3.5 px-4 rounded-xl shadow-sm transition-all flex items-center justify-center space-x-2 cursor-pointer">
                    <i class="fa-solid fa-wand-magic-sparkles"></i>
                    <span>મેજિક જનરેટ કરો</span>
                </button>
            </div>

            <!-- Right Side -->
            <div class="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col">
                <div class="flex items-center justify-between border-b border-slate-100 pb-4 mb-4">
                    <h2 class="text-lg font-bold text-slate-900">જનરેટ થયેલ કન્ટેન્ટ</h2>
                    <span id="outputBadge" class="text-xs font-semibold bg-slate-100 text-slate-600 px-2.5 py-1 rounded-md uppercase tracking-wider">નક્કી નથી</span>
                </div>

                <div class="flex-1 flex flex-col justify-between">
                    <div id="placeholderText" class="py-12 flex flex-col items-center justify-center text-slate-400">
                        <i class="fa-solid fa-sparkles text-3xl mb-3 text-indigo-200"></i>
                        <p class="text-sm text-center">તમારું નવું શોર્ટ કન્ટેન્ટ અહીં દેખાશે.</p>
                    </div>

                    <div id="outputContainer" class="hidden space-y-4">
                        <div class="bg-slate-50 border border-slate-200 rounded-xl p-4 relative group">
                            <button onclick="copyToClipboard('resultText')" class="absolute top-3 right-3 bg-white border border-slate-200 p-1.5 rounded-md text-slate-500 hover:text-indigo-600 shadow-xs transition-all" title="કોપી કરો">
                                <i class="fa-regular fa-copy"></i>
                            </button>
                            <div id="resultText" class="text-slate-700 whitespace-pre-wrap pr-6 text-sm leading-relaxed"></div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </main>

    <script>
        async function generateContent() {
            const content = document.getElementById('sourceContent').value;
            const platform = document.querySelector('input[name="platform"]:checked').value;
            
            if(!content.trim()) {
                alert('કૃપા કરીને પહેલા થોડું કન્ટેન્ટ એન્ટર કરો!');
                return;
            }

            document.getElementById('placeholderText').innerHTML = `
                <i class="fa-solid fa-circle-notch text-3xl animate-spin text-indigo-600 mb-3"></i>
                <p class="text-sm text-slate-500">AI વિચારી રહ્યું છે... થોડી સેકન્ડો રાહ જુઓ.</p>
            `;
            document.getElementById('outputContainer').classList.add('hidden');
            document.getElementById('placeholderText').classList.remove('hidden');

            try {
                // પ્રોડક્શન માટે પરફેક્ટ રિલેટિવ પાથ
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content: content, platform: platform })
                });

                const data = await response.json();
                document.getElementById('placeholderText').classList.add('hidden');
                
                if (data.success) {
                    document.getElementById('outputBadge').innerText = platform;
                    document.getElementById('resultText').innerText = data.generated_text;
                    document.getElementById('outputContainer').classList.remove('hidden');
                } else {
                    alert('સર્વર તરફથી ભૂલ: ' + data.error);
                }
            } catch (error) {
                document.getElementById('placeholderText').classList.add('hidden');
                alert('સર્વર કનેક્શનમાં ભૂલ આવી છે. કૃપા કરીને થોડીવાર પછી પ્રયત્ન કરો.');
            }
        }

        function copyToClipboard(elementId) {
            const text = document.getElementById(elementId).innerText;
            navigator.clipboard.writeText(text).then(() => {
                alert('કન્ટેન્ટ કોપી થઈ ગયું છે!');
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate_content():
    if not API_KEY:
        return jsonify({"success": False, "error": "Gemini API Key સેટ કરેલી નથી. કૃપા કરીને Render સેટિંગ્સ તપાસો."}), 500
        
    try:
        data = request.json or {}
        source_text = data.get('content', '').strip()
        platform = data.get('platform', 'linkedin')
        
        if not source_text:
            return jsonify({"success": False, "error": "કન્ટેન્ટ ખાલી છે."}), 400

        # એડવાન્સ શાર્પ પ્રોમ્પ્ટ
        system_prompt = f"""
        You are an elite, highly paid Social Media Copywriter. 
        Your job is to REPURPOSE and CONDENSE the source text into a high-performing {platform} post in GUJARATI.

        CRITICAL RULES:
        1. DO NOT just copy-paste or translate the source text. Rewrite it completely to match the platform's style.
        2. COMPRESSION: Extract only the top 3 core actionable insights. Cut the fluff.
        3. PLATFORM SPECIFIC FORMAT:
           - If 'linkedin': Start with a bold hook. Use exactly 3 bullet points with emojis. End with an engaging question. Keep it short.
           - If 'twitter': Must be under 280 characters. Write max 2 punchy sentences, 1 emoji, and 2 tags.
           - If 'reels': Give a clear "3-Second Hook Idea", then a short caption and relevant hashtags.
        4. Output ONLY the finalized post in Gujarati. No extra conversation.

        Source Text:
        {source_text}
        """

        # Gemini 2.5 Flash API URL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
        
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": system_prompt}]}]}
        
        # requests લાઇબ્રેરીનો ઉપયોગ કરીને વધુ સુરક્ષિત અને સ્ટેબલ કોલ
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            return jsonify({"success": False, "error": f"Gemini API Error (Status {response.status_code}): {response.text}"}), 500
            
        result = response.json()
        generated_text = result['candidates'][0]['content']['parts'][0]['text']
        
        return jsonify({"success": True, "generated_text": generated_text})

    except requests.exceptions.Timeout:
        return jsonify({"success": False, "error": "Gemini API તરફથી જવાબ મળવામાં સમય લાગ્યો (Timeout)."}), 544
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
