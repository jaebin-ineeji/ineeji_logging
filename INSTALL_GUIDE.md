# ineeji_logging 설치 및 사용 가이드

## 1. 설치 방법

### 가상 환경 생성 및 활성화 (권장)

```bash
# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화 (Linux/Mac)
source venv/bin/activate

# 가상 환경 활성화 (Windows)
venv\Scripts\activate
```

### 패키지 설치

```bash
# 개발 모드로 설치 (소스 코드 변경 시 재설치 필요 없음)
pip install -e .

# 또는 일반 설치
pip install .
```

## 2. 일별 로그 설정 방법

### 방법 1: 직접 일별 로그 파일 경로 설정

```python
from ineeji_logging import Logger
from datetime import datetime

# 일별 로그 파일 경로 생성
logs_dir = "logs"
today = datetime.now().strftime('%Y%m%d')
log_file = f"{logs_dir}/app_{today}.log"

# 로거 생성
logger = Logger("my_app", log_file=log_file)

# 로그 작성
logger.info("애플리케이션 시작")
logger.warning("경고 메시지")
logger.error("에러 메시지")
```

### 방법 2: 프로덕션 환경 설정 사용 (자동 일별 로그)

```python
from ineeji_logging import Logger

# 프로덕션 설정 사용 (자동으로 일별 로그 파일 생성)
prod_config = Logger.get_default_config("production")
logger = Logger("my_app", **prod_config)

# 로그 작성 (WARNING 레벨 이상만 기록됨)
logger.warning("경고 메시지")
logger.error("에러 메시지")
```

## 3. 환경별 설정

ineeji_logging은 세 가지 기본 환경 설정을 제공합니다:

1. **development**: 디버그 레벨 로깅, 콘솔 출력 활성화, 파일 로깅 비활성화
2. **test**: 정보 레벨 로깅, 콘솔 출력 활성화, 파일 로깅 비활성화
3. **production**: 경고 레벨 로깅, 콘솔 출력 비활성화, 일별 파일 로깅 활성화

```python
# 환경별 설정 가져오기
dev_config = Logger.get_default_config("development")
test_config = Logger.get_default_config("test")
prod_config = Logger.get_default_config("production")

# 설정 사용하여 로거 생성
dev_logger = Logger("dev_app", **dev_config)
test_logger = Logger("test_app", **test_config)
prod_logger = Logger("prod_app", **prod_config)
```

## 4. 주의사항

- 로그 파일을 사용할 경우 로그 디렉토리(`logs/`)가 자동 생성됩니다.
- 프로덕션 환경에서는 WARNING 레벨 이상의 로그만 기록됩니다.
- 일별 로그 파일은 `logs/app_YYYYMMDD.log` 형식으로 생성됩니다. 