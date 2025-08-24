#!/bin/bash

# Hugging Face 배포 준비 스크립트
# 최소한의 수정으로 배포하기

echo "🚀 Hugging Face Spaces 배포 준비 중..."

# 1. 배포용 디렉토리 생성
DEPLOY_DIR="../hf_deploy"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

# 2. 필요한 파일만 복사 (PHP 파일 제외)
cp app.py $DEPLOY_DIR/
cp requirements.txt $DEPLOY_DIR/
cp -r data $DEPLOY_DIR/ 2>/dev/null || true

# Python 모듈 파일들 복사
cp annotations_api.py $DEPLOY_DIR/
cp auth.py $DEPLOY_DIR/
cp database.py $DEPLOY_DIR/
cp database_api.py $DEPLOY_DIR/
cp models.db $DEPLOY_DIR/ 2>/dev/null || true
cp mtl_generator.py $DEPLOY_DIR/
cp optimize_texture.py $DEPLOY_DIR/
cp texture_optimizer.py $DEPLOY_DIR/
cp viewer.py $DEPLOY_DIR/
cp viewer_utils.py $DEPLOY_DIR/
cp web_db_sync.py $DEPLOY_DIR/
cp web_storage.py $DEPLOY_DIR/

# 3. README 생성
cat > $DEPLOY_DIR/README.md << 'EOF'
---
title: Streamlit 3D Viewer
emoji: 🎮
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
---

# 3D Model Viewer

3D 모델 관리 및 공유 시스템
EOF

echo "✅ 파일 복사 완료!"
echo "📁 배포 디렉토리: $DEPLOY_DIR"
echo ""
echo "다음 단계:"
echo "1. cd $DEPLOY_DIR"
echo "2. git init"
echo "3. git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/streamlit-3dviewer"
echo "4. git add ."
echo "5. git commit -m 'Initial deployment'"
echo "6. git push -u origin main"
