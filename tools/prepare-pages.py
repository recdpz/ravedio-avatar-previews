"""Generate a small Pages-only branch without checking out or altering artwork.

Run from any directory: python tools/prepare-pages.py --source main --index ABSENT_PATH.
Review and push gh-pages, then use gh-pages / as the repository Pages source.
"""
from pathlib import Path
import argparse,json,os,subprocess,re
from urllib.parse import urljoin,urlsplit,urlunsplit,unquote,quote
R=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--source',default='main');parser.add_argument('--index',required=True);parser.add_argument('--externalize-images',action='store_true',help='Keep image bytes in pinned GitHub source assets and rewrite only generated page URLs');args=parser.parse_args()
def git(*a,env=None,data=None):return subprocess.check_output(['git',*a],cwd=R,env=env,input=data)
source=git('rev-parse',args.source+'^{commit}').decode().strip();index=Path(args.index).resolve();assert not index.exists(),'Use a fresh index path; do not reuse the working index'
assert index != (R/'.git/index').resolve();index.parent.mkdir(parents=True,exist_ok=True)
env=dict(os.environ,GIT_INDEX_FILE=str(index));git('read-tree','--empty',env=env)
excluded={'.glb','.blend','.zip','.png','.exr'};entries=[];total=0;count=0;rewritten=[]
rows=git('ls-tree','-rz','--long','--full-tree',source).split(b'\0')
all_names={row.split(b'\t',1)[1].decode('utf8') for row in rows if row}
image_extensions={'.jpg','.jpeg','.webp','.png'}
if args.externalize_images:excluded|=image_extensions
raw_base='https://raw.githubusercontent.com/recdpz/ravedio-avatar-previews/'+source+'/'
prefix='/ravedio-avatar-previews/'
def image_url(url,name):
 parsed=urlsplit(urljoin('https://recdpz.github.io'+prefix+name,url))
 if parsed.netloc!='recdpz.github.io' or not parsed.path.startswith(prefix):return url
 target=unquote(parsed.path[len(prefix):])
 if target not in all_names or Path(target).suffix.lower() not in image_extensions:return url
 return raw_base+quote(target,safe='/')+('?' + parsed.query if parsed.query else '')+('#'+parsed.fragment if parsed.fragment else '')
def html_images(text,name):
 text=re.sub(r'\b(src|href)\s*=\s*(["\'])(.*?)\2',lambda m:m[1]+'='+m[2]+image_url(m[3],name)+m[2],text,flags=re.I)
 text=re.sub(r'url\(\s*(["\']?)([^)"\']+)\1\s*\)',lambda m:'url('+m[1]+image_url(m[2].strip(),name)+m[1]+')',text,flags=re.I)
 text=re.sub(r'<img\b[^>]*>',lambda m:re.sub(r'<img', '<img crossorigin="anonymous"',m[0],count=1,flags=re.I) if 'raw.githubusercontent.com/recdpz/ravedio-avatar-previews/' in m[0] and not re.search(r'\bcrossorigin\b',m[0],re.I) else m[0],text,flags=re.I)
 if name.endswith('.html') and not re.search(r'<script[^>]+src=["\'][^"\']*asset-host\.js',text,re.I):
  script='<script data-ravedio-asset-host src="/ravedio-avatar-previews/asset-host.js?v='+source[:12]+'"></script>'
  match=re.search(r'<head\b[^>]*>',text,re.I) or re.search(r'<html\b[^>]*>',text,re.I)
  text=text[:match.end()]+script+text[match.end():] if match else script+text
 return text
for row in rows:
 if not row:continue
 meta,path=row.split(b'\t',1);mode,kind,sha,size=meta.split();name=path.decode('utf8')
 if kind!=b'blob':raise RuntimeError('Unexpected non-blob entry: '+name)
 if Path(name).suffix.lower() in excluded or name.startswith('.github/'):continue
 if args.externalize_images and Path(name).suffix.lower() in {'.html','.css'}:
  before=git('cat-file','blob',sha.decode());after=html_images(before.decode('utf8'),name).encode('utf8')
  if after!=before:
   old_sha=sha.decode();sha=git('hash-object','-w','--stdin',data=after).strip();size=str(len(after)).encode();rewritten.append(dict(path=name,source_blob=old_sha,generated_blob=sha.decode()))
 entries.append(mode+b' '+sha+b'\t'+path+b'\0');total+=int(size);count+=1
assert total<300_000_000,('Unexpected Pages payload',total)
host=git('show',source+':asset-host.js').decode();asset_ref=re.search(r"const assetRef = '([0-9a-f]{40})';",host).group(1)
provenance=dict(source_commit=source,asset_commit=asset_ref,generated_branch='gh-pages',method='Exact source blobs with GLB/Blend/ZIP/PNG/EXR files excluded; binary URLs retain pinned asset-host mapping',files=count,bytes=total)
if args.externalize_images:provenance.update(method='Source blobs with large assets excluded; generated HTML/CSS image URLs point to exact pinned source images; missing legacy image routing is injected',external_image_commit=source,rewritten_ui=rewritten)
payload=(json.dumps(provenance,indent=2)+'\n').encode();blob=git('hash-object','-w','--stdin',data=payload).strip();entries.append(b'100644 '+blob+b'\thosting-source.json\0')
git('update-index','-z','--index-info',env=env,data=b''.join(entries));tree=git('write-tree',env=env).decode().strip()
old=subprocess.run(['git','rev-parse','--verify','refs/heads/gh-pages'],cwd=R,capture_output=True,text=True)
parents=[] if old.returncode else ['-p',old.stdout.strip()]
sha=git('commit-tree',tree,*parents,'-m','Publish review UI from '+source[:12]).decode().strip()
git('update-ref','refs/heads/gh-pages',sha,old.stdout.strip() if old.returncode==0 else '0'*40)
assert git('rev-parse',args.source+'^{commit}').decode().strip()==source
print(json.dumps(dict(pages_commit=sha,source_commit=source,asset_commit=asset_ref,files=count,bytes=total,index=str(index)),indent=2))
