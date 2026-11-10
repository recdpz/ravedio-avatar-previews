# Studio portraits in chat

Compare the studio portraits with a chat-specific light rig. Both use the
same eight revision 322 assemblies as review 324, with the same 15° camera,
crop, materials, and cool-white background. The revised rig places the broad
key higher and farther to the side and adds neutral frontal fill. The
colored rim lights preserve the glossy studio finish.

Use the preview at 24 px first. The larger view helps inspect the glasses,
eyes, and beard. Light lifts facial features in the shadows. It cannot make
small features such as individual lashes reliably distinguishable at 24 px.

Run `render_chat.py` in Blender 5.2 with `-- WORK TOOLS OUTPUT` using the same
inputs as review 324. Then run `324/bake.py OUTPUT TOOLS --variant chat --label Chat`
with NumPy and Pillow. Serve OUTPUT at `325/files`.
