import importlib.util,sys
spec=importlib.util.spec_from_file_location('t','ch10-tables-v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
s=''.join(open(f'parts/ch10-part{p}.md',encoding='utf8').read().rstrip()+'\n\n' for p in 'ABCD')
for k,f in (('@@T1@@',m.t1),('@@T2@@',m.t2),('@@T6@@',m.t6)):
    assert k in s,k
    s=s.replace(k,f())
assert '@@' not in s
open('ch10-v1.md','w',encoding='utf8').write(s)
print(len(s))
