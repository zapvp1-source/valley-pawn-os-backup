import qrcode
from PIL import Image, ImageDraw, ImageFont
DPI=100; W,H=120*DPI,48*DPI
RED=(200,16,46); WHITE=(255,255,255); BLACK=(0,0,0); GOLD=(218,165,32)
F='/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'; FM='/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf'
im=Image.new('RGB',(W,H),BLACK); d=ImageDraw.Draw(im)
# red frame, inset 1.5in from edge for hem/grommets
m=int(1.5*DPI); t=int(0.5*DPI)
d.rectangle([m,m,W-m,H-m],outline=RED,width=t)
# QR panel on right
qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,border=2,box_size=10)
qr.add_data('https://rocketpawnjewelry.com/?utm_source=banner&utm_medium=sign&utm_campaign=coming_soon'); qr.make(fit=True)
q=qr.make_image(fill_color='black',back_color='white').convert('RGB')
qs=int(26*DPI); q=q.resize((qs,qs),Image.NEAREST)
qx=W-m-int(3*DPI)-qs; qy=int(6.5*DPI)
im.paste(q,(qx,qy))
f=ImageFont.truetype(FM,int(2.1*DPI))
cap='Scan for opening-day deals'
cw=d.textlength(cap,font=f); d.text((qx+(qs-cw)/2, qy+qs+int(1.2*DPI)),cap,font=f,fill=WHITE)
# left content area
L=m+int(4*DPI); R=qx-int(4*DPI); cw_area=R-L
def center(text,font,y,fill):
    w=d.textlength(text,font=font); d.text((L+(cw_area-w)/2,y),text,font=font,fill=fill)
fC=ImageFont.truetype(F,int(7.0*DPI)); center('COMING SOON',fC,int(4.0*DPI),RED)
logo=Image.open('../../logo_final/kit/rocket_pawn_logo_dark_bg.png').convert('RGBA')
lw=cw_area; lh=int(logo.height*lw/logo.width)
logo=logo.resize((lw,lh),Image.LANCZOS)
ly=int(14.5*DPI); im.paste(logo,(L,ly),logo)
fS=ImageFont.truetype(F,int(3.6*DPI)); center('PAWN LOANS  •  GOLD & SILVER  •  JEWELRY',fS,ly+lh+int(2.0*DPI),WHITE)
fU=ImageFont.truetype(F,int(4.6*DPI)); center('rocketpawnjewelry.com',fU,ly+lh+int(8.6*DPI),GOLD)
im.save('rocket_pawn_banner_4x10_coming_soon.pdf',resolution=DPI)
im.resize((W//10,H//10),Image.LANCZOS).save('preview.jpg',quality=88)
im.save('rocket_pawn_banner_4x10_coming_soon.jpg',quality=92,dpi=(DPI,DPI))
print(lw,lh,ly+lh+int(8.6*DPI)+int(4.6*DPI)*1.3, H-m)
