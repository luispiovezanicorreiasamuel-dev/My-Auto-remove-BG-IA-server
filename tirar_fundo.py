import os
import io
import socket
from flask import Flask, request, send_file, render_template_string
from rembg import remove, new_session
from PIL import Image

# Inicia o Flask
app = Flask(__name__)

# Criamos a sessão com o modelo 'u2netp' (o mais leve possível para economizar RAM)
# Isso evita o erro de "Ran out of memory"
sessao_leve = new_session("u2netp")

def ler_html():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.route('/')
def home():
    return render_template_string(ler_html())

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return "Nenhuma imagem enviada", 400
    
    file = request.files['image']
    if file.filename == '':
        return "Nenhuma imagem selecionada", 400

    try:
        # Abre a imagem enviada
        img = Image.open(file.stream)
        
        # Redimensiona a imagem para no máximo 1000x1000 pixels
        # Isso garante que fotos muito pesadas não estourem a RAM de 512MB
        img.thumbnail((1000, 1000))
        
        # Remove o fundo usando a sessão leve que criamos acima
        img_sem_fundo = remove(img, session=sessao_leve)
        
        # Salva o resultado no formato PNG em um buffer
        output = io.BytesIO()
        img_sem_fundo.save(output, format='PNG')
        output.seek(0)
        
        return send_file(output, mimetype='image/png')
    
    except Exception as e:
        # Se algo der errado, retorna o erro para você saber o motivo
        return f"Erro ao processar imagem: {str(e)}", 500

# Substitua o final do seu arquivo por este bloco:
if __name__ == '__main__':
    # O Render define a porta através de uma variável de ambiente chamada PORT
    # Se ela não existir, usamos a 5000 como padrão
    port = int(os.environ.get("PORT", 5000))
    # O host deve ser '0.0.0.0' para o Render conseguir acessar
    app.run(host='0.0.0.0', port=port)
