import os
import io
from flask import Flask, request, send_file, render_template_string
from rembg import remove, new_session
from PIL import Image

# Inicia o Flask
app = Flask(__name__)

# Criamos a sessão com o modelo 'u2netp' (o mais leve)
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
        # Abre a imagem e força conversão para RGB para evitar erros de cor
        img = Image.open(file.stream).convert('RGB')
        
        # Reduz resolução para 600x600 para garantir que caiba na memória RAM do Render
        img.thumbnail((600, 600))
        
        # Remove o fundo
        img_sem_fundo = remove(img, session=sessao_leve)
        
        # Converte para RGBA para garantir a transparência do PNG
        img_final = img_sem_fundo.convert('RGBA')
        
        # Salva o resultado no formato PNG com otimização
        output = io.BytesIO()
        img_final.save(output, format='PNG', optimize=True)
        output.seek(0)
        
        return send_file(output, mimetype='image/png')
    
    except Exception as e:
        # Retorna o erro específico se falhar
        return f"Erro ao processar imagem: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
