# Supervisor

## 실행 요구사항

### Docker

아래 명령어를 실행해 `docker` 명령어가 가능한지 확인해주세요.

```sh
docker version
```

_**Docker Engine** 25.02 버전에서 테스트 됐습니다._

## 실행하는 방법

### .env 파일 복사하기

`.env.example` 파일을 `.env`로 복사합니다.  
환경 내 **8000**, **8100** 포트가 이미 사용 중인 경우,
`.env` 파일 내 `API_PORT`와 `DB_PORT` 값을 변경해주세요.

```sh
cp .env.example .env
```

### Docker Compose로 실행하기

아래 명령어를 호출해, 도커 환경에서 API 서버와 DB를 실행합니다.

```sh
docker compose -f compose.prod.yaml up --build
```
