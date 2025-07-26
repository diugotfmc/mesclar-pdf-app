import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import io
st.set_page_config(page_title="Mesclagem PDFs para RL", layout="wide")
st.title("📘 Mesclagem de PDFs para Relatório de Medição")
# ===============================
# INTERFACE DO USUÁRIO
# ===============================
st.subheader("📌 PDF Principal")
pdf_mae_file = st.file_uploader("Selecione o Relatório de Medição", type=["pdf"])
st.markdown("---")
# Uploads por capítulo
capitulos = {}
for i in range(6):
   st.markdown(f"### 📎 Anexo {i+1}")
   files = st.file_uploader(f"PDFs para o Anexo {i+1}", type=["pdf"], accept_multiple_files=True, key=f"cap_{i+1}")
   capitulos[f"cap_{i+1}"] = files
st.markdown("---")
# Coordenadas da numeração
st.subheader("✍️ Posição da Numeração (X e Y)")
colx, coly = st.columns(2)
with colx:
   pos_x = st.number_input("Coordenada X", min_value=0, max_value=1000, value=503)
with coly:
   pos_y = st.number_input("Coordenada Y", min_value=0, max_value=1000, value=779)
# Nome do arquivo final
nome_arquivo = st.text_input("📝 Nome do arquivo final (sem .pdf)", value="Relatorio_Final")

# ===============================
# FUNÇÕES DE PROCESSAMENTO
# ===============================
def processar_pdfs(pdf_mae_file, capitulos, pos_x, pos_y):
   reader = PdfReader(pdf_mae_file)
   total_paginas = len(reader.pages)
   if total_paginas < 6:
       raise Exception("O PDF principal precisa ter pelo menos 6 páginas para conter as capas dos capítulos.")
   # Dividir PDF Mãe em corpo e capas
   corpo_principal = reader.pages[:-6]  # Todas exceto as 6 últimas
   capas = reader.pages[-6:]            # Últimas 6 páginas
   # Construir o PDF final
   paginas_finais = []
   indices_mae_para_enum = []
   # Adiciona corpo do PDF mãe (com enumeração)
   for i, pagina in enumerate(corpo_principal):
       paginas_finais.append(pagina)
       indices_mae_para_enum.append(len(paginas_finais) - 1)
   # Para cada capítulo, adiciona capa + anexos
   for i in range(6):
       capa = capas[i]
       paginas_finais.append(capa)
       indices_mae_para_enum.append(len(paginas_finais) - 1)
       arquivos_anexos = capitulos.get(f"cap_{i+1}", [])
       for file in arquivos_anexos:
           leitor_anexo = PdfReader(file)
           for pagina_anexo in leitor_anexo.pages:
               paginas_finais.append(pagina_anexo)
               # Não adiciona anexos à lista de páginas a serem numeradas
   # Criar PDF temporário com todas as páginas mescladas
   writer_temp = PdfWriter()
   for pagina in paginas_finais:
       writer_temp.add_page(pagina)
   temp_bytes = io.BytesIO()
   writer_temp.write(temp_bytes)
   temp_bytes.seek(0)
   return adicionar_numeracao(temp_bytes, indices_mae_para_enum, pos_x, pos_y)
def adicionar_numeracao(pdf_stream, indices_para_numerar, pos_x, pos_y):
   reader = PdfReader(pdf_stream)
   writer = PdfWriter()
   total_paginas = len(reader.pages)
   for i, pagina in enumerate(reader.pages):
       if i in indices_para_numerar:
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
# Botão de geração
if st.button("🚀 Gerar Relatório Final"):
   if not pdf_mae_file:
       st.error("⚠️ PDF principal é obrigatório.")
   else:
       try:
           output_pdf = processar_pdfs(pdf_mae_file, capitulos, pos_x, pos_y)
           st.success("✅ PDF Gerado com Sucesso!")
           st.download_button(
               label="📥 Baixar PDF Final",
               data=output_pdf,
               file_name=f"{nome_arquivo.strip()}.pdf",
               mime="application/pdf"
           )
       except Exception as e:
           st.error(f"❌ Erro ao processar: {e}")
# ===============================
# RODAPÉ DE AUTORIA
# ===============================
st.markdown(
   """
<style>
   .rodape {
       position: fixed;
       bottom: 10px;
       left: 0;
       width: 100%;
       text-align: center;
       font-size: 13px;
       color: #888888;
       z-index: 100;
   }
</style>
<div class="rodape">
       Criado por: <strong>Diugo Silvano</strong>
</div>
   """,
   unsafe_allow_html=True
)