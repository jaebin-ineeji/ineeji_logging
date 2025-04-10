# ineeji_logging 문서

ineeji_logging 라이브러리의 공식 문서에 오신 것을 환영합니다.

## 문서 목차

1. [시작하기](#시작하기)
2. [인터페이스](interface.md)
3. [예제](../examples)
4. [고급 사용법](#고급-사용법)

## 시작하기

### 설치

```bash
# pip을 이용한 설치
pip install ineeji_logging

# 또는 소스에서 직접 설치
git clone https://github.com/ineeji/ineeji_logging.git
cd ineeji_logging
pip install -e .
```

### 기본 사용법

```python
from ineeji_logging import Logger

# 기본 로거 생성
logger = Logger("my_app")

# 로그 메시지 작성
logger.info("애플리케이션 시작")
logger.debug("디버그 정보")
logger.warning("경고: 메모리 사용량이 높습니다")
logger.error("오류가 발생했습니다")

# 예외 로깅
try:
    # 코드...
except Exception as e:
    logger.exception(f"예외가 발생했습니다: {e}")
```

### 로그 파일 사용

```python
# 파일 로깅 활성화
logger = Logger(
    "my_app", 
    log_file="logs/app.log", 
    level=Logger.DEBUG
)

# 로그 작성
logger.info("이 메시지는 파일에 기록됩니다")
```

## 고급 사용법

### 환경별 설정 사용

```python
# 개발 환경 설정 가져오기
dev_config = Logger.get_default_config("development")
# 개발 환경 로거 생성
dev_logger = Logger("dev_app", **dev_config)

# 프로덕션 환경 설정 가져오기
prod_config = Logger.get_default_config("production")
# 프로덕션 환경 로거 생성
prod_logger = Logger("prod_app", **prod_config)
```

### 사용자 정의 포맷 사용

```python
# 사용자 정의 포맷 지정
custom_format = "%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s"

# 사용자 정의 포맷으로 로거 생성
logger = Logger("custom_app", format_string=custom_format)
```

## 추가 문서

더 자세한 내용은 [인터페이스 문서](interface.md)를 참조하세요. 