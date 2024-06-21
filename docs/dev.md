# 개발 환경 구성

## 실행 요구사항

### Docker

[README](../README.md) 내 **실행 요구사항 - Docker**를 확인해주세요.

### Python

3.8 또는 그 이상

```sh
python --version
```

## 실행하는 방법

### 환경변수 파일 복사 및 DB 초기화

[README](../README.md) 내 **실행하는 방법 - 1. 환경변수 파일 복사, 2. DB 실행, 3. DB 마이그레이션**을 해주세요.

### Python 가상 환경 구성

```sh
python -m venv .venv

# Linux/macOS
. .venv/bin/activate

# pwsh
.venv\Scripts\activate.ps1

pip install -r requirements.txt
```

#### VS Code에서 Python 지원

VS Code에서 아무 `.py` 파일 연 상태에서,
오른쪽 하단 인터프리터 선택에서 .venv 인터프리터를 선택합니다.

### API 서버 실행

```sh
dotenv run -- fastapi dev src/main.py --reload
```

## DB 마이그레이션 생성

```sh
dotenv run -- alembic revision --autogenerate -m "<your message>"
```
