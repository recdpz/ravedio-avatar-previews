"""URL contract checks for the opt-in generated Pages image routing."""
import ast,unittest
from pathlib import Path
from urllib.parse import urljoin,urlsplit,urlunsplit,unquote,quote
import re
text=(Path(__file__).parent/'prepare-pages.py').read_text(encoding='utf8')
functions=[n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name in ['image_url','html_images']]
env=dict(urljoin=urljoin,urlsplit=urlsplit,urlunsplit=urlunsplit,unquote=unquote,quote=quote,re=re,Path=Path,all_names={'266/verification/test image.jpg','224/img.webp','266/local.png'},image_extensions={'.jpg','.jpeg','.webp','.png'},raw_base='https://raw.githubusercontent.com/recdpz/ravedio-avatar-previews/frozen/',prefix='/ravedio-avatar-previews/',source='frozen')
exec(compile(ast.Module(body=functions,type_ignores=[]),'<image routing>','exec'),env)
class Routing(unittest.TestCase):
 def test_relative_query_hash(self):self.assertEqual(env['image_url']('verification/test%20image.jpg?q=1#x','266/index.html'),env['raw_base']+'266/verification/test%20image.jpg?q=1#x')
 def test_parent_path(self):self.assertEqual(env['image_url']('../224/img.webp','266/index.html'),env['raw_base']+'224/img.webp')
 def test_foreign_unchanged(self):self.assertEqual(env['image_url']('https://example.com/a.jpg','266/index.html'),'https://example.com/a.jpg')
 def test_unknown_unchanged(self):self.assertEqual(env['image_url']('missing.jpg','266/index.html'),'missing.jpg')
 def test_dynamic_unchanged(self):self.assertEqual(env['image_url']('verification/${name}.jpg','266/index.html'),'verification/${name}.jpg')
 def test_model_not_changed(self):self.assertEqual(env['image_url']('./assets/test.glb','266/index.html'),'./assets/test.glb')
 def test_html_inject_and_image(self):
  html=env['html_images']('<html><head></head><body><IMG src="verification/test%20image.jpg"></body></html>','266/index.html');self.assertIn('crossorigin="anonymous"',html);self.assertIn(env['raw_base']+'266/verification/test%20image.jpg',html);self.assertIn('<head><script ',html)
 def test_loader_not_duplicated(self):self.assertEqual(env['html_images']('<html><script src="./asset-host.js"></script></html>','266/index.html').count('asset-host.js'),1)
 def test_css_url(self):self.assertIn(env['raw_base']+'224/img.webp',env['html_images']('a{background:url("../224/img.webp")}','266/style.css'))
 def test_noop_script(self):self.assertIn('src="viewer.js"',env['html_images']('<html><script src="viewer.js"></script></html>','266/index.html'))
if __name__=='__main__':unittest.main()
