import subprocess
import sys
import os

# Root directory of the project
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_script(script_path):
    print(f"\n==========================================")
    print(f"RUNNING: {os.path.basename(script_path)}")
    print(f"==========================================")
    try:
        # Run the script and wait for it to complete
        result = subprocess.run([sys.executable, script_path], check=True)
        if result.returncode == 0:
            print(f"SUCCESS: {os.path.basename(script_path)} finished successfully.")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {os.path.basename(script_path)} failed with exit code {e.returncode}.")
        sys.exit(1)

def main():
    print("Starting E-Commerce Project Master Runner...")
    
    # Define the order of scripts to execute
    scripts = [
        os.path.join(ROOT_DIR, 'data', 'mock_generator.py'),
        os.path.join(ROOT_DIR, 'python', 'eda.py'),
        os.path.join(ROOT_DIR, 'python', 'segmentation.py'),
        os.path.join(ROOT_DIR, 'python', 'clv_prediction.py'),
        os.path.join(ROOT_DIR, 'python', 'ab_testing.py'),
        os.path.join(ROOT_DIR, 'python', 'load_to_sqlite.py'),
        os.path.join(ROOT_DIR, 'python', 'run_queries.py')
    ]
    
    for script in scripts:
        if os.path.exists(script):
            run_script(script)
        else:
            print(f"Warning: Script not found at {script}")

    print("\n==========================================")
    print("ALL STEPS COMPLETED SUCCESSFULLY! 🎉")
    print("==========================================")

if __name__ == "__main__":
    main()
