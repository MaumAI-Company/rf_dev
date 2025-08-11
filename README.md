# ragflow-sdk 개발 환경 설정
- **중요** ragflow-sdk가 python 3.13 버전에서 동작하지 않는 문제가 있음 
- 3.11 이상 3.13 이하의 버전에서 정상 작동함
- 개발환경: vscode가 설치된 WIndows 환경을 가정
- vscode의 python extension이 여러 개 설치되어 있다면 Python 3.11 버전을 사용해야 함
- 개발 경로: ragflow_dev라는 경로 생성. vscode 터미널에서 아래 작업 진행
- 경로로 이동한 후 아래와 같이 가상 환경 생성
```
PS D:\dev\rf_dev> python3.11
Python 3.11.2 (tags/v3.11.2:878ead1, Feb  7 2023, 16:38:35) [MSC v.1934 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> quit()
PS D:\dev\rf_dev> python3.11 -m venv .venv	python -m venv .venv
```
- 가상환경을 활성화
```
.\.venv\Script\activate
```
- 가상환경이 활성화되면 vscode 터미널에서 아래와 같이 표시됨. _아래의 prompt는 항상 표시된다고 가정하고 이후 command 창 명령어에선 생략한다._
```
(.venv) PS D:\dev\rf_dev>
```
- 가상환경이 활성화된 상태에서 pip를 이용하여 Jupyter 노트북 실행에 필요한 패키지를 설치한다.
```
pip install ipykernel
```
- 랭체인과 랭그래프 패키지도 설치한다. _이후 필요한 패키지는 해당 패키지가 필요할 때 설치_
```
pip install langchain langgraph langfuse openai ragflow-sdk
```

`00-Ragflow_SDK_test.ipynb` 파일을 vscode에서 Jupyter Notebook 형태로 실행하려면 파이썬 커널을 가상환경을 설치한 .venv를 선택해서 실행해야 함