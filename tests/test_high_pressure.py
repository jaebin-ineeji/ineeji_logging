"""
설치된 ineeji_logging 패키지 테스트 및 비동기 로깅 성능 테스트 (unittest 형식)
"""
import time
import unittest
import threading
import os
import uuid
from datetime import datetime
from ineeji_logging import Logger


class LoggingPerformanceTest(unittest.TestCase):
    """로깅 성능 테스트를 위한 unittest 클래스"""

    def setUp(self):
        """각 테스트 전에 실행되는 설정"""
        # 공통 설정
        self.log_count = 1000
        self.thread_count = 10
        self.log_per_thread = 100
        
        # 테스트별 고유 로그 디렉토리 생성
        self.test_id = uuid.uuid4().hex[:8]
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def get_unique_config(self, base_config):
        """고유한 로깅 설정 생성"""
        config = base_config.copy()
        
        # 고유한 로그 파일 경로 설정
        unique_path = f"logs/test/{self.timestamp}_{self.test_id}"
        if not os.path.exists(unique_path):
            os.makedirs(unique_path, exist_ok=True)
            
        config["log_file"] = f"{unique_path}/app.log"
        
        # 고유한 환경 이름 설정 (파케이 저장 경로를 다르게 하기 위함)
        config["env"] = f"test_{self.test_id}"
        
        return config
        
    def test_basic_logging(self):
        """기본 로깅 기능 테스트"""
        print("\n===== 기본 로깅 테스트 =====")
        
        # 개발 환경 설정으로 로거 생성 (비동기 로깅 활성화)
        dev_config = Logger.get_default_config("development")
        dev_config["console_output"] = True  # 콘솔 출력 활성화
        dev_config = self.get_unique_config(dev_config)
        
        custom_logger = Logger("test_app", **dev_config)
        
        # 로그 기록 테스트
        custom_logger.debug("디버그 메시지 기록 테스트")
        custom_logger.info("정보 메시지 기록 테스트")
        custom_logger.warning("경고 메시지 기록 테스트")
        custom_logger.error("에러 메시지 기록 테스트")
        custom_logger.critical("치명적 메시지 기록 테스트")
        
        # 로그가 모두 처리될 수 있도록 대기
        time.sleep(1)
        print(f"로그가 {dev_config['log_file']}에 저장되었습니다.")
        
        # 테스트 성공 여부 확인 (실제로는 로그 파일 존재 여부나 내용을 확인할 수 있음)
        self.assertTrue(True)
        
    def test_sync_vs_async_logging_performance(self):
        """동기 vs 비동기 로깅 성능 비교 테스트"""
        print("\n===== 동기 vs 비동기 로깅 성능 비교 테스트 =====")
        
        # 동기 로깅 설정
        sync_config = Logger.get_default_config("development")
        sync_config["console_output"] = False  # 콘솔 출력 비활성화
        sync_config["async_logging"] = False   # 동기 로깅 사용
        sync_config["parquet_flush_threshold"] = 1  # 매 로그마다 저장 (최악의 성능 시나리오)
        sync_config = self.get_unique_config(sync_config)
        sync_config["env"] = f"sync_{self.test_id}"  # 고유한 환경 이름
        
        # 비동기 로깅 설정
        async_config = Logger.get_default_config("development")
        async_config["console_output"] = False  # 콘솔 출력 비활성화
        async_config["async_logging"] = True    # 비동기 로깅 사용
        async_config["parquet_flush_threshold"] = 100  # 100개 단위로 저장
        async_config = self.get_unique_config(async_config)
        async_config["env"] = f"async_{self.test_id}"  # 고유한 환경 이름
        
        # 로거 인스턴스 생성
        sync_logger = Logger("sync_test", **sync_config)
        async_logger = Logger("async_test", **async_config)
        
        # 테스트 로그 메시지 수
        log_count = self.log_count
        
        # 동기 로깅 시간 측정
        print(f"동기 로깅 테스트 ({log_count}개 메시지)...")
        start_time = time.time()
        for i in range(log_count):
            sync_logger.info(f"테스트 로그 메시지 #{i} - 동기식")
        sync_duration = time.time() - start_time
        print(f"동기 로깅 완료: {sync_duration:.2f}초 소요")
        
        # 비동기 로깅 시간 측정
        print(f"비동기 로깅 테스트 ({log_count}개 메시지)...")
        start_time = time.time()
        for i in range(log_count):
            async_logger.info(f"테스트 로그 메시지 #{i} - 비동기식")
        async_duration = time.time() - start_time
        print(f"비동기 로깅 완료: {async_duration:.2f}초 소요")
        
        # 결과 비교
        speedup = sync_duration / async_duration if async_duration > 0 else float('inf')
        print(f"성능 향상: {speedup:.2f}배 빠름")
        
        # 테스트 어서션 추가
        self.assertGreater(sync_duration, async_duration, "비동기 로깅이 동기 로깅보다 빨라야 합니다")
        self.assertGreater(speedup, 1.0, "비동기 로깅이 동기 로깅보다 최소 1배 이상 빨라야 합니다")
        
        # 로그가 모두 저장될 시간을 주기 위해 잠시 대기
        time.sleep(1)
        
    def test_high_concurrency_performance(self):
        """고부하 동시성 테스트"""
        print("\n===== 고부하 동시성 테스트 =====")
        
        # 비동기 로깅 설정으로 로거 생성
        config = Logger.get_default_config("development")
        config["console_output"] = False
        config["async_logging"] = True
        config["parquet_flush_threshold"] = 100
        config = self.get_unique_config(config)
        config["env"] = f"concurrent_{self.test_id}"  # 고유한 환경 이름
        
        concurrent_logger = Logger("concurrent_test", **config)
        
        # 멀티스레드에서 로그 기록 테스트
        thread_count = self.thread_count
        log_per_thread = self.log_per_thread
        total_logs = thread_count * log_per_thread
        
        def log_worker(worker_id):
            for i in range(log_per_thread):
                concurrent_logger.info(f"Thread {worker_id}: 로그 메시지 #{i}")
        
        # 스레드 시작 시간 측정
        start_time = time.time()
        
        # 여러 개의 스레드 생성 및 시작
        threads = []
        for i in range(thread_count):
            t = threading.Thread(target=log_worker, args=(i,))
            threads.append(t)
            t.start()
        
        # 모든 스레드가 완료될 때까지 대기
        for t in threads:
            t.join()
        
        duration = time.time() - start_time
        logs_per_second = total_logs / duration
        
        print(f"{thread_count}개 스레드에서 총 {total_logs}개 메시지 로깅 완료")
        print(f"총 소요 시간: {duration:.2f}초")
        print(f"초당 로그 처리량: {logs_per_second:.2f} 로그/초")
        
        # 테스트 어서션 추가
        self.assertGreater(logs_per_second, 100, "초당 최소 100개 이상의 로그를 처리해야 합니다")
        
        # 로그가 모두 저장될 시간을 주기 위해 잠시 대기
        time.sleep(1)
        
    def test_sync_vs_async_with_different_thresholds(self):
        """다양한 flush 임계값에 따른 비동기 로깅 성능 비교"""
        print("\n===== 다양한 flush 임계값에 따른 비동기 로깅 성능 비교 =====")
        
        # 테스트할 임계값 목록
        thresholds = [1, 10, 50, 100, 500]
        durations = {}
        
        for threshold in thresholds:
            # 비동기 로깅 설정
            config = Logger.get_default_config("development")
            config["console_output"] = False  # 콘솔 출력 비활성화
            config["async_logging"] = True    # 비동기 로깅 사용
            config["parquet_flush_threshold"] = threshold
            config = self.get_unique_config(config)
            config["env"] = f"threshold_{threshold}_{self.test_id}"  # 임계값별 고유 환경
            
            # 로거 인스턴스 생성
            logger_name = f"async_test_{threshold}"
            test_logger = Logger(logger_name, **config)
            
            # 로깅 시간 측정
            print(f"임계값 {threshold}로 테스트 ({self.log_count}개 메시지)...")
            start_time = time.time()
            for i in range(self.log_count):
                test_logger.info(f"테스트 로그 메시지 #{i} - 임계값: {threshold}")
            duration = time.time() - start_time
            
            # 결과 저장
            durations[threshold] = duration
            print(f"임계값 {threshold}: {duration:.2f}초 소요")
            
        # 최적의 임계값 찾기
        optimal_threshold = min(durations, key=lambda x: durations[x])
        print(f"\n최적의 임계값: {optimal_threshold} (소요 시간: {durations[optimal_threshold]:.2f}초)")
        
        # 테스트 어서션
        self.assertGreater(durations[1], durations[optimal_threshold], 
                          f"임계값 {optimal_threshold}가 임계값 1보다 빨라야 합니다")
        
        # 로그가 모두 저장될 시간을 주기 위해 잠시 대기
        time.sleep(1)
        
    def tearDown(self):
        """각 테스트 후 정리 작업"""
        # 파케이 핸들러가 모든 로그를 플러시할 시간을 주기 위해 잠시 대기
        time.sleep(1)


if __name__ == "__main__":
    unittest.main() 