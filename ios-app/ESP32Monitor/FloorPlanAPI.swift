import Foundation

/// 평면도 관련 API 호출 (APIClient 확장).
extension APIClient {

    private func jsonRequest(_ path: String, method: String, body: Data? = nil) -> URLRequest {
        let url = URL(string: "\(Config.apiBaseURL)/\(path)")!
        var req = URLRequest(url: url)
        req.httpMethod = method
        req.setValue(Config.apiKey, forHTTPHeaderField: "X-API-Key")
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = body
        req.timeoutInterval = 10
        return req
    }

    // 디코더/인코더 (날짜 ISO8601 소수초)
    private var fpDecoder: JSONDecoder {
        let d = JSONDecoder()
        d.dateDecodingStrategy = .custom { dec in
            let c = try dec.singleValueContainer()
            let s = try c.decode(String.self)
            let f1 = ISO8601DateFormatter(); f1.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
            let f2 = ISO8601DateFormatter(); f2.formatOptions = [.withInternetDateTime]
            if let date = f1.date(from: s) ?? f2.date(from: s) { return date }
            throw DecodingError.dataCorruptedError(in: c, debugDescription: "bad date: \(s)")
        }
        return d
    }

    /// 최신 평면도 가져오기. 없으면 nil(404).
    func fetchLatestFloorPlan() async throws -> FloorPlan? {
        let (data, resp) = try await URLSession.shared.data(for: jsonRequest("api/v1/floorplans/latest", method: "GET"))
        if let http = resp as? HTTPURLResponse, http.statusCode == 404 { return nil }
        return try fpDecoder.decode(FloorPlan.self, from: data)
    }

    /// 평면도 저장(스캔 결과 업로드).
    @discardableResult
    func saveFloorPlan(_ plan: FloorPlanCreate) async throws -> FloorPlan {
        let body = try JSONEncoder().encode(plan)
        let (data, _) = try await URLSession.shared.data(for: jsonRequest("api/v1/floorplans", method: "POST", body: body))
        return try fpDecoder.decode(FloorPlan.self, from: data)
    }
}
