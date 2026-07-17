import os
import io
import socket
from flask import Flask, request, send_file, render_template_string
from rembg import remove
from PIL import Image

app = Flask(__name__)

# Ler o arquivo index.html automaticamente
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
        # 1. Abre a imagem enviada pelo celular
        img_original = Image.open(file.stream)
        
        # 2. Remove o fundo
        img_sem_fundo = remove(img_original)
        
        # 3. Cria o fundo branco do mesmo tamanho
        fundo_branco = Image.new("RGBA", img_sem_fundo.size, "WHITE")
        fundo_branco.paste(img_sem_fundo, (0, 0), img_sem_fundo)
        
        # 4. Converte para salvar em JPG
        imagem_final = fundo_branco.convert("RGB")
        
        # 5. Salva na memória para enviar de volta
        img_io = io.BytesIO()
        imagem_final.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/jpeg')
    except Exception as e:
        return f"Erro no processamento: {str(e)}", 500

def obter_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == '__main__':
    # A nuvem define a porta automaticamente pela variável de ambiente PORT
    porta = int(os.environ.get("PORT", 5000))
    # Rodamos em 0.0.0.0 para aceitar conexões externas da nuvem
    app.run(host='0.0.0.0', port=porta)