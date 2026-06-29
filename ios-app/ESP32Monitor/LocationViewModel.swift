import SwiftUI

/// Location 화면의 상태를 관리하고 주기적으로 백엔드를 폴링한다.
@MainActor
final class LocationViewModel: ObservableObject {
    @Published var rooms: [RoomViewState] = []
    @Published var lastError: String?

    private var pollTask: Task<Void, Never>?

    /// 주기 폴링 시작
    func start() {
        pollTask?.cancel()
        pollTask = Task { [weak self] in
            while !Task.isCancelled {
                await self?.refresh()
                try? await Task.sleep(nanoseconds: Config.pollInterval)
            }
        }
    }

    func stop() {
        pollTask?.cancel()
        pollTask = nil
    }

    /// 장치 목록 + 각 장치 상태를 읽어 방별 표시 상태를 만든다.
    func refresh() async {
        do {
            let devices = try await APIClient.shared.fetchDevices()
            var result: [RoomViewState] = []

            for room in Config.rooms {
                if let device = devices.first(where: { $0.location == room }) {
                    if let state = try? await APIClient.shared.fetchState(deviceId: device.id) {
                        let scoreText = state.meanMovementScore.map { String(format: "%.2f", $0) } ?? "-"
                        let detail = "평균 \(scoreText) · 최근 \(state.samples)건"
                            + (state.transitionDetected ? " · ⚡전환" : "")
                        result.append(RoomViewState(room: room,
                                                    device: device,
                                                    status: RoomStatus.from(state: state.state),
                                                    detail: detail))
                    } else {
                        result.append(RoomViewState(room: room, device: device, status: .noData, detail: nil))
                    }
                } else {
                    result.append(RoomViewState(room: room, device: nil, status: .noSensor, detail: nil))
                }
            }

            self.rooms = result
            self.lastError = nil
        } catch {
            self.lastError = error.localizedDescription
        }
    }
}
