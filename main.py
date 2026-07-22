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
        <title>English-Swahili-Kikuyu Translator</title>

        <style>
            body{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }

            input, select{
                width:100%;
                padding:10px;
                margin-top:10px;
                margin-bottom:10px;
            }

            button{
                padding:10px 20px;
                cursor:pointer;
            }

            #result{
                margin-top:20px;
                font-size:24px;
                font-weight:bold;
            }
        </style>
    </head>

    <body>

    <h1>English • Swahili • Kikuyu Translator</h1>

    <input
        type="text"
        id="text"
        placeholder="Enter word or phrase"
    >

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

    <script>

    async function translateText(){

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
    }

    </script>

    </body>
    </html>
    """


@app.get("/translate")
def translate(text: str, source: str, target: str):

    text = text.strip().lower()

    # Try exact phrase first
    for _, row in df.iterrows():

        source_terms = [
            term.strip().lower()
            for term in str(row[source]).split(";")
        ]

        for term in source_terms:
            if text == term:
                return {
                    "translation":
                    str(row[target]).split(";")[0].strip()
                }

    # Otherwise translate word by word
    words = text.split()

    translated = []

    for word in words:

        found = False

        for _, row in df.iterrows():

            source_terms = [
                term.strip().lower()
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
