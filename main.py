import subprocess

scripts = ["scripts/update_batting.py", "scripts/update_pitching.py"]

for script in scripts:
    print(f"Running {script}")
    subprocess.run(["python", script], check = True)

print("Daily update complete")
