# sheet.py OUT.jpg label=path ...  -> side-by-side, all cropped to target height and scaled to 1200 tall
import sys; from PIL import Image, ImageDraw
items=[a.split('=',1) for a in sys.argv[2:]]; H=1200; ims=[]
for lab,p in items:
    im=Image.open(p).convert('RGB'); im=im.crop((0,0,im.width,min(im.height,2480))); ims.append((lab,im.resize((int(im.width*H/im.height),H))))
W=sum(i.width+20 for _,i in ims); S=Image.new('RGB',(W,H+30),'white'); d=ImageDraw.Draw(S); x=0
for lab,i in ims: S.paste(i,(x,30)); d.text((x+4,8),lab,fill='black'); x+=i.width+20
S.save(sys.argv[1],quality=88); print(sys.argv[1],S.size)
