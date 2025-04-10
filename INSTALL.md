# ineeji_logging 설치 및 사용 가이드

## 설치 방법

### 1. GitHub 저장소에서 직접 설치 (PyPI 배포 없이)

GitHub 저장소에 올린 패키지를 PyPI에 배포하지 않고도 pip 또는 uv로 직접 설치할 수 있습니다.

#### uv 사용 (권장)

```bash
# 최신 main 브랜치에서 설치
uv pip install git+https://github.com/jaebin-ineeji/ineeji_logging.git

# 특정 브랜치나 태그에서 설치
uv pip install git+https://github.com/jaebin-ineeji/ineeji_logging.git@main
uv pip install git+https://github.com/jaebin-ineeji/ineeji_logging.git@v0.1.0

# 개발 모드로 설치 (소스 수정 시 재설치 불필요)
uv pip install -e git+https://github.com/jaebin-ineeji/ineeji_logging.git@main#egg=ineeji_logging
```

#### pip 사용

```bash
# 최신 main 브랜치에서 설치
pip install git+https://github.com/jaebin-ineeji/ineeji_logging.git

# 특정 브랜치나 태그에서 설치
pip install git+https://github.com/jaebin-ineeji/ineeji_logging.git@main
pip install git+https://github.com/jaebin-ineeji/ineeji_logging.git@v0.1.0

# 개발 모드로 설치 (소스 수정 시 재설치 불필요)
pip install -e git+https://github.com/jaebin-ineeji/ineeji_logging.git@main#egg=ineeji_logging
```

#### requirements.txt에 추가하는 방법

다음과 같이 requirements.txt 파일에 추가할 수도 있습니다:

```
git+https://github.com/jaebin-ineeji/ineeji_logging.git@main
```

### 2. 로컬 소스에서 설치

#### uv를 사용한 설치 (권장)

[uv](https://github.com/astral-sh/uv)는 빠르고 효율적인 Python 패키지 설치 도구입니다.

```bash
# 프로젝트 디렉터리로 이동
cd /path/to/ineeji_logging

# 일반 설치
uv pip install .

# 또는 개발 모드로 설치 (코드 변경 시 재설치 필요 없음)
uv pip install -e .
```

#### pip를 사용한 설치

```bash
# 프로젝트 디렉터리로 이동
cd /path/to/ineeji_logging

# 일반 설치
pip install .

# 또는 개발 모드로 설치 (코드 변경 시 재설치 필요 없음)
pip install -e .
```

## 설치 확인

설치가 제대로 되었는지 확인하려면 다음 명령어를 실행해보세요:

```bash
python -c "from ineeji_logging import Logger; print(Logger.__module__)"
```

성공적으로 설치되었다면 `ineeji_logging.logger`가 출력됩니다.

## 패키지 사용 방법

설치 후 아래와 같이 패키지를 임포트하여 사용할 수 있습니다:

```python
from ineeji_logging import Logger

# 기본 로거 생성
logger = Logger("my_app")

# 다양한 레벨의 로그 메시지 출력
logger.debug("디버그 메시지입니다.")
logger.info("정보 메시지입니다.")
logger.warning("경고 메시지입니다.")
logger.error("에러 메시지입니다.")

# 로그 레벨 변경
logger.set_level(Logger.DEBUG)

# 파일 로깅 예제
file_logger = Logger(
    "file_example", 
    log_file="logs/app.log", 
    level=Logger.DEBUG
)
file_logger.info("이 메시지는 파일에 기록됩니다.")
```

더 자세한 사용 예제는 `examples` 디렉터리의 예제 파일을 참고하세요. 