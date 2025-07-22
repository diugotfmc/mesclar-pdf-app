import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import io
st.set_page_config(page_title="Mesclar e Enumerar PDFs", layout="wide")
st.title("📄 Mesclar PDFs com Enumeração Personalizada")
# --- COLUNAS PARA INTERAÇÃO ---
col1, col2 = st.columns(2)
with col1:
   st.subheader("📌 Escolha o PDF Mãe")
   pdf_mae_file = st.file_uploader("Selecione o PDF principal", type=["pdf"])
with col2:
   st.subheader("📎 Anexar PDFs Adicionais")
   anexos = st.file_uploader("Selecione até 6 PDFs", type=["pdf"], accept_multiple_files=True)
   posicoes = st.text_input("Digite as posições (ex: 2,5,8,12):")
st.markdown("---")
# Coordenadas para numeração
st.subheader("✍️ Posição da Numeração (X e Y)")
colx, coly = st.columns(2)
with colx:
   pos_x = st.number_input("Coordenada X", min_value=0, max_value=1000, value=280)
with coly:
   pos_y = st.number_input("Coordenada Y", min_value=0, max_value=1000, value=800)

# =============================================
# FUNÇÕES DE PROCESSAMENTO
# =============================================
def processar_pdfs(pdf_mae_file, anexos, posicoes, pos_x, pos_y):
   pdf_mae = PdfReader(pdf_mae_file)
   paginas_mae = list(pdf_mae.pages)
   for file, pos in sorted(zip(anexos, posicoes), key=lambda x: x[1]):
       leitor = PdfReader(file)
       paginas_mae[pos:pos] = list(leitor.pages)
   writer_temp = PdfWriter()
   for pagina in paginas_mae:
       writer_temp.add_page(pagina)
   temp_bytes = io.BytesIO()
   writer_temp.write(temp_bytes)
   temp_bytes.seek(0)
   return adicionar_numeracao(temp_bytes, pos_x, pos_y)
def adicionar_numeracao(pdf_stream, pos_x, pos_y):
   reader = PdfReader(pdf_stream)
   writer = PdfWriter()
   total_paginas = len(reader.pages)
   for i, pagina in enumerate(reader.pages):
       largura = float(pagina.mediabox.width)
       altura = float(pagina.mediabox.height)
       packet = io.BytesIO()
       can = canvas.Canvas(packet, pagesize=(largura, altura))
       texto = f"{i + 1} de {total_paginas}"
       can.setFont("Helvetica", 12)
       can.drawString(pos_x, pos_y, texto)
       can.save()
       packet.seek(0)
       overlay = PdfReader(packet)
       pagina.merge_page(overlay.pages[0])
       writer.add_page(pagina)
   final_bytes = io.BytesIO()
   writer.write(final_bytes)
   final_bytes.seek(0)
   return final_bytes
# Botão de gerar
if st.button("🚀 Gerar PDF Final"):
   if not pdf_mae_file or not anexos or not posicoes:
       st.error("Por favor, envie o PDF mãe, os anexos e as posições.")
   else:
       try:
           pos_list = [int(x.strip()) for x in posicoes.split(",")]
           if len(pos_list) != len(anexos):
               st.warning("⚠️ O número de posições deve ser igual ao número de PDFs anexados.")
           else:
               # Processamento
               output_pdf = processar_pdfs(pdf_mae_file, anexos, pos_list, pos_x, pos_y)
               st.success("✅ PDF Gerado com Sucesso!")
               st.download_button(
                   label="📥 Baixar PDF Final",
                   data=output_pdf,
                   file_name="PDF_Final.pdf",
                   mime="application/pdf"
               )
       except Exception as e:
           st.error(f"❌ Erro ao processar: {e}")