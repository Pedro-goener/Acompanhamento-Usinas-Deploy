import streamlit as st
from PIL import Image
import os
#Encontrando diretório atual
current_dir = os.path.dirname(os.path.abspath(__file__))
#Achando o caminho do icone
icon_path = os.path.join(current_dir,'.streamlit','Logo_azul_quadrada.PNG')
#Achando o caminho da logo
img_path = os.path.join(current_dir,'.streamlit','Logo_goener_colorida.png')
st.set_page_config(page_title="Goener", layout="wide",page_icon=icon_path)
# Carregar a imagem com Pillow
img = Image.open(img_path)

# Redimensionar a imagem (alterando a altura e mantendo a proporção)
img = img.resize((int(img.width * (50 / img.height)), 50))  # Altura = 30 pixels

# Exibir a imagem redimensionada
st.image(img)
st.title("Análise de Ocorrência das Usinas")





