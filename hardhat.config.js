require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

/**
 * Hardhat 설정
 * - 로컬 테스트: 별도 설정 불필요 (hardhat 내장 네트워크)
 * - Sepolia 배포: .env 파일에 SEPOLIA_RPC_URL, PRIVATE_KEY 입력 필요
 */
module.exports = {
  solidity: {
    version: "0.8.28",
    settings: {
      optimizer: { enabled: true, runs: 200 },
      evmVersion: "cancun",
    },
  },
  networks: {
    // 로컬 인메모리 네트워크 (기본)
    hardhat: {},

    // Sepolia 테스트넷
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL || "",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
    },
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY || "",
  },
};
