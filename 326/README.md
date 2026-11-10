# Catalogue phone review

The phone pack uses the 322 source catalogue and glossy studio reference
at the 15° chat angle. The 28 fitted looks cover all individual style
options with selected pairings, plus all four skin tones. The native sample
also exposes the same parts through its 3D renderer and a full-body rotation
view in Avatar Lab. The complete 1,792-row source library is a separate ZIP.

Use `package_source.py SOURCE ZIP` to export the verified full library.
Render `render_catalogue.py` in Blender 5.2 with `-- WORK MOBILE_TOOLS OUTPUT`.
The mobile checkout's `tools/avatar-proof/package_r322_catalogue.py` packages
the resulting `looks.json` and Blender references with the verified native
runtime inputs. The mounted delivery folder contains both ZIPs, their
checksums and the phone setup guide.
