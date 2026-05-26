# Step 3 — MCP 서버

웨이퍼 결함 진단 tool 4종을 제공하는 MCP 서버를 만들고 Claude Desktop에 연결한다.
발표 자료의 **Step 2 (MCP 서버 구축)** 에 해당한다.

제공하는 tool 4종:
- `log_defect()` — 결함 검사 결과 저장
- `query_history()` — 유사 결함 이력 조회
- `classify_defect()` — 결함 종류 분류
- `get_token_uri()` — 온체인 기록 확인

---

## 0. 폴더 구조

```
step3_mcp/
├── wafer_server.py      ← MCP 서버 본체
├── test_tools.py        ← 연결 전 동작 확인용
├── requirements.txt
└── data/
    └── history.json     ← 결함 이력 DB (Step 1에서 생성한 것)
```

`data/history.json` 이 없으면 Step 1의 `history.json` 을 `data/` 폴더에 복사한다.

---

## 1. 가상환경 만들기 + 패키지 설치

터미널에서 `step3_mcp` 폴더로 이동한 뒤:

```bash
cd step3_mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`.venv` 가 활성화되면 터미널 줄 앞에 `(.venv)` 가 표시된다.

---

## 2. 연결 전 동작 확인

Claude Desktop에 붙이기 전에 tool 로직이 맞는지 먼저 확인한다:

```bash
python3 test_tools.py
```

tool 6개 호출 결과가 쭉 출력되면 서버 로직은 정상이다.

---

## 3. Claude Desktop에 서버 등록

### 3-1. 설정 파일 위치

맥에서 Claude Desktop의 설정 파일은 여기에 있다:

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

터미널에서 바로 열려면:

```bash
open -a TextEdit "~/Library/Application Support/Claude/claude_desktop_config.json"
```

> 파일이 없다고 나오면, Claude Desktop을 한 번 실행했다 끄면 생성된다.
> 또는 아래 내용으로 새로 만든다.

### 3-2. 설정 내용 입력

파일에 아래 내용을 넣는다. **두 개의 경로를 본인 환경에 맞게 반드시 수정**해야 한다.

```json
{
  "mcpServers": {
    "wafer-defect": {
      "command": "/여기에/step3_mcp/.venv/bin/python3",
      "args": ["/여기에/step3_mcp/wafer_server.py"]
    }
  }
}
```

- `command` : 1번에서 만든 가상환경 안의 python3 경로
- `args` : `wafer_server.py` 의 전체 경로

**경로 쉽게 얻는 법:** 터미널에서 `step3_mcp` 폴더에 들어가 아래를 실행하면
복사해 쓸 경로가 그대로 출력된다.

```bash
echo "command: $(pwd)/.venv/bin/python3"
echo "args:    $(pwd)/wafer_server.py"
```

이미 `claude_desktop_config.json` 에 다른 서버가 등록돼 있다면,
`mcpServers` 안에 `"wafer-defect": { ... }` 항목만 추가하면 된다.

### 3-3. Claude Desktop 재시작

설정 파일을 저장한 뒤 **Claude Desktop을 완전히 종료(⌘Q)했다가 다시 켠다.**
재시작해야 새 서버가 인식된다.

---

## 4. 동작 확인

Claude Desktop 채팅창 입력란 근처에 도구(망치/슬라이더) 아이콘이 생기고,
`wafer-defect` 서버의 tool 4종이 보이면 연결 성공.

채팅에서 자연어로 시험해본다:

```
Edge-Ring 패턴 결함 최근 사례 3건 보여줘
```

Claude가 `query_history` tool을 호출하고 결과를 보여주면 정상 동작.

다른 예시 질문:
- "결함률 82%인 웨이퍼는 어떤 종류로 분류돼?"  → classify_defect
- "W001 웨이퍼 온체인에 기록됐어?"            → get_token_uri
- "W050, Scratch, 결함률 9% 결함 이력 저장해줘" → log_defect

---

## 5. 문제 해결

| 증상 | 해결 |
|------|------|
| 도구가 안 보임 | 설정 파일 경로 오타 확인, Claude Desktop 완전 재시작 |
| "server failed" | `command` 경로의 python3가 실제 존재하는지 확인 |
| tool 호출 시 에러 | `data/history.json` 이 있는지 확인 |
| JSON 형식 오류 | 쉼표/중괄호 짝 확인 (jsonlint.com 에 붙여넣어 검사) |

---

## 다음 단계

Step 4에서 Step 2(블록체인)와 이 MCP 서버를 연결한다.
`get_token_uri()` 가 실제 배포된 컨트랙트를 조회하도록 확장하고,
전체 시연 시나리오를 정리한다.
