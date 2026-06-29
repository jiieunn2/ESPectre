import SwiftUI

/// Location 탭: 방별 실시간 상태 목록.
struct LocationView: View {
    @StateObject private var vm = LocationViewModel()

    var body: some View {
        NavigationStack {
            List {
                if let err = vm.lastError {
                    Section {
                        Label(err, systemImage: "wifi.exclamationmark")
                            .font(.footnote)
                            .foregroundColor(.red)
                    } header: {
                        Text("연결 오류")
                    } footer: {
                        Text("백엔드 주소(Config.apiBaseURL = \(Config.apiBaseURL))와 같은 Wi-Fi 인지, PC 방화벽 8000 포트가 열려있는지 확인하세요.")
                    }
                }

                Section("우리집 방별 상태") {
                    ForEach(vm.rooms) { room in
                        RoomCardView(room: room)
                    }
                }
            }
            .navigationTitle("Location")
            .refreshable { await vm.refresh() }
        }
        .task { vm.start() }
        .onDisappear { vm.stop() }
    }
}

#Preview {
    LocationView()
}
