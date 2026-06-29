import Foundation

/// 백엔드 GET /api/v1/devices 응답 항목.
struct Device: Codable, Identifiable {
    let id: String
    let deviceKey: String
    let name: String
    let location: String?
    let lastSeenAt: Date?

    enum CodingKeys: String, CodingKey {
        case id, name, location
        case deviceKey = "device_key"
        case lastSeenAt = "last_seen_at"
    }
}

/// 백엔드 GET /api/v1/devices/{id}/state 응답.
struct ActivityState: Codable {
    let deviceId: String
    let state: String            // active / still / uncertain / no_data
    let transitionDetected: Bool
    let samples: Int
    let meanMovementScore: Double?
    let latestTime: Date?

    enum CodingKeys: String, CodingKey {
        case state, samples
        case deviceId = "device_id"
        case transitionDetected = "transition_detected"
        case meanMovementScore = "mean_movement_score"
        case latestTime = "latest_time"
    }
}

/// 화면 1개 방의 표시 상태 (방 이름 + 매칭된 device + 상태).
struct RoomViewState: Identifiable {
    let id = UUID()
    let room: String
    let device: Device?
    let status: RoomStatus
    let detail: String?
}
