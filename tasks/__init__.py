import subprocess
import sys


def format() -> None:
    subprocess.run([sys.executable, "-m", "isort", "."], check=True)
    subprocess.run([sys.executable, "-m", "black", "."], check=True)


def main() -> None:
    subprocess.run([sys.executable, "main.py"], check=True)
