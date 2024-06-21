# Supervisor

## 실행 요구사항

### Docker

아래 명령어를 실행해 `docker` 명령어가 가능한지 확인해주세요.

```sh
docker version
```

_**Docker Engine** 25.02 버전에서 테스트 됐습니다._

## 실행하는 방법

### 1. 환경변수 파일 복사

아래 명령어를 호출해, `.env.example` 파일을 `.env`로 복사합니다.

```sh
# Linux/macOS, Windows pwsh
cp .env.example .env
```

`DB_USERNAME`, `DB_PASSWORD`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`의
기본값은 `supervisor`입니다.

환경 내 **8000**, **8100** 포트가 이미 사용 중인 경우,
`.env` 파일 내 `API_PORT`와 `DB_PORT` 값을 변경해주세요.

### 2. DB 실행

아래 명령어를 호출해, DB를 실행합니다.

```sh
docker compose up -d db
```

### 3. DB 마이그레이션

아래 명령어를 호출해, DB를 마이그레이션하고 admin 유저를 생성합니다.

```sh
dotenv run -- alembic upgrade head
```

### 4. API 서버 빌드 및 실행

아래 명령어를 호출해, API 서버를 빌드하고 실행합니다.

```sh
docker compose build api
docker compose up -d api
```
