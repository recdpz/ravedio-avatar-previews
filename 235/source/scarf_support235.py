"""Shared cloth boundary and broad-form support queries; no source mutation."""
from common235 import *
import bmesh

def cloth_boundary(hood,axis,value):
 n=len(hood.data.vertices)//2;layer=hood.data.uv_layers.active;uv={}
 for poly in hood.data.polygons:
  if max(poly.vertices)>=n:continue
  for li,vi in zip(poly.loop_indices,poly.vertices):uv[vi]=layer.data[li].uv.copy()
 ids=[i for i,p in uv.items() if abs(p[axis]-value)<1e-5];ids.sort(key=lambda i:uv[i][1-axis]);assert len(ids)>10
 return [(float(uv[i][1-axis]),hood.matrix_world@hood.data.vertices[i].co) for i in ids]

def convex_support(obs):
 bm=bmesh.new();deps=bpy.context.evaluated_depsgraph_get()
 for o in obs:
  if o.type=='MESH':
   evaluated=o.evaluated_get(deps)
   for v in evaluated.data.vertices:bm.verts.new(o.matrix_world@v.co)
 bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False);bm.verts.ensure_lookup_table();bm.verts.index_update()
 support=BVHTree.FromPolygons([v.co.copy() for v in bm.verts],[[v.index for v in f.verts] for f in bm.faces]);bm.free();return support
