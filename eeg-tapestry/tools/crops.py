# crops.py OUT.jpg TARGET A B  -> 3 native 360px crops per image, columns T|A|B
import sys; from PIL import Image, ImageDraw
out,*ps=sys.argv[1:]; ims=[Image.open(p).convert("RGB") for p in ps]; h=min(i.height for i in ims+[Image.open(ps[0])]); h=min(h,2480)
regs=[(40,int(h*.12)),(300,int(h*.45)),(500,int(h*.8))]; S=Image.new("RGB",(3*370,3*370+20),"white"); d=ImageDraw.Draw(S)
for c,(lab,im) in enumerate(zip(["TARGET","A","B"],ims)):
    d.text((c*370+4,4),lab,fill="black")
    for r,(x,y) in enumerate(regs): S.paste(im.crop((x,y,x+360,y+360)),(c*370,20+r*370))
S.save(out,quality=90); print(out)
