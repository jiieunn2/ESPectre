import SwiftUI

/// 앱 진입점. 탭: Location(방별 상태 리스트) / 평면도(2D 도면 + RoomPlan 스캔).
/// 대시보드(HA)에서 `espectre://scan` 딥링크로 열면 평면도 탭 + 스캐너가 자동 실행된다.
@main
struct ESP32MonitorApp: App {
    @State private var selectedTab = 0
    @State private var scanRequest = false

    var body: some Scene {
        WindowGroup {
            TabView(selection: $selectedTab) {
                LocationView()
                    .tabItem { Label("Location", systemImage: "list.bullet") }
                    .tag(0)
                FloorPlanView(scanRequest: $scanRequest)
                    .tabItem { Label("평면도", systemImage: "square.split.bottomrightquarter") }
                    .tag(1)
            }
            .onOpenURL { url in
                // espectre://scan  → 평면도 탭으로 이동 + 스캐너 자동 실행
                if url.host == "scan" || url.path.contains("scan") {
                    selectedTab = 1
                    scanRequest = true
                }
            }
        }
    }
}
