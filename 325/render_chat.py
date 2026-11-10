"""Compare the current studio with softer lighting for 24 px chat portraits."""
import importlib.util
from pathlib import Path

from mathutils import Vector

source = Path(__file__).resolve().parents[1] / "324/render.py"
spec = importlib.util.spec_from_file_location("studio_compare324", source)
studio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(studio)


def aim(light, position, target):
    light.location = position
    light.rotation_euler = (Vector(target) - light.location).to_track_quat("-Z", "Y").to_euler()


def chat_studio(scene, _materials):
    key = scene.objects["Key"]
    # Keep the colored rim lights and move the broad key up and farther to the side.
    aim(key, (-4.85, -1.30, 5.65), (0, 0, 1.90))
    key.data.energy = 415
    key.data.size = 5.1
    key.data.color = (1, .976, .94)
    key.data.specular_factor = .38

    fill = scene.objects["Front"]
    # A soft, neutral wash near the camera lifts the eyes and beard shadows.
    aim(fill, (-.65, -4.6, 2.90), (0, 0, 1.84))
    fill.data.energy = 188
    fill.data.color = (1, .994, .981)
    fill.data.specular_factor = 0
    lower = scene.objects["Chat lower fill"]
    aim(lower, (3.9, -3.5, 2.60), (0, 0, 1.82))
    lower.data.energy = 105


if __name__ == "__main__":
    studio.main(variant="chat", configure=chat_studio)
