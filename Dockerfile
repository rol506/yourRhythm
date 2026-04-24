FROM python:3.14
WORKDIR /yourRhythm
RUN apt update && apt install gcc openssl
RUN mkdir models
RUN curl -L --output models/kokos2.gguf "https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 4421
EXPOSE 4222
CMD ["python", "src/flsite.py", "&", "python", "src/AIServer.py"]
