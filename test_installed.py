"""
설치된 ineeji_logging 패키지 테스트 및 비동기 로깅 성능 테스트
"""
import time
import logging
from ineeji_logging import Logger, logger

def test_basic_logging():
    """기본 로깅 테스트"""
    print("===== 기본 로깅 테스트 =====")
    
    # 개발 환경 설정으로 로거 생성 (비동기 로깅 활성화)
    dev_config = Logger.get_default_config("development")
    dev_config["console_output"] = True  # 콘솔 출력 활성화
    custom_logger = Logger("test_app", **dev_config)

    custom_logger.info("기본 로깅 테스트")
    custom_logger.debug("디버그 로그")
    custom_logger.warning("경고 로그")
    custom_logger.error("예외 발생")
    custom_logger.critical("치명적 로그")
    custom_logger.exception("예외 정보 로그")
    
    time.sleep(1)
    print(f"로그가 {dev_config['log_file']}에 저장되었습니다.")
    print("비동기 로깅이 활성화되어 있어 실제 파일 쓰기는 백그라운드에서 발생할 수 있습니다.")

def main():
    """메인 테스트 함수"""
    # 기본 로깅 테스트
    test_basic_logging()
    
    print("\n모든 테스트가 완료되었습니다.")

if __name__ == "__main__":
    main() 
    # logging.shutdown() # 프로그램 종료 전 로깅 시스템 종료