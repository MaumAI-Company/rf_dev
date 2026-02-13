from ragflow_sdk import RAGFlow
import requests
import json
import re
import uuid

# RAGFlow HTTP API 설정
api_key = "ragflow-U5ZGEyNTdlNjkyODExZjBiODE2MDI0Mm"
base_url = "http://10.50.7.154:8080"
# api_key = "ragflow-YyYWRhZmY0ODMyMTExZjA4OTQ3MDI0Mm"
# base_url = "http://10.50.3.11:80"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def filter_think_tags(text):
    """<think> 태그와 그 내용을 제거하는 함수"""
    # <think>...</think> 패턴을 제거
    filtered = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return filtered.strip()

# Ragflow SDK 함수를 사용해서 ask() API 호출
def ask(question, chat_name, session_name, stream=True):
    """세션에서 질문하고 스트림 응답을 받는 함수"""
    rag_object = RAGFlow(api_key=api_key, base_url=f"{base_url}")
    assistant = rag_object.list_chats(name=chat_name)
    assistant = assistant[0]
    # Find session using session_name
    session = None
    for sess in assistant.list_sessions():
        print(sess.name)
        if sess.name == session_name:
            print(f"Found session: {sess.id}")
            session = sess
            break

    if session == None:
        session = assistant.create_session(name=session_name)
        print(f"Created new session: {session.id}")

    for ans in session.ask(question, stream=True):
        yield ans

# Ragflow SDK 함수를 사용해서 ask() API 호출
def session_ask(question, chat_name, session_name, thinktag=True, stream=True):
    """세션에서 질문하고 스트림 응답을 화면에 출력하고 결과를 반환하는 함수"""
    final_answer = None
    displayed_chars = 0  # 이미 출력된 문자 수 추적

    print("==================== 답변 스트리밍 ====================")
    cont = ""
    for ans in ask(question, chat_name, session_name, stream=True):
        cont = ans.content
        
        # 이미 출력된 부분 이후의 새로운 내용만 출력
        if len(cont) > displayed_chars:
            new_content = cont[displayed_chars:]
            if new_content.strip():
                print(new_content, end='', flush=True)
                displayed_chars = len(cont)
        final_answer = ans
    return final_answer


def retrieve(question, kb_name):
    """kb_name으로 지정된 지식베이스에서 질문에 대한 검색하는 함수"""
    rag_object = RAGFlow(api_key=api_key, base_url=base_url)
    # name으로 지정된 지식베이스 조회
    dataset_ids = []
    for dataset in rag_object.list_datasets(name=kb_name):
        dataset_ids.append(dataset.id)

    chunks = rag_object.retrieve(dataset_ids=dataset_ids, question=question)
    for c in chunks:
        print(f'{c.document_id}-{c.id}, similarity: {c.similarity}: {c.content}')
    return chunks

# HTTP API usage
def get_chat_id_by_name(chat_name):
    """chat name으로 chat id를 구하는 함수"""
    url = f"{base_url}/api/v1/chats"
    params = {
        "page": 1,
        "page_size": 100,
        "name": chat_name
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("data") and len(data["data"]) > 0:
            chat_id = data["data"][0]["id"]
            print(f"Found chat '{chat_name}' with ID: {chat_id}")
            return chat_id
        else:
            print(f"No chat found with name: {chat_name}")
            return None
    else:
        print(f"Error getting chats: {response.status_code} - {response.text}")
        return None

def create_chat(chat_name, dataset_ids=[]):
    """새로운 채팅을 생성하는 함수"""
    url = f"{base_url}/api/v1/chats"
    data = {
        "name": chat_name,
        "dataset_ids": dataset_ids
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        data = response.json()
        if data.get("data") and len(data["data"]) > 0:
            chat = data["data"]
            chat_id = chat["id"]
            print(f"Found {chat_id} chat with {chat_name}")
            return chat
        else:
            print(f"No chat found with name: {chat_name}")
            return None
    else:
        print(f"Error creating chat: {response.status_code} - {response.text}")
        return None

def get_dataset_ids_by_name(dataset_name):
    """dataset name으로 dataset id 리스트를 구하는 함수"""
    url = f"{base_url}/api/v1/datasets"
    params = {
        "page": 1,
        "page_size": 100,
        "name": dataset_name
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("data") and len(data["data"]) > 0:
            dataset_ids = [dataset["id"] for dataset in data["data"]]
            print(f"Found {len(dataset_ids)} datasets with name '{dataset_name}'")
            for i, dataset in enumerate(data["data"]):
                print(f"  [{i+1}] {dataset['id']} - {dataset['name']}")
            return dataset_ids
        else:
            print(f"No datasets found with name: {dataset_name}")
            return []
    else:
        print(f"Error getting datasets: {response.status_code} - {response.text}")
        return []

def get_session_by_name(chat_id, session_name):
    """session name으로 session id를 구하는 함수"""
    url = f"{base_url}/api/v1/chats/{chat_id}/sessions"
    params = {
        "page": 1,
        "page_size": 100,
        "name": session_name
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("data") and len(data["data"]) > 0:
            session_id = data["data"][0]["id"]
            print(f"Found session '{session_name}' with ID: {session_id}")
            return session_id
        else:
            return None
    else:
        print(f"Error getting sessions: {response.status_code} - {response.text}")
        return None

def create_session(chat_id, session_name=None):
    """새 세션을 생성하는 함수"""
    url = f"{base_url}/api/v1/chats/{chat_id}/sessions"
    data = {
        "name": session_name
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        session_id = response.json()["data"]["id"]
        print(f"Created new session: {session_id}")
        return session_id
    else:
        print(f"Error creating session: {response.status_code} - {response.text}")
        return None

def search(question, kb_name=None):
    """지식베이스에 대해 질문하고 스트림 응답을 생성(yield)하는 제너레이터 함수"""
    # KB name으로 dataset ids 구하기
    dataset_ids = get_dataset_ids_by_name(kb_name)
    if not dataset_ids:
        print(f"해당 지식베이스({kb_name})의 dataset을 찾을 수 없습니다")
        return

    url = f"{base_url}/api/v1/sessions/ask"
    data = {
        "question": question,
        "stream": True,
        "dataset_ids": dataset_ids
    }

    try:
        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status()  # 200 OK가 아니면 예외 발생
        for line in response.iter_lines():
            yield line
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return

def session_search(question, kb_name=None):
    """search을 호출하여 스트림 응답을 화면에 출력하고 최종 결과를 반환하는 함수"""
    full_answer = ""
    final_reference = {}
    displayed_chars = 0

    print("==================== HTTP API 답변 스트리밍 ====================")
        # search 제너레이터로부터 원시 데이터 라인을 받음
    for line in search(question, kb_name):
        try:
            line_str = line.decode('utf-8')
            if line_str.startswith('data:'):
                json_data = line_str[5:].strip()
                if not json_data:
                    continue
                response_data = json.loads(json_data)
                # data: true 이면 스트리밍 종료
                if response_data.get("data") is True:
                    #print("\n>>> 응답이 완료되었습니다.")
                    break
                if (response_data.get("code") == 0 and
                        isinstance(response_data.get("data"), dict) and
                        "answer" in response_data["data"]):
                    current_answer = response_data["data"]["answer"]
                    current_reference = response_data["data"].get("reference", {})
                    # 이미 출력된 부분 이후의 새로운 내용만 출력
                    if len(current_answer) > displayed_chars:
                        new_content = current_answer[displayed_chars:]
                        if new_content.strip():
                            print(new_content, end='', flush=True)
                        displayed_chars = len(current_answer)
                    # 최종 답변과 참조 정보 업데이트
                    full_answer = current_answer
                    if current_reference:
                        final_reference = current_reference
        except json.JSONDecodeError as e:
            print(f"\n[DEBUG] JSON 파싱 오류: {e} | 데이터: {line_str}")
            continue
        except Exception as e:
            print(f"\n[DEBUG] 처리 오류: {e}")
            continue
    return {
        "answer": full_answer,
        "reference": final_reference
    }

def chat(question, kb_name=None, chat_name=None, session_name=None):
    """KB 기반으로 생성된 chat을 호출해서 스트림 응답을 생성(yield)하는 제너레이터 함수"""
    # KB name으로 dataset ids 구하기
    dataset_ids = get_dataset_ids_by_name(kb_name)
    if not dataset_ids:
        print(f"해당 지식베이스({kb_name})의 dataset을 찾을 수 없습니다")
        return
    else: 
        # chat name으로 chat_ids 구하기
        chat_id = get_chat_id_by_name(chat_name)
        if not chat_id:
            print(f"해당 챗봇({chat_name})의 ID를 찾을 수 없습니다")
            chat = create_chat(chat_name, dataset_ids)
            chat_id = chat.get("id")
            if not chat_id:
                return

    session_id = get_session_by_name(chat_id, session_name)
    if not session_id:
        session_id = create_session(chat_id, session_name)

    url = f"{base_url}/api/v1/chats/{chat_id}/completions"
    data = {
        "question": question,
        "stream": True,
        "session_id": session_id
    }

    try:
        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status()  # 200 OK가 아니면 예외 발생
        for line in response.iter_lines():
            yield line
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return

def session_chat(question, kb_name=None, chat_name=None, session_name=None):
    """chat을 호출하여 스트림 응답을 화면에 출력하고 최종 결과를 반환하는 함수"""
    full_answer = ""
    final_reference = {}
    displayed_chars = 0

    print("==================== HTTP API 답변 스트리밍 ====================")
    # chat 제너레이터로부터 원시 데이터 라인을 받음
    for line in chat(question, kb_name, chat_name, session_name):
        try:
            line_str = line.decode('utf-8')
            if line_str.startswith('data:'):
                json_data = line_str[5:].strip()
                if not json_data:
                    continue
                response_data = json.loads(json_data)
                # data: true 이면 스트리밍 종료
                if response_data.get("data") is True:
                    #print("\n>>> 응답이 완료되었습니다.")
                    break
                if (response_data.get("code") == 0 and
                        isinstance(response_data.get("data"), dict) and
                        "answer" in response_data["data"]):
                    # print(f'\n>>> code: {response_data.get("code")}, data: {len(response_data.get("data").get("answer"))}')
                    current_answer = response_data["data"]["answer"]
                    current_reference = response_data["data"].get("reference", {})
                    # 이미 출력된 부분 이후의 새로운 내용만 출력
                    if len(current_answer) > displayed_chars:
                        new_content = current_answer[displayed_chars:]
                        if new_content.strip():
                            print(new_content, end='', flush=True)
                        displayed_chars = len(current_answer)
                    # 최종 답변과 참조 정보 업데이트
                    full_answer = current_answer
                    if current_reference:
                        final_reference = current_reference
        except json.JSONDecodeError as e:
            print(f"\n[DEBUG] JSON 파싱 오류: {e} | 데이터: {line_str}")
            continue
        except Exception as e:
            print(f"\n[DEBUG] 처리 오류: {e}")
            continue
    return {
        "answer": full_answer,
        "reference": final_reference
    }
    
def get_chat_by_name(chat_name):
    """chat name으로 chat id를 구하는 함수"""
    url = f"{base_url}/api/v1/chats"
    params = {
        "page": 1,
        "page_size": 100,
        "name": chat_name
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("data") and len(data["data"]) > 0:
            chat = data["data"][0]
            # json data를 indent하여 출력
        #     print(json.dumps(chat, indent=2, ensure_ascii=False))
            print(f"Found chat '{chat_name}' with ID: {chat['id']}")
            return chat
        else:
            print(f"No chat found with name: {chat_name}")
            return None
    else:
        print(f"Error getting chats: {response.status_code} - {response.text}")
        return None

def update_chat_prompt(chat_name, **kwargs):
    """chat id로 chat을 업데이트하는 함수"""
    # get the prompt from the chat (existing template may exist)
    chat = get_chat_by_name(chat_name)
    if not chat:
        print(f"Chat not found: {chat_name}")
        return None

    # new chat prompt to update
    prompt_template = """
You are an intelligent assistant. Please follow the user feedback and use the knowledge base to produce concrete, citation-backed modifications to the current sales script. When all knowledge base content is irrelevant to the question, your answer must include the sentence "The answer you are looking for is not found in the knowledge base!" Answers need to consider chat history. Answers should list all citations which are used to generate answers.
Task for the assistant:
- Keep the original format of the current sales script
- Refer to the retrieved knowledge base
- Follow the instructions provided in the user feedback
- Generate a new sales script

    Here is the user feedback (instructions provided by the user):
    {user_feedback}
    The above is the user feedback.

    Here is the knowledge base:
    {knowledge}
    The above is the knowledge base.

    Here is the current sales script:
    {current_script}
    The above is the current sales script.
"""

    user_feedback = kwargs.get("user_feedback", "")
    current_script = kwargs.get("current_script", "")
    print(f"user_feedback: {user_feedback}")
    print(f"current_script: {current_script[:100]}")

    new_prompt = prompt_template  # default to the raw template
    # Use placeholders for knowledge by default; embed provided user_feedback/current_script
    filled = {
        'knowledge': '{knowledge}',
        'user_feedback': user_feedback if user_feedback else '',
        'current_script': current_script if current_script else ''
    }
    try:
        new_prompt = prompt_template.format(**filled)
    except Exception:
        # fallback to the raw template if formatting fails
        new_prompt = prompt_template

    # Prepare payload and stest_chat_idend update
    chat_id = chat.get("id")
    url = f"{base_url}/api/v1/chats/{chat_id}"

    # Build prompt_data from chat prompt safely and update required fields
    prompt_data = chat.get("prompt", {}).copy()
    prompt_data.update({
        "prompt": new_prompt,
        "variables": [
            {"key": "knowledge", "optional": False},
            {"key": "user_feedback", "optional": True},
            {"key": "current_script", "optional": True},
        ],
    })

    data = {
        "prompt": prompt_data,
        "name": chat.get("name"),
    }
    print(f'data: {data}')
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Successfully updated chat: {chat_id}")
        return response.json()
    else:
        print(f"Error updating chat: {response.status_code} - {response.text}")
        return None

def create_chat_with_prompt(kb_name=None, chat_name=None, **kwargs):
    """chat_name으로 chat을 생성하는 함수"""
    if not chat_name:
        print(f"Chat name({chat_name}) is required")
        return None
    else:
        chat = get_chat_by_name(chat_name)
        if chat:
            print(f"Chat already exists: {chat_name}")
            # check if the prompt has optional variable such as user_feedback or current_script
            key_list = [key['key'] for key in chat['prompt']['variables']]
            if 'user_feedback' in key_list and 'current_script' in key_list:
                print(f"Chat prompt is already up-to-date: {chat_name}")
                return 
            update_chat_prompt(chat_name, **kwargs)
            return None
    chat = create_chat(chat_name)
    if not chat:
        print(f"Failed to create chat: {chat_name}")
        return None

    # new chat prompt to create
    prompt_template = """
You are an intelligent assistant. Please follow the user feedback and use the knowledge base to produce concrete, citation-backed modifications to the current sales script. When all knowledge base content is irrelevant to the question, your answer must include the sentence "The answer you are looking for is not found in the knowledge base!" Answers need to consider chat history. Answers should list all citations which are used to generate answers.
Task for the assistant:
- Keep the original format of the current sales script
- Refer to the retrieved knowledge base
- Follow the instructions provided in the user feedback
- Generate a new sales script

    Here is the user feedback (instructions provided by the user):
    {user_feedback}
    The above is the user feedback.

    Here is the knowledge base:
    {knowledge}
    The above is the knowledge base.

    Here is the current sales script:
    {current_script}
    The above is the current sales script.
"""

    user_feedback = kwargs.get("user_feedback", "")
    current_script = kwargs.get("current_script", "")

    new_prompt = prompt_template  # default to the raw template
    # Use placeholders for knowledge by default; embed provided user_feedback/current_script
    filled = {
        'knowledge': '{knowledge}',
        'user_feedback': user_feedback if user_feedback else '',
        'current_script': current_script if current_script else ''
    }
    try:
        new_prompt = prompt_template.format(**filled)
    except Exception:
        # fallback to the raw template if formatting fails
        new_prompt = prompt_template

    # Prepare payload and send create request
    chat_id = chat.get("id")
    url = f"{base_url}/api/v1/chats/{chat_id}"

    # Build prompt_data from chat prompt safely and update required fields
    prompt_data = chat.get("prompt", {}).copy()
    prompt_data.update({
        "prompt": new_prompt,
        "variables": [
            {"key": "knowledge", "optional": False},
            {"key": "user_feedback", "optional": True},
            {"key": "current_script", "optional": True},
        ],
    })

    data = {
        "prompt": prompt_data,
        "name": chat.get("name"),
    }
    dataset_ids = get_dataset_ids_by_name(kb_name)
    if not dataset_ids:
        print(f"지식베이스({kb_name})를 찾을 수 없습니다. 지식베이스를 지정하지 않고 생성합니다")
    if dataset_ids:
        data["dataset_ids"] = dataset_ids

    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Successfully created chat: {chat_id}")
        return response.json()
    else:
        print(f"Error updating chat: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    user_queries = [
        "장기보험상품에서 암진단 후 지급기간은?",
        "장기보험상품에서 보장주기에 대해 알려줘",
        "장기보험상품에서 보장범위는 어떻게 되나요?", 
        "장기보험상품에서 보장 불가한 항목은 어떻게 되나요?",
        "장기보험상품에서 보장 가능한 병원등급은 어떻게 되나요?",
        "장기보험상품에서 보장하는 방식에서 몇 회까지 보장하는지 알려줘",
        "장기보험상품에서 보장하는 기준을 알려줘",
    ]
    question = user_queries[0]
    kb_name = "장기보험상품"
    chat_name = "장기보험_챗봇"
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