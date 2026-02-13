from ragflow_sdk import RAGFlow
import requests
import json
import re
import uuid
import os
from pathlib import Path
import time
import asyncio
import aiohttp
from typing import List, Dict

# RAGFlow HTTP API 설정
api_key = "ragflow-U5ZGEyNTdlNjkyODExZjBiODE2MDI0Mm"
base_url = "http://10.50.7.154:8080"
plus_base_url = "http://10.50.7.154:5000"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 파싱 타임아웃 설정 (초)
PARSING_TIMEOUT = 1800  # 30분 (필요에 따라 조정 가능)

async def parse_document_async(session: aiohttp.ClientSession, doc_id: str, doc_name: str = None, 
                               timeout: int = PARSING_TIMEOUT) -> Dict:
    """
    비동기로 단일 문서 파싱 요청 및 완료 대기
    
    Args:
        session: aiohttp 세션
        doc_id: 문서 ID
        doc_name: 문서 이름 (로깅용)
        timeout: 파싱 타임아웃 (초, 기본값: 1800초 = 30분)
        
    Returns:
        dict: 파싱 결과
    """
    url = f"{plus_base_url}/api/v1/knowledgebases/documents/{doc_id}/parse"
    display_name = doc_name or doc_id
    
    try:
        print(f"\n📤 Sending parse request for: {display_name} (timeout: {timeout}s)")
        start_time = time.time()
        
        # 타임아웃 설정
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        
        # 파싱 요청 및 응답 대기 (블로킹)
        async with session.post(url, headers=headers, timeout=timeout_obj) as response:
            result = await response.json()
            elapsed = int(time.time() - start_time)
            
            if result.get("code") == 0:
                print(f"✅ Parsing completed for: {display_name} (Time: {elapsed}s)")
                return {
                    "doc_id": doc_id,
                    "name": display_name,
                    "success": True,
                    "result": result,
                    "elapsed": elapsed
                }
            else:
                print(f"❌ Parsing failed for {display_name}: {result.get('message', 'Unknown error')}")
                return {
                    "doc_id": doc_id,
                    "name": display_name,
                    "success": False,
                    "result": result,
                    "elapsed": elapsed
                }
                
    except asyncio.TimeoutError:
        elapsed = int(time.time() - start_time)
        print(f"⏱️ Parsing timeout for {display_name} after {elapsed}s (limit: {timeout}s)")
        return {
            "doc_id": doc_id,
            "name": display_name,
            "success": False,
            "result": {"code": -1, "message": f"Timeout after {timeout}s"},
            "elapsed": elapsed
        }
    except Exception as e:
        elapsed = int(time.time() - start_time)
        print(f"❌ Error parsing {display_name}: {e}")
        return {
            "doc_id": doc_id,
            "name": display_name,
            "success": False,
            "result": {"code": -1, "message": str(e)},
            "elapsed": elapsed
        }

async def parse_documents_sequentially(document_infos: List[Dict], timeout_per_doc: int = PARSING_TIMEOUT) -> Dict:
    """
    문서를 순차적으로 파싱 (한 문서 완료 후 다음 문서 시작)
    
    Args:
        document_infos: 문서 정보 리스트 [{"doc_id": "...", "doc_name": "..."}, ...]
        timeout_per_doc: 문서당 파싱 타임아웃 (초, 기본값: 1800초 = 30분)
        
    Returns:
        dict: 문서별 파싱 결과
    """
    print(f"\n{'='*60}")
    print(f"📄 Starting sequential document parsing ({len(document_infos)} documents)")
    print(f"   Timeout per document: {timeout_per_doc}s ({timeout_per_doc // 60}min)")
    print(f"{'='*60}")
    
    results = {}
    total_start_time = time.time()
    
    # ClientSession에도 전역 타임아웃 설정
    timeout_obj = aiohttp.ClientTimeout(total=None, connect=60, sock_read=timeout_per_doc)
    
    async with aiohttp.ClientSession(timeout=timeout_obj) as session:
        for idx, doc_info in enumerate(document_infos, 1):
            doc_id = doc_info["doc_id"]
            doc_name = doc_info.get("doc_name", doc_id)
            
            print(f"\n{'─'*60}")
            print(f"📄 Document {idx}/{len(document_infos)}: {doc_name}")
            print(f"{'─'*60}")
            
            # 파싱 요청 및 완료 대기 (순차 처리)
            result = await parse_document_async(session, doc_id, doc_name, timeout=timeout_per_doc)
            results[doc_id] = result
    
    # 최종 결과 요약
    total_elapsed = int(time.time() - total_start_time)
    success_count = sum(1 for r in results.values() if r.get("success"))
    
    print(f"\n{'='*60}")
    print(f"📊 Parsing Summary")
    print(f"{'='*60}")
    print(f"  Total documents: {len(document_infos)}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {len(document_infos) - success_count}")
    print(f"  Total time: {total_elapsed}s ({total_elapsed // 60}min)")
    if len(document_infos) > 0:
        print(f"  Average time per doc: {total_elapsed // len(document_infos)}s")
    print(f"{'='*60}\n")
    
    return results

def get_document_parsing_progress(doc_id: str) -> Dict:
    """
    동기로 문서 파싱 진행 상황 확인
    
    Args:
        doc_id: 문서 ID
        
    Returns:
        dict: 문서 상태 정보
    """
    url = f"{plus_base_url}/api/v1/knowledgebases/documents/{doc_id}/parse/progress"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.json()
            # result의 샘플: 
            # {'code': 0, 'data': {'message': '파싱 완료', 'progress': 1.0, 'running': '3', 'status': '1'}, 'message': '작업 성공'}
            print(f"✅ doc parse {doc_id}: {result}")
            return result
        else:
            print(f"❌ Failed to get status for doc {doc_id}: HTTP {response.status_code}")
            return {"code": -1, "message": f"HTTP {response.status_code}"} 
    except Exception as e:
        print(f"❌ Error getting status for doc {doc_id}: {e}")
        return {"code": -1, "message": str(e)}

    

# Ragflow SDK 함수를 사용해서 doument 업로드 및 파싱
def parse_test():
    """문서 업로드 및 파싱 테스트 함수"""
    rag_object = RAGFlow(api_key=api_key, base_url=f"{base_url}")
    
    # dataset 이름
    dataset_name = "test"
    dataset = None
    
    try:
        # 기존 dataset 검색 시도
        datasets = rag_object.list_datasets(name=dataset_name)
        if len(datasets) > 0:
            dataset = datasets[0]
            print(f"Found existing dataset: {dataset.name} (ID: {dataset.id})")
        else:
            # 검색 결과가 없으면 새로 생성
            dataset = rag_object.create_dataset(
                name=dataset_name, 
                description="Dataset for user documents",
            )
            print(f"Created new dataset: {dataset.name} (ID: {dataset.id})")
            
    except Exception as e:
        # 권한 오류나 다른 오류 발생 시 새 dataset 생성
        if "don't own" in str(e).lower() or "not found" in str(e).lower():
            print(f"Dataset access error: {e}")
            print("Creating new dataset with unique name...")
            dataset = rag_object.create_dataset(name=dataset_name, description="Dataset for user documents")
            print(f"Created new dataset: {dataset.name} (ID: {dataset.id})")
        else:
            print(f"Unexpected error: {e}")
            raise
    
    if not dataset:
        print("Failed to get or create dataset")
        return

    # 1. 먼저 dataset에 있는 기존 문서 목록 확인
    print(f"\n{'='*60}")
    print("📂 Checking existing documents in dataset...")
    print(f"{'='*60}")
    
    existing_doc_names = set()
    try:
        existing_docs = dataset.list_documents()
        for doc in existing_docs:
            existing_doc_names.add(doc.name)
            print(f"  📄 Existing: {doc.name} (ID: {doc.id})")
        
        if existing_docs:
            print(f"\n✅ Found {len(existing_docs)} existing document(s)")
        else:
            print(f"\n📭 No existing documents in dataset")
            
    except Exception as e:
        print(f"⚠️  Error listing existing documents: {e}")
        existing_doc_names = set()

    # 2. test_pdf 폴더의 PDF 파일 목록 생성
    print(f"\n{'='*60}")
    print("📁 Scanning PDF files in test_pdf folder...")
    print(f"{'='*60}")
    
    pdf_folder = Path('./test_pdf')
    documents_to_upload = []
    skipped_files = []
    
    # test_pdf 폴더의 모든 PDF 파일 읽기
    for pdf_file in pdf_folder.glob('*.pdf'):
        file_name = pdf_file.name
        
        # 중복 체크
        if file_name in existing_doc_names:
            print(f"  ⏭️  Skipped (already exists): {file_name}")
            skipped_files.append(file_name)
            continue
        
        try:
            with open(pdf_file, 'rb') as f:
                documents_to_upload.append({
                    'display_name': file_name,
                    'blob': f.read()
                })
                print(f"  ➕ Added to upload queue: {file_name}")
        except Exception as e:
            print(f"  ❌ Error reading {file_name}: {e}")
    
    # 3. 업로드 요약
    print(f"\n{'='*60}")
    print("📊 Upload Summary")
    print(f"{'='*60}")
    print(f"  Total files found: {len(list(pdf_folder.glob('*.pdf')))}")
    print(f"  Files to upload: {len(documents_to_upload)}")
    print(f"  Files skipped (duplicates): {len(skipped_files)}")
    print(f"{'='*60}")
    
    if skipped_files:
        print("\n⏭️  Skipped files:")
        for file_name in skipped_files:
            print(f"    - {file_name}")
    
    # 4. 업로드 실행
    if not documents_to_upload:
        print("\n📭 No new documents to upload")
    else:
        print(f"\n⬆️  Uploading {len(documents_to_upload)} new document(s)...")
        try:
            result = dataset.upload_documents(documents_to_upload)
            print(f"✅ Upload result: {result}")
        except Exception as e:
            print(f"❌ Error uploading documents: {e}")
            return
    
    # 5. 업로드된 문서 확인 및 파싱할 문서 목록 생성
    print(f"\n{'='*60}")
    print("🔍 Checking uploaded documents for parsing...")
    print(f"{'='*60}")
    
    document_infos = []
    try:
        # 업로드한 파일 이름 세트
        uploaded_file_names = {doc['display_name'] for doc in documents_to_upload}
        
        # 최근 업로드된 문서만 파싱 대상으로 선택
        all_docs = dataset.list_documents()
        for doc in all_docs:
            status = get_document_parsing_progress(doc.id)
            if status.get('code') == 0:
                running = status.get('data').get('running')
                progress = status.get('data').get('progress')
                if running == '3' and progress == 1.0:
                    print(f"  ✅ Already parsed: {doc.name} (ID: {doc.id})")
                else:
                    print(f"  ✅ Ready to parse: {doc.name} (ID: {doc.id})")
                    document_infos.append({
                        "doc_id": doc.id,
                        "doc_name": doc.name
                    })
    except Exception as e:
        print(f"❌ Error listing documents: {e}")
        document_infos = []

    # 6. 파싱 실행
    if document_infos:
        print(f"\n🚀 Starting parsing for {len(document_infos)} document(s)...")
        # 순차적으로 파싱 실행 (타임아웃: 30분)
        results = asyncio.run(parse_documents_sequentially(document_infos, timeout_per_doc=PARSING_TIMEOUT))
    
        # 결과 상세 출력
        print("\n📋 Detailed Results:")
        for doc_id, result in results.items():
            status_icon = "✅" if result["success"] else "❌"
            elapsed = result.get("elapsed", 0)
            print(f"  {status_icon} {result['name']}: {'Success' if result['success'] else 'Failed'} ({elapsed}s / {elapsed // 60}min)")
    else:
        print("\n📭 No documents to parse")

if __name__ == "__main__":
    parse_test()