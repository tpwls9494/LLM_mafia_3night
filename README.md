```markdown
# 마피아 역할 맞추기 게임

OpenAI GPT API와 Streamlit을 활용한 마피아 게임 역할 추측 시뮬레이션입니다. 플레이어들의 대화를 분석하여 각 캐릭터의 역할을 맞추는 게임입니다.



## 📋 목차
- [기능 소개](#기능-소개)
- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)
- [게임 규칙](#게임-규칙)
- [기술 스택](#기술-스택)
- [개발 배경](#개발-배경)
- [라이센스](#라이센스)

## 🎮 기능 소개

- **AI 생성 대화**: OpenAI GPT API를 활용하여 마피아, 경찰, 의사, 시민 역할의 캐릭터 간 대화를 자동 생성합니다.
- **역할 추측**: 생성된 대화를 분석하여 각 캐릭터의 역할을 추측하는 퀴즈 기능을 제공합니다.
- **힌트 시스템**: 필요할 때 각 캐릭터의 역할에 대한 힌트를 제공합니다.
- **게임 결과 분석**: 추측 결과에 따른 점수 계산 및 피드백을 제공합니다.
- **커스텀 UI**: 게임 몰입도를 높이는 시각적 요소와 배경음악을 포함합니다.
- **대화 생성 최적화**: 최적화 모드와 일반 모드를 선택하여 대화 생성 방식을 조절할 수 있습니다.

## 💻 설치 방법

1. 리포지토리 클론
```bash
git clone https://github.com/your-username/mafia-role-guessing-game.git
cd mafia-role-guessing-game
```

2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

3. OpenAI API 키 설정
   - `.env` 파일을 생성하고 다음 내용을 추가하세요:
```
OPENAI_API_KEY=your_api_key_here
```

4. 구현 화면
<img width="1440" alt="mafia_3night" src="https://github.com/user-attachments/assets/cff6100d-2611-46dc-96d6-cfd5aa802a80" />

## 🎲 사용 방법

1. Streamlit 앱 실행
```bash
streamlit run app.py
```

2. 웹브라우저에서 로컬 서버 접속 (기본: http://localhost:8501)

3. "게임 시작" 버튼을 클릭하여 시뮬레이션 시작

4. 생성된 대화를 분석하고 각 캐릭터의 역할 추측

5. "정답 공개" 버튼을 클릭하여 결과 확인

## 📜 게임 규칙

### 역할 설명
- **경찰 👮‍♂️**: 밤마다 한 명을 조사해 마피아인지 확인할 수 있습니다.
- **의사 👨‍⚕️**: 밤마다 한 명을 선택해 마피아의 공격으로부터 보호할 수 있습니다.
- **시민 👨‍🌾**: 특별한 능력은 없지만 토론에 참여해 마피아를 색출해야 합니다.
- **마피아 🔪**: 밤마다 한 명을 제거할 수 있습니다.

### 캐릭터 소개
- **어기**: 어리버리하지만 한번씩 기질을 발휘하는 성격
- **똑끼**: 똑똑하지만 마지막은 허당끼가 있는 성격
- **소나**: 소심해서 나서기는 어려워하지만 게임 이해도가 높은 성격
- **멍지**: 멍청한척 하지만 멍청한게 아니라 지혜로운 성격

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **Backend**: Python
- **AI**: OpenAI GPT API
- **기타 라이브러리**: dotenv, base64

## 💡 개발 배경

이 프로젝트는 인공지능의 대화 생성 능력을 게임화하여 재미있는 방식으로 경험할 수 있도록 개발되었습니다. 마피아 게임의 심리전과 추리 요소를 AI 생성 대화로 재현하여, 플레이어가 대화 패턴을 분석하고 역할을 추측하는 과정에서 AI의 언어 모델링 능력을 경험할 수 있습니다.

## 📝 라이센스

MIT License
```

이 README는 기본적인 틀을 제공합니다. 실제 GitHub 저장소에 맞게 프로젝트 URL, 스크린샷, 정확한 설치 요구사항 등을 조정하세요. 또한 `requirements.txt` 파일을 추가하여 필요한 패키지 목록(streamlit, openai, python-dotenv 등)을 명시하는 것이 좋습니다.
