"""Build the frozen report to report/, preserving the published index.html."""
from pathlib import Path
import argparse,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['READER','REPRODUCTION'],default='READER');a=ap.parse_args()
    sys.path.insert(0,str(ROOT))
    for script in ['report/build_snapshot.py','report/build_inventory.py','report/build_notebook.py']:
        subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(ROOT/'report/export_html.py'),'--mode',a.mode,'--draft','off'],cwd=ROOT,check=True)
if __name__=='__main__':main()
