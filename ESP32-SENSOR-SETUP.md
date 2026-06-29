# ESP32(ESPectre) 연결 · 로그 · HA→백엔드 연동 가이드

> ⚠️ 먼저: **iOS 앱은 ESP32에 직접 연결되지 않는다.**
> 경로는 `ESP32 → Home Assistant → 백엔드 → iOS 앱`.
> 이 문서는 **센서 쪽(PC/HA에서 하는 작업)** 이고, 맥의 iOS 작업과는 별개다.
> 이걸 해야 앱에 "테스트 데이터"가 아닌 **진짜 센서 데이터**가 흐른다.

ESPectre = ESP32 WiFi CSI 모션 감지 펌웨어. **ESPHome 기반**이라 HA가 네이티브 API로 자동 발견한다.
- 프로젝트: https://espectre.dev/  ·  https://github.com/francescopace/espectre

---

## 1. ESP32가 이미 HA에 붙어 있나? (대부분 여기서 끝)

지금 HA에 `sensor.espectre_movement_score`, `binary_sensor.espectre_motion_detected`가 보이면
**ESP32 → HA 연결은 이미 완료**된 것이다. 다시 플래시할 필요 없음. → 바로 **3번(HA→백엔드)** 으로.

펌웨어를 새로 올려야 할 때만 2번을 본다.

---

## 2. (필요 시) ESP32에 ESPectre 플래시 + WiFi 연결

1. ESP32(C6/S3/C3/원본 ESP32 지원)를 USB로 PC에 연결.
2. **가장 쉬움 — Micro-ESPectre CLI 자동 감지**: 시리얼 포트·칩을 자동 인식해 맞는 펌웨어를 받아 플래시. (espectre.dev "Setup" 문서 참고)
3. 또는 ESPHome 방식: 예제 YAML 다운로드 → `esphome run your-config.yaml`.
4. **WiFi 설정**: 플래시 후 ESPHome 앱 또는 기기가 띄우는 웹 설정 페이지에서 집 WiFi 입력.
5. WiFi 붙으면 **HA가 ESPHome 네이티브 API로 자동 발견** → 설정 > 기기 및 서비스에 ESPectre 추가 → entity 생성.

완전 초기화가 필요하면(Windows는 포트가 `COMx`):
```bash
esptool.py --port COM3 erase_flash      # 그 다음 esphome run 으로 재플래시
```

---

## 3. ESP32 로그 따는 법

### 3-A. ESPHome 로그 (제일 많이 씀)
- **USB 연결 상태에서:** `esphome logs your-config.yaml` (보레이트 115200 자동). 부팅·CSI·movement_score 로그가 흐른다.
- **WiFi/OTA(USB 없이):** 같은 명령 `esphome logs your-config.yaml` → 네트워크로 로그 스트리밍(기기가 WiFi에 있을 때).
- **HA에서:** ESPHome 애드온(대시보드) → 해당 기기 → **LOGS** 버튼.

### 3-B. 로그가 안 보일 때 (USB-UART 칩 이슈)
CH340 / CP2102 / CH343 보드에서 플래시 후 로그가 안 나오면, config의 `logger:` 섹션에서
`hardware_uart: UART0` 줄의 주석을 해제해 UART0로 로그를 내보낸다.
```yaml
logger:
  hardware_uart: UART0   # 이 줄 주석 해제
```

### 3-C. 시리얼 모니터 직접
Arduino IDE Serial Monitor / PlatformIO `pio device monitor` 등으로 `COMx` @ **115200** 으로 봐도 된다.

---

## 4. HA → 백엔드 연동 (이게 빠진 핵심 링크)

ESP32→HA는 됐어도, **HA가 우리 백엔드로 POST하는 설정은 아직 없다.** 이걸 넣어야 앱에 데이터가 흐른다.
HA 설정 파일 3곳에 추가(File Editor / Studio Code Server 애드온으로 편집):

```yaml
# configuration.yaml
rest_command:
  send_reading_to_backend:
    url: "http://192.168.1.83:8000/api/v1/readings"   # PC LAN IP
    method: POST
    headers:
      Content-Type: "application/json"
      X-API-Key: !secret backend_api_key
    payload: >
      {
        "device_key": "esp32-livingroom-01",
        "movement_score": {{ states('sensor.espectre_movement_score') | float(0) }},
        "motion_detected": {{ is_state('binary_sensor.espectre_motion_detected', 'on') | lower }}
      }
```
```yaml
# automations.yaml  (센서값이 바뀔 때마다 백엔드로 전송)
- alias: "Send ESPectre data to backend"
  mode: queued
  max: 100
  trigger:
    - platform: state
      entity_id: sensor.espectre_movement_score
    - platform: state
      entity_id: binary_sensor.espectre_motion_detected
  action:
    - service: rest_command.send_reading_to_backend
```
```yaml
# secrets.yaml
backend_api_key: "YOUR_API_KEY"
```

추가 후 **HA 재시작(또는 YAML 재로딩)**.

### 네트워크 주의
- HA가 **VMware VM** 등에서 돌면, VM이 LAN에 닿아야 `192.168.1.83` 으로 PC 백엔드에 POST 가능(브리지 네트워크면 OK).
- PC **Windows 방화벽 8000 인바운드 허용** 필요.

---

## 5. 데이터가 실제로 흐르는지 검증

```bash
# (PC에서) 적재된 readings 개수/최근값 확인 — 늘어나면 성공
curl -s "http://localhost:8000/api/v1/readings?device_id=73f66039-175a-4ff9-aaa1-9dc9c6b01b08&limit=5" \
  -H "X-API-Key: YOUR_API_KEY"

# 현재 활동 상태
curl -s "http://localhost:8000/api/v1/devices/73f66039-175a-4ff9-aaa1-9dc9c6b01b08/state" \
  -H "X-API-Key: YOUR_API_KEY"
```
- HA 개발자도구 > 상태에서 `sensor.espectre_movement_score` 를 흔들어보고(사람이 움직이면 값 변함), 위 readings count 가 늘면 파이프라인 OK.

---

## 6. ⚠️ movement_score 스케일 — 임계값 재보정 필요

ESPectre의 movement_score는 **0~1 정규화가 아닐 수 있다.** (바이너리 감지 기본 임계값이 5.0)
HA로 나가는 값은 sigmoid 스케일링될 수도 있어 범위가 다를 수 있음.

→ 백엔드의 활동 분류 임계값(`activity_active_threshold=0.5`, `activity_still_threshold=0.2`)은 **추측값**이다.
실제 값을 보고 맞춰야 한다:
1. 위 `/api/v1/readings` 로 평상시 값과 움직일 때 값을 관찰.
2. 그 분포에 맞게 `docker-compose.yml` 의 backend `environment` 에 아래를 추가(또는 `.env`)해서 조정:
   ```yaml
   ACTIVITY_ACTIVE_THRESHOLD: "<움직일 때 값>"
   ACTIVITY_STILL_THRESHOLD: "<평상시 값>"
   ```
3. `docker compose up -d backend` 로 재기동.

---

## 요약 (할 일 순서)
1. (이미 됐으면 skip) ESP32에 ESPectre 플래시 + WiFi → HA 자동 발견.
2. **HA에 rest_command + automation 추가** (4번) → 데이터가 백엔드로 흐름.
3. `/api/v1/readings` count 로 검증 (5번).
4. 실제 movement_score 분포 보고 **임계값 재보정** (6번).
5. 그러면 iOS 앱 Location 화면에 진짜 데이터로 거실 상태가 실시간 표시됨.
