import SwiftUI

/// 방의 활동 상태. 백엔드 state 문자열 + "센서 없음" 을 합친 표시용 enum.
enum RoomStatus {
    case active     // 활동중
    case still      // 정지
    case uncertain  // 불확실 (임계값 사이)
    case noData     // 센서는 있는데 최근 데이터 없음
    case noSensor   // 그 방에 등록된 device 없음

    /// 백엔드 state 문자열 -> RoomStatus
    static func from(state: String?) -> RoomStatus {
        switch state {
        case "active": return .active
        case "still": return .still
        case "uncertain": return .uncertain
        case "no_data": return .noData
        default: return .noSensor
        }
    }

    var label: String {
        switch self {
        case .active: return "활동중"
        case .still: return "정지"
        case .uncertain: return "불확실"
        case .noData: return "데이터 없음"
        case .noSensor: return "센서 없음"
        }
    }

    var color: Color {
        switch self {
        case .active: return .green
        case .still: return .blue
        case .uncertain: return .orange
        case .noData: return .gray
        case .noSensor: return Color(.systemGray3)
        }
    }
}
