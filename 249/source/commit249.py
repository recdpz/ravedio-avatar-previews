from pathlib import Path
import subprocess,json,hashlib,datetime
P=Path(__file__).parent;R=P.parent/'floating138/mobile-preview'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()=='9cea4e0637473b9b73e9b9ea1c7fa0c7cdc0559a'
subprocess.run(['git','diff','--cached','--check'],cwd=R,check=True)
result=subprocess.run(['git','commit','-m','Restore hairstyle identity and coverage beneath pashmina'],cwd=R,capture_output=True,text=True);assert result.returncode==0,(result.stdout,result.stderr)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();print(result.stdout.splitlines()[0]);print(head)
q=json.loads((P/'progress249.json').read_text());q.update(status='Committed; publishing249',commit=head,manifest_sha256=hashlib.sha256((R/'249/manifest249.json').read_bytes()).hexdigest(),updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());(P/'progress249.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf8')
