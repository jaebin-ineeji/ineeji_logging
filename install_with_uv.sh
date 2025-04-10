#!/bin/bash
# ineeji_logging 패키지를 uv 또는 pip를 사용하여 설치하는 스크립트

# 스크립트가 있는 디렉터리로 이동
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 설치 도구 선택
echo "설치 도구를 선택하세요:"
echo "1) uv (고속 Python 패키지 관리자)"
echo "2) pip (기본 Python 패키지 관리자)"
read -p "선택 (기본값: 1): " install_tool

# 기본값 설정
if [ -z "$install_tool" ]; then
    install_tool="1"
fi

# uv 설치 확인 (uv를 선택한 경우)
if [ "$install_tool" = "1" ]; then
    if ! command -v uv &> /dev/null; then
        echo "uv가 설치되어 있지 않습니다. 먼저 uv를 설치해 주세요."
        echo "설치 방법: https://github.com/astral-sh/uv"
        exit 1
    fi
    INSTALL_CMD="uv pip"
else
    INSTALL_CMD="pip"
fi

# 설치 소스 선택
echo -e "\n설치 소스를 선택하세요:"
echo "1) 로컬 소스 (현재 디렉터리)"
echo "2) GitHub 저장소 (jaebin-ineeji/ineeji_logging)"
read -p "선택 (기본값: 1): " install_source

# 기본값 설정
if [ -z "$install_source" ]; then
    install_source="1"
fi

# 설치 모드 선택 (일반 또는 개발 모드)
echo -e "\n설치 모드를 선택하세요:"
echo "1) 일반 설치"
echo "2) 개발 모드 설치 (-e 옵션)"
read -p "선택 (기본값: 2): " install_mode

# 기본값 설정
if [ -z "$install_mode" ]; then
    install_mode="2"
fi

# GitHub 저장소에서 설치하는 경우
if [ "$install_source" = "2" ]; then
    echo -e "\nGitHub 저장소에서 설치합니다."
    
    # 브랜치/태그 입력 받기
    read -p "브랜치 또는 태그 (기본값: main): " branch
    if [ -z "$branch" ]; then
        branch="main"
    fi
    
    if [ "$install_mode" = "1" ]; then
        echo "일반 모드로 GitHub 저장소에서 설치합니다... ($INSTALL_CMD 사용)"
        $INSTALL_CMD install git+https://github.com/jaebin-ineeji/ineeji_logging.git@$branch
    else
        echo "개발 모드로 GitHub 저장소에서 설치합니다... ($INSTALL_CMD 사용)"
        $INSTALL_CMD install -e git+https://github.com/jaebin-ineeji/ineeji_logging.git@$branch#egg=ineeji_logging
    fi
else
    # 로컬 소스에서 설치
    if [ "$install_mode" = "1" ]; then
        echo "일반 모드로 로컬 소스에서 설치합니다... ($INSTALL_CMD 사용)"
        $INSTALL_CMD install .
    else
        echo "개발 모드로 로컬 소스에서 설치합니다... ($INSTALL_CMD 사용)"
        $INSTALL_CMD install -e .
    fi
fi

# 설치 확인
echo -e "\n설치 확인 중..."
python -c "from ineeji_logging import Logger; print('성공적으로 설치되었습니다! 모듈 경로:', Logger.__module__)" || echo "설치 중 문제가 발생했습니다." 