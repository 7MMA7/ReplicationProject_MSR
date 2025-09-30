import subprocess
import sys
import time

def run_script(script_name, args=None):
    cmd = [sys.executable, script_name]
    if args:
        cmd.extend(args)
    
    try:
        subprocess.run(cmd, check=True)
        print(f"{script_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error in {script_name}: {e}")
        return False
    
if __name__ == "__main__":
    scripts = [
        "3.1.2/github_repos_extraction.py",
        "3.1.2/xcm_generator.py"
    ]

    for script_name in scripts:
        print(f"Running {script_name}...")
        if not run_script(script_name):
            print(f"Process halted due to error in {script_name}")
            sys.exit(1)
        print()
        time.sleep(5)  

    print("Process completed successfully.")