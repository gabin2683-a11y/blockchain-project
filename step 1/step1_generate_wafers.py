"""
Step 1 — 웨이퍼맵 데이터 준비
WM-811K 데이터셋의 9종 결함 패턴을 재현한 시연용 웨이퍼맵을 생성한다.
- 결과: data/images/*.png  (웨이퍼맵 이미지)
- 결과: data/history.json  (MCP 서버가 사용할 이력 DB)
"""
import numpy as np
from PIL import Image
import json, os, random

random.seed(42)
np.random.seed(42)

# WM-811K의 9가지 결함 패턴
DEFECT_TYPES = [
    "Center", "Donut", "Edge-Loc", "Edge-Ring",
    "Loc", "Random", "Scratch", "Near-full", "None",
]

DIM = 64           # 웨이퍼맵 해상도 (WM-811K도 가변, 64x64로 통일)
OUT_DIR = "data"
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)


def wafer_mask(dim):
    """원형 웨이퍼 영역 마스크 (원 안=1, 밖=0)"""
    yy, xx = np.mgrid[0:dim, 0:dim]
    cx = cy = (dim - 1) / 2
    r = (xx - cx) ** 2 + (yy - cy) ** 2
    return r <= (dim / 2) ** 2, r, cx, cy


def make_wafer(defect_type, dim=DIM):
    """
    웨이퍼맵 1장 생성.
    값 의미:  0 = 웨이퍼 밖,  1 = 정상 die,  2 = 결함 die
    """
    mask, r, cx, cy = wafer_mask(dim)
    grid = np.zeros((dim, dim), dtype=np.uint8)
    grid[mask] = 1                       # 일단 전부 정상 die
    radius = dim / 2
    dist = np.sqrt(r)

    if defect_type == "Center":
        defect = (dist < radius * 0.28) & mask

    elif defect_type == "Donut":
        defect = (dist > radius * 0.4) & (dist < radius * 0.7) & mask

    elif defect_type == "Edge-Ring":
        defect = (dist > radius * 0.82) & mask

    elif defect_type == "Edge-Loc":
        ang = np.arctan2(np.mgrid[0:dim, 0:dim][0] - cy,
                         np.mgrid[0:dim, 0:dim][1] - cx)
        defect = (dist > radius * 0.78) & (ang > 0.3) & (ang < 1.5) & mask

    elif defect_type == "Loc":
        # 임의 위치의 국소 덩어리
        bx, by = random.uniform(0.2, 0.8) * dim, random.uniform(0.2, 0.8) * dim
        blob = (np.mgrid[0:dim, 0:dim][1] - bx) ** 2 + \
               (np.mgrid[0:dim, 0:dim][0] - by) ** 2
        defect = (blob < (dim * 0.16) ** 2) & mask

    elif defect_type == "Scratch":
        # 가는 사선 긁힘
        yy, xx = np.mgrid[0:dim, 0:dim]
        slope = random.uniform(-1.5, 1.5)
        offset = random.uniform(-dim * 0.2, dim * 0.2)
        line = np.abs(yy - (slope * (xx - cx) + cy + offset))
        defect = (line < 1.6) & mask

    elif defect_type == "Random":
        defect = (np.random.rand(dim, dim) < 0.12) & mask

    elif defect_type == "Near-full":
        defect = (np.random.rand(dim, dim) < 0.85) & mask

    else:  # "None" — 결함 없음, 약간의 노이즈만
        defect = (np.random.rand(dim, dim) < 0.01) & mask

    # 모든 패턴에 옅은 배경 노이즈 추가 (현실감)
    noise = (np.random.rand(dim, dim) < 0.015) & mask
    grid[defect | noise] = 2
    return grid


def grid_to_png(grid, path, scale=8):
    """0/1/2 grid를 색이 있는 PNG로 저장"""
    palette = {
        0: (245, 247, 251),   # 웨이퍼 밖 — 연회색
        1: (202, 220, 252),   # 정상 die — 연파랑
        2: (249, 97, 103),    # 결함 die — 코랄
    }
    dim = grid.shape[0]
    rgb = np.zeros((dim, dim, 3), dtype=np.uint8)
    for v, color in palette.items():
        rgb[grid == v] = color
    img = Image.fromarray(rgb, "RGB").resize(
        (dim * scale, dim * scale), Image.NEAREST)
    img.save(path)


def main():
    history = []
    token_id = 1
    # 패턴당 3장씩 = 27장
    for defect_type in DEFECT_TYPES:
        for k in range(3):
            grid = make_wafer(defect_type)
            wafer_id = f"W{token_id:03d}"
            fname = f"{wafer_id}_{defect_type}.png"
            grid_to_png(grid, os.path.join(IMG_DIR, fname))

            total = int((grid > 0).sum())
            bad = int((grid == 2).sum())
            history.append({
                "wafer_id": wafer_id,
                "token_id": token_id,
                "image_file": fname,
                "defect_type": defect_type,
                "die_total": total,
                "die_defect": bad,
                "defect_rate": round(bad / total, 4),
                "lot": f"LOT-{2026}{(token_id % 5) + 1:02d}",
                "inspected_at": f"2026-05-{(token_id % 18) + 1:02d}",
                "on_chain": False,          # 아직 민팅 안 됨
                "token_uri": None,
            })
            token_id += 1

    with open(os.path.join(OUT_DIR, "history.json"), "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    print(f"생성 완료: 이미지 {len(history)}장 -> {IMG_DIR}/")
    print(f"이력 DB  : {OUT_DIR}/history.json")
    # 요약 출력
    from collections import Counter
    c = Counter(h["defect_type"] for h in history)
    print("패턴별 개수:", dict(c))


if __name__ == "__main__":
    main()
