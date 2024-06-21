# Supervisor

**요구사항 외 구현사항**

- 삭제시 복구 가능성도 필요할 수 있으므로, soft delete로 구현했습니다.
- 비밀번호(해싱된)는 `users` 테이블이 아닌 `user_secrets` 테이블에 저장합니다.
  - 민감 정보를 잘못 반환하는 케이스를 줄이기 위해 테이블을 분리했습니다.
- 자동화된 API 테스트를 추가했습니다.

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

### API 테스트

테스트 실행시 아래 항목이 실행됩니다.

- 어드민 계정 생성
  - `.env` 내 `ADMIN_USERNAME`, `ADMIN_PASSWORD`로 생성됩니다.
  - 해당 사용자명이 존재하면, 스킵됩니다.
- API 테스트

아래 명령어를 사용해, 테스트를 실행해주세요.

```sh
pytest
```

## 모델 설명

### ERD

![erd](/images/erd.png)

### users 테이블

- `id`: primary key이며 정수형입니다.
- `username`: 사용자의 이름이며 unique입니다.
  - 사용자 이름으로 엔터티 조회가 필요해 index를 생성했습니다.
- `role`: 권한 역할입니다. `basic`과 `admin`이 있습니다. 기본값은 `basic`입니다.
- `created_at`, `updated_at`, `deleted_at`: timezone 정보를 포함한 timestamp이며 각각 생성시, 업데이트시, 삭제시 값을 저장합니다.
  - `deleted_at`은 nullable하며 이를 사용해 soft delete를 구현합니다.

### user_secrets 테이블

- `id`: primary key이며 정수형입니다.
- `user_id`: 정수형이며 `users.id`의 foreign key입니다.
- `hashed_password`: 문자열 타입이며 해싱된 비밀번호입니다.
- `created_at`, `updated_at`, `deleted_at`: 위 users의 기능과 같습니다.

user 조회시 민감정보가 실수로 공개되지 않도록, user_secrets 테이블을 분리했습니다.
user와 user_secret은 1:1 관계입니다.

### reservations 테이블

- `id`: primary key이며 정수형입니다.
- `user_id`: 정수형이며 `users.id`의 foreign key입니다.
- `start_at`: timezone 정보를 포함한 timestamp이며 예약 시험의 시작 시각입니다.
- `end_at`: timezone 정보를 포함한 timestamp이며 예약 시험의 종료 시각입니다.
- `applicant_count`: 정수형이며 응시자의 수입니다.
- `is_confirmed`: bool 타입이며 확정 유무입니다.
- `created_at`, `updated_at`, `deleted_at`: 위 users의 기능과 같습니다.

user와 reservation은 1:N 관계입니다.  
예약 생성이나 가능한 예약 시간 조회시 빈번히 사용해서,
`start_at`, `end_at`, `is_confirmed`, `deleted_at`을 묶어 index를 생성했습니다.  
아래는 python 구현 일부입니다.

```py
result = await self.db_service.execute(
    select(func.sum(models.Reservation.applicant_count)).where(
        models.Reservation.start_at <= dto.start_at,
        models.Reservation.end_at >= dto.end_at,
        models.Reservation.is_confirmed == True,
        models.Reservation.deleted_at == None,
    )
)
total_applicant_count = (result.scalar() or 0) + dto.applicant_count
```

## API 목록

- POST /auth/token
- POST /auth/refresh
- GET /users/me
- POST /users
- GET /reservations
- POST /reservations
- PATCH /reservations/{reservation_id}
- DELETE /reservations/{reservation_id}
- GET /reservations/publics

## API 설명

### POST /auth/token

로그인 후 토큰을 생성합니다.  
모든 사용자는 로그인 후 토큰을 발급받아, 다른 API 요청시 사용해야 합니다.

#### 패러미터

form data로 받습니다.

- `username`: 문자열
- `password`: 문자열

#### 반환 코드

- 201: 생성에 성공했습니다.
- 422: 패러미터가 비정상입니다.

#### 반환 데이터 예

```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "string"
}
```

### POST /auth/refresh

refresh token으로 access token을 갱신합니다.

#### 패러미터

query string으로 받습니다.

- `refresh_token`: 문자열
  - refresh token 값입니다.

### GET /users/me

현재 사용자의 정보를 조회합니다.

#### 패러미터

authorization bearer로 access token을 받습니다.

#### 반환 코드

- 성공시 200을 반환합니다.

#### 반환 데이터 예

```json
{
  "id": 0,
  "username": "string",
  "role": "basic",
  "created_at": "2024-06-21T07:56:52.597Z",
  "updated_at": "2024-06-21T07:56:52.597Z",
  "deleted_at": "2024-06-21T07:56:52.597Z"
}
```

### POST /users

사용자를 추가합니다.

#### 패러미터

json body로 받습니다.

- `username`: 문자열
  - 사용자의 이름입니다.
- `password`: 문자열
  - 사용자의 비밀번호입니다.

#### 반환 코드

- 201: 생성에 성공했습니다.
- 422: 패러미터가 비정상입니다.

#### 반환 데이터 예

```json
{
  "id": 0,
  "username": "string",
  "role": "basic",
  "created_at": "2024-06-21T08:02:08.379Z",
  "updated_at": "2024-06-21T08:02:08.379Z",
  "deleted_at": "2024-06-21T08:02:08.379Z"
}
```

### GET /reservations

현재 사용자의 예약을 조회합니다.

#### 패러미터

authorization bearer로 access token을 받습니다.

#### 반환 코드

- 200: 조회에 성공했습니다.

#### 반환 데이터 예

```json
[
  {
    "id": 0,
    "user_id": 0,
    "start_at": "2024-06-21T08:02:08.381Z",
    "end_at": "2024-06-21T08:02:08.381Z",
    "applicant_count": 0,
    "is_confirmed": true,
    "created_at": "2024-06-21T08:02:08.381Z",
    "updated_at": "2024-06-21T08:02:08.381Z",
    "deleted_at": "2024-06-21T08:02:08.381Z"
  }
]
```

### POST /reservations

예약을 추가합니다.

#### 패러미터

authorization bearer로 access token을 받습니다.

json body로 받습니다.

- `start_at`: iso utc 시간 문자열
  - 시험 시작 시각입니다.
- `end_at`: iso utc 시간 문자열
  - 시험 종료 시각입니다.
- `applicant_count`: 정수형
  - 시험 응시자 수입니다.

#### 반환 코드

- 201: 생성에 성공했습니다.
- 422: 패러미터가 비정상입니다.

#### 반환 데이터 예

```json
{
  "id": 0,
  "user_id": 0,
  "start_at": "2024-06-21T08:05:59.193Z",
  "end_at": "2024-06-21T08:05:59.193Z",
  "applicant_count": 0,
  "is_confirmed": true,
  "created_at": "2024-06-21T08:05:59.193Z",
  "updated_at": "2024-06-21T08:05:59.193Z",
  "deleted_at": "2024-06-21T08:05:59.193Z"
}
```

### PATCH /reservations/{reservation_id}

예약을 업데이트합니다.

#### 패러미터

authorization bearer로 access token을 받습니다.
path parameter로 `reservation_id`를 받습니다.

json body로 받습니다.

- `start_at`: iso utc 시간 문자열
  - 시험 시작 시각입니다.
- `end_at`: iso utc 시간 문자열
  - 시험 종료 시각입니다.
- `applicant_count`: 정수형
  - 시험 응시자 수입니다.
- `is_confirmed`: 확정 유무입니다.

#### 반환 코드

- 200: 업데이트에 성공했습니다.
- 422: 패러미터가 비정상입니다.

#### 반환 데이터 예

```json
{
  "id": 0,
  "user_id": 0,
  "start_at": "2024-06-21T08:10:08.230Z",
  "end_at": "2024-06-21T08:10:08.230Z",
  "applicant_count": 0,
  "is_confirmed": true,
  "created_at": "2024-06-21T08:10:08.230Z",
  "updated_at": "2024-06-21T08:10:08.230Z",
  "deleted_at": "2024-06-21T08:10:08.230Z"
}
```

### DELETE /reservations/{reservation_id}

예약을 삭제합니다.

#### 패러미터

authorization bearer로 access token을 받습니다.
path parameter로 `reservation_id`를 받습니다.

#### 반환 코드

- 200: 삭제에 성공했습니다.
- 422: 패러미터가 비정상입니다.

#### 반환 데이터 예

```json
{
  "id": 0,
  "user_id": 0,
  "start_at": "2024-06-21T08:13:17.576Z",
  "end_at": "2024-06-21T08:13:17.576Z",
  "applicant_count": 0,
  "is_confirmed": true,
  "created_at": "2024-06-21T08:13:17.576Z",
  "updated_at": "2024-06-21T08:13:17.576Z",
  "deleted_at": "2024-06-21T08:13:17.576Z"
}
```

### GET /reservations/publics

특정 시간대 내 공개 가능한 예약 정보들을 조회합니다.

#### 패러미터

authorization bearer로 access token을 받습니다.

query string으로 받습니다.

- `start_at`: iso utc 시간 문자열
  - 조회할 시작 시각입니다.
- `end_at`: iso utc 시간 문자열
  - 조회할 종료 시각입니다.

#### 반환 코드

- 200: 조회에 성공했습니다.
- 422: 패러미터가 비정상입니다.

#### 반환 데이터 예

```json
[
  {
    "start_at": "2024-06-21T08:16:54.580Z",
    "end_at": "2024-06-21T08:16:54.580Z",
    "applicant_count": 0
  }
]
```
