import subprocess
import sys

# Function to ensure required packages are installed
def install_requirements(required_packages = ["opencv-python", "numpy", "mss"]):
    required_packages = ["opencv-python", "numpy", "mss"]
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))  # Check if installed
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])