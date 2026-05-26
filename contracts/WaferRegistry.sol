// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title WaferRegistry
 * @notice 웨이퍼 결함 검사 결과를 NFT(ERC-721)로 발행하고,
 *         LLM/MCP의 진단 결과를 온체인 이벤트로 영구 기록한다.
 *
 * 발표 자료 매핑:
 *   - mintWafer()     : ⑤ RECORD - 검사된 웨이퍼를 NFT로 민팅
 *   - logDiagnosis()  : LLM 진단 결과를 온체인 이벤트로 기록
 *   - getDiagnosis()  : 검증 흐름 - 저장된 진단 이력 조회
 */
contract WaferRegistry is ERC721URIStorage, Ownable {
    // 다음에 발행할 토큰 ID (1부터 시작)
    uint256 private _nextTokenId = 1;

    // 토큰별 진단 기록 구조체
    struct Diagnosis {
        string defectType;   // 결함 종류 (Center, Edge-Ring 등 9종)
        string dataHash;     // IPFS 원본 데이터의 무결성 해시
        uint256 timestamp;   // 진단이 기록된 시각
        bool exists;         // 기록 존재 여부
    }

    // tokenId => 진단 기록
    mapping(uint256 => Diagnosis) private _diagnoses;

    // ── 이벤트 ──────────────────────────────────────────────
    event WaferMinted(
        uint256 indexed tokenId,
        address indexed to,
        string tokenURI
    );

    event DiagnosisLogged(
        uint256 indexed tokenId,
        string defectType,
        string dataHash,
        uint256 timestamp
    );

    constructor() ERC721("WaferDefectRegistry", "WAFER") Ownable(msg.sender) {}

    /**
     * @notice 검사된 웨이퍼를 NFT로 발행한다.
     * @param to        토큰을 받을 주소
     * @param uri       IPFS 메타데이터 URI ("ipfs://{CID}")
     * @return tokenId  새로 발행된 토큰 ID
     */
    function mintWafer(address to, string memory uri)
        public
        onlyOwner
        returns (uint256)
    {
        uint256 tokenId = _nextTokenId;
        _nextTokenId++;

        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);

        emit WaferMinted(tokenId, to, uri);
        return tokenId;
    }

    /**
     * @notice LLM/MCP가 분류한 결함 진단 결과를 온체인에 기록한다.
     * @param tokenId     대상 웨이퍼 토큰 ID
     * @param defectType  분류된 결함 종류
     * @param dataHash    IPFS 원본 데이터의 해시 (위변조 검증용)
     */
    function logDiagnosis(
        uint256 tokenId,
        string memory defectType,
        string memory dataHash
    ) public onlyOwner {
        require(_ownerOf(tokenId) != address(0), "WaferRegistry: token does not exist");

        _diagnoses[tokenId] = Diagnosis({
            defectType: defectType,
            dataHash: dataHash,
            timestamp: block.timestamp,
            exists: true
        });

        emit DiagnosisLogged(tokenId, defectType, dataHash, block.timestamp);
    }

    /**
     * @notice 저장된 진단 기록을 조회한다. (검증 흐름에서 사용)
     */
    function getDiagnosis(uint256 tokenId)
        public
        view
        returns (
            string memory defectType,
            string memory dataHash,
            uint256 timestamp
        )
    {
        require(_diagnoses[tokenId].exists, "WaferRegistry: no diagnosis logged");
        Diagnosis memory d = _diagnoses[tokenId];
        return (d.defectType, d.dataHash, d.timestamp);
    }

    /**
     * @notice 지금까지 발행된 웨이퍼 NFT 총 개수.
     */
    function totalMinted() public view returns (uint256) {
        return _nextTokenId - 1;
    }
}
