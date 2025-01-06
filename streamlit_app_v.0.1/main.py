import streamlit as st
from PIL import Image
from pathlib import Path
icon_path = Path('.streamlit/Logo_azul_quadrada.PNG')
img_path = Path(".streamlit/Logo_goener_colorida.png")
#icon = '.streamlit/Logo_azul_quadrada.PNG'
st.set_page_config(page_title="Goener", layout="wide",page_icon=icon_path)
# Carregar a imagem com Pillow
img = Image.open(img_path)

# Redimensionar a imagem (alterando a altura e mantendo a proporção)
img = img.resize((int(img.width * (50 / img.height)), 50))  # Altura = 30 pixels

# Exibir a imagem redimensionada
st.image(img)
st.title("Análise de Ocorrência das Usinas")





