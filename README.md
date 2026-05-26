#  웨이퍼 결함 이력 MCP·블록체인 시스템

블록체인실습 텀 프로젝트. 웨이퍼 결함 검사 이력을 블록체인에 위변조 없이 기록하고,
코딩을 모르는 엔지니어도 자연어로 과거 결함 사례를 조회·대조할 수 있게 한 시스템이다.

흐름은 다음과 같다.

```
웨이퍼 결함 이력 데이터  →  MCP 서버(tool 4종)  →  LLM(Claude Desktop)  →  ERC-721 기록
```

- ERC-721 `WaferRegistry` 컨트랙트로 웨이퍼를 NFT로 발행하고 진단 결과를 온체인 기록
- FastMCP 서버가 결함 진단 tool 4종을 제공, Claude Desktop에 연결
- 엔지니어가 자연어로 질문하면 LLM이 알맞은 MCP tool을 호출

---

## 폴더 구성

| 경로 | 내용 |
|------|------|
| `contracts/` | `WaferRegistry` 스마트 컨트랙트 (Solidity) |
| `scripts/` | 배포 스크립트(`deploy.js`), 시연 스크립트(`demo.js`) |
| `test/` | 컨트랙트 테스트 코드 |
| `step 1` | 데이터 준비 — 웨이퍼 결함 이력 데이터 |
| `step 3` | MCP 서버 — 결함 진단 tool 4종 (Python / FastMCP) |
| `hardhat.config.js`, `package.json` | Hardhat 프로젝트 설정 |
| `deployed.json` | 배포된 컨트랙트 주소 (MCP 서버가 참조) |
| `wafer_mcp_project_final.pptx` | 발표 자료 — 프로젝트 소개 |
| `demo_results.pptx` | 발표 자료 — 시연 결과 |

---

## 1. 준비물

- Node.js
- Python 3
- Claude Desktop (MCP 서버 연결용)
- 코드 에디터 (VS Code 권장)

---

## 2. 스마트 컨트랙트 — 컴파일 · 테스트

저장소 루트에서 의존성을 설치한다.

```bash
npm install
```

`package.json` 에 적힌 의존성(Hardhat 2, OpenZeppelin 5 등)이 설치된다.

컴파일:

```bash
npx hardhat compile
```

`Compiled ... successfully` 가 나오면 성공이다.
(막히면 `cache/` 와 `artifacts/` 폴더를 지우고 다시 실행한다.)

테스트:

```bash
npx hardhat test
```

`test/` 의 테스트가 모두 통과하면 컨트랙트 로직이 검증된 것이다.
민팅, 이벤트 발생, 진단 기록·조회, 권한 체크를 확인한다.

---

## 3. 로컬 네트워크 배포 & 시연

이 프로젝트는 **Hardhat 로컬 네트워크**에서 동작·시연한다. 터미널 두 개가 필요하다.

**터미널 A — 로컬 블록체인 켜기:**

```bash
npx hardhat node
```

테스트 계정 20개가 출력되고 로컬 체인이 켜진 상태로 유지된다.
이 터미널은 끄지 말고 그대로 둔다.

**터미널 B — 배포 + 시연:**

```bash
npx hardhat run scripts/deploy.js --network localhost
npx hardhat run scripts/demo.js --network localhost
```

`deploy.js` 가 컨트랙트를 배포하고 주소를 `deployed.json` 에 저장한다.
`demo.js` 가 웨이퍼 3건을 민팅 → 진단 기록 → 조회 검증까지 보여준다.

---

## 4. MCP 서버 — Claude Desktop 연동

`step 3` 폴더의 MCP 서버는 결함 진단 tool 4종을 제공한다.

| tool | 기능 |
|------|------|
| `log_defect` | 결함 검사 결과를 이력 DB에 저장 |
| `query_history` | 유사 결함 패턴의 과거 이력 조회 |
| `classify_defect` | 결함률·패턴으로 9종 분류 |
| `get_token_uri` | 온체인 NFT 기록 여부 확인 |

원본 데이터는 로컬 서버에만 존재하며, LLM은 tool 호출로만 접근한다.
`get_token_uri` 는 `deployed.json` 에 저장된 컨트랙트 주소를 참조한다.

Claude Desktop의 MCP 설정에 `step 3` 의 서버를 등록하면,
"Edge-Ring 패턴 결함 비슷한 사례 있어?" 같은 자연어 질문으로 tool을 호출할 수 있다.

---

## 5. (선택) Sepolia 테스트넷 배포

본 프로젝트는 로컬 네트워크로 구현·시연을 완료했다.
퍼블릭 테스트넷에서 외부 검증까지 하고 싶다면 Sepolia에 배포할 수 있다.

1. MetaMask에 테스트 전용 새 계정 생성 (실제 자산이 든 지갑은 쓰지 않는다)
2. Sepolia faucet에서 테스트 ETH 수령
3. Alchemy 등에서 Sepolia RPC URL 발급
4. `.env.example` 을 복사해 `.env` 작성, `SEPOLIA_RPC_URL` 과 `PRIVATE_KEY` 입력
5. `npx hardhat run scripts/deploy.js --network sepolia` 로 배포

> ⚠️ `.env` 파일은 절대 GitHub에 올리지 않는다. 개인키가 노출된다.
</file_text>
