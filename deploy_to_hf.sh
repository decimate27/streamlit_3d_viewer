#!/bin/bash

# 🚀 Hugging Face 완전 자동 배포 (코드 수정 없음)

echo "================================"
echo "Hugging Face Spaces 자동 배포"
echo "코드 수정 없이 그대로 배포!"
echo "================================"

# 설정
HF_USERNAME="YOUR_HF_USERNAME"  # 여기에 HF 사용자명 입력
SPACE_NAME="streamlit-3dviewer"
DEPLOY_DIR="../hf_deploy_auto"

echo ""
echo "1️⃣ 배포 디렉토리 준비 중..."
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

echo "2️⃣ 전체 프로젝트 복사 중..."
# .git, .venv, __pycache__ 제외하고 모두 복사
rsync -av --exclude='.git' \
          --exclude='.venv' \
          --exclude='__pycache__' \
          --exclude='.DS_Store' \
          --exclude='*.php' \
          --exclude='.yoyo' \
          --exclude='backup' \
          --exclude='php' \
          ./ $DEPLOY_DIR/

echo "3️⃣ HF용 README 생성..."
cat > $DEPLOY_DIR/README.md << 'EOF'
---
title: 3D Model Viewer
emoji: 🎮
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
---

# 3D Model Viewer & Manager

Features:
- Upload and manage 3D models (OBJ format)
- Multi-texture support
- Share models with public links
- Real-time 3D preview
- Automatic texture optimization
EOF

echo "4️⃣ Git 초기화..."
cd $DEPLOY_DIR
git init

echo "5️⃣ HF 리모트 추가..."
git remote add origin https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME

echo "6️⃣ 커밋 준비..."
git add .
git commit -m "Deploy 3D viewer without code changes"

echo ""
echo "✅ 준비 완료!"
echo ""
echo "🔑 다음 명령어를 실행하세요:"
echo ""
echo "cd $DEPLOY_DIR"
echo "git push -u origin main"
echo ""
echo "💡 팁:"
echo "- HF 로그인이 필요할 수 있습니다"
echo "- huggingface-cli login 명령어 사용"
echo ""
echo "🌐 배포 후 접속 주소:"
echo "https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"
