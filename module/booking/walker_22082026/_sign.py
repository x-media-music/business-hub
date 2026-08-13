from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader, PdfWriter
import io
from PIL import Image

SIG="/sessions/determined-funny-brahmagupta/mnt/business_hub_Dirk_STARTER/module/buchhaltung/eingang_event/_sig.png"
SRC="DOC160726-001.pdf"
OUT="Hofbraeu-Regiment-Vertrag-Schwieberdingen-2026-08-22_gegengezeichnet.pdf"

W,H=595,842
buf=io.BytesIO()
c=canvas.Canvas(buf,pagesize=(W,H))
# Datum nach "Stuttgart, den"
c.setFont("Helvetica",11)
c.drawString(440, H-536, "23.07.26")
# Unterschrift ueber V2-Linie
im=Image.open(SIG)
sw=100; sh=sw*im.size[1]/im.size[0]   # ~60
from reportlab.lib.utils import ImageReader
c.drawImage(ImageReader(SIG), 455, 252, width=sw, height=sh, mask='auto')
c.showPage(); c.save(); buf.seek(0)

overlay=PdfReader(buf).pages[0]
r=PdfReader(SRC); w=PdfWriter()
for i,p in enumerate(r.pages):
    if i==1:
        p.merge_page(overlay)
    w.add_page(p)
with open(OUT,"wb") as f: w.write(f)
print("geschrieben:",OUT)
