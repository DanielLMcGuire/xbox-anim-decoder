import os
import sys
import runpy

_HERE = os.path.dirname(os.path.abspath(__file__))

PIPELINE = [
    "logo_mesh/parse_logo.py",
    "logo_mesh/decode.py",
    "logo_mesh/build_obj.py",

    "primitives/parse_quats.py",
    "primitives/parse_data.py",
    "primitives/build_scene.py",

    "animation/parse_anim.py",
    "animation/parse_surfofrev.py",
    "animation/decode_anim_full.py",
    "animation/build_frame0.py",
    "animation/build_mid.py",
    "animation/export_anim.py",
]


def _run_stage(rel_path):
    script_path = os.path.join(_HERE, *rel_path.split("/"))
    script_dir = os.path.dirname(script_path)

    print(f"\n=== {rel_path} ===")
    old_cwd = os.getcwd()
    was_on_path = script_dir in sys.path
    if not was_on_path:
        sys.path.insert(0, script_dir)
    try:
        os.chdir(script_dir)
        runpy.run_path(script_path, run_name="__main__")
    finally:
        os.chdir(old_cwd)
        if not was_on_path:
            sys.path.remove(script_dir)


def run_pipeline():
    for stage in PIPELINE:
        _run_stage(stage)
    print("\nPipeline complete.")


if __name__ == "__main__":
    run_pipeline()
