import json,sys
sys.stdout.reconfigure(encoding='utf-8')
d=json.load(open(r'c:\Users\Admin1\Desktop\无穷复制\知源问病\data\acupoints.json',encoding='utf-8'))['acupoints']
for kw in ['髀关','气穴','气冲','归来','复溜','交信','水泉','照海','梁门','天枢','外丘','阳交']:
    hit=[a for a in d if a['name']==kw]
    if hit:
        a=hit[0]; print(kw.ljust(6), a['id'], a.get('code'), '|', a.get('location','')[:40])
    else: print(kw.ljust(6), '(无)')
