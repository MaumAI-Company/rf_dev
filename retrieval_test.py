from retrieval import session_ask, session_chat
import uuid
import re
from keyword_extractor import KeywordExtractor

def filter_think_tags(text):
    """<think> 태그와 그 내용을 제거하는 함수"""
    # <think>...</think> 패턴을 제거
    filtered = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return filtered.strip()

if __name__ == "__main__":
    # 키워드 추출기 초기화
    extractor = KeywordExtractor()

    queries = [
    "소송심의위원회의 심의 절차에서 간사의 주요 역할은 무엇인가요?",
    # "소송이 종결된 후 송무팀은 어떤 후속 조치를 취해야 하며, 관련 부서는 어떻게 활용해야 하나요?",
    # "소송 심의위원회의 구성원은 누구인가요?",
    # "송무팀에서 공탁금 관리기준을 수립한 목적은 무엇인가요?",
    # "공탁금 관리기준에서 정의하는 '공탁'의 의미는 무엇인가요?",
    # "주주총회 20일전 공시는 어떤 부서에서 주관하며, 담당부서는 무엇인가요?",
    # "지체없이 해야하는 공시사항의 주관부서와 관련법규는 무엇인가요?",
    # "일반현황 공시는 언제 이루어지고, 어떤 부서에서 주관하나요?",
    # "IT 사업 추진 과정에서 정보보호팀은 어떤 역할을 하나요?",
    # "CCM 매뉴얼의 주요 목적은 무엇인가요?",
    # "소송심의위원회의 심의절차 간사 역할",
    # "소송이 종결된 후 송무팀의 후속조치와 관련부서 활용",
    # "소송 심의위원회의 구성원",
    # "송무팀 공탁금 관리기준 목적",
    # "공탁금 관리기준에서 공탁 의미"
    ]
    # user_queries = []
    # for query in queries:
    #     keyword = extractor.extract_keywords(query)
    #     user_queries.append(' '.join(keyword))
    
    # print(f'user_queries: {user_queries}')
    user_queries = queries


    kb_name = "흥국화재_테스트"
    chat_name = "흥국화재_사내문서"
    use_sdk = False
    session_name = "sdk-session-" + str(uuid.uuid4())[:8]
    if use_sdk:
        for question in user_queries:
            print(f'\n\n==================== 질문 ====================')
            print(f'질문: {question}, 챗봇이름: {chat_name}, 지식베이스: {kb_name}, 세션이름: {session_name}')
            final_answer = session_ask(question, chat_name, session_name)
            # <think> 태그를 제거하고 최종 답변 길이 계산
            print("\n\n==================== 답변 ====================")
            final_answer_content = filter_think_tags(final_answer.content)
            print(f"답변 길이: {len(final_answer_content)} 문자")
            print(f"참조 문서 수: {len(final_answer.reference)} 개")
            print(f'{final_answer_content}')
            print("\n\n==================== 인용 ====================")
            if final_answer.reference:
                for i, ref in enumerate(final_answer.reference, 1):
                    print(f"ref [{i}]: {ref}")
    else:
        for question in user_queries:
            print(f'\n\n==================== 질문 ====================')
            print(f'질문: {question}, 챗봇이름: {chat_name}, 지식베이스: {kb_name}, 세션이름: {session_name}')
            result = session_chat(question, kb_name, chat_name, session_name)
            if result:
                # <think> 태그를 제거하고 최종 답변 길이 계산
                print("\n\n==================== 답변 ====================")
                final_answer_content = filter_think_tags(result['answer'])
                print(f"답변 길이: {len(final_answer_content)} 문자")
                print(f"참조 문서 수: {len(result['reference'].get('chunks', []))} 개")
                print(final_answer_content)
                print("\n\n==================== 인용 ====================")
                print(f'refs: {result["reference"].get("chunks", [])}')