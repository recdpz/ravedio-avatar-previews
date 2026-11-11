"""Verify source identities and export the independently selectable hair components."""
from pathlib import Path
import json
import sys

import bpy
import bmesh
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"332/tools"))
from study_bob import TO_BLENDER
from drape import read_glb

STYLES=("blowout","waves","asymmetric")


def body_geometry():
    return {obj.data.name:np.array([(obj.matrix_world@v.co)[:] for v in obj.data.vertices])
            for obj in bpy.context.scene.objects
            if obj.type=="MESH" and obj.get("component269")!="hair"}


def main(base,output):
    bpy.ops.wm.open_mainfile(filepath=str(base))
    original=body_geometry()
    report={}
    for style in STYLES:
        bpy.ops.wm.open_mainfile(filepath=str(output/f"Ravedio334-{style}.blend"))
        body=body_geometry()
        assert original.keys()==body.keys()
        assert all(np.array_equal(points,body[key]) for key,points in original.items())
        hair=[o for o in bpy.context.scene.objects if o.type=="MESH" and o.get("component269")=="hair"]
        assert len(hair)==1 and len(hair[0].data.vertices)>50000,style
        mesh=hair[0].data
        positions=np.array([v.co[:] for v in mesh.vertices]) @ TO_BLENDER.T
        assert np.isfinite(positions).all()
        bm=bmesh.new()
        bm.from_mesh(mesh)
        assert all(edge.is_manifold for edge in bm.edges),style+' has an open boundary'
        assert all(face.calc_area()>1e-14 for face in bm.faces),style+' has a collapsed face'
        bm.free()
        assert "Lock flow" in mesh.uv_layers
        uv=np.empty(len(mesh.loops)*2,dtype=np.float32)
        mesh.uv_layers["Lock flow"].data.foreach_get("uv",uv)
        assert np.isfinite(uv).all()
        for image in bpy.data.images:
            if image.name.startswith("bob-") and image.users:
                assert image.packed_file is not None
        bpy.ops.object.select_all(action="DESELECT")
        hair[0].select_set(True)
        path=output/f"{style}.glb"
        bpy.ops.export_scene.gltf(filepath=str(path),export_format="GLB",use_selection=True,
                                 export_materials="EXPORT")
        doc,_=read_glb(path)
        assert len(doc["materials"])==1
        material=doc["materials"][0]
        assert "normalTexture" in material
        assert "metallicRoughnessTexture" in material["pbrMetallicRoughness"]
        triangles=sum(doc["accessors"][p["indices"]]["count"]//3
                      for mesh in doc["meshes"] for p in mesh["primitives"])
        report[style]={"vertices":len(positions),"triangles":triangles,"materials":1,
                       "glb_bytes":path.stat().st_size,
                       "minimum_xyz":positions.min(axis=0).tolist(),
                       "maximum_xyz":positions.max(axis=0).tolist(),
                       "closed_boundaries":True,"body_unchanged":True}
    (output/"source-review.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    print("Verified three source models and their ordinary textured GLB exports.")


if __name__=="__main__":
    main(*(Path(p) for p in sys.argv[sys.argv.index("--")+1:]))
