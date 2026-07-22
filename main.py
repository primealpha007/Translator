from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pandas as pd

app = FastAPI()

# Load dictionary
df = pd.read_csv("dictionary.csv")


@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>English • Swahili • Kikuyu Translator</title>

    <style>

    body{
        font-family: Arial, sans-serif;
        max-width: 900px;
        margin: 50px auto;
        padding: 20px;
        background-color: #f5f5f5;
    }

    .container{
        background: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }

    h1{
        text-align:center;
    }

    input, select{
        width:100%;
        padding:12px;
        margin-top:10px;
        margin-bottom:10px;
        font-size:16px;
        box-sizing:border-box;
    }

    button{
        padding:12px;
        margin-top:10px;
        margin-bottom:10px;
        cursor:pointer;
        font-size:16px;
    }

    #result{
        margin-top:20px;
        font-size:24px;
        font-weight:bold;
        padding:15px;
        border-radius:10px;
        background:#eeeeee;
    }

    </style>
</head>

<body>

<div class="container">

<h1>English • Swahili • Kikuyu Translator</h1>

<input
    type="text"
    id="text"
    placeholder="Enter word or phrase"
>

<button onclick="startVoice()">
🎤 Speak
</button>

<select id="source">
    <option value="english">English</option>
    <option value="swahili">Swahili</option>
    <option value="kikuyu">Kikuyu</option>
</select>

<button onclick="swapLanguages()">
🔄 Swap Languages
</button>

<select id="target">
    <option value="kikuyu">Kikuyu</option>
    <option value="swahili">Swahili</option>
    <option value="english">English</option>
</select>

<button onclick="translateText()">
Translate
</button>

<div id="result"></div>

</div>

<script>

function startVoice() {

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert("Speech recognition is not supported in this browser.");
        return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-US";

    recognition.onresult = function(event) {

        document.getElementById("text").value =
            event.results[0][0].transcript;
    };

    recognition.onerror = function(event) {
        alert("Microphone error: " + event.error);
    };

    recognition.start();
}

function swapLanguages() {

    let source = document.getElementById("source");
    let target = document.getElementById("target");

    let temp = source.value;

    source.value = target.value;
    target.value = temp;
}

async function translateText() {

    let text =
        document.getElementById("text").value;

    let source =
        document.getElementById("source").value;

    let target =
        document.getElementById("target").value;

    let response = await fetch(
        `/translate?text=${encodeURIComponent(text)}&source=${source}&target=${target}`
    );

    let data = await response.json();

    document.getElementById("result").innerHTML =
        data.translation;

    let speech =
        new SpeechSynthesisUtterance(
            data.translation
        );

    window.speechSynthesis.speak(speech);
}

</script>

</body>
</html>
"""


@app.get("/translate")
def translate(text: str, source: str, target: str):

    text = text.strip().lower()

    # Exact phrase match
    for _, row in df.iterrows():

        source_terms = [
            str(term).strip().lower()
            for term in str(row[source]).split(";")
        ]

        for term in source_terms:

            if text == term:

                return {
                    "translation":
                    str(row[target]).split(";")[0].strip()
                }

    # Word-by-word translation
    words = text.split()

    translated = []

    for word in words:

        found = False

        for _, row in df.iterrows():

            source_terms = [
                str(term).strip().lower()
                for term in str(row[source]).split(";")
            ]

            if word in source_terms:

                translated.append(
                    str(row[target]).split(";")[0].strip()
                )

                found = True
                break

        if not found:
            translated.append(word)

    return {
        "translation": " ".join(translated)
    }
