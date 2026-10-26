# -*- coding: utf-8 -*-
"""PyPopART(Adam Taranto, GPL-3.0-or-later, GitHub 소스 설치)로 같은 haplotype를 MJN, MSN, MST로 만들어 JSON으로 낸다.
network-v1.py가 이 파일을 별도 가상환경의 파이썬(-I)으로 부른다. 입력: FASTA 경로. 사용: python -I pypopart-run-v1.py in.fasta"""
import json, sys
from pypopart.core.sequence import Sequence
from pypopart.core.alignment import Alignment
from pypopart.algorithms import MedianJoiningNetwork, MinimumSpanningNetwork, MinimumSpanningTree

def read_fasta(p):
    seqs, name, buf = [], None, []
    for line in open(p, encoding='utf-8'):
        line = line.strip()
        if line.startswith('>'):
            if name is not None:
                seqs.append(Sequence(name, ''.join(buf)))
            name, buf = line[1:], []
        elif line:
            buf.append(line)
    if name is not None:
        seqs.append(Sequence(name, ''.join(buf)))
    return Alignment(seqs)

def summarize(net):
    g = net.graph
    meds = [n for n, d in g.nodes(data=True) if d.get('median_vector')]
    tot = sum(float(d.get('distance', d.get('weight', 1))) for _, _, d in g.edges(data=True))
    return dict(nodes=g.number_of_nodes(), medians=len(meds), edges=g.number_of_edges(), total_len=tot,
                median_seqs=sorted(g.nodes[n]['sequence'] for n in meds),
                degrees=sorted(d for _, d in g.degree()),
                weights=sorted(float(d.get('distance', d.get('weight', 1))) for _, _, d in g.edges(data=True)))

al = read_fasta(sys.argv[1])
out = {}
out['mjn'] = summarize(MedianJoiningNetwork(distance_method='hamming', epsilon=0).build_network(al))
out['msn'] = summarize(MinimumSpanningNetwork(distance_method='hamming', epsilon=0).build_network(al))
out['mst'] = summarize(MinimumSpanningTree(distance_method='hamming', algorithm='prim').build_network(al))
import pypopart
out['version'] = getattr(pypopart, '__version__', 'unknown')
print(json.dumps(out, ensure_ascii=False))
