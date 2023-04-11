# ChatGPT 채팅

OpenAI의 GPT-3 모델을 사용하는 간단한 채팅 애플리케이션입니다.

## 설치

아래 명령어를 사용하여 필요한 패키지를 설치합니다:

```bash
pip install -r requirements.txt
```


또한 다음 내용으로 `key.yaml` 파일을 프로젝트의 루트 디렉토리에 생성해야 합니다:

```bash
key: test     # 토큰
apiKey: ""    # OpenAI API 키
flaskKey: ""  # Flask 비밀 키
```

빈 문자열을 자신의 설정에 맞는 값으로 바꿔주세요.

## 사용

애플리케이션을 시작하려면 다음 명령어를 실행하세요:
```
python chat.py
```

웹 브라우저에서 http://localhost:5000 주소로 접속하면 애플리케이션을 사용할 수 있습니다.