# 1. Imagem Base (Oficial do Python, versão "slim")
FROM python:3.10-slim

# 2. Define o diretório de trabalho
WORKDIR /app

# 3. Copia e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia o resto do seu código (app.py, index.html)
COPY . .

# 5. Expõe a porta padrão (8080) como documentação.
#    O Google Cloud Run vai ignorar isso e usar a variável $PORT.
EXPOSE 8080

# 7. Comando para rodar a aplicação
#    Usa a forma "shell" (sem colchetes) para que a variável $PORT
#    possa ser lida do ambiente.
#
#    ${PORT:-8080} significa:
#    - Use a variável $PORT se ela existir (definida pelo Google Cloud).
#    - Se não existir (ex: rodando localmente), use 8080 como padrão.
CMD uvicorn app:app --host 0.0.0.0 --port $PORT
