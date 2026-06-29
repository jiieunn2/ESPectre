# 우리집 평면도 — HTML 에디터 (HA iframe)

두 개의 단일 HTML 파일:

| 파일 | 용도 | HA 위치 |
|---|---|---|
| `floorplan.html` | **에디터**(설정용). 방 그리기 → 이름 → 배치 → 센서 연결 → 저장 | 설정 패널 |
| `floorplan-view.html` | **보기 전용**(실시간). 저장된 평면도를 화면에 꽉 차게 그리고 방별 상태로 색칠. 버튼/위저드 없음 | **Location 대시보드 iframe** |

한 번 에디터로 평면도를 만들어 저장하면, 일상에서는 **보기 전용 화면**을 Location에 iframe으로
띄워 둔다. (보기 전용은 3초마다 백엔드를 폴링해 자동으로 색이 바뀐다.)

- 저장: `POST /api/v1/floorplans`
- 불러오기: `GET /api/v1/floorplans/latest`
- 실시간: `GET /api/v1/devices` + `GET /api/v1/devices/{id}/state` (3초 폴링)
- 인증: 모든 호출에 `X-API-Key` 헤더 (Phase 1 공유 키)

데이터 형식은 iOS 앱(`FloorPlanModels.swift`)과 호환된다:
`data.rooms[].polygon = [[x,y],…]`(에디터 좌표) + `device_key`. 렌더는 자동 축척이라 단위 무관.

---

## 호스팅 = 옵션 A: **백엔드(FastAPI)가 HTML도 서빙** (HTTP 환경 권장)

HTML과 API가 **같은 origin**(`http://192.168.1.83:8000`)이 되므로 **CORS가 필요 없다.**
HTML 안의 `API_BASE`는 빈 문자열(상대경로)이라 그대로 동작한다.

### 1) 백엔드에 정적 서빙 추가

두 HTML을 백엔드 컨테이너가 접근 가능한 폴더(예: `app/static/`)에 복사한 뒤,
FastAPI 앱에 라우트 2개를 추가한다:

```python
# main.py (혹은 app 생성 파일)
from fastapi.responses import FileResponse
from pathlib import Path

STATIC_DIR = Path(__file__).parent / "static"

@app.get("/floorplan")          # 에디터(설정용)
def floorplan_editor():
    return FileResponse(STATIC_DIR / "floorplan.html")

@app.get("/floorplan/view")     # 보기 전용(Location iframe용)
def floorplan_view():
    return FileResponse(STATIC_DIR / "floorplan-view.html")
```

> Docker라면 `static/`이 이미지에 포함되도록 `COPY` 하거나 볼륨으로 마운트.
> 예: `docker-compose.yml`의 backend 서비스에
> ```yaml
> volumes:
>   - ./ha-floorplan/floorplan.html:/app/static/floorplan.html:ro
>   - ./ha-floorplan/floorplan-view.html:/app/static/floorplan-view.html:ro
> ```

### 2) 브라우저로 먼저 확인

- 에디터: `http://192.168.1.83:8000/floorplan` → 상단 **"백엔드 연결됨 · 센서 N개"**(초록)면 성공.
- 보기: `http://192.168.1.83:8000/floorplan/view` → 저장한 평면도가 실시간 색으로 보이면 성공.

빨간 배너/“연결 끊김”이면 주소/키/방화벽(8000 인바운드)을 확인.

### 3) Home Assistant에 iframe으로 추가

**(a) 에디터 — 설정용 사이드바 패널** — `configuration.yaml`:
```yaml
panel_iframe:
  floorplan_editor:
    title: "평면도 설정"
    icon: mdi:floor-plan
    url: "http://192.168.1.83:8000/floorplan"
    require_admin: true        # 설정은 관리자만
```

**(b) 보기 전용 — Location 대시보드 카드(이미지처럼)** — Lovelace에 카드 추가(YAML):
```yaml
type: iframe
url: http://192.168.1.83:8000/floorplan/view
aspect_ratio: 68%            # 평면도 viewBox(1000x680) 비율에 맞춤. 취향대로 조절
```
> 범례를 숨기고 더 "그림"처럼 쓰려면 URL 뒤에 `?legend=0` 을 붙인다:
> `http://192.168.1.83:8000/floorplan/view?legend=0`

평면도를 한 번 에디터에서 저장하면, Location 카드의 평면도가 **방 움직임에 따라 실시간으로
색**이 바뀐다. 같은 Wi-Fi에서 HA를 **HTTP**로 접속하면 이대로 동작한다.

---

## (대안) 옵션 B: HA `www/` 폴더 + 백엔드 CORS

HA를 HTTPS로 쓰거나 백엔드에 라우트를 못 넣는 경우.

1. `floorplan.html`을 HA의 `config/www/`에 복사 → `http://<HA>:8123/local/floorplan.html`.
2. 이때 페이지(`:8123`)와 API(`:8000`)의 **origin이 다르므로** 백엔드에 CORS 허용 필요:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],          # 로컬 전용. 운영시엔 HA origin만 지정 권장
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
3. iframe URL에 백엔드 주소를 넘긴다(상대경로가 안 되므로):
   `http://<HA>:8123/local/floorplan.html?api=http://192.168.1.83:8000`
4. HA iframe 설정은 위 (a)/(b)와 동일하되 `url`만 위 주소로.

> ⚠️ HA가 **HTTPS**면, HTTPS 페이지에서 HTTP(`:8000`) API 호출은 브라우저가 막는다
> (mixed content). 그 경우 백엔드도 HTTPS(리버스 프록시)로 올려야 한다. → 지금은 HTTP 사용이므로 옵션 A 권장.

---

## 설정값 바꾸기

`floorplan.html` 상단 `CONFIG`:
- `API_BASE`: 같은 origin이면 `""`. 다르면 `"http://192.168.1.83:8000"`. (또는 iframe URL `?api=`)
- `API_KEY`: 백엔드 `.env`의 `API_KEY`와 동일. (또는 `?key=`)
- `POLL_MS`: 실시간 갱신 주기(ms). 기본 3000.

## 동작 테스트

평면도를 저장한 뒤, PC에서 움직임 데이터를 넣으면 해당 방이 **활동중**(초록)으로 색칠된다:
```bash
curl -X POST http://localhost:8000/api/v1/readings \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"device_key":"esp32-livingroom-01","movement_score":0.9,"motion_detected":true}'
```

## 참고

- 위저드에서 만든 방은 **축 정렬 사각형**(polygon 4점)으로 저장된다. iOS 앱의 평면도 탭과
  같은 데이터라 둘 다 같은 평면도를 본다.
- 방을 백엔드 센서와 잇는 매칭 우선순위: **방에 지정한 `device_key`** → 없으면 백엔드가
  `device.location == 방이름` 으로 보조 매칭. 확실하게 하려면 4단계에서 센서를 직접 지정.
- 백엔드에 연결 안 되면 마지막 편집본을 브라우저 `localStorage`에 캐시해 두고 보여준다.
