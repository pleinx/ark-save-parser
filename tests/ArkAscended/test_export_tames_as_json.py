# tests/ArkAscended/test_export_tames_as_json.py

import subprocess
import re

def assert_export_success(result):
    assert result.returncode == 0, (
        f"Script failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    match = re.search(r"Saved \d+ tamed dinos to", result.stdout)
    assert match, f"'Saved X tamed dinos to' not found in output:\n{result.stdout}"

def test_export_tamed_runs_successfully_on_mixedUE5154_savegame():
    result = subprocess.run(
        [
            'python', 'examples/pleinx/export_tamed.py',
            '--savegame=tests/ArkAscended/savegames/Aberration_WP___UE51-54/Aberration_WP.ark',
            '--output=output'
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    assert_export_success(result)

def test_export_tamed_runs_successfully_on_pureUE54_savegame():
    result = subprocess.run(
        [
            'python', 'examples/pleinx/export_tamed.py',
            '--savegame=tests/ArkAscended/savegames/TheCenter_WP___PureUE54/TheCenter_WP.ark',
            '--output=output'
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    assert_export_success(result)
