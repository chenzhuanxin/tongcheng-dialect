# -*- coding: utf-8 -*-
"""
通城方言点 07D36 · 1000字音频批量下载脚本（老年男性 + 青年男性，共 2000 条）
用法：
  1) 用【已获音频授权】的账号登录 https://zhongguoyuyan.cn （普通用户/未实名会返回 401）
  2) 浏览器 F12 → Application → Cookies，复制整串 Cookie 粘到下面 COOKIE
  3) python download_audio.py
  音频存到 ./audio_07D36/老男/ 与 ./audio_07D36/青男/ ，支持断点续传（已存在则跳过）。
"""
import os, time, requests

COOKIE = "把已授权账号的整串Cookie粘贴到这里（至少含 JSESSIONID）"
POINT = "07D36"
API = "https://zhongguoyuyan.cn/api/mongo/resource/normal"
AUDIO = "https://zhongguoyuyan.cn/api/mongo/media/audioConvertion"
OUTDIR = "audio_" + POINT
H = {"User-Agent": "Mozilla/5.0 Chrome/124", "Cookie": COOKIE,
     "Referer": "https://zhongguoyuyan.cn/point/" + POINT}

def get_items():
    r = requests.post(API, data="id=" + POINT, headers=H, timeout=60)
    r.raise_for_status()
    rl = r.json()["data"]["resourceList"]
    out = []
    for g in rl:
        if g["type"] == "单字" and g["sounder"] in ("老男", "青男"):
            tag = "老男" if g["sounder"] == "老男" else "青男"
            for it in g["items"]:
                out.append((tag, it["iid"], it["name"], it["video"]))
    return out

def download():
    items = get_items()
    print("待下载音频:", len(items))
    for tag, iid, name, vid in items:
        d = os.path.join(OUTDIR, tag); os.makedirs(d, exist_ok=True)
        fn = os.path.join(d, f"{iid}_{name}.wav")
        if os.path.exists(fn) and os.path.getsize(fn) > 500:
            continue
        try:
            rr = requests.get(f"{AUDIO}?id={vid}", headers=H, timeout=40)
            if rr.status_code == 200 and len(rr.content) > 200:
                open(fn, "wb").write(rr.content)
                print("OK", tag, iid, name, len(rr.content))
            else:
                print("SKIP", tag, iid, name, "HTTP", rr.status_code, "→ 账号无音频权限(401)或未登录")
                if rr.status_code == 401:
                    print("  401：请改用已获音频授权的账号 Cookie 后重跑。"); return
        except Exception as e:
            print("ERR", tag, iid, e)
        time.sleep(0.15)
    print("完成，目录:", os.path.abspath(OUTDIR))

if __name__ == "__main__":
    download()
