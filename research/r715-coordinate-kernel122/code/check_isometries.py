import sys
from pathlib import Path
import json
P=Path(sys.argv[1]).resolve()
w=json.loads((P/'raw_word.json').read_text());s=json.loads((P/'best_kernel_selection.json').read_text())
assert w['lines'][:8]==[[2*int(i==j) for j in range(8)] for i in range(8)]
isos=[]
for E in sorted(set(tuple(x[0]) for x in s)):
 assert len(E) in (1,2) and all(0<=x<8 for x in E)
 rest=[i for i in range(8) if i not in E];order=list(E)+rest
 Q=[[int(j==order[i]) for j in range(8)] for i in range(8)]
 assert [[sum(Q[i][k]*Q[j][k] for k in range(8)) for j in range(8)] for i in range(8)]==[[int(i==j) for j in range(8)] for i in range(8)]
 projected=[[sum(Q[k][i]*Q[k][j] for k in range(len(E),8)) for j in range(8)] for i in range(8)]
 assert projected==[[int(i==j and i not in E) for j in range(8)] for i in range(8)]
 isos.append({'entrance':list(E),'width':8-len(E),'orthogonal_rows':Q,'determinant_squareclass':1,'denominator_primes':[]})
report={'status':'PASS_COORDINATE_RESIDUAL_ISOMETRIES','ambient_form':'I_8/2 embedded in I_78/2','slot_form':'I_width/2','distinct_nonzero_entrances':len(isos),'entries':isos,'rank3_predecessor_rejected':'The old entrance [1,7,10,11,12,13] has Euclidean determinant squareclass2; it was replaced by [1,7]. No claim uses it.'}
(P/'isometry_certificate.json').write_text(json.dumps(report,indent=2));print(report['status'],len(isos))
