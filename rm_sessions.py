from ragflow_sdk import RAGFlow
import requests
from typing import Optional
import time
from datetime import datetime

# RAGFlow HTTP API 설정
api_key = "ragflow-U5ZGEyNTdlNjkyODExZjBiODE2MDI0Mm"
base_url = "http://10.50.7.154:8080"

def format_timestamp(timestamp):
    """타임스탬프를 YYYY-MM-DD HH:MM:SS 형식으로 변환"""
    
    # Unix timestamp (숫자) 처리
    if isinstance(timestamp, (int, float)):
        if timestamp > 10000000000:  # 밀리초 단위
            timestamp = timestamp / 1000
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # ISO 8601 문자열 처리
    elif isinstance(timestamp, str):
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S"
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(timestamp, fmt)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

def remove_old_sessions(chat_name: str, keep_count: int = 5, dry_run: bool = True) -> dict:
    """
    특정 채팅의 오래된 세션들을 삭제하고 최근 N개만 유지
    
    Args:
        chat_name: 채팅 이름
        keep_count: 유지할 세션 개수 (기본값: 5)
        dry_run: True일 경우 실제 삭제하지 않고 삭제 대상만 출력 (기본값: True)
        
    Returns:
        dict: 삭제 결과 정보
    """
    
    # RAGFlow 객체 생성
    rag_object = RAGFlow(api_key=api_key, base_url=base_url)
    assistant = rag_object.list_chats(name=chat_name)
    assistant = assistant[0]
    
    try:
        # 1. 모든 세션 가져오기 (최근 생성된 순서로 정렬)
        print("📋 Fetching all sessions...")
        all_sessions = []
        page = 1
        page_size = 100
        
        while True:
            sessions = assistant.list_sessions(
                page=page,
                page_size=page_size,
                orderby="create_time",
                desc=True  # 최근 생성된 것부터
            )
            
            if not sessions:
                break
                
            all_sessions.extend(sessions)
            print(f"  Page {page}: {len(sessions)} sessions fetched")
            
            if len(sessions) < page_size:
                break
                
            page += 1
        
        total_count = len(all_sessions)
        print(f"\n✅ Total sessions found: {total_count}")
        
        # 2. 유지할 세션과 삭제할 세션 구분
        sessions_to_keep = all_sessions[:keep_count]
        sessions_to_delete = all_sessions[keep_count:]
        
        print(f"\n{'─'*60}")
        print(f"📊 Session Analysis")
        print(f"{'─'*60}")
        print(f"  Total sessions: {total_count}")
        print(f"  Sessions to keep: {len(sessions_to_keep)}")
        print(f"  Sessions to delete: {len(sessions_to_delete)}")
        print(f"{'─'*60}\n")
        
        # 3. 유지할 세션 목록 출력
        if sessions_to_keep:
            print(f"✅ Sessions to KEEP (most recent {len(sessions_to_keep)}):")
            for i, session in enumerate(sessions_to_keep, 1):
                session_name = getattr(session, 'name', 'N/A')
                session_id = getattr(session, 'id', 'N/A')
                create_time = getattr(session, 'create_time', 'N/A')
                formatted_time = format_timestamp(create_time)
                print(f"  {i:2d}. {session_name[:45]:<45} | {formatted_time}")
                print(f"      ID: {session_id}")
        
        # 4. 삭제할 세션 목록 출력
        if sessions_to_delete:
            print(f"\n🗑️  Sessions to DELETE (oldest {len(sessions_to_delete)}):")
            session_ids_to_delete = []
            
            for i, session in enumerate(sessions_to_delete, 1):
                session_name = getattr(session, 'name', 'N/A')
                session_id = getattr(session, 'id', 'N/A')
                create_time = getattr(session, 'create_time', 'N/A')
                session_ids_to_delete.append(session_id)
                formatted_time = format_timestamp(create_time)
                print(f"  {i:2d}. {session_name[:45]:<45} | {formatted_time}")
                print(f"      ID: {session_id}")
            
            # 5. 실제 삭제 수행 (dry_run이 False일 경우만)
            if not dry_run:
                print(f"\n{'─'*60}")
                print(f"⚠️  Deleting {len(session_ids_to_delete)} sessions...")
                print(f"{'─'*60}")
                
                try:
                    # 세션 삭제 (배치로 삭제)
                    assistant.delete_sessions(ids=session_ids_to_delete)
                    print(f"✅ Successfully deleted {len(session_ids_to_delete)} sessions")
                    
                    return {
                        "success": True,
                        "total_sessions": total_count,
                        "kept_sessions": len(sessions_to_keep),
                        "deleted_sessions": len(sessions_to_delete),
                        "deleted_session_ids": session_ids_to_delete
                    }
                    
                except Exception as e:
                    print(f"❌ Error deleting sessions: {e}")
                    return {
                        "success": False,
                        "error": str(e),
                        "total_sessions": total_count,
                        "kept_sessions": len(sessions_to_keep),
                        "deleted_sessions": 0
                    }
            else:
                print(f"\n{'─'*60}")
                print(f"ℹ️  DRY RUN MODE - No sessions were actually deleted")
                print(f"{'─'*60}")
                print(f"💡 To perform actual deletion, run with dry_run=False")
                
                return {
                    "success": True,
                    "dry_run": True,
                    "total_sessions": total_count,
                    "kept_sessions": len(sessions_to_keep),
                    "would_delete": len(sessions_to_delete),
                    "would_delete_session_ids": session_ids_to_delete
                }
        else:
            print(f"\n✅ No sessions to delete (total sessions <= keep_count)")
            return {
                "success": True,
                "total_sessions": total_count,
                "kept_sessions": len(sessions_to_keep),
                "deleted_sessions": 0
            }
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "total_sessions": 0,
            "kept_sessions": 0,
            "deleted_sessions": 0
        }


if __name__ == "__main__":
    print("=" * 60)
    print("Session Cleanup Utility")
    chat_name = input("Enter chat name: ").strip()
    # 기본값과 입력 검증 추가
    keep_count_input = input("Enter number of sessions to keep (default 5): ").strip()
    keep_count = int(keep_count_input) if keep_count_input else 5

    dry_run_input = input("Dry run? (y/n, default y): ").strip().lower()
    dry_run = dry_run_input != 'n'
    print("=" * 60)
    
    # 사용 예제
    result = remove_old_sessions(chat_name, keep_count=keep_count, dry_run=dry_run)
    print(f"\nResult: {result}")