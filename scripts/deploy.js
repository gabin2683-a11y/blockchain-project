const hre = require("hardhat");

/**
 * WaferRegistry 배포 스크립트
 *   로컬:    npx hardhat run scripts/deploy.js --network localhost
 *   Sepolia: npx hardhat run scripts/deploy.js --network sepolia
 */
async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("배포 계정:", deployer.address);

  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("계정 잔액:", hre.ethers.formatEther(balance), "ETH");

  console.log("\nWaferRegistry 배포 중...");
  const Factory = await hre.ethers.getContractFactory("WaferRegistry");
  const registry = await Factory.deploy();
  await registry.waitForDeployment();

  const address = await registry.getAddress();
  console.log("✅ 배포 완료!");
  console.log("컨트랙트 주소:", address);
  console.log("\n네트워크:", hre.network.name);

  if (hre.network.name === "sepolia") {
    console.log("\nSepolia Etherscan에서 확인:");
    console.log(`https://sepolia.etherscan.io/address/${address}`);
  }

  // MCP 서버 / 프론트엔드가 쓸 수 있도록 주소를 파일로 저장
  const fs = require("fs");
  const info = {
    network: hre.network.name,
    address: address,
    deployedAt: new Date().toISOString(),
  };
  fs.writeFileSync("deployed.json", JSON.stringify(info, null, 2));
  console.log("\n주소를 deployed.json 에 저장했습니다.");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
