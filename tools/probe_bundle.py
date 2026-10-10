import re,sys,json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(r'c:\Users\Admin1\Desktop\无穷复制\知源问病')
for tag,f in [('local',ROOT/'static/js/bundle.js'),('online',ROOT/'online_bundle.js')]:
    if not f.exists(): print(tag,'文件不存在'); continue
    s=f.read_text(encoding='utf-8')
    m=re.search(r'window\.ZYW_BUNDLE\s*=\s*(\{.*\})\s*;?\s*$',s,re.S)
    print(f'--- {tag}: {len(s)} 字节')
    if not m: print('   解析失败'); continue
    d=json.loads(m.group(1))
    print('   顶层键:',list(d.keys()))
    for k,v in d.items():
        if isinstance(v,list): print(f'     {k}: {len(v)}')
