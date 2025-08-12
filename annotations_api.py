"""
Annotations API endpoints for 3D viewer
"""
import streamlit as st
from database import ModelDatabase
import json

# API 엔드포인트 페이지
def annotation_api_page():
    """Handle annotation API requests"""
    
    # CORS 헤더 설정
    st.set_page_config(page_title="Annotation API", layout="wide")
    
    # URL 파라미터 처리
    query_params = st.query_params
    action = query_params.get("action", [""])[0]
    
    db = ModelDatabase()
    response = {"success": False}
    
    try:
        if action == "add":
            # 새 annotation 추가
            model_token = query_params.get("model_token", [""])[0]
            x = float(query_params.get("x", ["0"])[0])
            y = float(query_params.get("y", ["0"])[0])
            z = float(query_params.get("z", ["0"])[0])
            text = query_params.get("text", [""])[0]
            
            if model_token and text:
                annotation_id = db.add_annotation(
                    model_token, 
                    {"x": x, "y": y, "z": z}, 
                    text
                )
                response = {"success": True, "id": annotation_id}
        
        elif action == "update":
            # annotation 상태 업데이트
            annotation_id = int(query_params.get("id", ["0"])[0])
            completed = query_params.get("completed", ["false"])[0] == "true"
            
            if annotation_id:
                db.update_annotation_status(annotation_id, completed)
                response = {"success": True}
        
        elif action == "delete":
            # annotation 삭제
            annotation_id = int(query_params.get("id", ["0"])[0])
            
            if annotation_id:
                db.delete_annotation(annotation_id)
                response = {"success": True}
        
        elif action == "list":
            # 모델의 모든 annotations 가져오기
            model_token = query_params.get("model_token", [""])[0]
            
            if model_token:
                annotations = db.get_annotations(model_token)
                response = {"success": True, "annotations": annotations}
    
    except Exception as e:
        response = {"success": False, "error": str(e)}
    
    # JSON 응답 반환
    st.json(response)

# URL 경로가 /api/annotations인 경우 API 처리
if __name__ == "__main__":
    annotation_api_page()
