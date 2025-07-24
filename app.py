import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import io
st.set_page_config(page_title="Mesclagem de PDFs para RL", layout="wide")
st.title("📄 Mesclagem de PDFs para Relatório de Medição ")
# ===============================
# INTERFACE DO USUÁRIO
# ===============================
col1, col2 = st.columns(2)
with col1:
   st.subheader("📌 PDF principal")
   pdf_mae_file = st.file_uploader("Selecione o Relatório de Medição", type=["pdf"])
with col2:
   st.subheader("📎 PDFs Anexos")
   anexos = st.file_uploader("Selecione até 6 PDFs adicionais", type=["pdf"], accept_multiple_files=True)
   posicoes = st.text_input("Posições para inserir (ex: 2,5,8):")
st.markdown("---")
# Coordenadas da numeração
st.subheader("✍️ Posição da Numeração (X e Y)")
colx, coly = st.columns(2)
with colx:
   pos_x = st.number_input("Coordenada X", min_value=0, max_value=1000, value=503)
with coly:
   pos_y = st.number_input("Coordenada Y", min_value=0, max_value=1000, value=779)
# Nome do arquivo final
nome_arquivo = st.text_input("📝 Nome do arquivo final (sem .pdf)", value="PDF_Final")

# ===============================
# FUNÇÕES DE PROCESSAMENTO
# ===============================
def processar_pdfs(pdf_mae_file, anexos, posicoes, pos_x, pos_y):
   pdf_mae = PdfReader(pdf_mae_file)
   paginas_mae = list(pdf_mae.pages)
   total_paginas_mae = len(paginas_mae)
   # Lista para guardar os índices onde estão as páginas do PDF mãe após inserção
   indices_mae_no_final = list(range(total_paginas_mae))
   # Insere anexos nas posições
   for file, pos in sorted(zip(anexos, posicoes), key=lambda x: x[1]):
       leitor = PdfReader(file)
       paginas_anexo = list(leitor.pages)
       # Inserir anexo nas páginas
       paginas_mae[pos:pos] = paginas_anexo
       # Corrigir os índices das páginas do PDF mãe após a inserção
       indices_mae_no_final = [
           i if i < pos else i + len(paginas_anexo)
           for i in indices_mae_no_final
       ]
   # Escreve o PDF temporário
   writer_temp = PdfWriter()
   for pagina in paginas_mae:
       writer_temp.add_page(pagina)
   temp_bytes = io.BytesIO()
   writer_temp.write(temp_bytes)
   temp_bytes.seek(0)
   return adicionar_numeracao_somente_mae(temp_bytes, indices_mae_no_final, pos_x, pos_y)
def adicionar_numeracao_somente_mae(pdf_stream, indices_para_numerar, pos_x, pos_y):
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
# Botão principal
if st.button("🚀 Gerar PDF Final"):
   if not pdf_mae_file or not anexos or not posicoes:
       st.error("Por favor, envie o PDF principal, os anexos e as posições.")
   else:
       try:
           pos_list = [int(x.strip()) for x in posicoes.split(",")]
           if len(pos_list) != len(anexos):
               st.warning("⚠️ O número de posições deve ser igual ao número de PDFs anexados.")
           else:
               output_pdf = processar_pdfs(pdf_mae_file, anexos, pos_list, pos_x, pos_y)
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