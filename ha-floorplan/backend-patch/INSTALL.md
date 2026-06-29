# 평면도 HTML을 백엔드(esp32-pipeline)로 서빙하기 — 설치 가이드

대상 환경(확인됨):
- 백엔드 폴더: `C:\Users\kimji\OneDrive\바탕 화면\esp32-pipeline`
- 컨테이너: `esp32-pipeline-backend-1` (FastAPI, `uvicorn app.main:app --reload`)
- `docker-compose.yml` 에 `./backend:/app` **볼륨 마운트** + `--reload` →
  **소스 수정 시 재빌드 불필요**, 컨테이너 재시작만 하면 됨.
- API_KEY 가 `.env` 와 HTML 이 일치함 → 그대로 동작.

> 같은 origin(:8000)에서 서빙하므로 **CORS 설정이 필요 없습니다.**

---

## 1) static 폴더 만들고 HTML 2개 넣기

`esp32-pipeline\backend\` 안에 **`static`** 폴더를 만들고, 받은 HTML 2개를 복사:

```
esp32-pipeline\
└─ backend\
   ├─ app\
   ├─ Dockerfile
   ├─ requirements.txt
   └─ static\                ← 새로 만들기
      ├─ floorplan.html      ← (채팅에서 받은 파일)
      └─ floorplan-view.html ← (채팅에서 받은 파일)
```

> 탐색기에서 `backend` 폴더 안에 새 폴더 `static` 생성 → 그 안에 두 HTML 붙여넣기.

## 2) app\main.py 교체

`backend\app\main.py` 를 이 폴더의 **`main.py`(수정본)** 으로 덮어씁니다.
(추가된 것: `FileResponse`/`Path` import + `/floorplan`, `/floorplan/view` 라우트 2개. 나머지는 원본 그대로.)

> 직접 고치고 싶다면 원본에 아래만 추가해도 됩니다:
> - 상단 import: `from pathlib import Path` / `from fastapi.responses import FileResponse, JSONResponse`
> - 라우터 등록 아래에:
>   ```python
>   STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
>
>   @app.get("/floorplan", include_in_schema=False)
>   async def floorplan_editor():
>       return FileResponse(STATIC_DIR / "floorplan.html")
>
>   @app.get("/floorplan/view", include_in_schema=False)
>   async def floorplan_view_page():
>       return FileResponse(STATIC_DIR / "floorplan-view.html")
>   ```

## 3) 백엔드 재시작

cmd 에서 백엔드 폴더로 이동 후 재시작:
```
cd "C:\Users\kimji\OneDrive\바탕 화면\esp32-pipeline"
docker compose restart backend
```
> `--reload` 라 보통 자동 반영되지만, 확실히 하려면 위 명령으로 재시작.

## 4) 브라우저로 확인 (PC에서)

```
http://localhost:8000/floorplan        ← 에디터
http://localhost:8000/floorplan/view   ← 보기 전용
```
- 에디터에서 상단 **"백엔드 연결됨 · 센서 N개"**(초록)면 성공.
- 화면이 안 뜨고 `{"detail":"Not Found"}` 면 → static 폴더/파일명 확인.

## 5) Home Assistant 에 넣기

> URL의 IP는 **PC의 현재 IPv4**(WiFi 어댑터)로. `ipconfig` 의 `Wireless LAN adapter Wi-Fi` IPv4.
> (WiFi 를 바꿨으면 예전 192.168.1.83 이 아닐 수 있음. 예시는 `192.168.0.12` 로 둠 — 본인 IP로 교체.)

### (A) Location 대시보드 — 보기 전용 카드 (그림처럼)
HA 대시보드 → 우상단 ✏️ → 카드 추가 → **수동(Manual)** → 붙여넣기:
```yaml
type: iframe
url: http://192.168.0.12:8000/floorplan/view
aspect_ratio: 68%
```
범례 숨기려면: `url: http://192.168.0.12:8000/floorplan/view?legend=0`

### (B) 평면도 설정용 에디터 — 사이드바 패널
HA 의 `configuration.yaml` (보통 `C:\homeassistant\configuration.yaml`) 에 추가:
```yaml
panel_iframe:
  floorplan_editor:
    title: "평면도 설정"
    icon: mdi:floor-plan
    url: "http://192.168.0.12:8000/floorplan"
    require_admin: true
```
저장 → HA 재시작(`docker restart homeassistant`) → 사이드바에 패널 생성.

## 6) 사용 흐름

1. (A 또는 B의 에디터)에서 방 그리기 → 이름 → 배치 → **방마다 센서(`esp32-livingroom-01`) 연결** → **"Home Assistant에 저장"**
2. Location 카드(보기 전용)가 그 평면도를 표시하고, **방 움직임에 따라 실시간으로 색**이 바뀜.

---

## 문제 해결

| 증상 | 원인 / 해결 |
|---|---|
| `/floorplan` 이 `Not Found` | `backend/static/` 위치·파일명 확인, `docker compose restart backend` |
| 에디터 상단 빨간 배너(연결 실패) | 같은 PC면 보통 OK. 다른 기기서 열면 URL을 `localhost` 말고 PC IP로 |
| HA 카드가 빈 화면 | 폰/PC 브라우저에서 그 `url` 이 직접 열리는지 확인(반드시 PC LAN IP) |
| 평면도는 뜨는데 색이 안 변함 | HA→백엔드로 readings 적재가 되는지(아래) + 방에 센서 연결했는지 |
| 방이 항상 "센서 없음" | 4단계에서 그 방에 device(`esp32-livingroom-01`) 를 지정했는지 |

> ⚠️ **실시간 색**이 뜨려면 HA가 ESP32 데이터를 백엔드 `/api/v1/readings` 로 보내고 있어야 합니다.
> (HA automation / rest_command). 이 연동이 안 돼 있으면 평면도는 그려지지만 상태는 "데이터 없음"으로 남습니다.
> 이 부분은 백엔드 README(`ESP32-SENSOR-SETUP.md`)나 별도 안내 참고 — 필요하면 같이 봐드립니다.
