import json,sys
d=json.load(sys.stdin)
for k,v in d.items(): print(k, v)
