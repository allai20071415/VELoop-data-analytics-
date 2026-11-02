"""Convenience entry point: python run.py all"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))
from veloop_analytics.cli import main
main()
