# ineeji_logging 인터페이스 설계

이 문서는 ineeji_logging 라이브러리의 인터페이스 설계를 설명합니다.

## Logger 클래스

### 생성자

```python
Logger(
    name: str, 
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    console_output: bool = True,
    format_string: Optional[str] = None
)
```

#### 매개변수
- `name`: 로거 이름
- `level`: 로깅 레벨 (기본값: INFO)
- `log_file`: 로그 파일 경로 (없으면 파일 로깅 비활성화)
- `console_output`: 콘솔 출력 여부 (기본값: True)
- `format_string`: 사용자 정의 로그 포맷 (없으면 기본 포맷 사용)

### 메서드

#### 로그 레벨 메서드
```python
debug(message: str, **kwargs)
info(message: str, **kwargs)
warning(message: str, **kwargs)
error(message: str, **kwargs)
critical(message: str, **kwargs)
exception(message: str, exc_info=True, **kwargs)
```

#### 설정 메서드
```python
set_level(level: int)
```

#### 정적 메서드
```python
@staticmethod
get_default_config(env: str = "development") -> Dict[str, Any]
```

## 확장 계획 (향후 구현)

### LogFormatter 인터페이스
```python
class LogFormatter:
    def format(self, record: logging.LogRecord) -> str:
        pass
```

### JSONFormatter 클래스
```python
class JSONFormatter(LogFormatter):
    def __init__(self, fields: Optional[List[str]] = None):
        pass
    
    def format(self, record: logging.LogRecord) -> str:
        pass
```

### 로그 핸들러
```python
class EmailHandler(logging.Handler):
    def __init__(self, recipients: List[str], subject: str, ...):
        pass

class DatabaseHandler(logging.Handler):
    def __init__(self, connection_string: str, table: str, ...):
        pass

class RemoteHandler(logging.Handler):
    def __init__(self, host: str, port: int, ...):
        pass
```

### 로그 필터
```python
class FieldFilter(logging.Filter):
    def __init__(self, field: str, value: Any):
        pass
    
    def filter(self, record: logging.LogRecord) -> bool:
        pass
```

### 비동기 로깅
```python
class AsyncLogger(Logger):
    def __init__(self, name: str, queue_size: int = 1000, ...):
        pass
    
    def flush(self):
        pass
``` 