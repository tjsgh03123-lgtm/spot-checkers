#!/usr/bin/env python3
"""Build the 카운팅 (counting-only) edition at counting/ from index.html. Run after every change to index.html."""
import re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
s = (root / "index.html").read_text(encoding="utf-8")
def sub(old, new, count=1):
    global s
    assert s.count(old) >= 1, old[:60]
    s = s.replace(old, new, count)
sub('const LITE = false;', 'const LITE = true;')
sub('<title>원 모어</title>', '<title>카운팅</title>')
sub('<meta name="application-name" content="원 모어">', '<meta name="application-name" content="카운팅">')
sub('<meta name="apple-mobile-web-app-title" content="원 모어">', '<meta name="apple-mobile-web-app-title" content="카운팅">')
sub('<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">', '<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">')
sub('<h1>원 모어 <span style="font-size:14px;color:var(--muted);font-weight:700;letter-spacing:.08em">ONE MORE</span></h1>',
    '<h1>카운팅 <span style="font-size:14px;color:var(--muted);font-weight:700;letter-spacing:.08em">COUNTING</span></h1>')
sub('<p>카메라로 횟수 · 가동범위 · 렙당 시간을 잽니다. 영상은 폰 밖으로 나가지 않습니다.</p>',
    '<p>카메라로 횟수와 렙당 시간을 셉니다. 영상은 폰 밖으로 나가지 않습니다.</p>')
sub('app: "원 모어 (One More)"', 'app: "카운팅 (Counting)"')
sub('const name = `onemore-diag-', 'const name = `counting-diag-')
sub('const q = indexedDB.open("reptempo", 1);', 'const q = indexedDB.open("counting", 1);')   # separate clip store from the full app
(root / "counting" / "index.html").write_text(s, encoding="utf-8")
(root / "counting" / "404.html").write_text(s, encoding="utf-8")
print("counting/index.html written", len(s))
