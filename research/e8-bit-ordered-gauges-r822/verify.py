"""One standard-library entrypoint. Only independently written local scripts execute."""
import os,sys,json,hashlib,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
if sys.version_info < (3,10):raise SystemExit('Python 3.10 or newer required')
for item in json.load(open(P/'SOURCES.json')):
 assert hashlib.sha256((P/item['file']).read_bytes()).hexdigest()==item['sha256'],item['file']
for script in ['reconstruct.py','pools.py','synthesize.py','ordered_search.py','price111.py','price_ordered.py','mutations.py']:
 subprocess.run([sys.executable,'-B',str(P/script)],cwd=P,check=True)
for name in ['bit_r822.json','candidate111.json','candidate_ordered.json']:
 assert (P/name).read_bytes()==(P/'expected'/name).read_bytes(),name
manifest=P/'AUDIT_SCRIPTS.json'
if not manifest.exists():
 raise SystemExit('Local reconstruction and mutations passed; finite audit integration pending. No full admission claimed.')
env=os.environ.copy();env.update(E8_AUDIT_ROOT=str(P/'audit'),E8_DATA_ROOT=str(P),PYTHONDONTWRITEBYTECODE='1')
for script in json.load(open(manifest)):
 subprocess.run([sys.executable,str(P/'audit'/script)],cwd=P,env=env,check=True)
results={f.name:json.load(open(f)) for f in sorted((P/'audit').glob('*_results.json'))}
(P/'verification_results.json').write_text(json.dumps({'status':'PASS_SYMBOLIC_FINITE_CONTRACT_CHECKS','candidate_sha256':hashlib.sha256((P/'candidate_ordered.json').read_bytes()).hexdigest(),'audit_results':results,'scope':'No assembled kappa gain; inherited generic interfaces and no combined physical emitter remain explicit in README.'},indent=2))
print('PASS: reconstruction, exact local audits, packing, price, finite checks and mutations. Read README scope boundaries.')
