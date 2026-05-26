# Step 2 — 스마트 컨트랙트 (ERC-721)

웨이퍼 결함 검사 결과를 NFT로 발행하고, 진단 결과를 온체인 이벤트로 기록하는
`WaferRegistry` 컨트랙트를 작성·테스트·배포한다.

발표 자료의 **Step 3 (블록체인 연동)** 에 해당하며, 다음을 다룬다.
- `mintWafer()` — 검사된 웨이퍼를 NFT로 민팅
- `logDiagnosis()` — LLM/MCP 진단 결과를 온체인 기록
- `getDiagnosis()` — 검증 흐름에서 진단 이력 조회

---

## 0. 준비물

- Node.js (이미 설치됨)
- 코드 에디터 (VS Code 권장)
- MetaMask 브라우저 확장 — Sepolia 배포 단계에서만 필요

---

## 1. 프로젝트 폴더 세팅

이 `step2_contract` 폴더를 통째로 작업 폴더에 둔다. 터미널에서:

```bash
cd step2_contract
npm install
```

`package.json` 에 적힌 의존성(hardhat 2, openzeppelin 5 등)이 설치된다.

---

## 2. 컴파일 — 컨트랙트가 문법적으로 맞는지 확인

```bash
npx hardhat compile
```

처음 실행하면 Solidity 컴파일러(solc 0.8.28)를 자동 다운로드한다.
`Compiled 1 Solidity file successfully` 가 나오면 성공.

> 막히면: `cache/` 와 `artifacts/` 폴더를 지우고 다시 `npx hardhat compile`.

---

## 3. 테스트 — 컨트랙트가 의도대로 동작하는지 확인

```bash
npx hardhat test
```

`test/WaferRegistry.test.js` 의 8개 테스트가 모두 통과해야 한다.
민팅, 이벤트 발생, 진단 기록/조회, 권한 체크를 검증한다.

전부 초록색 체크가 뜨면 컨트랙트 로직은 완성된 것이다.

---

## 4. 로컬 네트워크에서 시연 — 배포 없이 전체 흐름 확인

터미널 **두 개**가 필요하다.

**터미널 A — 로컬 블록체인 켜기:**
```bash
npx hardhat node
```
20개의 테스트 계정이 출력되고, 로컬 체인이 켜진 상태로 유지된다.
이 터미널은 끄지 말고 그대로 둔다.

**터미널 B — 배포 + 시연:**
```bash
npx hardhat run scripts/deploy.js --network localhost
npx hardhat run scripts/demo.js --network localhost
```

`deploy.js` 가 컨트랙트를 배포하고 주소를 `deployed.json` 에 저장한다.
`demo.js` 가 웨이퍼 3건을 민팅 → 진단 기록 → 조회 검증까지 보여준다.

여기까지 되면 **Step 2의 핵심은 끝**이다. 시연용으로는 로컬만으로도 충분하다.

---

## 5. (선택) Sepolia 테스트넷 실제 배포

발표 자료에 "Sepolia 테스트넷 배포"라고 적었으니, 가능하면 실제 배포까지 한다.

### 5-1. MetaMask에서 테스트 지갑 준비
- MetaMask 설치 후 새 계정 생성 (★ 실제 자산이 든 지갑 쓰지 말 것)
- 네트워크를 **Sepolia** 로 전환

### 5-2. 테스트 ETH 받기 (무료)
아래 faucet 중 하나에서 본인 지갑 주소로 테스트 ETH를 받는다.
- https://sepoliafaucet.com  (Alchemy)
- https://www.infura.io/faucet/sepolia
- https://faucet.quicknode.com/ethereum/sepolia

0.05 ETH 정도면 배포에 충분하다.

### 5-3. RPC URL 발급
- https://www.alchemy.com 가입 → 새 앱 생성 → Network를 Ethereum Sepolia로
- 발급된 HTTPS URL 복사

### 5-4. .env 파일 작성
```bash
cp .env.example .env
```
`.env` 를 열어 `SEPOLIA_RPC_URL` 과 `PRIVATE_KEY` 를 채운다.

> PRIVATE_KEY 얻는 법: MetaMask → 계정 메뉴 → 계정 세부정보 → 비공개 키 표시
> ⚠️ `.env` 는 절대 GitHub에 올리지 말 것 (.gitignore에 이미 등록됨)

### 5-5. 배포
```bash
npx hardhat run scripts/deploy.js --network sepolia
npx hardhat run scripts/demo.js --network sepolia
```

출력되는 Etherscan 링크(`https://sepolia.etherscan.io/address/...`)에 들어가면
실제 트랜잭션과 발행된 NFT를 확인할 수 있다. **이 화면이 시연의 핵심 증거물**이다.

---

## 다음 단계

`deployed.json` 에 저장된 컨트랙트 주소는 **Step 3 (MCP 서버)** 의
`get_token_uri()` tool 이 그대로 가져다 쓴다. 이 파일을 잘 보관할 것.
