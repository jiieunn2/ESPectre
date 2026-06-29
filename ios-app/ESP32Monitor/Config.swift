import Foundation

/// 앱 전역 설정. 백엔드 주소·키·방 목록을 한곳에서 관리한다.
enum Config {
    /// 백엔드(FastAPI) 주소.
    /// - 시뮬레이터/실기기 모두 Windows PC 의 LAN IP 를 써야 한다 (localhost 아님!).
    /// - PC 의 현재 IP: 192.168.1.83 (바뀌면 여기 수정).
    static let apiBaseURL = "http://192.168.1.83:8000"

    /// Phase 1 공유 키 (.env 의 API_KEY 와 동일해야 함).
    /// Phase 2 에서 JWT 로 교체 예정.
    static let apiKey = "YOUR_API_KEY"

    /// 집의 방 목록. device 의 location 값과 매칭한다.
    /// 센서가 없는 방은 "센서 없음" 으로 표시된다.
    static let rooms = ["거실", "침실", "주방", "욕실", "현관"]

    /// 실시간 갱신 주기 (나노초). 3초.
    static let pollInterval: UInt64 = 3_000_000_000
}
