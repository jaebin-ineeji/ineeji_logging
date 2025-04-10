"""
Logger 클래스 구현
"""

import logging
import sys
import os
import pandas as pd
import signal
import atexit
import queue
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
from logging.handlers import QueueHandler, QueueListener


class ColoredFormatter(logging.Formatter):
    """
    색상이 적용된 로그 포맷터
    """
    
    # 로그 레벨별 색상 코드
    COLORS = {
        'DEBUG': '\033[0;36m',     # 청록색 (Cyan)
        'INFO': '\033[0;32m',      # 녹색 (Green)
        'WARNING': '\033[0;33m',   # 노란색 (Yellow)
        'ERROR': '\033[0;31m',     # 빨간색 (Red)
        'CRITICAL': '\033[1;31m',  # 굵은 빨간색 (Bold Red)
        'RESET': '\033[0m',        # 리셋
    }
    
    def format(self, record):
        # 원래 포맷 적용
        log_message = super().format(record)
        
        # 레벨명에만 색상 적용
        levelname = record.levelname
        if levelname in self.COLORS:
            # 로그 메시지에서 [레벨명] 부분만 색상을 적용
            colored_level = f"{self.COLORS[levelname]}[{levelname}]{self.COLORS['RESET']}"
            log_message = log_message.replace(f"[{levelname}]", colored_level)
        
        return log_message


class ParquetLogHandler(logging.Handler):
    """
    파케이 형식으로 로그를 저장하는 핸들러
    """
    
    _instances = []  # 모든 인스턴스를 추적
    
    def __init__(self, base_path: str, env: str, project_name: str, flush_threshold: int = 100):
        """
        파케이 로그 핸들러 초기화
        
        Args:
            base_path: 기본 로그 저장 경로
            env: 환경 이름 ('development', 'test', 'production')
            flush_threshold: 버퍼 플러시 임계값 (이 개수만큼 로그가 쌓이면 저장)
        """
        super().__init__()
        self.env = env
        self.project_name = project_name
        self.base_path = base_path
        self.logs_buffer: List[Dict[str, Any]] = []
        self.flush_threshold = flush_threshold  # 버퍼 플러시 임계값 
        self.buffer_lock = threading.RLock()  # 스레드 안전성을 위한 락
        
        # 인스턴스 등록 및 종료 시 처리
        ParquetLogHandler._instances.append(self)
        if len(ParquetLogHandler._instances) == 1:
            # 첫 번째 인스턴스에서만 종료 핸들러 등록
            atexit.register(ParquetLogHandler._flush_all_on_exit)
            signal.signal(signal.SIGTERM, ParquetLogHandler._handle_signal)
            signal.signal(signal.SIGINT, ParquetLogHandler._handle_signal)
    
    @classmethod
    def _flush_all_on_exit(cls):
        """프로그램 종료 시 모든 인스턴스의 버퍼 저장"""
        for instance in cls._instances:
            try:
                instance.flush()
            except Exception:
                # 종료 시 예외는 무시
                pass
    
    @classmethod
    def _handle_signal(cls, signum, frame):
        """시그널 처리"""
        cls._flush_all_on_exit()
        # 기본 시그널 핸들러 호출
        signal.default_int_handler(signum, frame)
        
    def emit(self, record):
        """로그 레코드 처리"""
        try:
            log_entry = {
                'datetime': datetime.fromtimestamp(record.created),
                'levelname': record.levelname,
                'name': record.name,
                'message': self.format(record),  # 포맷된 메시지
                'raw_message': record.getMessage(),  # 원본 메시지
                'pathname': record.pathname,
                'lineno': record.lineno,
                'funcName': record.funcName
            }
            
            # 예외 정보가 있으면 추가
            if record.exc_info:
                if self.formatter:
                    log_entry['exception'] = self.formatter.formatException(record.exc_info)
                else:
                    log_entry['exception'] = logging.Formatter().formatException(record.exc_info)
            
            with self.buffer_lock:
                self.logs_buffer.append(log_entry)
                
                # 버퍼 크기가 임계값에 도달하면 파일에 저장
                if len(self.logs_buffer) >= self.flush_threshold:
                    self.flush()
        except Exception:
            self.handleError(record)
    
    def flush(self):
        """버퍼에 있는 로그를 파케이 파일로 저장"""
        buffer_copy = None
        with self.buffer_lock:
            if not self.logs_buffer:
                return
            
            # 버퍼 복사 후 비우기
            buffer_copy = self.logs_buffer.copy()
            self.logs_buffer = []
        
        if not buffer_copy:
            return
            
        try:    
            # 로그 저장 경로 생성 (~/user/.ineeji/logs/<project_name>/<env>/<YYYY-MM-DD>/log.parquet)
            today = datetime.now().strftime('%Y-%m-%d')
            log_dir = Path(os.path.expanduser(self.base_path)) / self.project_name / self.env / today
            log_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = log_dir / 'log.parquet'
            
            # 데이터프레임 생성
            df = pd.DataFrame(buffer_copy)
            
            # 기존 파일이 있으면 추가, 없으면 새로 생성
            try:
                if log_file.exists():
                    existing_df = pd.read_parquet(log_file)
                    df = pd.concat([existing_df, df], ignore_index=True)
            except Exception:
                # 파일 읽기 실패 시 새로 저장
                pass
            
            # 파케이 파일로 저장
            df.to_parquet(log_file, index=False, engine='fastparquet', compression='snappy')
        except Exception:
            # 에러가 발생해도 계속 진행 (로깅 실패가 애플리케이션을 중단해서는 안 됨)
            pass
    
    def close(self):
        """핸들러 종료 시 버퍼에 남은 로그 저장"""
        try:
            self.flush()
        finally:
            super().close()


class DetailedFormatter(logging.Formatter):
    """
    심각한 로그 레벨에만 상세 정보를 추가하는 로그 포맷터
    """
    
    def __init__(self, fmt=None, datefmt=None, style: str = '%', detailed_fmt=None):
        # typing 오류 회피: Literal 타입으로 강제 변환
        style_char = '%'  # 기본값
        if style == '{':
            style_char = '{'
        elif style == '$':
            style_char = '$'
            
        super().__init__(fmt=fmt, datefmt=datefmt, style=style_char)
        self.detailed_fmt = detailed_fmt or fmt
    
    def format(self, record):
        # WARNING, ERROR, CRITICAL 레벨은 상세 포맷 사용
        if record.levelno >= logging.WARNING and self.detailed_fmt:
            original_fmt = self._style._fmt
            self._style._fmt = self.detailed_fmt
            result = super().format(record)
            self._style._fmt = original_fmt
            return result
        else:
            return super().format(record)


class ColoredDetailedFormatter(ColoredFormatter):
    """
    색상과 심각한 로그 레벨에 상세 정보를 추가하는 로그 포맷터
    """
    
    def __init__(self, fmt=None, datefmt=None, style: str = '%', detailed_fmt=None):
        # typing 오류 회피: Literal 타입으로 강제 변환
        style_char = '%'  # 기본값
        if style == '{':
            style_char = '{'
        elif style == '$':
            style_char = '$'
            
        super().__init__(fmt=fmt, datefmt=datefmt, style=style_char)
        self.detailed_fmt = detailed_fmt or fmt
    
    def format(self, record):
        # WARNING, ERROR, CRITICAL 레벨은 상세 포맷 사용
        if record.levelno >= logging.WARNING and self.detailed_fmt:
            original_fmt = self._style._fmt
            self._style._fmt = self.detailed_fmt
            result = super().format(record)
            self._style._fmt = original_fmt
            return result
        else:
            return super().format(record)


class Logger:
    """
    ineeji 프로젝트를 위한 통합 로깅 클래스
    비동기 로깅 기능을 지원합니다.
    """
    
    # 로그 레벨 상수
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    
    # 각 로거 이름당 하나의 QueueListener를 유지 
    _listeners = {}
    
    def __init__(
        self, 
        name: str, 
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        console_output: bool = True,
        format_string: Optional[str] = None,
        detailed_format_string: Optional[str] = None,  # 추가: 심각한 레벨용 상세 포맷
        parquet_logging: bool = False,
        project_name: Optional[str] = None,
        env: str = "development",
        colored_console: bool = True,
        async_logging: bool = True,
        parquet_flush_threshold: int = 100
    ):
        """
        Logger 초기화
        
        Args:
            name: 로거 이름
            level: 로깅 레벨
            log_file: 로그 파일 경로 (없으면 파일 로깅 비활성화)
            console_output: 콘솔 출력 여부
            format_string: 사용자 정의 로그 포맷
            detailed_format_string: 심각한 로그 레벨용 상세 포맷
            parquet_logging: 파케이 로그 저장 여부
            env: 환경 이름 ('development', 'test', 'production')
            colored_console: 콘솔 출력에 색상 적용 여부
            async_logging: 비동기 로깅 사용 여부 (True 권장)
            parquet_flush_threshold: 파케이 로그 버퍼 플러시 임계값
        """
        self.name = name
        self.async_logging = async_logging
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False

        self.project_name = project_name if project_name else Path.cwd().name

        
        # 기존 핸들러 제거
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 모든 리스너 등록 취소 (리로드 시)
        if name in Logger._listeners:
            listener = Logger._listeners.pop(name)
            if hasattr(listener, 'stop') and listener.is_alive():
                listener.stop()
        
        # 기본 포맷
        if format_string is None:
            format_string = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            
        # 상세 포맷 (심각한 로그 레벨용)
        if detailed_format_string is None:
            detailed_format_string = "%(asctime)s [%(levelname)s] %(name)s (%(pathname)s:%(lineno)d - %(funcName)s): %(message)s"
        
        # 실제 로그 핸들러 생성 (큐 리스너에 전달될)
        handlers = []
        
        # 콘솔 출력 핸들러
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            
            # 색상 적용 여부에 따라 포맷터 선택
            if colored_console:
                console_formatter = ColoredDetailedFormatter(format_string, detailed_fmt=detailed_format_string)
            else:
                console_formatter = DetailedFormatter(format_string, detailed_fmt=detailed_format_string)
                
            console_handler.setFormatter(console_formatter)
            handlers.append(console_handler)
        
        # 일반 포맷터 (파일 및 파케이용)
        file_formatter = DetailedFormatter(format_string, detailed_fmt=detailed_format_string)
        
        # 파일 출력 핸들러
        if log_file:
            # 로그 디렉토리 생성
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(file_formatter)
            handlers.append(file_handler)
        
        # 파케이 로그 핸들러
        if parquet_logging:
            parquet_handler = ParquetLogHandler(
                base_path="~/.ineeji/logs", 
                project_name=self.project_name,
                env=env,
                flush_threshold=parquet_flush_threshold
            )
            parquet_handler.setFormatter(file_formatter)
            handlers.append(parquet_handler)
        
        if async_logging and handlers:
            # 비동기 로깅 설정
            self._setup_async_logging(handlers)
        else:
            # 동기식 로깅 (직접 핸들러 추가)
            for handler in handlers:
                self.logger.addHandler(handler)
    
    def _setup_async_logging(self, handlers):
        """비동기 로깅 설정"""
        # 로그 메시지를 담을 큐 생성
        log_queue = queue.Queue(-1)  # 무제한 큐 크기
        
        # 큐 핸들러 생성 및 로거에 연결
        queue_handler = QueueHandler(log_queue)
        self.logger.addHandler(queue_handler)
        
        # 큐 리스너 생성 및 시작
        listener = QueueListener(log_queue, *handlers, respect_handler_level=True)
        listener.start()
        
        # 나중에 종료를 위해 리스너 저장
        Logger._listeners[self.name] = listener
        
        # 프로그램 종료 시 리스너 정리
        if len(Logger._listeners) == 1:
            atexit.register(Logger._stop_all_listeners)
    
    @classmethod
    def _stop_all_listeners(cls):
        """모든 큐 리스너 정지"""
        for name, listener in cls._listeners.items():
            try:
                if hasattr(listener, 'stop') and listener.is_alive():
                    listener.stop()
            except:
                pass
        cls._listeners.clear()
    
    def debug(self, message: Any, *args, **kwargs):
        """디버그 레벨 로그 메시지"""
        self.logger.debug(message, *args, stacklevel=2, **kwargs)
    
    def info(self, message: Any, *args, **kwargs):
        """정보 레벨 로그 메시지"""
        self.logger.info(message, *args, stacklevel=2, **kwargs)
    
    def warning(self, message: Any, *args, **kwargs):
        """경고 레벨 로그 메시지"""
        self.logger.warning(message, *args, stacklevel=2, **kwargs)
    
    def error(self, message: Any, *args, **kwargs):
        """에러 레벨 로그 메시지"""
        self.logger.error(message, *args, stacklevel=2, **kwargs)
    
    def critical(self, message: Any, *args, **kwargs):
        """치명적 레벨 로그 메시지"""
        self.logger.critical(message, *args, stacklevel=2, **kwargs)
    
    def exception(self, message: Any, *args, exc_info=True, **kwargs):
        """예외 정보를 포함한 에러 로그"""
        self.logger.exception(message, *args, exc_info=exc_info, stacklevel=2, **kwargs)
    
    def set_level(self, level: int):
        """로그 레벨 변경"""
        self.logger.setLevel(level)
    
    @staticmethod
    def get_default_config(env: str = "development") -> Dict[str, Any]:
        """
        환경별 기본 로거 설정 반환
        
        Args:
            env: 환경 이름 ('development', 'test', 'production')
            
        Returns:
            로거 설정 딕셔너리
        """
        # 기본 포맷 
        basic_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        
        # 심각한 로그 레벨(WARNING, ERROR, CRITICAL)을 위한 상세 포맷
        # 파일 위치, 라인 번호, 함수명 포함
        detailed_format = "%(asctime)s [%(levelname)s] %(name)s (%(pathname)s:%(lineno)d - %(funcName)s): %(message)s"
        
        configs = {
            "development": {
                "level": logging.DEBUG,
                "console_output": True,
                "log_file": f"logs/development/{datetime.now().strftime('%Y-%m-%d')}/app.log",
                "format_string": basic_format,
                "detailed_format_string": detailed_format,  # 심각한 레벨용 상세 포맷 추가
                "parquet_logging": True,
                "env": "development",
                "colored_console": True,
                "async_logging": True,
                "parquet_flush_threshold": 20
            },
            "test": {
                "level": logging.INFO,
                "console_output": True,
                "log_file": f"logs/test/{datetime.now().strftime('%Y-%m-%d')}/app.log",
                "format_string": basic_format,
                "detailed_format_string": detailed_format,  # 심각한 레벨용 상세 포맷 추가
                "parquet_logging": True,
                "env": "test", 
                "colored_console": True,
                "async_logging": True,
                "parquet_flush_threshold": 10
            },
            "production": {
                "level": logging.WARNING,
                "console_output": False,
                "log_file": f"logs/production/{datetime.now().strftime('%Y-%m-%d')}/app.log",
                "format_string": basic_format,
                "detailed_format_string": detailed_format,  # 심각한 레벨용 상세 포맷 추가
                "parquet_logging": True,
                "env": "production",
                "colored_console": False,
                "async_logging": True,
                "parquet_flush_threshold": 30  # 프로덕션 환경에서는 더 큰 버퍼
            }
        }
        
        return configs.get(env, configs["development"]) 
    
logger = Logger("ineeji_log", **Logger.get_default_config("development"))