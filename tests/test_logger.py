"""
Logger 클래스에 대한 단위 테스트
"""

import sys
import os
import unittest
import tempfile
import logging
import shutil
import pandas as pd
from io import StringIO
from pathlib import Path
from datetime import datetime

# 라이브러리 임포트를 위한 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from src import Logger
from ineeji_logging import Logger
from ineeji_logging.logger import ParquetLogHandler

class TestParquetLogHandler(unittest.TestCase):
    """ParquetLogHandler 테스트"""
    
    def setUp(self):
        """테스트 셋업"""
        # 테스트용 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()
        self.test_log_dir = os.path.join(self.temp_dir, "logs")
        
    def tearDown(self):
        """테스트 정리"""
        # 임시 디렉토리 삭제
        shutil.rmtree(self.temp_dir)
    
    def test_parquet_handler_initialization(self):
        """파케이 핸들러 초기화 테스트"""
        handler = ParquetLogHandler(self.test_log_dir, "test")
        self.assertEqual(handler.base_path, self.test_log_dir)
        self.assertEqual(handler.env, "test")
        self.assertEqual(handler.flush_threshold, 1)
    
    def test_log_entry_format(self):
        """로그 항목 형식 테스트"""
        # 로거 설정
        logger_name = "parquet_test"
        handler = ParquetLogHandler(self.test_log_dir, "test")
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        
        # 테스트 메시지 로깅
        test_message = "테스트 메시지"
        logger.info(test_message)
        
        # 현재 날짜로 파케이 파일 경로 생성
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = Path(self.test_log_dir) / "test" / today / "log.parquet"
        
        # 파일 존재 확인
        self.assertTrue(log_file.exists(), f"파케이 로그 파일이 생성되지 않았습니다: {log_file}")
        
        # 로그 내용 확인
        df = pd.read_parquet(log_file)
        self.assertEqual(len(df), 1)
        
        # 컬럼 확인
        expected_columns = ['datetime', 'levelname', 'name', 'message', 
                           'raw_message', 'pathname', 'lineno', 'funcName']
        for col in expected_columns:
            self.assertIn(col, df.columns)
        
        # 값 확인
        self.assertEqual(df.iloc[0]['levelname'], 'INFO')
        self.assertEqual(df.iloc[0]['name'], logger_name)
        self.assertEqual(df.iloc[0]['raw_message'], test_message)
    
    def test_multiple_log_entries(self):
        """여러 로그 항목 저장 테스트"""
        # 로거 설정
        handler = ParquetLogHandler(self.test_log_dir, "test")
        logger = logging.getLogger("multiple_logs")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        
        # 여러 레벨의 로그 메시지 생성
        logger.debug("디버그 메시지")
        logger.info("정보 메시지")
        logger.warning("경고 메시지")
        logger.error("에러 메시지")
        
        # 현재 날짜로 파케이 파일 경로 생성
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = Path(self.test_log_dir) / "test" / today / "log.parquet"
        
        # 로그 내용 확인
        df = pd.read_parquet(log_file)
        self.assertEqual(len(df), 4)
        
        # 레벨별 로그 개수 확인
        level_counts = df['levelname'].value_counts()
        self.assertEqual(level_counts['DEBUG'], 1)
        self.assertEqual(level_counts['INFO'], 1)
        self.assertEqual(level_counts['WARNING'], 1)
        self.assertEqual(level_counts['ERROR'], 1)

class TestLogger(unittest.TestCase):
    """Logger 클래스 테스트"""
    
    def setUp(self):
        """테스트 셋업"""
        # 테스트 로그 캡처를 위한 StringIO 설정
        self.log_capture = StringIO()
        # 임시 로그 파일 생성
        self.temp_log_file = tempfile.NamedTemporaryFile(delete=False).name
        # 테스트용 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """테스트 정리"""
        # 임시 로그 파일 제거
        if os.path.exists(self.temp_log_file):
            os.unlink(self.temp_log_file)
        # 임시 디렉토리 삭제
        shutil.rmtree(self.temp_dir)
    
    def test_logger_initialization(self):
        """로거 초기화 테스트"""
        logger = Logger("test_logger")
        self.assertEqual(logger.logger.level, logging.INFO)
        self.assertEqual(logger.logger.name, "test_logger")
        self.assertFalse(logger.logger.propagate)

    def test_log_levels(self):
        """로그 레벨 테스트"""
        logger = Logger("test_levels", level=Logger.DEBUG)
        self.assertEqual(logger.logger.level, logging.DEBUG)
        
        logger.set_level(Logger.WARNING)
        self.assertEqual(logger.logger.level, logging.WARNING)
    
    def test_file_logging(self):
        """파일 로깅 테스트"""
        test_message = "파일 로깅 테스트 메시지"
        logger = Logger("file_test", log_file=self.temp_log_file)
        logger.info(test_message)
        
        # 파일에서 로그 내용 읽기
        with open(self.temp_log_file, 'r') as f:
            log_content = f.read()
        
        self.assertIn(test_message, log_content)
        self.assertIn("[INFO]", log_content)
        self.assertIn("file_test", log_content)
    
    def test_default_configs(self):
        """기본 설정 테스트"""
        dev_config = Logger.get_default_config("development")
        test_config = Logger.get_default_config("test")
        prod_config = Logger.get_default_config("production")
        
        # 개발 환경 설정 검증
        self.assertEqual(dev_config["level"], logging.DEBUG)
        self.assertTrue(dev_config["console_output"])
        self.assertTrue(dev_config["parquet_logging"])
        self.assertEqual(dev_config["env"], "development")
        
        # 테스트 환경 설정 검증
        self.assertEqual(test_config["level"], logging.INFO)
        self.assertTrue(test_config["console_output"])
        self.assertTrue(test_config["parquet_logging"])
        self.assertEqual(test_config["env"], "test")
        
        # 프로덕션 환경 설정 검증
        self.assertEqual(prod_config["level"], logging.WARNING)
        self.assertFalse(prod_config["console_output"])
        self.assertIsNotNone(prod_config["log_file"])
        self.assertTrue(prod_config["parquet_logging"])
        self.assertEqual(prod_config["env"], "production")
    
    def test_invalid_environment(self):
        """잘못된 환경 이름 테스트"""
        # 존재하지 않는 환경 이름으로 설정 요청 시 개발 환경 설정 반환
        invalid_config = Logger.get_default_config("invalid_env")
        dev_config = Logger.get_default_config("development")
        
        self.assertEqual(invalid_config, dev_config)
    
    def test_parquet_logging(self):
        """파케이 로깅 테스트"""
        # 환경변수 설정으로 홈 디렉토리 변경
        original_home = os.environ.get('HOME')
        try:
            os.environ['HOME'] = self.temp_dir
            
            # 로거 생성
            logger = Logger("parquet_test", parquet_logging=True, env="test")
            
            # 테스트 메시지 로깅
            logger.info("정보 메시지")
            logger.error("에러 메시지")
            
            # 현재 날짜로 파케이 파일 경로 생성
            today = datetime.now().strftime('%Y-%m-%d')
            log_file = Path(self.temp_dir) / ".ineeji/logs/test" / today / "log.parquet"
            
            # 파일 존재 확인
            self.assertTrue(os.path.exists(log_file.parent), f"로그 디렉토리가 생성되지 않았습니다: {log_file.parent}")
            self.assertTrue(os.path.exists(log_file), f"파케이 로그 파일이 생성되지 않았습니다: {log_file}")
            
            # 로그 내용 확인
            df = pd.read_parquet(log_file)
            self.assertEqual(len(df), 2)
            
            # 레벨별 로그 개수 확인
            level_counts = df['levelname'].value_counts()
            self.assertEqual(level_counts.get('INFO', 0), 1)
            self.assertEqual(level_counts.get('ERROR', 0), 1)
        finally:
            # 환경변수 복원
            if original_home:
                os.environ['HOME'] = original_home
    
    def test_format_string_args(self):
        """포맷 문자열과 인자 테스트"""
        # 로거 설정
        logger = Logger("format_test", parquet_logging=True, env="test")
        
        # 파케이 로그 핸들러의 base_path 재설정
        for handler in logger.logger.handlers:
            if isinstance(handler, ParquetLogHandler):
                handler.base_path = self.temp_dir
        
        # 포맷 문자열과 인자 사용
        name = "테스트"
        code = 123
        logger.info("%s에서 코드 %d 발생", name, code)
        
        # 현재 날짜로 파케이 파일 경로 생성
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = Path(self.temp_dir) / "test" / today / "log.parquet"
        
        # 로그 내용 확인
        df = pd.read_parquet(log_file)
        log_entry = df.iloc[0]
        
        # 포맷된 메시지 확인
        expected_text = "테스트에서 코드 123 발생"
        self.assertEqual(log_entry['raw_message'], expected_text)
        self.assertIn(expected_text, log_entry['message'])


if __name__ == "__main__":
    unittest.main() 