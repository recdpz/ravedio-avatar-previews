"""Assemble the fixed Development fixture input consumed by both native teams."""
import hashlib
import json


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf8")


def write_stage(out, fixtures):
    fixed = {}
    appearances = []
    names = {}
    for build, fixture in fixtures.items():
        fixture_id = fixture["id"]
        selected = fixture["features"]
        slots = []
        for slot, part in fixture["components"].items():
            source = {"file": part["file"], "sha256": part["sha256"],
                      "bytes": part["bytes"], "triangles": part["triangles"]}
            # The two levels point to the same authored file for the
            # appearance comparison. Record any future derivative separately.
            slots.append({"id": f"{fixture_id}-{slot}", "role": slot,
                          "levels": {"portrait": source, "detail": source}})
        fixed[fixture_id] = {
            "build": build, "parts": slots, "features": selected,
            "overrides": fixture["appearance_overrides"],
            "camera": fixture["references"][0]["camera"],
        }
        for skin, tone in ((0, "Fair"), (3, "Brown")):
            look = f"{fixture_id}-skin{skin}"
            appearances.append({
                "id": look, "assembly_id": fixture_id, "build": build, "skin": skin,
                "eye": selected["eyes"], "top": selected["top"], "groom": selected["groom"],
                "hair_tone": 0, "top_tone": 0,
            })
            names[look] = ("Curls" if build == "Feminine" else "Flow") + " / " + tone

    messages = []
    for round_number, body in enumerate((
        "Where should we meet?", "I'm near the entrance.", "See you there.", "On my way."
    )):
        for look in appearances:
            index = len(messages)
            messages.append({
                "id": f"r298-row-{index:02d}", "sender": f"r298-sender-{round_number}-{look['id']}",
                "display_name": names[look["id"]], "appearance": look["id"],
                "body": body, "arrival_ms": 0,
            })
    seeded = encode({"name": "r298-visual", "appearances": appearances, "messages": messages})
    (out / "fixtures").mkdir()
    (out / "fixtures/r298-visual.json").write_bytes(seeded)
    stage = {
        "schema": "ravedio-art-lab-stage-1", "art_revision": 298,
        "mobile_base": "36c1fd735f9f06ab575127d2663d7ab6e681095a",
        "assemblies": fixed, "palette": "palette.json",
        "seed": {"file": "fixtures/r298-visual.json", "name": "r298-visual",
                 "sha256": hashlib.sha256(seeded).hexdigest(), "rows": len(messages),
                 "distinct_visual_keys": len(appearances)},
        "portrait_framing": {"orthographic_span": 1.35, "target_y": 1.90},
        "chat_sizes_px": [48, 64],
        "workloads": {
            "visual_and_real_fixture_cold": "r298-visual",
            "high_cardinality_and_arrivals": ["repeat", "unique-stress", "burst"],
        },
    }
    (out / "mobile-stage.json").write_bytes(encode(stage))


def verify_stage(archive, art):
    stage = json.loads(archive.read("mobile-stage.json"))
    assert stage["art_revision"] == art["revision"] == 298
    assert stage["palette"] in art["files"]
    assemblies = stage["assemblies"]
    assert set(assemblies) == {f["id"] for f in art["fixtures"].values()}
    for fixture in art["fixtures"].values():
        entry = assemblies[fixture["id"]]
        assert entry["features"] == fixture["features"]
        assert entry["overrides"] == fixture["appearance_overrides"]
        assert entry["camera"] == fixture["references"][0]["camera"]
        assert {p["role"] for p in entry["parts"]} == set(fixture["components"])
        for part in entry["parts"]:
            source = fixture["components"][part["role"]]
            for level in part["levels"].values():
                assert all(source[key] == value for key, value in level.items())
    seed = stage["seed"]
    data = archive.read(seed["file"])
    assert hashlib.sha256(data).hexdigest() == seed["sha256"]
    fixture = json.loads(data)
    assert fixture["name"] == seed["name"]
    assert len(fixture["messages"]) == seed["rows"] == 16
    assert len(fixture["appearances"]) == seed["distinct_visual_keys"] == 4
    assert {(a["assembly_id"], a["skin"]) for a in fixture["appearances"]} == {
        (assembly, skin) for assembly in assemblies for skin in (0, 3)}
    keys = {a["id"] for a in fixture["appearances"]}
    assert all(sum(m["appearance"] == key for m in fixture["messages"]) == 4 for key in keys)
    assert len({m["id"] for m in fixture["messages"]}) == 16
