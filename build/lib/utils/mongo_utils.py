# app/utils/mongo_utils.py

import subprocess

def is_mongodb_running():
    try:
        result = subprocess.run(["pgrep", "mongod"], 
                                check=False, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception as e:
        print(f"Error checking MongoDB status: {e}")
        return False

def start_mongodb():
    try:
        result = subprocess.run(["sudo", "systemctl", "start", "mongod"], 
                                check=True, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
        print(result.stdout.decode())
    except Exception as e:
        print(f"Error starting MongoDB: {e}")


