# ESP32Monitor — 빌드 가이드

방별 실시간 상태(활동중/정지/불확실/데이터없음/센서없음)를 보여주는 SwiftUI iOS 앱.
탭 2개: **Location**(방별 상태 리스트) / **평면도**(2D 도면 렌더 + RoomPlan 스캔).
백엔드(FastAPI)의 `/api/v1/devices`, `/api/v1/devices/{id}/state`, `/api/v1/floorplans`를 폴링한다.

## 구성 파일

```
ios-app/
├── ESP32Monitor.xcodeproj/        # Xcode 프로젝트 (그대로 열면 됨)
└── ESP32Monitor/
    ├── ESP32MonitorApp.swift      # @main 진입점 → TabView(Location / 평면도)
    ├── Config.swift               # apiBaseURL / apiKey / rooms / pollInterval
    ├── Models.swift               # Device, ActivityState, RoomViewState (snake_case 매핑)
    ├── RoomStatus.swift           # 상태 enum + 한글 라벨 + 색
    ├── APIClient.swift            # fetchDevices() / fetchState() · ISO8601 소수초 디코더
    ├── LocationViewModel.swift    # @MainActor, 3초 폴링, 방별 상태 조립
    ├── RoomCardView.swift         # 방 1행 (이름 + 상세 + 상태 배지)
    ├── LocationView.swift         # List 화면 + pull-to-refresh
    ├── FloorPlanModels.swift      # FloorPlan, FloorPlanData, FloorPlanRoom, FloorPlanCreate
    ├── FloorPlanAPI.swift         # APIClient 확장: fetchLatestFloorPlan() / saveFloorPlan()
    ├── FloorPlanViewModel.swift   # 평면도 + 방별 상태 폴링, 스캔 결과 저장
    ├── FloorPlanView.swift        # Canvas 폴리곤 렌더 + 상태 색칠 + "측정하기"
    ├── RoomScanView.swift         # RoomPlan(LiDAR) 스캔 → 2D 폴리곤 변환 → 업로드
    └── Info.plist                 # 로컬 HTTP/네트워크 + 카메라 권한 (부분 plist, 자동 병합)
```

## 빌드 (macOS + Xcode 15+)

1. `ios-app/ESP32Monitor.xcodeproj`를 Xcode로 연다.
2. 상단에서 시뮬레이터(예: iPhone 15) 또는 실기기를 선택한다.
3. ▶︎ 실행.

> **배포 타깃: iOS 17.0.** `FloorPlanView`가 `ContentUnavailableView`(iOS 17+)를 사용하기 때문.
> RoomPlan 자체는 iOS 16+이지만 17은 상위호환이라 무방하다.
>
> 실기기 빌드 시: 타깃 > Signing & Capabilities 에서 본인 Team을 한 번 선택해야 한다.
> Bundle Identifier 기본값은 `com.espectre.ESP32Monitor` (필요 시 변경).
>
> **RoomPlan 스캔은 LiDAR 탑재 기기(iPhone/iPad Pro)에서만** 동작한다. 시뮬레이터·비-LiDAR
> 기기에서는 `RoomScanView`가 "미지원" 안내 화면을 띄우도록 `#if canImport(RoomPlan)` +
> `RoomCaptureSession.isSupported`로 가드되어 있다. (평면도 **렌더**는 모든 기기에서 동작)

`Info.plist`는 커스텀 키(아래 3개)만 담은 **부분 plist**이고, 나머지 표준 키는
`GENERATE_INFOPLIST_FILE = YES` 설정으로 Xcode가 자동 생성·병합한다.

```xml
<key>NSAppTransportSecurity</key>
<dict><key>NSAllowsLocalNetworking</key><true/></dict>
<key>NSLocalNetworkUsageDescription</key>
<string>같은 집 Wi-Fi의 모니터링 서버에서 센서 상태를 가져오기 위해 로컬 네트워크에 접속합니다.</string>
<key>NSCameraUsageDescription</key>
<string>집 평면도를 측정(스캔)하기 위해 카메라를 사용합니다.</string>
```

## 백엔드 연결 체크리스트

- `Config.swift`의 `apiBaseURL`이 **Windows PC의 LAN IP** 여야 한다 (현재 `http://192.168.1.83:8000`). `localhost` 금지.
- 아이폰/맥/PC가 **같은 Wi-Fi**.
- **Windows 방화벽 8000 포트 인바운드 허용**.
- `apiKey`가 백엔드 `.env`의 `API_KEY`와 동일.
- 백엔드 구동: PC에서 `docker compose up -d`.

## 동작 검증

PC에서 테스트 데이터를 넣으면 3초 내 "거실" 카드가 **활동중**으로 바뀐다:

```bash
curl -X POST http://localhost:8000/api/v1/readings \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"device_key":"esp32-livingroom-01","movement_score":0.9,"motion_detected":true}'
```

**평면도 탭**은 저장된 평면도가 없으면 "측정하기" 안내가 뜬다. LiDAR 기기 없이 렌더만
확인하려면 PC에서 샘플 평면도를 넣으면 된다(3초 내 "평면도" 탭에 거실 폴리곤이 그려짐):

```bash
curl -X POST http://localhost:8000/api/v1/floorplans \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"name":"우리집","data":{"unit":"m","rooms":[{"name":"거실","device_key":"esp32-livingroom-01","polygon":[[0,0],[4.2,0],[4.2,3.1],[0,3.1]]}]}}'
```

## 프로젝트 파일 재생성

`ESP32Monitor.xcodeproj`는 `gen_xcodeproj.py`로 결정론적으로 생성된다.
소스 파일을 추가/제거하면 스크립트의 `SWIFT_FILES`를 수정하고 다시 실행:

```bash
cd ios-app && python3 gen_xcodeproj.py
```

## 참고 — 이 프로젝트가 빌드된 환경

`.xcodeproj`와 소스는 Linux 컨테이너에서 생성·정합성 검증되었다(Swift/Xcode 툴체인 없음).
실제 컴파일·실행은 macOS + Xcode에서 이뤄진다. 만약 프로젝트가 열리지 않으면,
새 iOS App 프로젝트를 만들고 `ESP32Monitor/`의 `.swift` 13개 + `Info.plist`를 드래그해
추가하는 수동 방식으로 대체할 수 있다(배포 타깃 iOS 17.0 설정).

`RoomScanView.swift`는 SPEC상 **골격(스캔부 device 검증 필요)** 이다. 컴파일은 되지만,
폴리곤 추출(현재 벽 끝점 각도정렬 근사), 다중 방 분리, 문/개구부 반영, 스캔 후 방별
센서(device_key) 배치 UI는 LiDAR 기기에서 실측하며 보완해야 한다.
