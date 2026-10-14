#!/usr/bin/env python3
"""Replay this authored supplement in an isolated temporary directory."""
from pathlib import Path
import json, os, shutil, subprocess, sys, tempfile
if not __debug__:
    raise RuntimeError('Run without -O/-OO; verification requires assertions.')
root=Path(__file__).resolve().parent
env=dict(os.environ);env.pop('PYTHONOPTIMIZE',None)
scripts=['layout/schedule/sequential_union.py','layout/schedule/test_transpose_controls.py','layout/schedule/test_failure_controls.py','layout/review/independent_review.py','layout/review/direct_scalar_audit.py','layout/review/cost_audit.py','rhs/check_interface.py','prefix/EXACT_CHECK.py','prefix/review/INDEPENDENT_CHECK.py']
with tempfile.TemporaryDirectory(prefix='sparse-union-replay-') as td:
    work=Path(td)/'package'
    shutil.copytree(root,work,ignore=shutil.ignore_patterns('__pycache__'))
    for script in scripts:
        print('RUN',script,flush=True)
        subprocess.run([sys.executable,str(work/script)],cwd=work,env=env,check=True,timeout=600)
    a=json.loads((work/'layout/schedule/RESULTS.json').read_text())
    if (a['support_tuples'],a['basis_columns'],a['complete_exhaustive'])!=(5036,281312,True):
        raise RuntimeError('Exhaustive coverage differs from declared scope.')
    b=json.loads((work/'rhs/RESULTS.json').read_text())
    if (b['status'],b['layout_cases'],b['algebra_cases'])!=('PASS',48,8):
        raise RuntimeError('RHS coverage differs from declared scope.')
print(json.dumps({'status':'PASS_SCOPED_SUPPLEMENT_REPLAY','scripts':scripts,'new_kappa':False,'full_multiplication_theorem':False},indent=2))
