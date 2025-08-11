# ragflow-sdk 개발 환경 설정
- **중요** ragflow-sdk가 python 3.13 버전에서 동작하지 않는 문제가 있음 
- 3.11 이상 3.13 이하의 버전에서 정상 작동함
- 개발환경: vscode가 설치된 WIndows 환경을 가정
- vscode의 python extension이 여러 개 설치되어 있을 수 있는데 Python 3.11.2를 가정
- 개발 경로: ragflow_dev라는 경로 생성. vscode 터미널에서 아래 작업 진행
- 경로로 이동한 후 아래와 같이 가상 환경 생성
	```
	python -m venv .rf_dev
	```
- 가상환경을 활성화
	```
	.\.rf_dev\Script\activate
	```
- 가상환경이 활성화되면 vscode 터미널에서 아래와 같이 표시됨. _아래의 prompt는 항상 표시된다고 가정하고 이후 command 창 명령어에선 생략한다._
	```
	(.rf_dev) PS D:\dev\ragflow_dev>
	```
- 가상환경이 활성화된 상태에서 pip를 이용하여 Jupyter 노트북 실행에 필요한 패키지를 설치한다.
	```
	pip install ipykernel
	```
- 랭체인과 랭그래프 패키지도 설치한다. _이후 필요한 패키지는 해당 패키지가 필요할 때 설치_
	```
	pip install langchain langgraph langfuse openai ragflow-sdk
	```