from ollama import chat

query = "В среду нужно вынести мусор и выгулять собаку"
user_prompt = '''Из запроса "''' + query + '''" извлеки задания в следующем формате '{"task": "текстовое описание задания", "date": "дата выполнения задания"}' и в одном списке JSON. Respond only with valid JSON list. Do not write an introduction or summary.'''

user_prompt = "Hello!"
responce = chat(model="deepseek-r1:latest", messages=[{"role": "user", "content": user_prompt}])
print(responce.message.content)
