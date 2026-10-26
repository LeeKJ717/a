# -*- coding: utf-8 -*-
"""제1권 11장 원고(본문)와 주장 검증 장부(11.15절)를 점검기의 self 방식으로 점검하고,
실행 전에 적어 둔 예측(vol1-targets-v1.json)과 견준다. 모델이 필요 없다."""
import importlib.util, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('hc', os.path.join(HERE, 'halluccheck-v1.py'))
hc = importlib.util.module_from_spec(spec); spec.loader.exec_module(hc)
tg = json.load(open(os.path.join(HERE, 'vol1-targets-v1.json'), encoding='utf-8'))['targets']
inputs = {'본문': 'vol1-ch11-body-v1.md', '장부': 'vol1-ch11-ledger-v1.md'}
res = {}
for nm, fn in inputs.items():
    lines = hc.read_lines(os.path.join(HERE, 'input', fn))
    st = {}
    F = hc.run_self(lines, st)
    res[nm] = (lines, F, st)
    by = {}
    for x in F: by[x['code']] = by.get(x['code'], 0) + 1
    print('== %s 입력(%s, %d줄): 지적 %d건 %s' % (nm, fn, len(lines), len(F), dict(sorted(by.items()))))
    print('   검사한 항목 %s' % dict(sorted(st.items())))
print()
print('%-6s %-8s %-30s %-8s %-8s %s' % ('항목', '입력', '위치(줄)', '예측', '결과', '지적 부호'))
tline = {nm: set() for nm in inputs}
rows = []
for t in tg:
    for nm, key in (('본문', 'loc_body'), ('장부', 'loc_ledger')):
        lines, F, st = res[nm]
        ls = [i for i, l in enumerate(lines, 1) if re.search(t[key], l)]
        tline[nm] |= set(ls)
        codes = sorted({x['code'] for x in F if x['line'] in ls})
        pred = t['pred_body' if nm == '본문' else 'pred_ledger']
        hit = bool(codes)
        rows.append((t['id'], nm, ls, pred, hit, codes))
        print('%-6s %-8s %-30s %-8s %-8s %s' % (t['id'], nm, ','.join(map(str, ls[:4])) + ('…' if len(ls) > 4 else '') if ls else '(줄 못 찾음)', '지적' if pred else '없음', '지적됨' if hit else '없음', ','.join(codes) or '-'))
print()
for nm in inputs:
    sub = [r for r in rows if r[1] == nm]
    print('%s: 예측과 결과가 같은 항목 %d/%d, 지적된 항목 %d개(%s)' % (nm, sum(1 for r in sub if r[3] == r[4]), len(sub), sum(r[4] for r in sub), ', '.join(r[0] for r in sub if r[4]) or '없음'))
print()
print('--- 목표 줄 밖의 지적(분류 필요) ---')
for nm in inputs:
    lines, F, st = res[nm]
    for x in sorted(F, key=lambda x: (x['line'], x['code'])):
        if x['line'] in tline[nm]:
            continue
        print('[%s %s %s] %d줄: %s' % (nm, x['code'], x['sev'], x['line'], x['msg']))
        print('      문맥: %s' % x['ctx'][:150])
json.dump({nm: {'findings': res[nm][1], 'stats': res[nm][2]} for nm in inputs}, open(os.path.join(HERE, 'eval-vol1-result.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
