"""
일별 로그 파일 생성 예제
"""

import os
from datetime import datetime

# 패키지가 설치된 경우, 아래 임포트를 사용하세요
from ineeji_logging import Logger

# 패키지를 설치하지 않은 경우, 아래 경로 설정 코드를 주석 해제하고 사용하세요
# import sys
# # 라이브러리 임포트를 위한 경로 설정
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from src import Logger

def get_daily_log_path():
    """오늘 날짜의 로그 파일 경로 반환"""
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    today = datetime.now().strftime('%Y%m%d')
    return os.path.join(logs_dir, f"app_{today}.log")

def main():
    # 일별 로그 파일 경로 생성
    log_file = get_daily_log_path()
    
    # 로거 생성 (콘솔 + 파일)
    logger = Logger(
        "my_app", 
        log_file=log_file,
        level=Logger.DEBUG,
        console_output=True
    )
    
    # 간단한 로그 메시지 기록
    logger.info(f"애플리케이션 시작 - 로그 파일: {log_file}")
    logger.debug("디버그 메시지")
    logger.warning("경고 메시지")
    logger.error("에러 메시지")
    
    print(f"\n로그가 {log_file}에 저장되었습니다.")
    
    # 프로덕션 설정 사용 (자동으로 일별 로그 파일 사용)
    prod_config = Logger.get_default_config("production")
    prod_logger = Logger("prod_app", **prod_config)
    
    # 경고 레벨 이상만 기록 (프로덕션 설정)
    prod_logger.info("이 INFO 메시지는 프로덕션 로그에 기록되지 않습니다.")
    prod_logger.warning("이 WARNING 메시지는 프로덕션 로그에 기록됩니다.")
    
    print(f"\n프로덕션 로그가 {prod_config['log_file']}에 저장되었습니다.")

if __name__ == "__main__":
    main() 