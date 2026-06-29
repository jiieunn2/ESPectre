import SwiftUI

/// 평면도 화면: 저장된 2D 평면도를 그리고 방별 상태로 색칠. "측정하기"로 RoomPlan 스캔.
struct FloorPlanView: View {
    @StateObject private var vm = FloorPlanViewModel()
    @State private var showScanner = false
    /// 대시보드 deep link(espectre://scan)로 들어오면 자동으로 스캐너를 연다.
    var scanRequest: Binding<Bool> = .constant(false)

    var body: some View {
        NavigationStack {
            Group {
                if let plan = vm.floorPlan {
                    VStack(spacing: 12) {
                        FloorPlanCanvas(rooms: plan.data.rooms, statusByRoom: vm.statusByRoom)
                            .padding()
                        LegendBar()
                        Button {
                            showScanner = true
                        } label: {
                            Label("다시 측정하기", systemImage: "arkit")
                        }
                        .buttonStyle(.bordered)
                        .padding(.bottom)
                    }
                } else {
                    // 평면도 없음 → 스캔 유도
                    ContentUnavailableView {
                        Label("저장된 평면도가 없어요", systemImage: "square.dashed")
                    } description: {
                        Text("‘측정하기’를 눌러 집을 스캔하면 2D 평면도가 만들어집니다.\n(LiDAR 탑재 아이폰/아이패드 Pro 필요)")
                    } actions: {
                        Button {
                            showScanner = true
                        } label: {
                            Label("측정하기", systemImage: "arkit")
                        }
                        .buttonStyle(.borderedProminent)
                    }
                }
            }
            .navigationTitle("평면도")
            .toolbar {
                if let err = vm.lastError {
                    ToolbarItem(placement: .bottomBar) {
                        Text(err).font(.caption2).foregroundColor(.red)
                    }
                }
            }
        }
        .task { vm.start() }
        .onDisappear { vm.stop() }
        .onAppear { if scanRequest.wrappedValue { showScanner = true; scanRequest.wrappedValue = false } }
        .onChange(of: scanRequest.wrappedValue) { _, want in
            if want { showScanner = true; scanRequest.wrappedValue = false }
        }
        .fullScreenCover(isPresented: $showScanner) {
            RoomScanView { create in
                showScanner = false
                if let create { Task { await vm.save(create) } }
            }
        }
    }
}

/// 폴리곤들을 캔버스에 축척 맞춰 그린다.
struct FloorPlanCanvas: View {
    let rooms: [FloorPlanRoom]
    let statusByRoom: [String: RoomStatus]

    var body: some View {
        Canvas { context, size in
            let pts = rooms.flatMap { $0.polygon }
            guard pts.count >= 2 else { return }
            let xs = pts.map { $0[0] }, ys = pts.map { $0[1] }
            let minX = xs.min()!, maxX = xs.max()!
            let minY = ys.min()!, maxY = ys.max()!
            let spanX = max(maxX - minX, 0.001), spanY = max(maxY - minY, 0.001)
            let pad = 24.0
            let scale = min((size.width - 2*pad) / spanX, (size.height - 2*pad) / spanY)

            func map(_ p: [Double]) -> CGPoint {
                CGPoint(x: pad + (p[0] - minX) * scale,
                        y: pad + (maxY - p[1]) * scale)   // y 뒤집기(평면도 y는 위쪽)
            }

            for room in rooms {
                guard room.polygon.count >= 3 else { continue }
                var path = Path()
                path.move(to: map(room.polygon[0]))
                for p in room.polygon.dropFirst() { path.addLine(to: map(p)) }
                path.closeSubpath()

                let status = statusByRoom[room.name] ?? .noSensor
                context.fill(path, with: .color(status.color.opacity(0.22)))
                context.stroke(path, with: .color(status.color), lineWidth: 2)

                // 방 이름 라벨(중심)
                let cx = room.polygon.map { $0[0] }.reduce(0,+) / Double(room.polygon.count)
                let cy = room.polygon.map { $0[1] }.reduce(0,+) / Double(room.polygon.count)
                let center = map([cx, cy])
                context.draw(Text(room.name).font(.caption).bold(), at: center)
            }
        }
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

struct LegendBar: View {
    var body: some View {
        HStack(spacing: 16) {
            legend(.active, "활동중")
            legend(.still, "정지")
            legend(.noSensor, "센서없음")
        }
        .font(.caption)
    }
    private func legend(_ s: RoomStatus, _ t: String) -> some View {
        HStack(spacing: 4) {
            RoundedRectangle(cornerRadius: 3).fill(s.color.opacity(0.4)).frame(width: 14, height: 14)
            Text(t).foregroundColor(.secondary)
        }
    }
}
