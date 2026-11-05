"""Generate a small Pages-only branch without checking out or altering artwork.

Run from any directory: python tools/prepare-pages.py --source main --index ABSENT_PATH.
Review and push gh-pages, then use gh-pages / as the repository Pages source.
"""
from pathlib import Path
import argparse,json,os,subprocess,re
R=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--source',default='main');parser.add_argument('--index',required=True);args=parser.parse_args()
def git(*a,env=None,data=None):return subprocess.check_output(['git',*a],cwd=R,env=env,input=data)
source=git('rev-parse',args.source+'^{commit}').decode().strip();index=Path(args.index).resolve();assert not index.exists(),'Use a fresh index path; do not reuse the working index'
assert index != (R/'.git/index').resolve();index.parent.mkdir(parents=True,exist_ok=True)
env=dict(os.environ,GIT_INDEX_FILE=str(index));git('read-tree','--empty',env=env)
excluded={'.glb','.blend','.zip','.png','.exr'};entries=[];total=0;count=0
for row in git('ls-tree','-rz','--long','--full-tree',source).split(b'\0'):
 if not row:continue
 meta,path=row.split(b'\t',1);mode,kind,sha,size=meta.split();name=path.decode('utf8')
 if kind!=b'blob':raise RuntimeError('Unexpected non-blob entry: '+name)
 if Path(name).suffix.lower() in excluded or name.startswith('.github/'):continue
 entries.append(mode+b' '+sha+b'\t'+path+b'\0');total+=int(size);count+=1
assert total<300_000_000,('Unexpected Pages payload',total)
host=git('show',source+':asset-host.js').decode();asset_ref=re.search(r"const assetRef = '([0-9a-f]{40})';",host).group(1)
provenance=dict(source_commit=source,asset_commit=asset_ref,generated_branch='gh-pages',method='Exact source blobs with GLB/Blend/ZIP/PNG/EXR files excluded; binary URLs retain pinned asset-host mapping',files=count,bytes=total)
payload=(json.dumps(provenance,indent=2)+'\n').encode();blob=git('hash-object','-w','--stdin',data=payload).strip();entries.append(b'100644 '+blob+b'\thosting-source.json\0')
git('update-index','-z','--index-info',env=env,data=b''.join(entries));tree=git('write-tree',env=env).decode().strip()
old=subprocess.run(['git','rev-parse','--verify','refs/heads/gh-pages'],cwd=R,capture_output=True,text=True)
parents=[] if old.returncode else ['-p',old.stdout.strip()]
sha=git('commit-tree',tree,*parents,'-m','Publish review UI from '+source[:12]).decode().strip()
git('update-ref','refs/heads/gh-pages',sha,old.stdout.strip() if old.returncode==0 else '0'*40)
assert git('rev-parse',args.source+'^{commit}').decode().strip()==source
print(json.dumps(dict(pages_commit=sha,source_commit=source,asset_commit=asset_ref,files=count,bytes=total,index=str(index)),indent=2))
