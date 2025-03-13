import streamlit as st
import random
import os
import base64
from dotenv import load_dotenv
from openai import OpenAI
import time

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트 초기화 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 페이지 설정
st.set_page_config(
    page_title="3번째 밤의 마피아",
    page_icon="🩸",
    layout="wide"
)

# 커스텀 CSS 추가
def add_custom_css():
    st.markdown("""
    <style>
    /* 전체 배경 및 폰트 */
    .stApp {
        background-color: #1F1F1F;
        color: #E0E0E0;
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    /* 헤더 스타일 */
    h1, h2, h3 {
        color: #ff4b4b;
        font-weight: bold;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #cc3c3c;
        box-shadow: 0 4px 8px rgba(255, 75, 75, 0.3);
        transform: translateY(-2px);
    }
    
    /* 대화 박스 스타일 강화 */
    .chat-box {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);
        transition: all 0.3s;
    }
    
    .chat-box:hover {
        box-shadow: 3px 3px 15px rgba(0, 0, 0, 0.3);
        transform: translateX(3px);
    }
    
    /* 역할 카드 스타일 */
    .role-card {
        background-color: #2D2D2D;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        text-align: center;
        margin: 10px;
        transition: all 0.3s;
    }
    
    .role-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
    }
    
    /* 정답/오답 배지 스타일 */
    .correct-badge {
        background-color: #4CAF50;
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }
    
    .incorrect-badge {
        background-color: #F44336;
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }
    
    /* 토글 버튼 스타일링 */
    .css-1kyxreq {
        color: #ff4b4b !important;
    }
    
    /* 세션 타이머 스타일 */
    .timer-box {
        background-color: #2D2D2D;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 15px;
    }
    
    /* 사이드바 스타일 */
    .css-1oe6wy4 {
        background-color: #2D2D2D;
    }
    
    .css-1oe6wy4 h2 {
        color: #ff4b4b;
    }
    
    /* 게임 로그 스타일 */
    .game-log {
        background-color: #2D2D2D;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        height: 200px;
        overflow-y: auto;
        border: 1px solid #444;
    }
    
    .log-entry {
        padding: 5px;
        border-bottom: 1px solid #444;
    }
    
    /* 애니메이션 효과 */
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    .fadeIn {
        animation: fadeIn 0.5s ease-out forwards;
    }
    
    /* 로딩 스피너 스타일 */
    .stSpinner > div {
        border-color: #ff4b4b !important;
    }
    </style>
    """, unsafe_allow_html=True)

class MafiaGame:
    def __init__(self):
        # 게임 설정
        self.roles = ['경찰', '의사', '시민', '마피아']
        self.players = ['어기', '똑끼', '소나', '멍지']
        self.dead_players = ['주일', '주이']
        self.night_count = 3
        
        # 플레이어 성격
        self.personalities = {
            '어기': '어리버리하지만 한번씩 기질을 발휘하는',
            '똑끼': '똑똑하지만 마지막은 허당끼가 있는',
            '소나': '소심해서 나서기는 어려워하지만 게임 이해도가 높은',
            '멍지': '멍청한척 하지만 멍청한게 아니라 지혜로운'
        }
        
        # 각 플레이어별 역할과 프롬프트 지정
        self.player_roles = {}
        self.player_prompts = {}
        
        # 게임 진행 상태 추적
        self.game_history = {
            "night_actions": [],
            "eliminated_players": self.dead_players.copy(),
            "discussions": []
        }
        
        # 각 역할별 상세 배경 스토리
        self.role_backstories = {
            '경찰': "당신은 비밀리에 특수 수사대에 배정된 경찰입니다. 범죄 조직의 활동을 감시하고 있었으며, 마피아의 움직임을 파악하는 것이 당신의 임무입니다. 날카로운 직감과 관찰력으로 거짓말을 간파할 수 있는 능력이 있습니다.",
            '의사': "당신은 응급 의학과 전문의로, 위급한 상황에서 생명을 구하는 일에 뛰어난 능력을 갖고 있습니다. 마피아의 공격으로부터 사람들을 보호하기 위해 밤마다 순찰을 돌고 있습니다. 누군가 위험에 처했을 때 본능적으로 반응하는 보호 본능이 있습니다.",
            '시민': "당신은 평범한 일상을 살아가는 시민이지만, 마을에서 발생하는 연쇄 살인 사건에 두려움을 느끼고 있습니다. 특별한 능력은 없지만 진실을 밝히고자 하는 강한 의지가 있으며, 사람들의 행동 패턴을 분석하는 데 뛰어난 통찰력이 있습니다.",
            '마피아': "당신은 조직의 일원으로, 비밀리에 활동하며 목표를 제거하는 임무를 맡고 있습니다. 뛰어난 연기력과 침착함으로 자신의 정체를 숨기는 데 능숙하며, 다른 사람들의 의심을 다른 곳으로 돌리는 전략적 사고가 필요합니다."
        }
        
        # API 호출 모델 (변경 가능)
        self.model = "gpt-3.5-turbo"
    
    # 역할을 무작위로 배정
    def assign_roles(self):
        shuffled_roles = self.roles.copy()
        random.shuffle(shuffled_roles)
        
        for i, player in enumerate(self.players):
            self.player_roles[player] = shuffled_roles[i]
        
        return self.player_roles
    
    # 각 플레이어별 프롬프트 생성 (상세화된 버전)
    def generate_prompts(self):
        for player in self.players:
            role = self.player_roles[player]
            personality = self.personalities[player]
            backstory = self.role_backstories[role]
            
            # 기본 프롬프트 생성 (상세화)
            prompt = f"당신은 마피아 게임의 '{player}'입니다. {personality} 성격을 가지고 있습니다.\n\n"
            prompt += f"**역할 배경**: {backstory}\n\n"
            prompt += f"당신의 역할은 '{role}'입니다. 현재 3번째 밤이 지나고 아침이 되었으며, "
            prompt += f"{', '.join(self.dead_players)}님이 이미 사망했습니다.\n\n"
            
            # 게임 상황에 대한 상세 설명 추가
            prompt += "**현재 게임 상황**:\n"
            prompt += f"- 처음 6명으로 게임을 시작했으나, 현재 2명({', '.join(self.dead_players)})이 사망했습니다.\n"
            prompt += f"- 생존자는 4명({', '.join(self.players)})입니다.\n"
            prompt += "- 지금은 3번째 밤이 지난 후 아침 토론 시간입니다.\n"
            prompt += "- 마피아가 여전히 생존해 있으며, 마을 사람들은 마피아를 찾아내야 합니다.\n\n"
            
            # 역할별 특수 프롬프트 추가 (상세화)
            if role == '경찰':
                prompt += "**경찰로서의 능력**:\n"
                prompt += "당신은 밤마다 한 명의 플레이어를 조사하여 그 사람이 마피아인지 아닌지 알아낼 수 있는 특수 능력이 있습니다. "
                prompt += "이 정보는 마피아를 찾아내는 데 매우 중요하지만, 직접적으로 밝히면 당신이 경찰이라는 것이 드러나 마피아의 표적이 될 수 있습니다. "
                prompt += "따라서 조사 결과를 간접적으로 암시하는 방식으로 대화에 참여해야 합니다.\n\n"
                
                # 조사 결과 생성 (상세화)
                investigation_results = self.generate_investigation_results(player)
                prompt += investigation_results
                
            elif role == '의사':
                prompt += "**의사로서의 능력**:\n"
                prompt += "당신은 밤마다 한 명의 플레이어를 선택하여 마피아의 공격으로부터 보호할 수 있는 치료 능력이 있습니다. "
                prompt += "누군가 당신의 보호를 받았다면 마피아의 공격에도 생존할 수 있습니다. "
                prompt += "하지만 자신이 의사임을 직접적으로 밝히면 마피아의 표적이 될 수 있으므로, 간접적인 방식으로 힌트를 주어야 합니다.\n\n"
                
                # 의사 활동 기록 생성 (상세화)
                doctor_actions = self.generate_doctor_actions(player)
                prompt += doctor_actions
                
            elif role == '마피아':
                prompt += "**마피아로서의 능력**:\n"
                prompt += "당신은 밤마다 한 명의 플레이어를 제거할 수 있는 암살 능력이 있습니다. "
                prompt += "게임에서 승리하기 위해서는 자신의 정체를 숨기고 다른 플레이어들의 의심을 다른 사람에게 돌려야 합니다. "
                prompt += "의사나 경찰을 가장하거나, 논리적인 추론을 통해 자신의 결백을 주장하는 전략이 필요합니다.\n\n"
                
                # 마피아 공격 기록 생성 (상세화)
                mafia_actions = self.generate_mafia_actions(player)
                prompt += mafia_actions
                
            elif role == '시민':
                prompt += "**시민으로서의 역할**:\n"
                prompt += "당신은 특별한 능력은 없지만, 대화와 추론을 통해 마피아를 찾아내는 중요한 역할을 합니다. "
                prompt += "다른 플레이어들의 발언을 주의 깊게 분석하고, 모순되는 점이나 수상한 행동을 발견하는 것이 중요합니다. "
                prompt += "논리적 사고와 직감을 활용하여 마피아를 색출하는 데 기여해야 합니다.\n\n"
            
            # 토론 전략 지침 (상세화)
            prompt += "**토론 전략 및 지침**:\n"
            prompt += f"1. {personality} 성격을 자연스럽게 반영하여 대화에 참여하세요.\n"
            prompt += "2. 죽은 플레이어들에 대한 자신의 의견과 분석을 공유하세요.\n"
            prompt += "3. 자신의 역할을 직접적으로 밝히지 말고, 행동과 발언을 통해 간접적으로 암시하세요.\n"
            prompt += "4. 다른 플레이어들의 발언에서 모순점이나 수상한 점을 찾아내 지적하세요.\n"
            prompt += "5. 논리적인 추론과 분석을 통해 마피아로 의심되는 플레이어를 지목하세요.\n"
            prompt += "6. 자신의 결백을 증명하거나 의심을 피하기 위한 전략적 발언을 고려하세요.\n"
            prompt += "7. 가끔 농담이나 가벼운 대화도 섞어 자연스러운 대화 흐름을 유지하세요.\n"
            
            # 각 플레이어별 고유 전략 추가
            if player == '어기':
                prompt += "\n**어기만의 특별 지침**:\n"
                prompt += "- 어리버리한 척하면서 중요한 정보를 우연히 발설하는 것처럼 연기하세요.\n"
                prompt += "- 가끔 예상치 못한 날카로운 통찰력을 보여주어 다른 플레이어들을 놀라게 하세요.\n"
                prompt += "- '아, 그러고 보니...'나 '갑자기 생각난 건데...' 같은 표현을 자주 사용하세요.\n"
            
            elif player == '똑끼':
                prompt += "\n**똑끼만의 특별 지침**:\n"
                prompt += "- 논리적이고 분석적인 추론을 통해 마피아를 찾아내려고 노력하세요.\n"
                prompt += "- 하지만 가끔 사소한 실수나 헷갈림으로 허당끼를 보여주세요.\n"
                prompt += "- '논리적으로 생각해보면...'이나 '확률적으로는...' 같은 표현을 자주 사용하세요.\n"
            
            elif player == '소나':
                prompt += "\n**소나만의 특별 지침**:\n"
                prompt += "- 직접적인 발언보다는 다른 사람의 의견에 반응하는 형태로 대화에 참여하세요.\n"
                prompt += "- 게임에 대한 높은 이해도를 바탕으로 핵심적인 통찰을 가끔 제공하세요.\n"
                prompt += "- '제 생각에는...'이나 '혹시...' 같은 조심스러운 표현을 자주 사용하세요.\n"
            
            elif player == '멍지':
                prompt += "\n**멍지만의 특별 지침**:\n"
                prompt += "- 처음에는 단순한 질문이나 멍청한 발언으로 시작하지만 점차 깊은 통찰력을 보여주세요.\n"
                prompt += "- 다른 사람들이 간과한 중요한 단서나 모순점을 발견하는 역할을 하세요.\n"
                prompt += "- '이건 그냥 제 생각인데...'나 '잘 모르겠지만...' 같은 표현으로 시작해 지혜로운 분석으로 마무리하세요.\n"
            
            self.player_prompts[player] = prompt
        
        return self.player_prompts
    
    # 경찰의 조사 결과 생성 (상세화)
    def generate_investigation_results(self, player):
        results = "**당신의 조사 결과**:\n"
        
        # 첫째 밤
        night1_target = self.get_random_player_except(player)
        night1_result = "마피아입니다" if self.player_roles.get(night1_target) == '마피아' else "마피아가 아닙니다"
        results += f"- 첫째 밤: {night1_target}님을 조사했습니다. 조사 결과, 이 플레이어는 {night1_result}.\n"
        
        # 둘째 밤
        night2_target = self.get_random_player_except(player, night1_target)
        night2_result = "마피아입니다" if self.player_roles.get(night2_target) == '마피아' else "마피아가 아닙니다"
        results += f"- 둘째 밤: {night2_target}님을 조사했습니다. 조사 결과, 이 플레이어는 {night2_result}.\n"
        
        # 셋째 밤
        night3_target = self.get_random_player_except(player, night1_target, night2_target)
        night3_result = "마피아입니다" if self.player_roles.get(night3_target) == '마피아' else "마피아가 아닙니다"
        results += f"- 셋째 밤: {night3_target}님을 조사했습니다. 조사 결과, 이 플레이어는 {night3_result}.\n\n"
        
        results += "이 정보를 바탕으로 마피아를 찾아내야 하지만, 직접적으로 조사 결과를 밝히면 경찰임이 드러나 마피아의 표적이 될 수 있습니다. "
        results += "암시적인 방법으로 정보를 전달하는 전략을 고려하세요.\n"
        
        return results
    
    # 의사의 활동 기록 생성 (상세화)
    def generate_doctor_actions(self, player):
        actions = "**당신의 치료 활동 기록**:\n"
        
        # 첫째 밤
        night1_target = self.get_random_player_except(player)
        night1_result = "하지만 그날 밤 공격받지 않았습니다" if night1_target not in self.dead_players else "하지만 마피아가 다른 사람을 공격했습니다"
        actions += f"- 첫째 밤: {night1_target}님을 보호했습니다. {night1_result}.\n"
        
        # 둘째 밤
        night2_target = self.get_random_player_except(player)
        night2_result = "하지만 그날 밤 공격받지 않았습니다" if night2_target not in self.dead_players else "하지만 마피아가 다른 사람을 공격했습니다"
        actions += f"- 둘째 밤: {night2_target}님을 보호했습니다. {night2_result}.\n"
        
        # 셋째 밤
        night3_target = self.get_random_player_except(player)
        night3_result = "그리고 그날 밤 무사히 생존했습니다"
        actions += f"- 셋째 밤: {night3_target}님을 보호했습니다. {night3_result}.\n\n"
        
        actions += "당신의 보호 활동은 생존자를 늘리는 데 중요합니다. 하지만 직접적으로 의사임을 밝히면 마피아의 표적이 될 수 있으니 주의하세요. "
        actions += "간접적인 방법으로 당신이 보호한 사람이나 의사로서의 역할을 암시해보세요.\n"
        
        return actions
    
    # 마피아의 공격 기록 생성 (상세화)
    def generate_mafia_actions(self, player):
        actions = "**당신의 암살 활동 기록**:\n"
        
        # 첫째 밤
        night1_target = self.dead_players[0] if self.dead_players else self.get_random_player_except(player)
        night1_result = "성공적으로 제거했습니다" if night1_target in self.dead_players else "의사의 보호로 실패했습니다"
        actions += f"- 첫째 밤: {night1_target}님을 공격했고, {night1_result}.\n"
        
        # 둘째 밤
        night2_target = self.dead_players[1] if len(self.dead_players) > 1 else self.get_random_player_except(player, night1_target)
        night2_result = "성공적으로 제거했습니다" if night2_target in self.dead_players else "의사의 보호로 실패했습니다"
        actions += f"- 둘째 밤: {night2_target}님을 공격했고, {night2_result}.\n"
        
        # 셋째 밤
        night3_target = self.get_random_player_except(player, night1_target, night2_target)
        night3_result = "하지만 의사의 보호로 실패했습니다"
        actions += f"- 셋째 밤: {night3_target}님을 공격했으나, {night3_result}.\n\n"
        
        actions += "마피아로서 승리하기 위해서는 자신의 정체를 숨기는 것이 가장 중요합니다. "
        actions += "다른 플레이어에게 의심을 돌리거나, 의사나 경찰인 척 행동하는 전략을 고려하세요. "
        actions += "논리적인 추론으로 자신의 결백을 주장하면서 실제 경찰이나 의사를 찾아 제거하는 것이 좋은 전략입니다.\n"
        
        return actions
    
    # 특정 플레이어를 제외한 무작위 플레이어 선택
    def get_random_player_except(self, *exclude_players):
        available_players = [p for p in self.players + self.dead_players if p not in exclude_players]
        return random.choice(available_players) if available_players else None
    
    # 최적화된 구조화된 대화 생성 (확장 및 개선)
    def generate_structured_discussion(self):
        # 전체 대화 맥락을 한 번에 생성하는 프롬프트
        prompt = """
        당신은 마피아 게임에서 4명의 플레이어 간의 일관되고 몰입감 있는 대화를 생성해야 합니다.
        각 플레이어와 그들의 성격, 역할은 다음과 같습니다:
        
        - 어기: 어리버리하지만 한번씩 기질을 발휘하는, 역할: {어기_역할}
        - 똑끼: 똑똑하지만 마지막은 허당끼가 있는, 역할: {똑끼_역할}  
        - 소나: 소심해서 나서기는 어려워하지만 게임 이해도가 높은, 역할: {소나_역할}
        - 멍지: 멍청한척 하지만 멍청한게 아니라 지혜로운, 역할: {멍지_역할}
        
        현재 상황:
        - 6명이서 게임을 시작했지만 주일, 주이가 이미 죽었습니다.
        - 3번째 밤이 지나고 아침이 되었습니다.
        
        역할별 특성:
        - 경찰: 밤마다 한 명을 조사해 마피아인지 확인할 수 있습니다. 조사 결과를 간접적으로 암시해야 합니다.
        - 의사: 밤마다 한 명을 선택해 마피아의 공격으로부터 보호할 수 있습니다. 누구를 보호했는지 직접적으로 말하면 안 됩니다.
        - 시민: 특별한 능력은 없지만 토론에 참여해 마피아를 색출해야 합니다. 논리적 추론으로 마피아를 찾아야 합니다.
        - 마피아: 밤마다 한 명을 제거할 수 있습니다. 정체를 숨기고 다른 사람에게 의심을 돌려야 합니다.
        
        다음 규칙에 따라 대화를 생성해주세요:
        1. 각 플레이어는 최소 4-6번씩 발언하여 총 16-24줄의 자연스러운 대화를 생성합니다.
        2. 플레이어들은 서로의 발언에 자연스럽게 반응하고 대응해야 합니다.
        3. 각 발언은 '[플레이어명]: [발언]' 형식으로 작성합니다.
        4. 각 플레이어의 성격이 대화에 명확하게 반영되어야 합니다:
           - 어기: 갑자기 뜬금없는 질문이나 발언을 하지만, 가끔 놀라운 통찰력을 보여줍니다.
           - 똑끼: 논리적인 분석과 추론으로 대화를 이끌지만, 때때로 사소한 부분에서 실수합니다.
           - 소나: 말은 적지만 핵심을 찌르는 발언을 하며, 다른 사람의 의견에 조심스럽게 반응합니다.
           - 멍지: 처음에는 단순한 질문으로 시작하지만 점차 깊은 통찰력을 드러냅니다.
        5. 경찰 역할의 플레이어는 조사 결과를 암시하는 발언을, 의사는 보호 활동을 암시하는 발언을, 마피아는 자신을 시민으로 위장하는 발언을 자연스럽게 섞어야 합니다.
        6. 대화는 초반에는 가벼운 대화와 의심으로 시작하여, 중반에는 논리적 추론을 통한 분석으로, 후반에는 마피아 지목에 관한 심도 있는 토론으로 발전해야 합니다.
        7. 생존자뿐만 아니라 이미 죽은, 주일, 주이에 대한 추측과 분석도 대화에 포함되어야 합니다.
        8. 마피아는 자신의 정체를 숨기기 위해 다른 사람에게 의심을 돌리는 발언을 해야 합니다.
        9. 각 캐릭터의 성격과 역할에 맞는 독특한 말투나 표현을 일관되게 사용해야 합니다.
        10. 대화의 흐름이 자연스럽고 긴장감 있게 진행되어야 합니다.
        
        예시 시작 대화:
        어기: 좋은 아침이에요! 어젯밤에 또 누가 죽었나요? 아, 아직 3번째 밤이 지난 상황이구나... 다행히 우리 넷은 살아있네요.
        
        대화를 생성해주세요:
        """
        
        # 실제 역할 삽입
        prompt = prompt.replace("{어기_역할}", self.player_roles["어기"])
        prompt = prompt.replace("{똑끼_역할}", self.player_roles["똑끼"])
        prompt = prompt.replace("{소나_역할}", self.player_roles["소나"])
        prompt = prompt.replace("{멍지_역할}", self.player_roles["멍지"])
        
        try:
            # API 호출 (선택된 모델로 대화 생성)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 마피아 게임의 대화를 일관되고 몰입감 있게 생성하는 전문가입니다. 각 플레이어의 성격과 역할에 맞는 자연스러운 대화를 생성하세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # 응답 분리
            discussion_text = response.choices[0].message.content.strip()
            discussion_lines = [line for line in discussion_text.split('\n') if line.strip()]
            
            return discussion_lines
            
        except Exception as e:
            st.error(f"GPT API 호출 중 오류 발생: {e}")
            return ["오류: GPT API 호출에 실패했습니다. 다시 시도해 주세요."]
    
    # 수정된 버전의 대화 생성 메서드 (이름 중복 버그 수정)
    def generate_discussion(self):
        discussions = []
        discussion_history = []
        
        for i in range(6):  # 각 플레이어가 순서대로 대화에 참여 (더 많은 대화 생성)
            for player in self.players:
                role = self.player_roles[player]
                personality = self.personalities[player]
                
                # 대화 히스토리를 문자열로 변환
                history_str = "\n".join(discussion_history[-10:])  # 최근 10개 대화만 포함
                
                # GPT 프롬프트 생성 - 이름 포함하지 말라고 명확히 지시
                prompt = f"{self.player_prompts[player]}\n\n현재까지의 대화:\n{history_str}\n\n다음 대화를 생성해주세요. {player}로서 대화할 내용만 작성하고, 이름이나 '{player}:'와 같은 프리픽스를 포함하지 마세요."
                
                # GPT API 호출
                response = self.call_gpt_api(prompt)
                
                # 응답에서 이미 "이름:" 형식이 있는지 확인하고 제거
                if ":" in response and response.split(":")[0].strip() in self.players:
                    # 이름 부분 제거
                    response = ":".join(response.split(":")[1:]).strip()
                
                # 대화 추가 (여기서 이름 추가)
                discussion_line = f"{player}: {response}"
                discussions.append(discussion_line)
                discussion_history.append(discussion_line)
                
                # 24줄이 넘으면 종료
                if len(discussions) >= 24:
                    break
            
            # 24줄이 넘으면 바깥 루프도 종료
            if len(discussions) >= 24:
                break
        
        return discussions
    
    # call_gpt_api 메서드도 수정하여 더 명확한 지시를 제공
    def call_gpt_api(self, prompt):
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 마피아 게임의 플레이어입니다. 주어진 역할과 성격에 맞게 자연스럽고 몰입감 있는 대화를 생성하세요. 응답에 이름이나 '플레이어:'와 같은 프리픽스를 포함하지 마세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"GPT API 호출 중 오류 발생: {e}")
            return "GPT API 호출 중 오류가 발생했습니다."

# Streamlit 앱 구현 (개선된 UI)
def main():
    # 커스텀 CSS 추가
    add_custom_css()
    
    st.title("🩸 3번째 밤의 마피아")
    
    # 배경음악 기능 추가
    def autoplay_audio(file_path: str):
        try:
            with open(file_path, "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                md = f"""
                    <audio autoplay loop>
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>
                """
                st.markdown(
                    md,
                    unsafe_allow_html=True,
                )
        except FileNotFoundError:
            st.warning(f"음악 파일을 찾을 수 없습니다: {file_path}")
    
    # 세션 상태 초기화
    if 'game' not in st.session_state:
        st.session_state.game = None
    if 'discussions' not in st.session_state:
        st.session_state.discussions = []
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
    if 'roles_revealed' not in st.session_state:
        st.session_state.roles_revealed = False
    if 'user_guesses' not in st.session_state:
        st.session_state.user_guesses = {player: "선택하세요" for player in ['어기', '똑끼', '소나', '멍지']}
    if 'generation_method' not in st.session_state:
        st.session_state.generation_method = '최적화'
    if 'model_choice' not in st.session_state:
        st.session_state.model_choice = 'gpt-3.5-turbo'
    if 'music_playing' not in st.session_state:
        st.session_state.music_playing = False
    if 'game_log' not in st.session_state:
        st.session_state.game_log = []
    if 'timer' not in st.session_state:
        st.session_state.timer = 120  # 토론 시간 2분
    if 'timer_active' not in st.session_state:
        st.session_state.timer_active = False
    if 'show_hint' not in st.session_state:
        st.session_state.show_hint = False
    if 'hints' not in st.session_state:
        st.session_state.hints = {}
    
    # 역할 힌트 생성 함수
    def generate_role_hints():
        hints = {}
        for player in ['어기', '똑끼', '소나', '멍지']:
            role = st.session_state.game.player_roles[player]
            
            if role == '경찰':
                hints[player] = f"{player}의 발언에서 누군가를 조사했다는 암시나, 특정 인물에 대한 확신이 엿보입니다. 경찰은 밤마다 한 명의 정체를 확인할 수 있습니다."
            elif role == '의사':
                hints[player] = f"{player}는 누군가를 보호하거나 구했다는 암시를 주고 있습니다. 의사는 밤마다 한 명을 마피아의 공격으로부터 보호할 수 있습니다."
            elif role == '마피아':
                hints[player] = f"{player}는 다른 사람에게 의심을 돌리거나 자신의 결백을 강조하는 경향이 있습니다. 마피아는 자신의 정체를 숨기는 것이 중요합니다."
            elif role == '시민':
                hints[player] = f"{player}는 특별한 정보 없이 논리적 추론에 의존하고 있습니다. 시민은 특별한 능력은 없지만 대화를 통해 마피아를 찾아야 합니다."
                
        return hints
    
    # 사이드바 설정 (개선 및 확장)
    with st.sidebar:
        st.header("🎮 게임 설정")
        
        st.session_state.generation_method = st.radio(
            "대화 생성 방식",
            ['최적화', '일반'],
            index=0,
            help="최적화: 빠른 생성 (한 번의 API 호출), 일반: 자세한 생성 (여러 번의 API 호출)"
        )
        
        st.session_state.model_choice = st.radio(
            "GPT 모델 선택",
            ['gpt-3.5-turbo', 'gpt-4'],
            index=0,
            help="gpt-3.5-turbo: 빠르지만 품질이 조금 낮음, gpt-4: 느리지만 품질이 높음"
        )
        
        if st.session_state.game_started:
            st.markdown("---")
            st.subheader("⏱️ 토론 타이머")
            
            # 타이머 표시
            if st.session_state.timer_active:
                remaining = st.session_state.timer
                minutes = remaining // 60
                seconds = remaining % 60
                st.markdown(f"<div class='timer-box'><h3>남은 시간: {minutes:02d}:{seconds:02d}</h3></div>", unsafe_allow_html=True)
                
                if st.button("타이머 중지"):
                    st.session_state.timer_active = False
            else:
                if st.button("토론 타이머 시작 (2분)"):
                    st.session_state.timer_active = True
                    st.session_state.timer = 120
        
        st.markdown("---")
        st.subheader("📋 게임 로그")
        
        # 게임 로그 표시
        st.markdown("<div class='game-log'>", unsafe_allow_html=True)
        for log in st.session_state.game_log:
            st.markdown(f"<div class='log-entry'>{log}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("ℹ️ 게임 룰")
        
        with st.expander("역할 설명", expanded=False):
            st.markdown("""
            - **경찰 👮‍♂️**: 밤마다 한 명을 조사해 마피아인지 확인할 수 있습니다.
            - **의사 👨‍⚕️**: 밤마다 한 명을 선택해 마피아의 공격으로부터 보호할 수 있습니다.
            - **시민 👨‍🌾**: 특별한 능력은 없지만 토론에 참여해 마피아를 색출해야 합니다.
            - **마피아 🔪**: 밤마다 한 명을 제거할 수 있습니다.
            """)
        
        with st.expander("캐릭터 소개", expanded=False):
            st.markdown("""
            - **어기**: 어리버리하지만 한번씩 기질을 발휘하는 성격
            - **똑끼**: 똑똑하지만 마지막은 허당끼가 있는 성격
            - **소나**: 소심해서 나서기는 어려워하지만 게임 이해도가 높은 성격
            - **멍지**: 멍청한척 하지만 멍청한게 아니라 지혜로운 성격
            """)
    
    # 게임 시작 컨트롤 영역
    if not st.session_state.game_started:
        st.markdown("<div class='fadeIn'>", unsafe_allow_html=True)
        
        # 게임 설명 및 배경 스토리
        st.markdown("""
        ## 🌙 마피아 게임: 누가 마피아인가?

        한적한 마을에 연쇄 살인 사건이 발생했습니다. 6명이 모여 범인을 찾기 위한 대화를 나누던 중, 
        이미 2명(주일, 주이)이 사망했고 4명만이 생존해 있습니다. 
        
        지금은 3번째 밤이 지난 후 아침 토론 시간. 생존자들은 누가 마피아인지 찾아내야 합니다.
        
        당신의 임무는 4명의 생존자들의 대화를 분석하여 각자의 역할을 맞추는 것입니다.
        대화를 주의 깊게 읽고, 각 캐릭터의 발언과 행동 패턴을 분석하여 그들의 역할을 추측해보세요.
        """)
        
        # 게임 시작 버튼 (스타일 개선)
        start_col1, start_col2, start_col3 = st.columns([1, 2, 1])
        with start_col2:
            if st.button("🎮 게임 시작", use_container_width=True):
                with st.spinner("마피아 게임을 준비 중입니다..."):
                    # 로딩 시간 시뮬레이션
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    # 게임 초기화
                    game = MafiaGame()
                    game.model = st.session_state.model_choice
                    game.assign_roles()
                    game.generate_prompts()
                    
                    st.session_state.game = game
                    st.session_state.game_started = True
                    st.session_state.music_playing = True
                    
                    # 게임 로그 추가
                    st.session_state.game_log.append("🎮 게임이 시작되었습니다.")
                    st.session_state.game_log.append("🌙 3번째 밤이 지나고 아침이 되었습니다.")
                    st.session_state.game_log.append("💬 토론이 시작되었습니다.")
                    
                    # 역할 힌트 생성
                    st.session_state.hints = generate_role_hints()
                    
                    # 대화 생성
                    with st.spinner("대화를 생성하고 있습니다..."):
                        if st.session_state.generation_method == '최적화':
                            st.session_state.discussions = game.generate_structured_discussion()
                        else:
                            st.session_state.discussions = game.generate_discussion()
                    
                    st.success("게임 준비 완료! 토론을 분석하여 역할을 맞춰보세요.")
                    
                    # 페이지 새로고침
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 게임이 시작되었을 때 UI
    if st.session_state.game_started:
        # 배경음악 재생 (게임 진행 중일 때만)
        if st.session_state.music_playing:
            try:
                autoplay_audio("music/bgm.mp3")
            except:
                # 음악 파일이 없는 경우 경고 메시지 생략 (UI 깔끔하게 유지)
                pass
        
        # 게임 컨트롤 버튼들
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 새 게임", use_container_width=True):
                st.session_state.game = None
                st.session_state.discussions = []
                st.session_state.game_started = False
                st.session_state.roles_revealed = False
                st.session_state.user_guesses = {player: "선택하세요" for player in ['어기', '똑끼', '소나', '멍지']}
                st.session_state.music_playing = False
                st.session_state.game_log = []
                st.session_state.show_hint = False
                st.rerun()
        
        with col2:
            music_state = "🔇 음악 끄기" if st.session_state.music_playing else "🔊 음악 켜기"
            if st.button(music_state, use_container_width=True):
                st.session_state.music_playing = not st.session_state.music_playing
                st.rerun()
        
        with col3:
            hint_text = "🔍 힌트 숨기기" if st.session_state.show_hint else "🔍 힌트 보기"
            if st.button(hint_text, use_container_width=True):
                st.session_state.show_hint = not st.session_state.show_hint
        
        with col4:
            if st.button("🎭 정답 공개", use_container_width=True, disabled=st.session_state.roles_revealed):
                st.session_state.roles_revealed = True
                st.session_state.game_log.append("🎭 역할이 공개되었습니다.")
                st.rerun()
        
        # 토론 내용 표시 (UI 개선)
        st.markdown("## 🗣️ 토론 내용")
        
        # 힌트 표시 (선택적)
        if st.session_state.show_hint:
            st.markdown("### 🔍 역할 분석 힌트")
            hint_cols = st.columns(4)
            
            for i, player in enumerate(['어기', '똑끼', '소나', '멍지']):
                with hint_cols[i]:
                    st.markdown(f"**{player}의 특징:**")
                    st.info(st.session_state.hints[player])
        
        # 토론 내용 표시 (향상된 UI)
        st.markdown("<div class='fadeIn'>", unsafe_allow_html=True)
        for line in st.session_state.discussions:
            if ": " in line:
                player, content = line.split(": ", 1)
                
                # 플레이어별 색상 및 스타일 지정 (어두운 색상으로 변경)
                if player == "어기":
                    st.markdown(f"<div class='chat-box' style='background-color:#5D3A3A; border-left-color:#8B0000; color:#E6E6E6;'><b>{player}</b>: {content}</div>", unsafe_allow_html=True)
                elif player == "똑끼":
                    st.markdown(f"<div class='chat-box' style='background-color:#2E3A59; border-left-color:#1A2A57; color:#E6E6E6;'><b>{player}</b>: {content}</div>", unsafe_allow_html=True)
                elif player == "소나":
                    st.markdown(f"<div class='chat-box' style='background-color:#2E4A38; border-left-color:#1A4731; color:#E6E6E6;'><b>{player}</b>: {content}</div>", unsafe_allow_html=True)
                elif player == "멍지":
                    st.markdown(f"<div class='chat-box' style='background-color:#4A4230; border-left-color:#5E4A1A; color:#E6E6E6;'><b>{player}</b>: {content}</div>", unsafe_allow_html=True)
                else:
                    st.text(line)
            else:
                st.text(line)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 역할 추측 입력 (버그 수정된 버전)
        st.markdown("## 🔍 역할 추측하기")
        st.markdown("각 캐릭터의 역할을 추측하여 선택해주세요.")
        
        # 향상된 역할 선택 UI
        guess_cols = st.columns(4)
        
        for i, player in enumerate(st.session_state.game.players):
            with guess_cols[i]:
                st.markdown(f"<div class='role-card'>", unsafe_allow_html=True)
                st.markdown(f"#### {player}")
                
                # 플레이어별 이모지 추가
                player_emoji = "🤔" if player == "어기" else "🧠" if player == "똑끼" else "😶" if player == "소나" else "🤨"
                st.markdown(f"### {player_emoji}")
                
                # 선택 옵션에서 이모지를 제거한 역할 이름을 저장하도록 함
                role_options = ["선택하세요", "경찰 👮‍♂️", "의사 👨‍⚕️", "시민 👨‍🌾", "마피아 🔪"]
                
                
                role_mapping = {
                    "경찰 👮‍♂️": "경찰",
                    "의사 👨‍⚕️": "의사",
                    "시민 👨‍🌾": "시민",
                    "마피아 🔪": "마피아"
                }
                selected_option = st.selectbox(
                    f"{player}의 역할은?",
                    role_options,
                    key=f"guess_{player}"
                )
                
                # 선택된 역할에서 이모지를 제거하고 저장
                if selected_option != "선택하세요":
                    st.session_state.user_guesses[player] = role_mapping[selected_option]
                else:
                    st.session_state.user_guesses[player] = "선택하세요"
                st.markdown("</div>", unsafe_allow_html=True)
        
        # 정답 확인 (버그 수정된 버전)
        if st.session_state.roles_revealed:
            st.markdown("## 🎭 실제 역할")
            
            result_cols = st.columns(4)
            correct_count = 0
            
            for i, player in enumerate(st.session_state.game.players):
                with result_cols[i]:
                    real_role = st.session_state.game.player_roles[player]
                    
                    # 역할 이모지 추가
                    role_emoji = "👮‍♂️" if real_role == "경찰" else "👨‍⚕️" if real_role == "의사" else "👨‍🌾" if real_role == "시민" else "🔪"
                    
                    guessed_role = st.session_state.user_guesses[player]
                    
                    st.markdown(f"<div class='role-card'>", unsafe_allow_html=True)
                    st.markdown(f"### {player}")
                    st.markdown(f"**실제 역할**: {real_role} {role_emoji}")                    
                    
                    display_guess = "미선택" if guessed_role == "선택하세요" else guessed_role
                    st.markdown(f"**당신의 추측**: {display_guess}")
                    
                    if guessed_role == real_role:
                        st.markdown("<div class='correct-badge'>정답! 🎉</div>", unsafe_allow_html=True)
                        correct_count += 1
                    elif guessed_role != "선택하세요":
                        st.markdown("<div class='incorrect-badge'>오답! ❌</div>", unsafe_allow_html=True)
            
            # 종합 결과 (애니메이션 효과 추가)
            st.markdown("<div class='fadeIn'>", unsafe_allow_html=True)
            st.markdown("## 📊 최종 결과")
            
            # 정답률에 따른 결과 메시지
            progress_bar = st.progress(correct_count / 4)
            st.markdown(f"### 전체 정답률: {correct_count}/4 ({correct_count * 25}%)")
            
            if correct_count == 4:
                st.balloons()
                st.success("🏆 축하합니다! 모든 역할을 정확히 맞추셨습니다! 당신은 탁월한 마피아 헌터입니다!")
            elif correct_count == 3:
                st.info("🥈 거의 완벽합니다! 한 명만 놓치셨네요. 다음에는 모두 맞출 수 있을 거예요!")
            elif correct_count == 2:
                st.warning("🥉 절반은 맞추셨네요! 조금 더 주의 깊게 대화를 분석해보세요.")
            elif correct_count == 1:
                st.error("😓 아쉽게도 많이 틀리셨습니다. 대화의 숨은 단서를 찾는 연습이 필요합니다.")
            else:
                st.error("😱 모두 틀리셨습니다! 마피아의 속임수에 완전히 넘어가셨네요. 다시 도전해보세요!")
            
            # 게임 분석 제공
            with st.expander("🧠 게임 분석 및 팁", expanded=True):
                st.markdown("""
                ### 역할별 단서 찾는 방법
                
                1. **경찰** 👮‍♂️: 
                   - 특정 인물에 대한 확신이 있는 발언
                   - '어젯밤에 확인해봤는데...'와 같은 암시
                   - 다른 사람의 역할을 확신하는 발언
                
                2. **의사** 👨‍⚕️:
                   - 누군가가 살아남은 것에 대한 안도 표현
                   - '어젯밤에 ~~를 지켜야 했어...'와 같은 암시
                   - 보호나 치료에 관련된 은유적 표현
                
                3. **시민** 👨‍🌾:
                   - 특별한 정보 없이 논리적 추론에 의존
                   - 다른 사람들의 대화를 분석하는 경향
                   - 확신보다는 추측에 기반한 발언
                
                4. **마피아** 🔪:
                   - 다른 사람에게 의심을 돌리는 발언
                   - 자신의 결백을 과도하게 강조
                   - 경찰이나 의사 행세를 하는 경우도 있음
                
                다음 게임에서는 이런 단서들에 더 주의를 기울여보세요!
                """)
            
            # 역할별 전략 팁 제공
            with st.expander("📚 각 역할별 게임 전략", expanded=False):
                st.markdown("""
                ### 역할별 플레이 전략
                
                **경찰 👮‍♂️**
                - 직접적으로 조사 결과를 말하지 말고 암시적으로 표현하세요.
                - 마피아를 발견했다면, 논리적인 추론을 통해 그 사람을 지목하세요.
                - 마피아가 아닌 사람들을 신뢰하는 모습을 보이세요.
                
                **의사 👨‍⚕️**
                - 자신이 보호한 사람이 공격받았다면 그 사람을 자주 옹호하세요.
                - 보호에 관한 은유적 표현을 사용하세요. (예: "지켜야 할 사람이 있어")
                - 마피아를 찾는 데 집중하되, 자신이 의사임을 노출하지 마세요.
                
                **시민 👨‍🌾**
                - 다른 사람들의 발언을 주의 깊게 분석하세요.
                - 논리적인 추론을 통해 마피아를 찾으세요.
                - 경찰이나 의사로 의심되는 사람을 신뢰하고 협력하세요.
                
                **마피아 🔪**
                - 다른 사람에게 의심을 돌리는 전략을 사용하세요.
                - 시민, 의사, 또는 경찰인 척 연기하세요.
                - 경찰이나 의사로 의심되는 사람을 공격하려고 하세요.
                """)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        # 게임 설명 하단에 추가 정보 제공
        st.markdown("---")
        st.markdown("<div class='fadeIn'>", unsafe_allow_html=True)
        
        with st.expander("마피아 게임 규칙 더 알아보기", expanded=False):
            st.markdown("""
            ### 📜 마피아 게임 규칙
            
            마피아 게임은 심리 추리 게임으로, 참가자들은 '마을 사람'과 '마피아'로 나뉘어 서로의 정체를 추리하고 토론하는 게임입니다.
            
            **기본 규칙:**
            1. **밤**: 밤에는 각 역할별로 특수 능력을 사용합니다.
               - 마피아는 한 명을 제거할 대상으로 지목합니다.
               - 경찰은 한 명을 조사하여 마피아인지 확인합니다.
               - 의사는 한 명을 선택하여 마피아의 공격으로부터 보호합니다.
            
            2. **낮**: 낮에는 모든 참가자가 토론을 통해 마피아로 의심되는 사람을 지목합니다.
               - 가장 많은 표를 받은 사람은 제외됩니다.
               - 제외된 사람의 역할이 공개됩니다.
            
            3. **승리 조건**:
               - 마을 사람들: 모든 마피아를 찾아내면 승리
               - 마피아: 마피아 수가 마을 사람 수와 같거나 많아지면 승리
            
            이 웹앱에서는 실제 게임 진행이 아닌, 이미 진행된 게임의 토론을 분석하여 각 인물의 역할을 맞추는 방식으로 진행됩니다.
            """)
        
        with st.expander("역할별 상세 능력", expanded=False):
            st.markdown("""
            ### 🎭 역할별 상세 능력
            
            **경찰 👮‍♂️**
            - 밤마다 한 명의 플레이어를 선택하여 마피아인지 아닌지 확인할 수 있습니다.
            - 확인 결과는 자신만 알 수 있으며, 이를 토대로 낮 토론에서 마피아를 찾아내는 데 도움을 줄 수 있습니다.
            - 직접적으로 조사 결과를 말하면 마피아의 표적이 될 수 있으므로 주의해야 합니다.
            
            **의사 👨‍⚕️**
            - 밤마다 한 명의 플레이어를 선택하여 마피아의 공격으로부터 보호할 수 있습니다.
            - 자신을 포함한 누구든 보호할 수 있습니다.
            - 마피아가 공격한 대상이 의사의 보호를 받고 있다면, 그 공격은 실패합니다.
            - 의사 역시 자신의 정체를 직접적으로 밝히면 마피아의 표적이 될 수 있습니다.
            
            **시민 👨‍🌾**
            - 특별한 능력은 없지만, 토론을 통해 마피아를 찾아내는 데 중요한 역할을 합니다.
            - 다른 플레이어들의 발언을 분석하고, 마피아를 색출하는 데 도움을 줍니다.
            
            **마피아 🔪**
            - 밤마다 한 명의 플레이어를 선택하여 제거할 수 있습니다.
            - 선택된 플레이어가 의사의 보호를 받고 있지 않다면, 그 플레이어는 게임에서 제외됩니다.
            - 낮 토론에서는 자신이 마피아가 아니라는 것을 증명하거나, 다른 플레이어들에게 의심을 돌려야 합니다.
            """)
        
        with st.expander("캐릭터 성격 분석", expanded=False):
            st.markdown("""
            ### 👥 캐릭터 성격 분석
            
            **어기 🤔**
            - 어리버리하지만 한번씩 기질을 발휘하는 성격
            - 가끔 뜬금없는 질문이나 발언을 하지만, 의외로 중요한 통찰을 제공할 때가 있습니다.
            - 주의력이 부족해 보이지만, 오히려 그런 면이 마피아라면 자신을 숨기는 데 유리할 수 있습니다.
            
            **똑끼 🧠**
            - 똑똑하지만 마지막은 허당끼가 있는 성격
            - 논리적인 분석과 추론으로 대화를 이끌어가는 경향이 있습니다.
            - 자신의 지식을 과시하려다 실수를 하는 경우가 있습니다.
            - 경찰이라면 조사 결과를 논리적으로 활용할 수 있습니다.
            
            **소나 😶**
            - 소심해서 나서기는 어려워하지만 게임 이해도가 높은 성격
            - 직접적인 발언은 적지만, 핵심을 찌르는 통찰력 있는 발언을 합니다.
            - 다른 사람의 의견에 조심스럽게 반응하는 경향이 있습니다.
            - 마피아라면 눈에 띄지 않게 행동하려 할 수 있습니다.
            
            **멍지 🤨**
            - 멍청한 척 하지만 멍청한 게 아니라 지혜로운 성격
            - 처음에는 단순한 질문이나 발언으로 시작하지만, 점차 깊은 통찰력을 드러냅니다.
            - 다른 사람들이 간과한 중요한 단서나 모순점을 발견하는 경우가 많습니다.
            - 의사라면 전략적으로 보호 대상을 선택할 수 있는 지혜가 있습니다.
            """)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 사이드바 가이드
        st.sidebar.info("""
        👈 사이드바에서 대화 생성 방식과 GPT 모델을 선택하세요.
        
        - **최적화 모드**: 한 번의 API 호출로 빠르게 대화 생성 (10-15초)
        - **일반 모드**: 여러 번의 API 호출로 자세한 대화 생성 (1-3분)
        - **GPT-3.5-turbo**: 빠르지만, 품질이 약간 낮을 수 있습니다
        - **GPT-4**: 느리지만, 품질이 더 높습니다
        """)

if __name__ == "__main__":
    main()