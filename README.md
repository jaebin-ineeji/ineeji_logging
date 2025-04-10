# ineeji_logging

ineeji 프로젝트를 위한 공통 로깅 라이브러리입니다.

## 특징

- 다양한 로깅 레벨 지원 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- 파일 및 콘솔 로깅 지원
- 커스텀 포맷터 지원
- 다양한 환경(개발, 테스트, 프로덕션)에 맞는 설정 제공
- 일별 로그 파일 자동 생성 지원

## 설치 방법

### GitHub 저장소에서 직접 설치

```bash
# uv 사용 (권장)
uv pip install git+https://github.com/jaebin-ineeji/ineeji_logging.git

# 또는 pip 사용
pip install git+https://github.com/jaebin-ineeji/ineeji_logging.git
```

자세한 설치 옵션은 [INSTALL.md](INSTALL.md) 파일을 참고하세요.

### 로컬 소스에서 설치

### uv를 사용한 설치 (권장)

```bash
# 패키지 설치
uv pip install .

# 개발 모드 설치 (소스 변경 시 재설치 필요 없음)
uv pip install -e .
```

### pip를 사용한 설치

```bash
# 패키지 설치
pip install .

# 개발 모드 설치 (소스 변경 시 재설치 필요 없음)
pip install -e .
```

## 사용법

### 기본 사용 방법
```python
from ineeji_logging import Logger

# 로거 생성
logger = Logger("my_application")

# 로그 작성
logger.debug("디버그 메시지")
logger.info("정보 메시지")
logger.warning("경고 메시지")
logger.error("에러 메시지")
logger.critical("치명적 에러 메시지")
```

### 일별 로그 파일 생성
```python
from ineeji_logging import Logger
from datetime import datetime

# 일별 로그 파일 경로 생성
today = datetime.now().strftime('%Y%m%d')
log_file = f"logs/app_{today}.log"

# 로거 생성
logger = Logger("my_application", log_file=log_file)

# 로그 작성
logger.info("이 메시지는 오늘 날짜의 로그 파일에 저장됩니다")
```

### 프로덕션 환경 설정 사용 (자동 일별 로그)
```python
from ineeji_logging import Logger

# 프로덕션 설정 가져오기 (자동으로 일별 로그 파일 사용)
prod_config = Logger.get_default_config("production")
logger = Logger("my_application", **prod_config)

# 로그 작성 (WARNING 레벨 이상만 기록됨)
logger.warning("이 메시지는 오늘 날짜의 로그 파일에 저장됩니다")
```

## 라이센스

Copyright (c) 2025 ineeji Team 