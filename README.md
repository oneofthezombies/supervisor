# Supervisor

## 실행 요구사항

### Docker

아래 명령어를 실행해 `docker` 명령어가 가능한지 확인해주세요.  
API 서버와 DB 실행을 위해 필요합니다.

```sh
docker version
```

_**Docker Engine** 25.02 버전에서 테스트 됐습니다._

### Python

3.8 또는 그 이상의 버전이 필요합니다.  
DB 마이그레이션, 어드민 계정 생성 그리고 API 테스트를 위해 필요합니다.

```sh
python --version
```

_**Python** 3.8 버전에서 테스트 됐습니다._

## 실행하는 방법

### 환경변수 파일 복사

프로젝트 경로의 `.env.example` 파일을 `.env`로 복사해주세요.  
아래 명령어를 사용하거나 파일 탐색기에서 복사 붙여넣기 해주세요.

```sh
# Linux, macOS, Windows pwsh
cp .env.example .env
```

아래는 `.env` 파일 내 환경변수 목록입니다.  
실행 장비의 **8000**, **8100** 포트를 필요로 합니다.  
만약 해당 포트가 사용중일 경우, `.env` 파일 내 `API_PORT` 또는 `DB_PORT`를 수정해주세요.

```sh
API_PORT=8000
DB_USERNAME=supervisor
DB_PASSWORD=supervisor
DB_HOST=127.0.0.1
DB_PORT=8100
ADMIN_USERNAME=supervisor
ADMIN_PASSWORD=supervisor
AUTH_JWT_SECRET_KEY=supervisor
```

### DB 및 API 서버 실행

아래 명령어를 호출해, DB와 API 서버를 실행합니다.

```sh
docker compose up --build -d
```

### DB 마이그레이션

먼저, 파이썬 가상환경을 활성화해주세요.

```sh
# 가상환경 생성
python -m venv .venv

# Windows pwsh에서 활성화
.venv\Scripts\activate.ps1

# Linux, macOS에서 활성화
source .venv/bin/activate

# 가상환경에 패키지 설치
pip install -r requirements.txt
```

아래 명령어를 호출해, DB를 마이그레이션 해주세요.

```sh
dotenv run -- alembic upgrade head
```

### API 서버 확인

브라우저에서 `http://127.0.0.1:8000/docs`를 접속해주세요.

_만약 환경변수 `API_PORT`의 값을 바꿨다면, 해당 포트로 접속해주세요._

Swagger (OpenAPI) UI가 떴다면, 정상 실행이 된 것입니다.

### 자동화된 테스트

테스트 실행시 아래 항목이 실행됩니다.

- 어드민 계정 생성
  - `.env` 내 `ADMIN_USERNAME`, `ADMIN_PASSWORD`로 생성됩니다.
  - 해당 사용자명이 존재하면, 스킵됩니다.
- API 테스트

아래 명령어를 사용해, 테스트를 실행해주세요.

```sh
pytest
```
