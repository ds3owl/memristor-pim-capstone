"""
embed_figures.py — paper.html 내의 <img src="figures/*.png"> 를 base64 data URL로 인라인.

제출 시 그림 파일이 누락되어도 HTML 단독으로 모든 그림이 표시되도록 한다.
"""
import os
import re
import base64
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER = os.path.join(BASE_DIR, 'paper.html')
FIG_DIR = os.path.join(BASE_DIR, 'figures')


def embed():
    with open(PAPER, 'r', encoding='utf-8') as f:
        html = f.read()

    pattern = re.compile(r'<img\s+src="figures/([^"]+\.png)"', re.IGNORECASE)
    matches = pattern.findall(html)
    print(f"발견된 그림 참조: {len(matches)}개 → {matches}")

    for fname in matches:
        path = os.path.join(FIG_DIR, fname)
        if not os.path.exists(path):
            print(f"  [경고] 파일 없음: {path}")
            continue
        with open(path, 'rb') as f:
            data = base64.b64encode(f.read()).decode('ascii')
        kb = len(data) / 1024
        original = f'<img src="figures/{fname}"'
        embedded = f'<img src="data:image/png;base64,{data}"'
        html = html.replace(original, embedded)
        print(f"  [OK] {fname} embed ({kb:.1f} KB base64)")

    out = PAPER
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)

    size_mb = len(html.encode('utf-8')) / 1024 / 1024
    print(f"\n저장: {out}")
    print(f"최종 paper.html 크기: {size_mb:.2f} MB")


if __name__ == "__main__":
    embed()
