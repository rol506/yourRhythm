from llama_cpp import Llama
from flask import Flask, jsonify
from dotenv import load_dotenv
import datetime
import re
import json
import locale
import os

load_dotenv()

locale.setlocale(locale.LC_ALL, "ru_RU.utf-8")

app = Flask("ai-server")
app.config["AI_PORT"] = int(os.environ.get("AI_PORT", "4222"))

if int(os.environ.get("DISABLE_AI", "0")) > 0:
    print("[INFO] AI is disabled by environment variable")
    exit(0)

llm = Llama(model_path="models/kokos.gguf")

@app.route("/processTasks/<query>")
def processRequest(query):
    systemPrompt = """Ты - умный помощник-трекер учебных задач. Твоя задача - проанализировать присланный пользователем текст и извлечь из него все ключевые задания.
    1) Установи дедлайн. Распознай дату и время выполнения. Если указано "завтра", "до пятницы" - переведи в конкретную дату. Если время не укзано, поставь дефолтное 23:59.
    2) Для каждой задачи отдельно составь объект JSON по такому формату {"date": "дата дедлайна в формате ДД/ММ/ГГГГ", "time": "время дедлайна", "task": "текстовое описание задания"}.
    Объекты разделяй между собой только запятыми.
    Текущая дата: """ + datetime.datetime.now().strftime("%A %d/%m/%Y")
    #userPrompt = """В среду нужно вынести мусор и выгулять собаку. В пятницу нужно подготовиться к дню рождения Саши"""
    userPrompt = query

    prompt = f"""<|begin_of_text|><|start_header_id|><|end_header_id|>

    Cutting Knowledge Date: December 2023
    Today Date: {datetime.datetime.now().strftime("%d %b %Y")}

    {systemPrompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

    {userPrompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    options = llm(prompt, max_tokens=0)
    print("\nRES:",options["choices"][0]["text"],"\n")
    found = re.findall(r"((\[[^\}]{3,})?\{s*[^\}\{]{3,}?:.*\}([^\{]+\])?)", options["choices"][0]["text"].replace("\n", "").replace("}{", "},{"))
    print("FOUND:",found)

    res = []
    for j in found:
        try:
            if len(j[0]) < 1:
                continue
            js = json.loads("[" + j[0] + "]")
            res += js
        except json.JSONDecodeError as e:
            print("error:", e)

    print("decoded " + str(len(res)))
    print("RESULT: ",res)
    return jsonify(res)

@app.route("/healthcheck")
@app.route("/")
def healthcheck():
    return "", 200

if __name__ == "__main__":
    app.run("0.0.0.0", app.config.get("AI_PORT", 4222), debug=True)
