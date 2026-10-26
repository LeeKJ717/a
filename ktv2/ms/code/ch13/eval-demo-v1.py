# -*- coding: utf-8 -*-
"""시연 출력(demo-model-output-v1.md)에 점검기를 실행하고, 실행 전에 적어 둔 정답 목록과 견준다.
사용: python eval-demo-v1.py [원문 경로]   (기본: input/vol1-ch11-sec3-v1.md)"""
import importlib.util, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('hc', os.path.join(HERE, 'halluccheck-v1.py'))
hc = importlib.util.module_from_spec(spec); spec.loader.exec_module(hc)
src_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'input', 'vol1-ch11-sec3-v1.md')
mline = hc.read_lines(os.path.join(HERE, 'demo-model-output-v1.md'))
sline = hc.read_lines(src_path)
key = json.load(open(os.path.join(HERE, 'demo-answer-key-v1.json'), encoding='utf-8'))['items']
stats = {}
F = hc.run_verify(mline, sline, stats)
byline = {}
for x in F:
    byline.setdefault(x['line'], []).append(x)
print('원문: %s (%d줄), 모델 출력(시연값): %d줄' % (os.path.relpath(src_path, HERE), len(sline), len(mline)))
print('점검기 지적 %d건, 검사 항목 %s' % (len(F), dict(sorted(stats.items()))))
print()
covered = set()
rows = []
for it in key:
    ls = [i for i, l in enumerate(mline, 1) if re.search(it['loc'], l)]
    if len(ls) != 1:
        print('!! 위치 표지가 한 줄에 맞지 않음', it['id'], ls); sys.exit(2)
    ln = ls[0]; covered.add(ln)
    got = byline.get(ln, [])
    codes = sorted({x['code'] for x in got})
    hit = bool(set(codes) & set(it['expect'])) if it['expect'] else bool(codes)
    rows.append((it, ln, codes, hit))
print('%-4s %-22s %4s %-14s %-8s %-6s %s' % ('번호', '종류', '줄', '지적 부호', '예측', '결과', '내용'))
for it, ln, codes, hit in rows:
    if it['kind'] == '정상':
        res = '오탐' if codes else '정상'
    else:
        res = '찾음' if hit else '못 찾음'
    print('%-4s %-22s %4d %-14s %-8s %-6s %s' % (it['id'], it['kind'][:14], ln, ','.join(codes) or '-', '찾을것' if it['pred'] else '못찾을것', res, it['what'][:46]))
print()
inj = [r for r in rows if r[0]['kind'].startswith('심은 오류') and not r[0]['kind'].endswith('못 찾음)')]
und = [r for r in rows if r[0]['kind'].endswith('못 찾음)')]
mild = [r for r in rows if r[0]['kind'] == '가벼운 변형']
src = [r for r in rows if r[0]['kind'].startswith('원문 결함')]
ctl = [r for r in rows if r[0]['kind'] == '정상']
print('찾을 수 있게 설계한 심은 오류 %d개 중 %d개 지적' % (len(inj), sum(r[3] for r in inj)))
print('가벼운 변형 %d개 중 %d개 지적' % (len(mild), sum(r[3] for r in mild)))
print('설계상 못 찾는 심은 오류 %d개 중 %d개 지적' % (len(und), sum(r[3] for r in und)))
print('원문 결함의 충실한 옮김 %d개 중 %d개 지적' % (len(src), sum(r[3] for r in src)))
print('정상 줄 %d개 중 지적이 붙은 줄(오탐) %d개' % (len(ctl), sum(1 for r in ctl if r[2])))
extra = sorted(set(byline) - covered)
print('정답 목록에 없는 줄의 지적: %s' % (extra or '없음'))
for ln in extra:
    for x in byline[ln]:
        print('   [%s] %d줄 %s' % (x['code'], ln, x['msg']))
print()
print('--- 지적 전체 ---')
for x in sorted(F, key=lambda x: (x['line'], x['code'])):
    print('[%s %s] %d줄: %s' % (x['code'], x['sev'], x['line'], x['msg']))
json.dump({'rows': [{'id': r[0]['id'], 'kind': r[0]['kind'], 'line': r[1], 'codes': r[2], 'hit': r[3], 'pred': r[0]['pred']} for r in rows], 'stats': stats, 'n_findings': len(F)}, open(os.path.join(HERE, 'eval-demo-result%s.json' % ('-wide' if 'sec3' not in src_path else '')), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
