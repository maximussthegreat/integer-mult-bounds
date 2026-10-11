#!/usr/bin/env python3
"""Clean-output verifier for a conditional mathematical component supplement.
Runs only newly authored checkers in code/, with frozen JSON as inert input.
"""
from pathlib import Path
import hashlib,json,gzip,shutil,subprocess,sys
if not __debug__:
    raise SystemExit('Verification requires assertions; do not run Python with -O or PYTHONOPTIMIZE.')
ROOT=Path(__file__).resolve().parent
if len(sys.argv)!=2:raise SystemExit('usage: python verify.py /absolute/new/output-directory')
out=Path(sys.argv[1]).resolve()
if out.exists():raise SystemExit('Refusing to reuse existing output: '+str(out))
manifest=json.loads((ROOT/'MANIFEST.json').read_text())
for name,want in manifest.items():
 p=ROOT/name
 if hashlib.sha256(p.read_bytes()).hexdigest()!=want:raise SystemExit('Input/code hash mismatch: '+name)
source=json.loads((ROOT/'SOURCE.json').read_text())
data=ROOT/'data'
assert hashlib.sha256((data/'R715_FP_final.json.gz').read_bytes()).hexdigest()==source['r715']['sha256']
assert json.loads(gzip.decompress((data/'R715_FP_final.json.gz').read_bytes()))==json.loads((data/'raw_word.json').read_text())
out.mkdir(parents=True)
for p in data.iterdir():
 if p.is_file():shutil.copyfile(p,out/p.name)
steps=['check_candidate.py','rebuild_mixed_frozen.py','replay_mixed.py','check_isometries.py','certify_packing.py','certify_moments.py','check_controls.py']
for name in steps:
 r=subprocess.run([sys.executable,'-I','-B',str(ROOT/'code'/name),str(out)],capture_output=True,text=True)
 (out/(name+'.log')).write_text(r.stdout+r.stderr)
 if r.returncode:
  print(r.stdout+r.stderr);raise SystemExit('FAILED '+name)
 print('PASS',name,flush=True)
# Require the exact frozen constructed words, events, ownership and frame data.
for name in ['kernel_word.json','mixed_word.json','mixed_records.json','frame_metadata.json','whole_slots.json','ownership.json']:
 assert (out/name).read_bytes()==(data/name).read_bytes(),('reconstruction byte mismatch',name)
for p in (ROOT/'evidence').glob('*.json'):
 assert json.loads((out/p.name).read_text())==json.loads(p.read_text()),('receipt mismatch',p.name)
receipt={'status':'PASS_SOURCE_BOUND_CONDITIONAL_COMPONENT_SUPPLEMENT','steps':steps,'source':source,'kappa':'1288410092125091/1000000000000000000','bit_lower':'1290072234211219280603/1000000000000000000000000','physical_scalar_prefix_bits':607,'charged_scalar_prefix_bits':640,'charged_three_level_bits':1920,'scope':['The607-bit quantity is a scalar physical-family envelope, not a complete routed/literal compiler-prefix certificate.','Finite invoice categories, correlated whole-call hosting and all inherited all-size compiler/cover/analytic hypotheses remain conditional.','The next grid point is rejected for this fixed six-bootstrap parameter choice only.','The complex endpoint is retained from pinned PR458; this entrypoint does not reconstruct that supplier.'],'source_tree_unchanged':True}
for name,want in manifest.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==want
(out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status']);print('Conditional component kappa = 0.001288410092125091');print('No complete routed/literal compiler-prefix proof is claimed.')
