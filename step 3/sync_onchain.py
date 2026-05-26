"""
Step 4 — 블록체인 ↔ MCP 연결고리
─────────────────────────────────────────────────
Step 2에서 ERC-721 컨트랙트에 실제로 민팅한 웨이퍼들을
MCP 서버의 이력 DB(history.json)에 "온체인 기록됨" 으로 반영한다.

이 스크립트를 실행한 뒤 MCP의 get_token_uri() 를 호출하면,
"미기록" 대신 실제 token_id / token_uri 가 표시된다.
→ 발표 자료의 ⑤ RECORD 단계와 검증 흐름이 한 줄로 이어진다.

실행:  python3 sync_onchain.py
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

# Step 2의 demo.js 가 실제로 민팅한 웨이퍼들
# (scripts/demo.js 의 wafers 배열과 동일 — token_uri, data_hash 일치)
MINTED = {
    "W001": {"token_id": 1, "token_uri": "ipfs://QmWaferW001Center",
             "data_hash": "0xa1b2c3"},
    "W010": {"token_id": 2, "token_uri": "ipfs://QmWaferW010EdgeR",
             "data_hash": "0xd4e5f6"},
    "W019": {"token_id": 3, "token_uri": "ipfs://QmWaferW019Scrat",
             "data_hash": "0x7a8b9c"},
}


def main():
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)

    updated = 0
    for r in records:
        wid = r.get("wafer_id")
        if wid in MINTED:
            r["on_chain"] = True
            r["token_id"] = MINTED[wid]["token_id"]
            r["token_uri"] = MINTED[wid]["token_uri"]
            r["data_hash"] = MINTED[wid]["data_hash"]
            updated += 1
            print(f"  {wid} -> 온체인 기록됨 "
                  f"(token_id={r['token_id']}, {r['token_uri']})")

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"\n{updated}개 웨이퍼를 온체인 기록 상태로 업데이트했습니다.")
    print("이제 MCP의 get_token_uri() 가 실제 token_uri 를 반환합니다.")


if __name__ == "__main__":
    main()
