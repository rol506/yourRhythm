from llama_cpp import Llama
import datetime
import re
import json
import locale

locale.setlocale(locale.LC_ALL, "ru_RU.utf-8")
llm = Llama.from_pretrained(repo_id="bartowski/Meta-Llama-3.1-8B-Instruct-GGUF", filename="Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf", n_ctx=0)

systemPrompt = """Ты - умный помощник-трекер учебных задач. Твоя зажача - проанализировать присланный пользователем текст и извлечь из него все ключевые задания.
1) Установи дедлайн. Распознай дату и время выполнения. Если указано "завтра", "до пятницы" - переведи в конкретную дату. Если время не укзано, поставь дефолтное 23:59.
2) Сформулируй задание. Кратко и чётко перепиши суть задания.
3) Оцени приоритет. Если есть сдлва "срочно", "важно" или очень близкий дедлайн, поставь приоритет "Высокий". В остальных случаях - "Средний".
4) Для каждой задачи отдельно составь объект JSON по такому формату {"date": "дата дедлайна в формате ДД/ММ/ГГГГ", "time": "время дедлайна", "task": "текстовое описание задания", "priority": "приоритет"}.
Объекты разделяй между собой только запятыми.
Текущая дата: """ + datetime.datetime.now().strftime("%A %d/%m/%Y")
userPrompt = """В среду нужно вынести мусор и выгулять собаку. В пятницу нужно подготовиться к дню рождения Саши"""

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

