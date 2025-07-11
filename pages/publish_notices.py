import streamlit as st
import subprocess
from pathlib import Path
import time

st.set_page_config(page_title="Publicar Notícias", layout="centered")
st.title("🚀 Publicar Notícias")

if st.button("Publicar Notícias"):
    status = st.empty()
    with st.spinner("Iniciando…"):
        PAGES_DIR   = Path(__file__).parent              # .../dtecflex-search/pages
        ROOT_DIR    = PAGES_DIR.parent                   # .../dtecflex-search
        SERVICE_DIR = ROOT_DIR / "transfer_dtec_file"    # onde está seu serviço
        script_path = SERVICE_DIR / "index.py"           

        status.text(f"🔍 Verificando script em:\n{script_path}")
        time.sleep(0.5)  # só pra dar tempo de ver o path na tela

        if not script_path.exists():
            status.error(f"❗ Script não encontrado em:\n{script_path}")
            st.stop()

        python_bin = "python3"   # ou o caminho do seu venv, se for o caso
        cmd = [python_bin, "-u", str(script_path)]
        status.text(f"▶️ Executando:\n{' '.join(cmd)}")
        time.sleep(0.5)

        proc = subprocess.Popen(
            cmd,
            cwd=str(SERVICE_DIR),     # garante que ele leia o .env correto
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        saw_output = False
        for line in proc.stdout:
            saw_output = True
            status.text(line.rstrip())

        if not saw_output:
            status.warning("⚠️ Nenhuma linha de saída capturada do processo!")

        proc.wait()

    if proc.returncode == 0:
        st.success("👍 Processo finalizado com sucesso!")
    else:
        st.error(f"❌ Processo saiu com código {proc.returncode}")
