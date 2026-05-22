# -*- coding: utf-8 -*-
"""embed_b5.py — paper_b5.html의 figures/*.png 참조를 base64로 내장.
출력: paper_b5_embedded.html (단일 자립 파일)"""
import re, os, base64
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(BASE, "paper_b5.html")
html = open(src, encoding="utf-8").read()

def repl(m):
    rel = m.group(1)
    p = os.path.join(BASE, rel)
    with open(p, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f'src="data:image/png;base64,{b64}"'

n = len(re.findall(r'src="(figures/[^"]+)"', html))
html2 = re.sub(r'src="(figures/[^"]+)"', repl, html)
out = os.path.join(BASE, "paper_b5_embedded.html")
open(out, "w", encoding="utf-8").write(html2)
print(f"임베드 {n}개 그림 -> {out}")
print(f"파일 크기: {len(html2):,} bytes ({len(html2)/1024/1024:.2f} MB)")
print("남은 외부참조(figures/):", len(re.findall(r'figures/', html2)))
