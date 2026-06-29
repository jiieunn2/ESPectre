import SwiftUI
#if canImport(RoomPlan)
import RoomPlan
import simd
#endif

/// "측정하기" → Apple RoomPlan 으로 방을 스캔하고, 벽을 2D 폴리곤으로 변환해
/// FloorPlanCreate 로 콜백한다. (취소 시 nil)
///
/// ⚠️ RoomPlan 은 LiDAR 탑재 기기(iPhone/iPad Pro) + iOS 16+ 에서만 동작.
/// ⚠️ 시뮬레이터/비-LiDAR 기기에서는 미지원 안내만 표시한다.
/// ⚠️ Windows 에서 작성된 골격 — 맥에서 RoomPlan SDK 시그니처/동작 검증·보완 필요(아래 TODO).
struct RoomScanView: View {
    let onFinish: (FloorPlanCreate?) -> Void

    var body: some View {
        #if canImport(RoomPlan)
        if RoomCaptureSession.isSupported {
            RoomScanContainer(onFinish: onFinish)
                .ignoresSafeArea()
        } else {
            unsupported
        }
        #else
        unsupported
        #endif
    }

    private var unsupported: some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle")
                .font(.largeTitle).foregroundColor(.orange)
            Text("이 기기는 RoomPlan 스캔을 지원하지 않습니다.")
                .multilineTextAlignment(.center)
            Text("LiDAR 탑재 iPhone/iPad Pro(iOS 16+)에서 실행하세요.")
                .font(.caption).foregroundColor(.secondary)
            Button("닫기") { onFinish(nil) }.buttonStyle(.borderedProminent)
        }
        .padding()
    }
}

#if canImport(RoomPlan)

/// RoomCaptureView 를 감싸는 UIViewController 래퍼.
struct RoomScanContainer: UIViewControllerRepresentable {
    let onFinish: (FloorPlanCreate?) -> Void

    func makeUIViewController(context: Context) -> RoomScanController {
        let vc = RoomScanController()
        vc.onFinish = onFinish
        return vc
    }
    func updateUIViewController(_ uiViewController: RoomScanController, context: Context) {}
}

final class RoomScanController: UIViewController, RoomCaptureViewDelegate {
    var onFinish: ((FloorPlanCreate?) -> Void)?
    private var captureView: RoomCaptureView!

    override func viewDidLoad() {
        super.viewDidLoad()
        captureView = RoomCaptureView(frame: view.bounds)
        captureView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        captureView.delegate = self
        view.addSubview(captureView)

        // 취소 버튼
        let cancel = UIButton(type: .system)
        cancel.setTitle("취소", for: .normal)
        cancel.addTarget(self, action: #selector(cancelTapped), for: .touchUpInside)
        cancel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(cancel)
        NSLayoutConstraint.activate([
            cancel.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 12),
            cancel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
        ])
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        captureView.captureSession.run(configuration: RoomCaptureSession.Configuration())
    }

    @objc private func cancelTapped() {
        captureView.captureSession.stop()
        onFinish?(nil)
    }

    // RoomCaptureView 가 "Done" 처리 후 최종 CapturedRoom 을 전달.
    // TODO(iOS): 현재 SDK 의 정확한 delegate 시그니처 확인. (captureView(_:didPresent:error:))
    func captureView(didPresent processedResult: CapturedRoom, error: Error?) {
        if let error {
            print("RoomPlan error: \(error)")
            onFinish?(nil)
            return
        }
        let create = RoomGeometry.toFloorPlan(processedResult)
        onFinish?(create)
    }
}

/// CapturedRoom -> 2D 평면도 변환.
/// TODO(iOS): 현재는 모든 벽 끝점을 중심 기준 각도로 정렬해 한 개의 방 폴리곤을 근사한다.
///            실제로는 (1) 다중 방 분리, (2) 문/개구부 반영, (3) 노이즈 제거, (4) 센서 device_key 배치
///            를 device 에서 보완할 것.
enum RoomGeometry {
    static func toFloorPlan(_ room: CapturedRoom) -> FloorPlanCreate {
        var pts: [[Double]] = []
        for wall in room.walls {
            let t = wall.transform
            let center = SIMD3<Float>(t.columns.3.x, t.columns.3.y, t.columns.3.z)
            let localX = SIMD3<Float>(t.columns.0.x, t.columns.0.y, t.columns.0.z)
            let half = wall.dimensions.x / 2
            let a = center - localX * half
            let b = center + localX * half
            // 바닥 평면 = (x, z)
            pts.append([Double(a.x), Double(a.z)])
            pts.append([Double(b.x), Double(b.z)])
        }
        guard pts.count >= 3 else {
            return FloorPlanCreate(name: "우리집",
                                   data: FloorPlanData(source: "roomplan", unit: "m", rooms: []))
        }
        // 중심 기준 각도 정렬 → 대략적인 폴리곤
        let cx = pts.map { $0[0] }.reduce(0,+) / Double(pts.count)
        let cy = pts.map { $0[1] }.reduce(0,+) / Double(pts.count)
        let ordered = pts.sorted { atan2($0[1]-cy, $0[0]-cx) < atan2($1[1]-cy, $1[0]-cx) }

        let room0 = FloorPlanRoom(name: "스캔된 방", deviceKey: nil, polygon: ordered)
        return FloorPlanCreate(name: "우리집",
                               data: FloorPlanData(source: "roomplan", unit: "m", rooms: [room0]))
    }
}
#endif
