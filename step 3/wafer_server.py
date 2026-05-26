"""
웨이퍼 결함 진단 MCP 서버
─────────────────────────────────────────────────
발표 자료의 MCP 서버 내부 구조(tool 4종)를 구현한다.

  log_defect()      — 결함 이미지/이력 저장
  query_history()   — 유사 결함 이력 조회
  classify_defect() — 결함 종류 분류 (규칙 기반)
  get_token_uri()   — 온체인 기록 확인

원본 데이터(history.json)는 이 서버 안에만 존재하며, LLM은
도구 호출(tool call)을 통해서만 데이터에 접근한다 — 발표 자료의
"보안 유지: 원본 데이터는 로컬 MCP 서버에만 존재" 컨셉.
"""
import json
import os
import hashlib
from mcp.server.fastmcp import FastMCP

# ── 서버 초기화 ──────────────────────────────────────
mcp = FastMCP("wafer-defect")

# 데이터 파일 경로 (이 스크립트와 같은 폴더의 data/ 안)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

# WM-811K의 9가지 결함 패턴
DEFECT_TYPES = [
    "Center", "Donut", "Edge-Loc", "Edge-Ring",
    "Loc", "Random", "Scratch", "Near-full", "None",
]


def _load_history():
    """이력 DB(history.json)를 읽어 리스트로 반환한다."""
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_history(records):
    """이력 DB를 파일에 저장한다."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


# ── Tool 1: log_defect ──────────────────────────────
@mcp.tool()
def log_defect(wafer_id: str, defect_type: str, defect_rate: float,
               lot: str = "LOT-UNKNOWN") -> str:
    """
    새로운 웨이퍼 결함 검사 결과를 이력 DB에 저장한다.

    Args:
        wafer_id: 웨이퍼 식별자 (예: "W028")
        defect_type: 결함 종류 (9종 중 하나)
        defect_rate: 결함 die 비율 (0.0 ~ 1.0)
        lot: 생산 lot 번호
    """
    records = _load_history()

    # 데이터 무결성 해시 생성 (위변조 검증용)
    payload = f"{wafer_id}|{defect_type}|{defect_rate}|{lot}"
    data_hash = "0x" + hashlib.sha256(payload.encode()).hexdigest()[:12]

    new_id = max([r.get("token_id", 0) for r in records], default=0) + 1
    record = {
        "wafer_id": wafer_id,
        "token_id": new_id,
        "defect_type": defect_type,
        "defect_rate": defect_rate,
        "lot": lot,
        "data_hash": data_hash,
        "on_chain": False,
        "token_uri": None,
    }
    records.append(record)
    _save_history(records)

    return (f"결함 이력 저장 완료\n"
            f"  wafer_id: {wafer_id}\n"
            f"  defect_type: {defect_type}\n"
            f"  data_hash: {data_hash}\n"
            f"  token_id: {new_id}")


# ── Tool 2: query_history ───────────────────────────
@mcp.tool()
def query_history(defect_type: str, limit: int = 3) -> str:
    """
    특정 결함 종류의 과거 검사 이력을 조회한다.
    엔지니어가 "Edge-Loc 패턴 최근 사례 보여줘" 같은 질문을 할 때 사용된다.

    Args:
        defect_type: 찾으려는 결함 종류 (9종 중 하나)
        limit: 반환할 최대 건수
    """
    records = _load_history()
    matched = [r for r in records if r.get("defect_type") == defect_type]

    if not matched:
        return f"'{defect_type}' 패턴의 이력이 없습니다."

    # 결함률 높은 순으로 정렬
    matched.sort(key=lambda r: r.get("defect_rate", 0), reverse=True)
    matched = matched[:limit]

    lines = [f"'{defect_type}' 패턴 이력 {len(matched)}건 (결함률 높은 순):"]
    for r in matched:
        rate = r.get("defect_rate", 0)
        chain = "온체인 기록됨" if r.get("on_chain") else "미기록"
        lines.append(
            f"  - {r['wafer_id']} (lot {r.get('lot', '?')}) "
            f"결함률 {rate:.1%} / {chain}")
    return "\n".join(lines)


# ── Tool 3: classify_defect ─────────────────────────
@mcp.tool()
def classify_defect(defect_rate: float, pattern_hint: str = "") -> str:
    """
    결함률과 패턴 힌트를 바탕으로 웨이퍼 결함 종류를 분류한다.
    (규칙 기반 분류 — 실제 구현에서는 LLM 이미지 분석으로 확장 가능)

    Args:
        defect_rate: 결함 die 비율 (0.0 ~ 1.0)
        pattern_hint: 패턴 위치 힌트 (예: "center", "edge", "line")
    """
    hint = pattern_hint.lower().strip()

    # 결함률 기반 1차 판정
    if defect_rate >= 0.7:
        guess = "Near-full"
    elif defect_rate < 0.03:
        guess = "None"
    # 패턴 힌트 기반 2차 판정
    elif "center" in hint:
        guess = "Center"
    elif "ring" in hint or "edge" in hint and "ring" in hint:
        guess = "Edge-Ring"
    elif "edge" in hint:
        guess = "Edge-Loc"
    elif "donut" in hint:
        guess = "Donut"
    elif "line" in hint or "scratch" in hint:
        guess = "Scratch"
    elif "random" in hint or "scatter" in hint:
        guess = "Random"
    else:
        guess = "Loc"

    return (f"결함 분류 결과: {guess}\n"
            f"  근거: 결함률 {defect_rate:.1%}, 힌트 '{pattern_hint}'\n"
            f"  (9종 분류: {', '.join(DEFECT_TYPES)})")


# ── Tool 4: get_token_uri ───────────────────────────
@mcp.tool()
def get_token_uri(wafer_id: str) -> str:
    """
    웨이퍼가 블록체인에 NFT로 기록되었는지, tokenURI가 무엇인지 확인한다.
    (Step 2에서 배포한 ERC-721 컨트랙트의 온체인 기록 조회에 해당)

    Args:
        wafer_id: 웨이퍼 식별자 (예: "W001")
    """
    records = _load_history()
    record = next((r for r in records if r.get("wafer_id") == wafer_id), None)

    if record is None:
        return f"'{wafer_id}' 웨이퍼를 찾을 수 없습니다."

    if not record.get("on_chain"):
        return (f"'{wafer_id}' 는 아직 온체인에 기록되지 않았습니다.\n"
                f"  (블록체인 민팅 후 token_uri 가 채워집니다)")

    return (f"'{wafer_id}' 온체인 기록 확인:\n"
            f"  token_id: {record.get('token_id')}\n"
            f"  token_uri: {record.get('token_uri')}\n"
            f"  data_hash: {record.get('data_hash', 'N/A')}")


# ── 서버 실행 ────────────────────────────────────────
if __name__ == "__main__":
    mcp.run()
