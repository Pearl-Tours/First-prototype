import subprocess
import os

def test_alembic_upgrade_runs():
    # Run alembic upgrade to head
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
        capture_output=True,
        text=True
    )
    print(result.stdout)
    assert result.returncode == 0, f"Alembic upgrade failed:\n{result.stderr}"
