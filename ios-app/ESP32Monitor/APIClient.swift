import Foundation

/// 백엔드 REST 호출 클라이언트.
struct APIClient {
    static let shared = APIClient()

    // ISO8601 (소수 초 있음/없음 둘 다 대응) 디코더
    private static let isoFractional: ISO8601DateFormatter = {
        let f = ISO8601DateFormatter()
        f.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return f
    }()
    private static let isoPlain: ISO8601DateFormatter = {
        let f = ISO8601DateFormatter()
        f.formatOptions = [.withInternetDateTime]
        return f
    }()

    private let decoder: JSONDecoder = {
        let d = JSONDecoder()
        d.dateDecodingStrategy = .custom { dec in
            let c = try dec.singleValueContainer()
            let s = try c.decode(String.self)
            if let date = APIClient.isoFractional.date(from: s) ?? APIClient.isoPlain.date(from: s) {
                return date
            }
            throw DecodingError.dataCorruptedError(in: c, debugDescription: "bad date: \(s)")
        }
        return d
    }()

    private func request(_ path: String) -> URLRequest {
        let url = URL(string: "\(Config.apiBaseURL)/\(path)")!
        var req = URLRequest(url: url)
        req.setValue(Config.apiKey, forHTTPHeaderField: "X-API-Key")
        req.timeoutInterval = 8
        return req
    }

    /// 등록된 장치 목록
    func fetchDevices() async throws -> [Device] {
        let (data, _) = try await URLSession.shared.data(for: request("api/v1/devices"))
        return try decoder.decode([Device].self, from: data)
    }

    /// 특정 장치의 현재 활동 상태
    func fetchState(deviceId: String) async throws -> ActivityState {
        let (data, _) = try await URLSession.shared.data(for: request("api/v1/devices/\(deviceId)/state"))
        return try decoder.decode(ActivityState.self, from: data)
    }
}
