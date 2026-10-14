from pathlib import Path
import subprocess,sys,time,json
root=Path(__file__).resolve().parent
scripts=['schedule/sequential_union.py','schedule/test_transpose_controls.py','schedule/test_failure_controls.py','review/independent_review.py','review/direct_scalar_audit.py','review/cost_audit.py']
start=time.time()
for script in scripts:
 print('RUN',script,flush=True)
 subprocess.run([sys.executable,str(root/script)],check=True,cwd=root)
receipt={'status':'PASS_CLEAN_RELOCATED_RUN','scripts':scripts,'elapsed_seconds':round(time.time()-start,3)}
(root/'CLEAN-RUN.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
