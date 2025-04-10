"""
ineeji_logging 기본 사용법 예제
"""

# 패키지가 설치된 경우, 아래 임포트를 사용하세요
from ineeji_logging import Logger

# 패키지를 설치하지 않은 경우, 아래 경로 설정 코드를 주석 해제하고 사용하세요
# import sys
# import os
# # 라이브러리 임포트를 위한 경로 설정
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from src import Logger

def main():
    # 기본 로거 생성
    logger = Logger("example_app")
    
    # 다양한 레벨의 로그 메시지 출력
    logger.debug("이것은 디버그 메시지입니다.")
    logger.info("이것은 정보 메시지입니다.")
    logger.warning("이것은 경고 메시지입니다.")
    logger.error("이것은 에러 메시지입니다.")
    
    # 로그 레벨 변경
    logger.set_level(Logger.DEBUG)
    logger.debug("이제 디버그 메시지가 보입니다.")
    
    # 예외 로깅 예제
    try:
        result = 10 / 0
    except Exception as e:
        logger.exception(f"예외가 발생했습니다: {e}")
    
    # 파일 로깅 예제
    file_logger = Logger(
        "file_example", 
        log_file="logs/example.log", 
        level=Logger.DEBUG
    )
    file_logger.info("이 메시지는 파일에 기록됩니다.")
    
    # 환경별 설정 사용
    dev_config = Logger.get_default_config("development")
    prod_config = Logger.get_default_config("production")
    
    print("\n개발 환경 설정:", dev_config)
    print("\n프로덕션 환경 설정:", prod_config)
    
    # 프로덕션 설정으로 로거 생성
    prod_logger = Logger("production_app", **prod_config)
    prod_logger.info("이 INFO 메시지는 프로덕션 환경에서는 표시되지 않습니다.")
    prod_logger.warning("이 WARNING 메시지는 프로덕션 환경에서 표시됩니다.")

if __name__ == "__main__":
    main() 