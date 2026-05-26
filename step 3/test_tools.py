"""
MCP 서버 tool 4종이 제대로 동작하는지 직접 호출해서 확인하는 테스트.
(Claude Desktop 연결 전에 로직만 검증)
"""
import wafer_server as ws

print("=" * 55)
print("MCP 서버 tool 4종 동작 테스트")
print("=" * 55)

print("\n[1] query_history — Edge-Ring 패턴 이력 조회")
print("-" * 55)
print(ws.query_history("Edge-Ring", limit=3))

print("\n[2] classify_defect — 결함 분류 (edge ring 힌트)")
print("-" * 55)
print(ws.classify_defect(0.15, "edge ring"))

print("\n[3] classify_defect — 결함 분류 (결함률 매우 높음)")
print("-" * 55)
print(ws.classify_defect(0.82, ""))

print("\n[4] get_token_uri — W001 온체인 기록 확인")
print("-" * 55)
print(ws.get_token_uri("W001"))

print("\n[5] log_defect — 새 결함 이력 저장")
print("-" * 55)
print(ws.log_defect("W099", "Scratch", 0.08, "LOT-202699"))

print("\n[6] query_history — 방금 저장한 Scratch 다시 조회")
print("-" * 55)
print(ws.query_history("Scratch", limit=5))

print("\n" + "=" * 55)
print("테스트 완료")
print("=" * 55)
