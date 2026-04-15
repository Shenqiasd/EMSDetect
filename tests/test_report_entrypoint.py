import main


def test_root_main_exposes_report_app():
    assert main.app.title == "Storage Report Platform"
