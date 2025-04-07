import google.generativeai as genai

genai.configure(api_key="AIzaSyAZo0bscN0f8Uz9Cp_V_OziIsXI8C0bn7w")  # Replace with your real Gemini API key
model = genai.GenerativeModel("gemini-1.5-flash")

LANG_NAMES = {
    "hi": "Hindi",
    "ta": "Tamil",
    "bn": "Bengali"
}

def translate_to_lang(text, lang_code):
    try:
        target_lang = LANG_NAMES.get(lang_code)
        if not target_lang:
            print(f"❌ Unsupported language: {lang_code}")
            return text

        prompt = f'Translate the following to {target_lang}:\n\n"{text}"\n\nOnly return the translated version.'

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print(f"❌ Translation failed: {e}")
        return text
