import io, pymupdf
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader, PdfWriter
from PIL import Image

UP="/sessions/eloquent-inspiring-clarke/mnt/Projects--uploads"
SIG=f"{UP}/Unterschrift-Dik Wöhrle.png"
STAMP=f"{UP}/stempel x-media music 2020.png"
SRC="_eingang/Vertrag Regiment 2027.pdf"
OUT="Hofbraeu-Regiment-Vertrag-Esslingen-2027-04-11_gegengezeichnet.pdf"

W,H=596,842
buf=io.BytesIO()
c=canvas.Canvas(buf,pagesize=(W,H))
# --- rechte Spalte "Vertragspartner 2" ---
# Datum nach "Stuttgart, den"
c.setFont("Helvetica",12)
c.drawString(372, 291, "13.08.26")
# Unterschrift Dirk Woehrle ueber der V2-Linie
sig=Image.open(SIG); sw=105; sh=sw*sig.size[1]/sig.size[0]
c.drawImage(ImageReader(SIG), 335, 245, width=sw, height=sh, mask='auto')
# Firmenstempel rechts daneben, ueberlappend
st=Image.open(STAMP); tw=140; th=tw*st.size[1]/st.size[0]
c.drawImage(ImageReader(STAMP), 442, 226, width=tw, height=th, mask='auto')
c.showPage(); c.save(); buf.seek(0)

overlay=PdfReader(buf).pages[0]
r=PdfReader(SRC); w=PdfWriter()
for i,p in enumerate(r.pages):
    if i==1:
        p.merge_page(overlay)
    w.add_page(p)
with open(OUT,"wb") as f: w.write(f)
print("geschrieben:",OUT)

# Kontroll-Render Seite 2
d=pymupdf.open(OUT)
d[1].get_pixmap(matrix=pymupdf.Matrix(150/72,150/72)).save("_check_p2.png")
Image.open("_check_p2.png").crop((0,1000,1242,1420)).save("_check_p2_crop.png")
print("render ok")
