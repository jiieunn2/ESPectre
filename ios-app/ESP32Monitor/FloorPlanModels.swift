import Foundation

/// 백엔드 /api/v1/floorplans 응답.
struct FloorPlan: Codable, Identifiable {
    let id: String
    let name: String
    let data: FloorPlanData
    let createdAt: Date
    let updatedAt: Date

    enum CodingKeys: String, CodingKey {
        case id, name, data
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
}

/// 평면도 geometry. JSONB 안의 구조.
struct FloorPlanData: Codable {
    var source: String?          // "roomplan" | "manual"
    var unit: String?            // "m"
    var rooms: [FloorPlanRoom]
}

/// 방 1개: 이름 + (선택)센서 device_key + 폴리곤(꼭짓점 [x,y] 배열, 단위 m).
struct FloorPlanRoom: Codable, Identifiable {
    var id: String { name }
    let name: String
    let deviceKey: String?
    let polygon: [[Double]]      // [[x,y], [x,y], ...]

    enum CodingKeys: String, CodingKey {
        case name, polygon
        case deviceKey = "device_key"
    }
}

/// 평면도 저장 요청 바디.
struct FloorPlanCreate: Codable {
    let name: String
    let data: FloorPlanData
}
