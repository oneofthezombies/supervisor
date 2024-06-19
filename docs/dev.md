# 개발 환경

## 실행하는 방법

### .env 파일 복사하기

[README](../README.md) 내 **실행하는 방법 - .env 파일 복사하기**를 확인해주세요.

### Docker Compose로 실행하기

아래 명령어를 호출해, 도커 환경에서 API 서버와 DB를 실행합니다.

```sh
docker compose -f compose.dev.yaml up --build
```

### VS Code Python 지원

```sh
python -m venv .venv

# pwsh에서
.venv\Scripts\activate.ps1

pip install -r requirements.txt
```

VS Code에서 아무 `.py` 파일 연 상태에서,
오른쪽 하단 인터프리터 선택에서 .venv 인터프리터를 선택합니다.
