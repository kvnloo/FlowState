
import numpy as np, json, sys
from PIL import Image
B=sys.argv[1]
im=np.asarray(Image.open(B+'/inspo/measurement_large.jpg').convert('RGB')).astype(int)
sat=(im.max(2)-im.min(2))>60
cols=np.where(sat.mean(0)>0.5)[0]; rows=np.where(sat[:, cols.min():cols.max()].mean(1)>0.5)[0]
print('field x',cols.min(),cols.max(),'y',rows.min(),rows.max())
x0,x1,y0,y1=cols.min(),cols.max()+1,rows.min(),rows.max()+1
t=Image.open(B+'/inspo/measurement_large.jpg').convert('RGB').crop((x0,y0,x1,y1)); t.save(B+'/loop/target_field.png'); print(t.size)
