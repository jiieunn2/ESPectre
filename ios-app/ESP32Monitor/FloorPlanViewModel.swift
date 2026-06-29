import SwiftUI

/// 평면도 화면: 최신 평면도 + 방별 상태(색칠용)를 로드/폴링한다.
@MainActor
final class FloorPlanViewModel: ObservableObject {
    @Published var floorPlan: FloorPlan?
    @Published var statusByRoom: [String: RoomStatus] = [:]   // 방 이름 -> 상태
    @Published var lastError: String?
    @Published var isLoading = false

    private var pollTask: Task<Void, Never>?

    func start() {
        pollTask?.cancel()
        pollTask = Task { [weak self] in
            while !Task.isCancelled {
                await self?.refresh()
                try? await Task.sleep(nanoseconds: Config.pollInterval)
            }
        }
    }

    func stop() { pollTask?.cancel(); pollTask = nil }

    func refresh() async {
        do {
            // 평면도(없으면 nil)
            if floorPlan == nil { floorPlan = try await APIClient.shared.fetchLatestFloorPlan() }

            // 방별 상태: device 목록 → location/device_key 매칭 → state
            let devices = try await APIClient.shared.fetchDevices()
            var map: [String: RoomStatus] = [:]
            if let plan = floorPlan {
                for room in plan.data.rooms {
                    // 우선 polygon 의 device_key, 없으면 방 이름==location 으로 매칭
                    let device = devices.first { d in
                        (room.deviceKey != nil && d.deviceKey == room.deviceKey) || d.location == room.name
                    }
                    if let device,
                       let state = try? await APIClient.shared.fetchState(deviceId: device.id) {
                        map[room.name] = RoomStatus.from(state: state.state)
                    } else {
                        map[room.name] = .noSensor
                    }
                }
            }
            statusByRoom = map
            lastError = nil
        } catch {
            lastError = error.localizedDescription
        }
    }

    /// 스캔 결과 평면도 저장 후 다시 로드.
    func save(_ create: FloorPlanCreate) async {
        isLoading = true
        defer { isLoading = false }
        do {
            let saved = try await APIClient.shared.saveFloorPlan(create)
            floorPlan = saved
            await refresh()
        } catch {
            lastError = error.localizedDescription
        }
    }
}
