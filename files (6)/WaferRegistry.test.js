const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("WaferRegistry", function () {
  let registry, owner, other;

  beforeEach(async function () {
    [owner, other] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("WaferRegistry");
    registry = await Factory.deploy();
    await registry.waitForDeployment();
  });

  it("이름과 심볼이 올바르게 설정된다", async function () {
    expect(await registry.name()).to.equal("WaferDefectRegistry");
    expect(await registry.symbol()).to.equal("WAFER");
  });

  it("웨이퍼 NFT를 민팅하고 tokenURI가 저장된다", async function () {
    const uri = "ipfs://QmTestCID12345";
    const tx = await registry.mintWafer(owner.address, uri);
    await tx.wait();

    expect(await registry.totalMinted()).to.equal(1n);
    expect(await registry.ownerOf(1)).to.equal(owner.address);
    expect(await registry.tokenURI(1)).to.equal(uri);
  });

  it("민팅 시 WaferMinted 이벤트가 발생한다", async function () {
    const uri = "ipfs://QmAbc";
    await expect(registry.mintWafer(owner.address, uri))
      .to.emit(registry, "WaferMinted")
      .withArgs(1, owner.address, uri);
  });

  it("진단 결과를 기록하고 조회할 수 있다", async function () {
    await registry.mintWafer(owner.address, "ipfs://QmX");
    await registry.logDiagnosis(1, "Edge-Ring", "0xhash123");

    const [defectType, dataHash] = await registry.getDiagnosis(1);
    expect(defectType).to.equal("Edge-Ring");
    expect(dataHash).to.equal("0xhash123");
  });

  it("진단 기록 시 DiagnosisLogged 이벤트가 발생한다", async function () {
    await registry.mintWafer(owner.address, "ipfs://QmX");
    await expect(registry.logDiagnosis(1, "Center", "0xhashA"))
      .to.emit(registry, "DiagnosisLogged");
  });

  it("존재하지 않는 토큰에 진단을 기록하면 실패한다", async function () {
    await expect(
      registry.logDiagnosis(999, "Loc", "0xhash")
    ).to.be.revertedWith("WaferRegistry: token does not exist");
  });

  it("진단이 없는 토큰을 조회하면 실패한다", async function () {
    await registry.mintWafer(owner.address, "ipfs://QmX");
    await expect(
      registry.getDiagnosis(1)
    ).to.be.revertedWith("WaferRegistry: no diagnosis logged");
  });

  it("owner가 아니면 민팅할 수 없다", async function () {
    await expect(
      registry.connect(other).mintWafer(other.address, "ipfs://QmX")
    ).to.be.reverted;
  });
});
