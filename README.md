# 🛰️ ESPectre 모션 감지 시스템 설치 가이드

Wi-Fi CSI 기반 ESP32 모션 감지 시스템(ESPectre) 설치를 처음부터 끝까지 안내하는 가이드입니다.

> **기준 환경**: ESP32-S3-N16R8 + Windows + Docker

---

## 📋 목차

- [전체 흐름](#-전체-흐름)
- [0. 사전 준비](#-0-사전-준비)
- [1. 프로젝트 다운로드 (Git 클론)](#-1-프로젝트-다운로드-git-클론)
- [2. 가상환경 + ESPHome 설치](#-2-가상환경--esphome-설치)
- [3. Wi-Fi 정보 입력 (secrets.yaml)](#-3-wi-fi-정보-입력-secretsyaml)
- [4. ESP32에 펌웨어 굽기 (빌드 & 플래시)](#-4-esp32에-펌웨어-굽기-빌드--플래시)
- [5. 터미널로 로그 보기](#-5-터미널로-로그-보기)
- [6. Home Assistant 설치 (Docker)](#-6-home-assistant-설치-docker)
- [7. ESP32와 Home Assistant 연동](#-7-esp32와-home-assistant-연동)
- [8. 대시보드 만들기](#-8-대시보드-만들기)
- [9. 외부 접속 설정 (선택)](#-9-외부-접속-설정-선택)
- [10. 문제 해결](#-10-문제-해결)
- [참고](#-참고)

---

## 🔄 전체 흐름

```
프로젝트 다운로드 (git clone)
   ↓
가상환경 + ESPHome 설치
   ↓
Wi-Fi 정보 입력 (secrets.yaml)
   ↓
ESP32에 펌웨어 굽기
   ↓
터미널로 로그 확인 (모션 감지 작동 확인)
   ↓
Home Assistant 설치 (Docker)
   ↓
ESP32 연동 → 대시보드 만들기
   ↓
외부 접속 설정 (선택)
```

---

## 🧰 0. 사전 준비

### 하드웨어

- **ESP32-S3** 보드 (ESP32-S3-N16R8 기준)
- **USB 데이터 케이블** — 데이터 전송이 가능한 케이블이어야 합니다 (충전 전용 ❌)
- **2.4GHz Wi-Fi** — 5GHz 전용 네트워크는 ESP32가 연결하지 못합니다 ⚠️

### 소프트웨어

가이드를 따라가며 하나씩 설치합니다.

| 프로그램 | 버전 | 용도 |
| --- | --- | --- |
| Python | 3.13 권장 (3.14는 피하기) | ESPHome 실행용 |
| Git | 최신 | 프로젝트 다운로드용 |
| ESPHome | 최신 | 펌웨어 빌드/플래시용 |
| Docker Desktop | 최신 | Home Assistant 실행용 |

---

## 📥 1. 프로젝트 다운로드 (Git 클론)

### 1-1. Git 설치 확인

```powershell
git --version
```

> 버전이 표시되지 않으면 [git-scm.com/download/win](https://git-scm.com/download/win)에서 설치한 뒤 PowerShell을 새로 엽니다.

### 1-2. 프로젝트 클론

> ⚠️ **경로에 한글이나 띄어쓰기가 있으면 빌드가 실패합니다.**
> 예를 들어 "바탕 화면"은 띄어쓰기 때문에 사용할 수 없습니다.
> → `C:\espectre` 처럼 영문·공백 없는 경로를 사용하세요.

```powershell
git clone https://github.com/francescopace/espectre.git
cd espectre
```

현재 위치 확인:

```powershell
pwd
```

> ✅ `C:\espectre` 가 나오면 성공입니다.

---

## 📦 2. 가상환경 + ESPHome 설치

### 2-1. 가상환경 생성

`espectre` 폴더 안에서 실행합니다.

```powershell
python -m venv venv
```

생성 확인:

```powershell
dir
```

> ✅ 목록에 `venv` 폴더가 보이면 성공입니다.

### 2-2. 실행 정책 설정 (처음 한 번만)

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

> 안내가 나오면 `Y` 입력 후 엔터를 누릅니다.

### 2-3. 가상환경 활성화

```powershell
.\venv\Scripts\Activate.ps1
```

> ✅ 터미널 맨 앞에 `(venv)` 가 붙으면 성공입니다.
> 예: `(venv) PS C:\espectre>`

> 💡 PowerShell을 새로 열 때마다 가상환경은 해제됩니다. 작업 전 항상 아래 두 줄을 실행하세요.
>
> ```powershell
> cd C:\espectre
> .\venv\Scripts\Activate.ps1
> ```

### 2-4. ESPHome 설치

`(venv)` 상태에서 실행합니다.

```powershell
pip install esphome
```

설치 확인:

```powershell
esphome version
```

> ✅ 버전 번호가 나오면 성공입니다.

---

## 🔑 3. Wi-Fi 정보 입력 (secrets.yaml)

> 개발용 설정 파일(`-dev.yaml`)은 Wi-Fi 정보를 `secrets.yaml`에서 읽어옵니다.

### 3-1. 파일 만들기

```powershell
notepad examples\secrets.yaml
```

> "새 파일을 만들겠냐"고 물으면 `예`를 클릭합니다.

### 3-2. 내용 입력

메모장에 아래 내용을 본인 Wi-Fi 정보로 수정해 입력합니다.

```yaml
wifi_ssid: "본인_와이파이_이름"
wifi_password: "본인_와이파이_비밀번호"
```

> ⚠️ **체크리스트**
> - 대소문자를 정확히 입력했는지 확인
> - 반드시 **2.4GHz** Wi-Fi 사용 (5GHz는 ESP32가 연결하지 못함)

---

## ⚡ 4. ESP32에 펌웨어 굽기 (빌드 & 플래시)

### 4-1. ESP32 연결

USB 데이터 케이블로 ESP32-S3를 PC에 연결합니다.

### 4-2. 포트 번호 확인 (선택)

`Windows 키` + `R` → `devmgmt.msc` → `포트 (COM 및 LPT)` 펼치기

> `USB-SERIAL (COM3)` 처럼 표시됩니다. 괄호 안의 `COM3` 이 포트 번호입니다.
> (보이지 않으면 보통 "1"입니다.)

### 4-3. 빌드 & 플래시 실행

`(venv)` 상태에서 실행합니다 (ESP32-S3 기준).

```powershell
esphome run examples\espectre-s3-dev.yaml
```

> 다른 보드는 파일명만 변경하면 됩니다.
> - ESP32-C6 → `espectre-c6-dev.yaml`
> - ESP32-C3 → `espectre-c3-dev.yaml`
> - ESP32 오리지널 → `espectre-esp32-dev.yaml`

### 4-4. 포트 선택

컴파일 후 선택지가 나옵니다.

```
[1] COM3 (USB Serial Device (COM3))
[2] Over The Air (espectre.local)
(number):
```

> ⭐ **첫 플래시는 반드시 USB로** 진행합니다. → `1` 입력 후 엔터
> 첫 컴파일은 5~15분 걸릴 수 있습니다.

### 4-5. 플래시가 안 될 때

> ⚠️ `no serial data received` 에러가 나면 ESP32를 강제 다운로드 모드로 진입시킵니다.

"Connecting…" 문구가 보이는 순간:

```
1. BOOT 버튼을 누른 채 유지
2. RST 버튼을 짧게 눌렀다 떼기
3. 1~2초 후 BOOT 버튼 떼기
```

> 그래도 안 되면 다른 USB 데이터 케이블로 교체해 보세요.

### 4-6. 성공 확인

```
INFO Successfully compiled program.
INFO Successfully uploaded program.
INFO Starting log output from COM...
```

### 4-7. 자동 캘리브레이션 ⭐ 중요

> ⚠️ **부팅 후 약 13초간 방에서 움직이지 마세요!**
> 이 시간 동안 "빈 방 상태"를 기준으로 잡습니다. 사람이 움직이면 감지 정확도가 떨어집니다.

```
1단계 Gain Lock        (약 3초)   → Wi-Fi 신호 안정화
2단계 NBVI 캘리브레이션   (약 10초)  → 최적 신호 12개 선택 + 임계값 설정
```

---

## 🖥️ 5. 터미널로 로그 보기

플래시 이후 언제든 로그를 다시 보려면 아래를 실행합니다.

```powershell
cd C:\espectre
.\venv\Scripts\Activate.ps1
esphome logs examples\espectre-s3-dev.yaml
```

> 포트 선택이 나오면 `1` (COM 포트)을 입력합니다.

### 정상 로그 예시

```
[wifi] WiFi Connected
[wifi] IP Address: 192.168.x.x
mvmt: 0.20  thr: 1.00  motion: OFF
```

| 항목 | 의미 |
| --- | --- |
| mvmt (movement score) | 현재 움직임 강도 (0~10) |
| thr (threshold) | 감지 임계값 (이 값을 넘으면 ON) |
| motion | 움직임 감지 여부 (ON/OFF) |
| free heap | 남은 메모리 (높을수록 좋음, 정상 100KB+) |
| loop time | 처리 속도 (낮을수록 좋음, 정상 ~20ms) |

### 테스트

> ESP32 앞에서 손을 흔들면 `mvmt` 값이 올라가고 `motion`이 `OFF → ON` 으로 바뀝니다.

> 💡 로그를 멈추려면 `Ctrl + C`. 로그 도중 RST를 누르면 `serial port closed`가 뜨는데, USB가 잠시 끊긴 것으로 정상입니다.

---

## 🏠 6. Home Assistant 설치 (Docker)

> Home Assistant는 별도의 서버 프로그램입니다. Windows에서는 Docker로 실행합니다.

### 6-1. Docker Desktop 설치

1. [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)에서 **Windows + AMD64** 버전을 다운로드합니다.
2. `Docker Desktop Installer.exe` 실행 → 기본 옵션으로 설치합니다.
3. 필요 시 재부팅합니다.
4. Docker Desktop 실행 → 약관 `Accept` → 가입 시 `Personal` 선택 (무료).
5. 작업표시줄에 고래 아이콘 🐳 과 `Docker Desktop is running`이 보이면 준비 완료입니다.

### 6-2. Home Assistant 컨테이너 실행

PowerShell **새 창**에서 실행합니다 (ESPHome 로그 창은 그대로 둡니다).

```powershell
docker run -d --name homeassistant --privileged --restart=unless-stopped -e TZ=Asia/Seoul -v C:\homeassistant:/config -p 8123:8123 ghcr.io/home-assistant/home-assistant:stable
```

> ⭐ `-p 8123:8123` 옵션이 있어야 `localhost:8123` 접속이 됩니다.
> (`--network=host` 는 Windows Docker에서 작동하지 않습니다.)

### 6-3. 실행 확인

```powershell
docker ps
```

> ✅ `homeassistant` 컨테이너 STATUS가 `Up ...` 이면 성공입니다.

### 6-4. 접속

브라우저에서 접속합니다.

```
http://localhost:8123
```

> 1~2분 로딩 후 계정 생성 화면이 나옵니다. 이름/아이디/비밀번호를 입력해 계정을 만듭니다.

---

## 🔗 7. ESP32와 Home Assistant 연동

### 7-1. 자동 발견되는 경우

`설정 → 기기 및 서비스 → ESPHome`에서 `espectre` 기기가 보이면 `구성`을 클릭합니다.

### 7-2. 자동 발견이 안 될 때 (Docker 환경에서 흔함)

ESP32의 IP 주소로 직접 추가합니다.

**① ESP32 IP 확인** — ESPHome 로그에서 `IP Address: 192.168.x.x` 줄을 확인합니다.

**② 수동 추가**

```
설정 → 기기 및 서비스 → 우측 하단 "통합 구성요소 추가" (+)
→ "ESPHome" 검색 → 클릭
→ Host: ESP32의 IP 주소 입력
→ 제출
```

### 7-3. 생성되는 엔티티

| 엔티티 | 설명 |
| --- | --- |
| sensor.espectre_movement_score | 움직임 강도 |
| binary_sensor.espectre_motion_detected | 움직임 감지 ON/OFF |
| number.espectre_threshold | 감지 임계값 (조정 가능) |
| button.espectre_recalibrate | 재캘리브레이션 |
| sensor.espectre_free_heap | 메모리 여유 |
| sensor.espectre_loop_time | 처리 속도 |

> 💡 실제 엔티티 ID는 기기 이름에 따라 다를 수 있습니다.
> `설정 → 기기 및 서비스 → ESPHome → espectre → Sensors`에서 확인하세요.

---

## 📊 8. 대시보드 만들기

### 8-1. 새 대시보드 생성

```
설정 → 대시보드 → 우측 하단 "+ 대시보드 추가"
→ "새 대시보드 (처음부터)" 선택
→ Title: ESPectre Motion Monitor
→ Icon: mdi:walk
→ Create
```

### 8-2. 카드 구성 (추천)

| 순서 | 카드 종류 | 대상 엔티티 | 설명 |
| --- | --- | --- | --- |
| 1 | Gauge | movement_score | 움직임 강도 게이지 (0~3) |
| 2 | Entity | motion_detected | 현재 감지 상태 |
| 3 | History Graph | movement_score + threshold | 실시간 그래프 (1시간) |
| 4 | Entities | threshold | 임계값 슬라이더 |
| 5 | Entities | recalibrate | 재캘리브레이션 |
| 6 | Entities | free_heap, loop_time | 디버그 센서 |

### 8-3. YAML 방식 (Raw editor가 있을 때)

> 편집 모드 → 우측 상단 점 3개(⋮) → `Raw configuration editor` → 아래 내용을 붙여넣습니다.

```yaml
views:
  - title: ESPectre Motion Monitor
    icon: mdi:walk
    cards:
      - type: gauge
        entity: sensor.espectre_movement_score
        name: Movement Level
        min: 0
        max: 3
        severity:
          green: 0
          yellow: 1
          red: 2

      - type: entity
        entity: binary_sensor.espectre_motion_detected
        name: Motion Status
        state_color: true

      - type: history-graph
        title: Movement & Threshold
        entities:
          - entity: sensor.espectre_movement_score
            name: Movement
          - entity: number.espectre_threshold
            name: Threshold
        hours_to_show: 1

      - type: entities
        title: Controls
        entities:
          - entity: number.espectre_threshold
            name: Threshold
          - entity: button.espectre_recalibrate
            name: Recalibrate

      - type: entities
        title: Debug Sensors
        entities:
          - entity: sensor.espectre_free_heap
            name: Free Heap
          - entity: sensor.espectre_loop_time
            name: Loop Time
```

> 입력 후 `Save`를 클릭합니다.

### 8-4. 카드 의미

- **Movement Level (게이지)** — 실시간 움직임 강도. 초록(안정) ~ 빨강(활발)
- **Threshold (임계값)** — 낮으면 민감, 높으면 둔감. 낮에는 높게, 밤에는 낮게 조정하면 노인 케어에 유용합니다.
- **Recalibrate** — OFF가 정상 대기 상태. 위치나 가구가 바뀌면 ON으로 토글합니다 (13초 정지).
- **Free Heap / Loop Time** — 시스템 건강 상태. 24시간 운영 시 메모리 누수 모니터링용입니다.

---

## 🌐 9. 외부 접속 설정 (선택)

> 기본적으로 `localhost:8123` 은 본인 PC에서만 접속됩니다.

### 9-1. 같은 Wi-Fi 안에서 접속 (가장 간단)

**① 노트북 IP 확인**

```powershell
ipconfig
```

> `IPv4 주소` (예: `192.168.1.100`)를 확인합니다.

**② 같은 Wi-Fi의 다른 기기에서 접속**

```
http://192.168.1.100:8123
```

**③ 사용자 계정 추가**

```
설정 → 사람 → 사용자 추가 → 관리자 권한 OFF
```

### 9-2. 외부(다른 네트워크)에서 접속 — ngrok (참고)

**① 가입 및 다운로드** — [ngrok.com](https://ngrok.com) 가입 → Windows용 다운로드 → 압축 풀기

**② 인증 토큰 설정** (ngrok.exe가 있는 폴더에서)

```powershell
.\ngrok.exe config add-authtoken (대시보드에서_복사한_토큰)
```

**③ Home Assistant 프록시 허용 설정**

컨테이너에 접속합니다.

```powershell
docker exec -it homeassistant bash
```

파일을 편집합니다 (vi 사용).

```bash
vi /config/configuration.yaml
```

> `i`를 눌러 편집 모드로 전환한 뒤 아래 내용을 추가합니다 (들여쓰기는 스페이스로 정확히).

```yaml
http:
  use_x_forwarded_for: true
  trusted_proxies:
    - 127.0.0.1
    - ::1
```

> `ESC` → `:wq` → 엔터 (저장 후 종료) → `exit`로 컨테이너를 빠져나옵니다.

**④ HA 재시작**

```powershell
docker restart homeassistant
```

**⑤ ngrok 실행**

```powershell
.\ngrok.exe http 8123 --host-header="localhost:8123"
```

> `Forwarding` 줄의 `https://xxxx.ngrok-free.app` 주소를 보호자에게 공유합니다.

> ⚠️ 무료 ngrok은 재실행할 때마다 주소가 바뀝니다. 노트북이 켜져 있고 ngrok이 실행 중일 때만 접속됩니다. 안정적인 운영은 Nabu Casa(HA Cloud, 유료)를 권장합니다.

---

## 🛠️ 10. 문제 해결

| 증상 | 원인 | 해결 |
| --- | --- | --- |
| `python` not recognized | PATH 미설정 | PATH 정리 후 PowerShell 새로 열기 |
| 가상환경 활성화 안 됨 | 실행 정책 차단 | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| whitespace in project paths | 경로에 한글/공백 | `C:\espectre` 영문 경로로 재클론 |
| no serial data received | 부트 모드 문제 | BOOT 누른 채 RST 눌렀다 떼기 |
| OTA로 업로드 시도 (IP 에러) | 포트 선택 잘못 | 다시 실행 후 `1`(COM 포트) 선택 |
| WiFi connecting→disconnected 반복 | Wi-Fi 정보 오류 / 5GHz | secrets.yaml 확인, 2.4GHz 사용 |
| localhost:8123 접속 안 됨 | 포트 매핑 누락 | `-p 8123:8123` 붙여 컨테이너 재생성 |
| HA에 espectre 안 보임 | 자동 발견 실패 | ESPHome 통합에 IP 직접 추가 |
| ngrok 400 Bad Request | 프록시 설정 누락 | configuration.yaml에 http 설정 + `--host-header` |

### 컨테이너 재생성 (포트 문제 등)

```powershell
docker stop homeassistant
docker rm homeassistant
docker run -d --name homeassistant --privileged --restart=unless-stopped -e TZ=Asia/Seoul -v C:\homeassistant:/config -p 8123:8123 ghcr.io/home-assistant/home-assistant:stable
```

---

## 📎 참고

- ESPectre 공식 저장소 → [github.com/francescopace/espectre](https://github.com/francescopace/espectre)
- 환경에 맞는 세부 튜닝은 저장소의 `TUNING.md`를 참고하세요.
- 빨간/초록 LED는 보드 전원 표시이며, 로그가 정상이면 신경 쓰지 않아도 됩니다.

---

> 이 가이드는 **ESP32-S3-N16R8 + Windows + Docker** 환경 기준으로 작성되었습니다.
