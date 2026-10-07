import sys,os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
F=sys.argv[1]; out=sys.argv[2]
for n,f in [("PFBlack","PF-Black.ttf"),("PFItal","PF-Italic.ttf"),("PFBold","PF-Bold.ttf"),("Inter","Inter-SemiBold.ttf")]:
    pdfmetrics.registerFont(TTFont(n,os.path.join(F,f)))
NAVY,GOLD,IVORY=HexColor("#0F1A2E"),HexColor("#B08A3E"),HexColor("#F4EDE0")
IN=72; W=6.5*IN; C=W/2
R_BLEED=3.25*IN   # 6.5" circle incl 1/4" bleed
R_CUT=3.0*IN      # 6" finished circle
c=canvas.Canvas(out,pagesize=(W,W),initialFontName="Inter",initialFontSize=10)
c.setTitle("Valley Pawn - Dang You Look Fine - 6in circle")
c.setFillColor(NAVY); c.circle(C,C,R_BLEED,stroke=0,fill=1)
c.setStrokeColor(GOLD)
c.setLineWidth(3.2); c.circle(C,C,R_CUT-15,stroke=1,fill=0)
c.setLineWidth(0.8); c.circle(C,C,R_CUT-23,stroke=1,fill=0)
def text(s,font,size,dy,color,track=0):
    c.setFillColor(color); c.setFont(font,size)
    w=pdfmetrics.stringWidth(s,font,size)+track*(len(s)-1)
    c.drawString(C-w/2,C-dy-6,s,charSpace=track)
text("VALLEY PAWN","Inter",9.5,-122,GOLD,3)
c.setStrokeColor(GOLD); c.setLineWidth(0.7); c.line(C-58,C+102,C+58,C+102)
text("Dang…","PFItal",27,-74,IVORY)
text("you look fine!","PFItal",27,-42,IVORY)
text("Smile","PFBlack",62,17,GOLD)
text("for the camera.","PFBold",25.5,58,IVORY)
c.setLineWidth(0.7); c.line(C-55,C-92,C-10,C-92); c.line(C+10,C-92,C+55,C-92)
c.setFillColor(GOLD); p=c.beginPath(); p.moveTo(C,C-88); p.lineTo(C+4,C-92); p.lineTo(C,C-96); p.lineTo(C-4,C-92); p.close(); c.drawPath(p,stroke=0,fill=1)
text("WHAT’S RIGHT IS RIGHT","Inter",6.8,112,GOLD,1.6)
c.showPage(); c.save()
