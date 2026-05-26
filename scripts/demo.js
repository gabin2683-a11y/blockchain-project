const hre = require("hardhat");
const fs = require("fs");

/**
 * 시연용 스크립트 — 배포된 컨트랙트에 웨이퍼를 민팅하고 진단을 기록한다.
 * 실행 전 deploy.js 를 먼저 실행해서 deployed.json 이 있어야 한다.
 *
 *   npx hardhat run scripts/demo.js --network localhost
 *   npx hardhat run scripts/demo.js --network sepolia
 */
async function main() {
  const { address } = JSON.parse(fs.readFileSync("deployed.json", "utf8"));
  console.log("컨트랙트 주소:", address);

  const registry = await hre.ethers.getContractAt("WaferRegistry", address);
  const [owner] = await hre.ethers.getSigners();

  // 시연용 웨이퍼 3건 (Step 1의 history.json 과 동일한 형태)
  const wafers = [
    { uri: "ipfs://QmWaferW001Center", defect: "Center",    hash: "0xa1b2c3" },
    { uri: "ipfs://QmWaferW010EdgeR",  defect: "Edge-Ring", hash: "0xd4e5f6" },
    { uri: "ipfs://QmWaferW019Scrat",  defect: "Scratch",   hash: "0x7a8b9c" },
  ];

  for (let i = 0; i < wafers.length; i++) {
    const w = wafers[i];

    // 1) 웨이퍼 NFT 민팅
    const mintTx = await registry.mintWafer(owner.address, w.uri);
    await mintTx.wait();
    const tokenId = i + 1;
    console.log(`\n[${tokenId}] 민팅 완료 — tokenURI: ${w.uri}`);

    // 2) 진단 결과 온체인 기록
    const logTx = await registry.logDiagnosis(tokenId, w.defect, w.hash);
    await logTx.wait();
    console.log(`    진단 기록 — ${w.defect} (hash: ${w.hash})`);

    // 3) 검증: 다시 읽어서 확인
    const [defectType, dataHash, ts] = await registry.getDiagnosis(tokenId);
    console.log(`    조회 확인 — ${defectType} / ${dataHash} / ts=${ts}`);
  }

  const total = await registry.totalMinted();
  console.log(`\n총 발행된 웨이퍼 NFT: ${total}개`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
