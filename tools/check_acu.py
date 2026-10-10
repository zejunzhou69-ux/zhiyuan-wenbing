import json,sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')
d=json.load(open(r'c:\Users\Admin1\Desktop\无穷复制\知源问病\data\acupoints.json',encoding='utf-8'))['acupoints']
print('总穴数:',len(d))
print('ID唯一:',len({a['id'] for a in d})==len(d))
print('code唯一:',len({a.get('code') for a in d})==len(d))
print('穴名唯一:',len({a['name'] for a in d})==len(d))
req=('id','name','code','meridian','location','anatomy_note','depth_limit','indications','needling','contraindication')
bad=[(a['name'],k) for a in d for k in req if not a.get(k) or (isinstance(a.get(k),list) and not a[k])]
print('字段缺失:',len(bad),bad[:5])
c=Counter(a.get('meridian') for a in d)
S={'手太阴肺经':11,'手阳明大肠经':20,'足阳明胃经':45,'足太阴脾经':21,'手少阴心经':9,'手太阳小肠经':19,'足太阳膀胱经':67,'足少阴肾经':27,'手厥阴心包经':9,'手少阳三焦经':23,'足少阳胆经':44,'足厥阴肝经':23,'任脉':24,'督脉':28}
print()
print('经络          现有  要求  缺口')
tot=0
for m,n in S.items():
    g=n-c[m]; tot+=max(0,g)
    print(f'{m:<12}{c[m]:>5}{n:>5}{g:>6}')
print()
print(f'十四经穴 {sum(c[m] for m in S)}/361   剩余缺口 {tot}')
