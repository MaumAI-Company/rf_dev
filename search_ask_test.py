from search_ask import session_ask, session_chat, get_chat_by_name, session_search
from search_ask import update_chat_prompt, create_chat_with_prompt
import uuid
import re
import json

def filter_think_tags(text):
    """<think> 태그와 그 내용을 제거하는 함수"""
    # <think>...</think> 패턴을 제거
    filtered = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return filtered.strip()

def session_ask_test(kb_name, chat_name, session_name):
    """ session_ask 테스트 함수 """

    user_queries = [
        "소송심의위원회의 심의 절차에서 간사의 주요 역할은 무엇인가요?",
        "소송이 종결된 후 송무팀은 어떤 후속 조치를 취해야 하며, 관련 부서는 어떻게 활용해야 하나요?",
        "소송 심의위원회는 어떻게 구성하나요?",
        "송무팀에서 공탁금 관리기준을 만든 목적은 무엇인가요?",
        "공탁금 관리기준에서 정의하는 '공탁'의 의미는 무엇인가요?",
        "기획관리팀 공시관리세부기준에서 주주총회 20일전 공시는 어떤 부서에서 주관하며, 공시내용은 무엇인가요?",
        "기획관리팀 공시관리세부기준에서 지체없이 해야하는 공시사항의 주관부서와 관련법규는 무엇인가요?",
        "기획관리팀 공시관리세부기준에서 일반현황 공시는 언제 이루어지고, 어떤 부서에서 주관하나요?",
        "IT 사업 추진 과정에서 정보보호팀은 어떤 역할을 하나요?",
        "CCM 매뉴얼의 주요 목적은 무엇인가요?",
        "IT 사업의 정의는 무엇인가요?",
        "부정한 행위나 중대한 과실로 인한 사고보고 시 어떻게 해야하나요?",
        "회계감사인의 변경정보를 공개해야 하는 책임부서는?",
        "재무공시에서 외국기업 관련 추가고려 사항을 담당하는 하는 부서는?",
        "보험대리점이 업무를 수행할 때 제한사항이 있나요?",
        "민원심의소위원회의 부의사항은?",
        "위법계약심의소위원회는 어떤 사안을 심의하는가요?",
        "전산위원회 운영 이유는?",
        "전산위원회는 어떤 사안을 심의하나요?",
        "오픈점검 회의의 목적, 시점, 참석자는?",
        "산출물테일러링 회의의 목적, 시점, 참석대상은?",
    ]
    use_sdk = False
    use_search = True
    if use_sdk:
        if use_search:
            for question in user_queries:
                print(f'\n\n==================== 질문 ====================')
                print(f'질문: {question}, 지식베이스: {kb_name}')
                final_answer = session_search(question, kb_name)
        else:
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
                # print(f'refs: {result["reference"].get("chunks", [])}')
                if len(result['reference']): 
                    for i, ref in enumerate(result['reference'].get('chunks', [])):
                        print(f"ref [{i}]: {ref}")

def test_update_chat_prompt():
    """ update_chat_prompt 테스트 함수 """
    chat = get_chat_by_name(chat_name = "테스트")
    if not chat:
        print(f"Test aborted: chat '{chat_name}' not found.")
    else:
        sample_user_feedback = """
무배당 흥Good 행복든든 재산보험(25.06)_(1종) 상품의 장점을 더 부각시키고, 고객이 쉽게 이해할 수 있도록 설명을 간결하게 해주세요. 
또한, 고객이 보험 가입 후 빠른 보상 처리를 받을 수 있다는 점을 강조해 주세요.
스프링클러가 없는 건물이나 아파트가 많은데 이거에 대한 보장도 가능한지 여부를 추가로 설명해 주세요.
"""
        sample_current_script = """
[인사말]
안녕하세요, 고객님. 요즘 집안에서 화재나 누수 같은 작은 사고라도 생기면 복구 비용이 만만치 않다는 걸 많이들 느끼셨을 텐데요. 예전 같으면 이런 부분은 그냥 감수하시거나 보험 없이 넘어가셨을 텐데, 요즘은 보다 체계적으로 대비하는 분들이 많아졌죠.
생활하면서 예상치 못한 손해는 누구에게나 찾아올 수 있고, 특히 집에 대한 보장은 꼭 필요합니다. 특히 40대 분들 같은 경우, 가족과 집을 동시에 안정적으로 보호하고 싶어 하시는 경우가 많아요.
오늘은 그런 부분을 좀 더 안심하고 대비할 수 있는 방법에 대해 간단히 안내드리고자 연락드린 건데, 혹시 관심 있으신가요?
[보험 영업]
오늘 안내들리 상품은 **무배당 흥Good 행복든든 재산보험(25.06)_(1종)**입니다. 이 상품은 집에 대한 다양한 손해를 한 번에 보장해 드리는 종합 보험으로, 특히 화재나 물 누수 같은 사고에 대해 실손을 보상해 드리고 있어요.
주요 보장은 크게 네가지로 구성되어 있는데요. 첫 번째는 **화재손해(건물)(실손보상형)**입니다. 집이 화재로 인해 손상되었을 때 실제 지출한 복구 비용을 보상해 드리고요.
두 번째는 **스프링클러 누출손해(비례보상형)**입니다. 집에 설치된 스프링클러가 고장이나 누수로 인해 손해가 발생했을 때, 보상 한도 내에서 비례해서 보상해 드리는 부분이에요.
또한, **임대인배상책임(주택)(화재배상제외)**과 **화재배상책임**도 포함되어 있어요, 이 부분은 집을 임대하거나 거주하면서 발생할 수 있는 제 3자 배상 책임도 커버해 드리고요.
특히 고객님처럼 40대 중반에 계시고, 집을 소유하고 계신 분들께는 이런 종합적인 보장이 큰 도움이 될 수 있어요. 집은 단 한 번의 사고로도 큰 손해가 발생할 수 있기 때문에, 미리 대비해 두는게 중요하죠.
이 상품은 집에 대한 보장을 체계적으로 구성할 수 있도록 설계되어 있어서, 보험에 익숙하지 않으신 분들도 쉽게 이해하시고 가입하실 수 있어요.
[마무리]
월 1만 원, 7년 납입하는 상품으로, 집에 대한 다양한 손해를 보장받을 수 있어요. 화재나 물 누수뿐 아니라 배상책임도 함께 커버해 드리고요.
이 정도 금액으로 집의 안전을 체계적으로 지켜볼 수 있다면, 꼭 고려해보시는 게 좋을 것 같아요.
궁금한 점이나 문의하실 내용 있으시면 언제든지 말씀해 주세요. 도움을 드릴 수 있어 정말 기쁩니다.
[요약]
고객님처럼 집을 소유하고 계신 분께는 예상치 못한 화재나 누수에 대비하는 것이 중요합니다.
주요 보장은 화재손해(건물)(실손보상형), 스프링클러 누출손해(비례보상형), 임대인배상 책임, 화재배상착임입니다.
집에 대한 다양한 손해를 한 번에 보장받을 수 있어, 가입 시 큰 도움이 될 수 있습니다.
"""

    print("사용자 피드백과 현재 스크립트를 기반으로 update_chat_prompt() 호출")
    result = update_chat_prompt(chat_name, user_feedback=sample_user_feedback, current_script=sample_current_script)
    print("결과: ")
    try:
        print(json.dumps(result, ensure_ascii=False, indent=0))
    except Exception:
        print(result)

def test_create_chat_with_prompt(chat_name):
    """ create_chat_with_prompt 테스트 함수 """
    kb_name = "흥국화재_테스트"
    sample_user_feedback = """
무배당 흥Good 행복든든 재산보험(25.06)_(1종) 상품의 장점을 더 부각시키고, 고객이 쉽게 이해할 수 있도록 설명을 간결하게 해주세요. 
또한, 고객이 보험 가입 후 빠른 보상 처리를 받을 수 있다는 점을 강조해 주세요.
스프링클러가 없는 건물이나 아파트가 많은데 이거에 대한 보장도 가능한지 여부를 추가로 설명해 주세요.
"""
    sample_current_script = """
[인사말]
안녕하세요, 고객님. 요즘 집안에서 화재나 누수 같은 작은 사고라도 생기면 복구 비용이 만만치 않다는 걸 많이들 느끼셨을 텐데요. 예전 같으면 이런 부분은 그냥 감수하시거나 보험 없이 넘어가셨을 텐데, 요즘은 보다 체계적으로 대비하는 분들이 많아졌죠.
생활하면서 예상치 못한 손해는 누구에게나 찾아올 수 있고, 특히 집에 대한 보장은 꼭 필요합니다. 특히 40대 분들 같은 경우, 가족과 집을 동시에 안정적으로 보호하고 싶어 하시는 경우가 많아요.
오늘은 그런 부분을 좀 더 안심하고 대비할 수 있는 방법에 대해 간단히 안내드리고자 연락드린 건데, 혹시 관심 있으신가요?
[보험 영업]
오늘 안내들리 상품은 **무배당 흥Good 행복든든 재산보험(25.06)_(1종)**입니다. 이 상품은 집에 대한 다양한 손해를 한 번에 보장해 드리는 종합 보험으로, 특히 화재나 물 누수 같은 사고에 대해 실손을 보상해 드리고 있어요.
주요 보장은 크게 네가지로 구성되어 있는데요. 첫 번째는 **화재손해(건물)(실손보상형)**입니다. 집이 화재로 인해 손상되었을 때 실제 지출한 복구 비용을 보상해 드리고요.
두 번째는 **스프링클러 누출손해(비례보상형)**입니다. 집에 설치된 스프링클러가 고장이나 누수로 인해 손해가 발생했을 때, 보상 한도 내에서 비례해서 보상해 드리는 부분이에요.
또한, **임대인배상책임(주택)(화재배상제외)**과 **화재배상책임**도 포함되어 있어요, 이 부분은 집을 임대하거나 거주하면서 발생할 수 있는 제 3자 배상 책임도 커버해 드리고요.
특히 고객님처럼 40대 중반에 계시고, 집을 소유하고 계신 분들께는 이런 종합적인 보장이 큰 도움이 될 수 있어요. 집은 단 한 번의 사고로도 큰 손해가 발생할 수 있기 때문에, 미리 대비해 두는게 중요하죠.
이 상품은 집에 대한 보장을 체계적으로 구성할 수 있도록 설계되어 있어서, 보험에 익숙하지 않으신 분들도 쉽게 이해하시고 가입하실 수 있어요.
[마무리]
월 1만 원, 7년 납입하는 상품으로, 집에 대한 다양한 손해를 보장받을 수 있어요. 화재나 물 누수뿐 아니라 배상책임도 함께 커버해 드리고요.
이 정도 금액으로 집의 안전을 체계적으로 지켜볼 수 있다면, 꼭 고려해보시는 게 좋을 것 같아요.
궁금한 점이나 문의하실 내용 있으시면 언제든지 말씀해 주세요. 도움을 드릴 수 있어 정말 기쁩니다.
[요약]
고객님처럼 집을 소유하고 계신 분께는 예상치 못한 화재나 누수에 대비하는 것이 중요합니다.
주요 보장은 화재손해(건물)(실손보상형), 스프링클러 누출손해(비례보상형), 임대인배상 책임, 화재배상착임입니다.
집에 대한 다양한 손해를 한 번에 보장받을 수 있어, 가입 시 큰 도움이 될 수 있습니다.
"""

    print("사용자 피드백과 현재 스크립트를 기반으로 create_chat_with_prompt() 호출")
    result = create_chat_with_prompt(kb_name, chat_name,
        user_feedback=sample_user_feedback, 
        current_script=sample_current_script
    )
    print("결과: ")
    try:
        print(json.dumps(result, ensure_ascii=False, indent=0))
    except Exception:
        print(result)

if __name__ == "__main__":

    # Test with chat
    kb_name = "흥국화재_사내문서2"
#    kb_name = "흥국화재_사규"
    chat_name = "흥국_사내문서_챗봇2"
#    chat_name = "흥국화재_사내문서_챗봇"
    session_name = "sdk-session-" + str(uuid.uuid4())[:8]
    session_ask_test(kb_name, chat_name, session_name)
    # 1. Test to update chat prompt
    # test_update_chat_prompt()

    # 2. Test to create chat with prompt & generate new script
    # chat_name = "상품판매_스크립트_테스트"
    # test_create_chat_with_prompt(chat_name)
    # question = (
    #     "무배당 흥Good 행복든든 재산보험(25.06)_(1종) 상품에서 보험가입 후 빠른 보상 처리와 "
    #     "스프링클러가 없는 집에 대한 보장여부 확인해서 스크립트를 수정해줘"
    # )
    # print(f'question: {question}')
    # kb_name = "흥국화재_테스트"
    # session_name = "sdk-session-" + str(uuid.uuid4())[:8]
    # result = session_chat(question, kb_name, chat_name, session_name) 
    # if result:
    #     # <think> 태그를 제거하고 최종 답변 길이 계산
    #     print("\n\n==================== 답변 ====================")
    #     final_answer_content = filter_think_tags(result['answer'])
    #     print(f"답변 길이: {len(final_answer_content)} 문자")
    #     print(f"참조 문서 수: {len(result['reference'].get('chunks', []))} 개")
    #     print(final_answer_content)
    #     print("\n\n==================== 인용 ====================")
    #     print(f'refs: {result["reference"].get("chunks", [])}')
