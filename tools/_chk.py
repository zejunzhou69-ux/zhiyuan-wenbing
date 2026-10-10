import re,sys
sys.stdout.reconfigure(encoding='utf-8')
s=open('ap_t2a.py',encoding='utf-8').read()
print('大小:',len(s))
bad=[m.start() for m in re.finditer(chr(9888)+'{9,}',s)]
print('警告堆砌处:',len(bad))
tail=s.rstrip()[-60:]
print('结尾:',repr(tail))
print('语法检查:', 'OK' if compile(s,'ap_t2a.py','exec') else '')

