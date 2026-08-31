import importlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
UI_DIR = REPO_ROOT / "ui"


def _drop_cached_modules():
    for name in list(sys.modules):
        if name == "app" or name.startswith("app.") or name == "ui.app":
            del sys.modules[name]


def test_ui_app_resolves_real_app_package_when_ui_dir_precedes_repo_root():
    """
    Regression test for the app/ vs ui/app.py name collision.

    `streamlit run ui/app.py` inserts ui/ at the front of sys.path before
    executing the script, exactly like this. Since ui/ contains a file
    named app.py, `import app` would otherwise resolve to that file
    instead of the real `app` backend package.
    """

    original_path = list(sys.path)
    _drop_cached_modules()

    sys.path.insert(0, str(UI_DIR))

    try:
        module = importlib.import_module("ui.app")
        from app.pipeline import screen_job as real_screen_job

        assert module.screen_job is real_screen_job
    finally:
        sys.path[:] = original_path
        _drop_cached_modules()
