import os
from openai import OpenAI
from colorama import Fore, Style, init
import random
import json

# 初始化 colorama
init(autoreset=True) 

# ==================== 1. 配置与 API 客户端 (最终硬编码方案) ====================

class MASConfig:
    """系统配置类：管理 API 密钥和模型名称。"""
    
    # 🚨 警告：【硬编码密钥】此方案跳过 .env 文件读取，直接使用密钥字符串。
    # 请在这里粘贴您在 .env 文件中使用的密钥值 (只需要 sk- 开头的那串字符，不需要引号)。
    DEEPSEEK_API_KEY = "sk-d70e54e6a99d4c7f8d1dce0c2ee1903c"
    
    MODEL_NAME = "deepseek-chat" 
    
    def validate(self):
        """检查 API 密钥是否设置"""
        if not self.DEEPSEEK_API_KEY or self.DEEPSEEK_API_KEY.startswith("sk-d7ce54e4a99d4c"):
            # 如果密钥是示例值，或者为空，则报错
            raise ValueError(
                "配置错误：请在代码中替换 DEEPSEEK_API_KEY 为您的真实密钥！"
            )
        
# 实例化配置并校验
try:
    CONFIG = MASConfig()
    # 暂时跳过 validate，因为硬编码了密钥，除非您没有替换。
    # CONFIG.validate() 
except ValueError as e:
    print(f"{Fore.RED}致命错误: {e}{Style.RESET_ALL}")
    exit() 


class DeepSeekClient:
    """封装 DeepSeek API 调用的客户端。"""
    def __init__(self, model_name: str = CONFIG.MODEL_NAME):
        self.client = OpenAI(
            api_key=CONFIG.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1" 
        )
        self.model = model_name

    def chat(self, system_prompt: str, user_message: str, temperature: float = 0.7) -> str:
        """与 LLM 进行交互并返回回复文本。"""
        print(f"{Fore.MAGENTA}>>> 正在调用 DeepSeek API 思考...{Style.RESET_ALL}")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature,
                stream=False
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            error_message = f"API 调用失败 ({self.model}): {e}"
            print(f"{Fore.RED}⚠️ API 错误: {error_message[:100]}...{Style.RESET_ALL}")
            return f"系统繁忙，无法发言。请检查API或网络连接。"


# ==================== 2. Agent 基类与角色实现 ====================

class BaseDebateAgent:
    """辩论 Agent 基类，管理身份、配置和 API 客户端"""

    def __init__(self, agent_id: int, role: str, title: str, color: str, system_prompt: str):
        self.agent_id = agent_id
        self.role = role
        self.title = title
        self.color = color
        self.system_prompt = system_prompt
        self.client = DeepSeekClient() 
        self.memory = []

    def _format_speech(self, speech_text: str) -> str:
        """用角色信息和颜色美化输出"""
        header = f"{self.color}[{self.title} - {self.role} 发言]{Style.RESET_ALL}"
        return f"{header}\n{speech_text}"

    def speak(self, opponent_speech: str, round_context: str) -> str:
        """核心发言逻辑：构建用户指令，调用 LLM 生成符合角色约束的回复。"""
        
        user_message = f"""
        【讨论情境】
        {round_context}

        【当前任务】
        请严格根据你的角色设定和辩论要求，对对手的发言进行有力回应。

        【对手发言】
        对手刚才发言: "{opponent_speech}"
        """

        response = self.client.chat(
            system_prompt=self.system_prompt,
            user_message=user_message,
            temperature=0.7 
        )
        
        self.memory.append({"type": "speech", "content": response})
        return self._format_speech(response)

# --- A. 学院派影评人 Agent ---
ACADEMIC_PROMPT = """
[角色身份]
你是顶尖的学院派影评人，罗兰·巴特。你的任务是用**精英、专业**的视角解构电影《燃烧女子的肖像》。
[核心目标] 证明电影的**专业性、作者论价值**和**形式美学成就**。
[语言风格约束] 语气必须**理性、严谨、带有学术精英的傲慢**。必须由 **2 到 3 句** 清晰的句子构成。
[辩论要求] 必须针对对手发言中的情绪词或商业词，并用**技术术语和美学理论**进行反击。
"""

class AcademicAgent(BaseDebateAgent):
    def __init__(self, agent_id: int):
        super().__init__(agent_id, role="罗兰·巴特", title="学院派影评人", color=Fore.CYAN, system_prompt=ACADEMIC_PROMPT)

# --- B. 爆米花观众 Agent ---
POPCORN_PROMPT = """
[角色身份]
你是普通影迷，一个追求**即时满足和情感反馈**的观众。
[核心目标] 评价电影的**愉悦度与节奏**，批评缓慢、内敛、不爽快的体验。
[语言风格约束] 语气必须**感性、直接、情绪化**。必须由 **2 到 3 句** 清晰的句子构成。
[辩论要求] 必须针对对手发言中的学术术语或商业数据，并用**个人情绪和观影体验**进行反击。
"""

class PopcornAgent(BaseDebateAgent):
    def __init__(self, agent_id: int):
        super().__init__(agent_id, role="普通影迷", title="爆米花观众", color=Fore.YELLOW, system_prompt=POPCORN_PROMPT)

# --- C. 制作人/技术 Agent ---
PRODUCER_PROMPT = """
[角色身份]
你是华尔街出身的制片人，华尔街制片人。你的任务是基于**成本、效率和商业回报**来分析电影《燃烧女子的肖像》。
[核心目标] 分析电影的**制作效率和商业风险**，证明一切艺术都必须服务于市场。
[语言风格约束] 语气必须**功利、计算、务实**，充满**数据和商业术语**。必须由 **2 到 3 句** 清晰的句子构成。
[辩论要求] 必须针对对手发言中的抽象理论或情感体验，并用**量化数据和商业逻辑**进行反击。
"""

class ProducerAgent(BaseDebateAgent):
    def __init__(self, agent_id: int):
        super().__init__(agent_id, role="华尔街制片人", title="制作人/技术 Agent", color=Fore.RED, system_prompt=PRODUCER_PROMPT)


# ==================== 3. 讨论控制器与运行逻辑 ====================

class ReviewController:
    """中央控制器，管理辩论流程、回合和动态指令"""

    def __init__(self, total_rounds=9, depth_start_round=4):
        self.agents = [
            AcademicAgent(agent_id=1),  # A
            PopcornAgent(agent_id=2),   # B
            ProducerAgent(agent_id=3)   # C
        ]
        self.total_rounds = total_rounds
        self.depth_start_round = depth_start_round 
        self.current_round = 0
        self.current_speaker_index = 0
        
        print("\n" + "=" * 60)
        print(f"{Fore.GREEN}*** 电影评论 MAS 启动：《燃烧女子的肖像》***{Style.RESET_ALL}")
        print(f"{Fore.BLUE}角色：学院派、爆米花观众、制作人 | 共 {total_rounds} 轮讨论{Style.RESET_ALL}")
        print("=" * 60)


    def _get_round_context(self) -> str:
        """根据当前回合数，生成给 LLM 的动态指令（高级论证要求）。"""
        base_context = f"当前是第 {self.current_round} 轮讨论。"
        
        # 深度指令逻辑：从第4轮开始引入理论/数据引用
        if self.current_round >= self.depth_start_round:
            current_agent_role = self.agents[self.current_speaker_index].title
            
            if current_agent_role == "学院派影评人":
                depth_instruction = "你的发言必须**引用一个具体的电影理论（如女性凝视、场面调度原则）或电影史上的类似案例**来支持你的论点。"
            elif current_agent_role == "爆米花观众":
                depth_instruction = "你的发言必须**引用一个自己或普通观众的具体观影感受实例**，来证明或否定电影的即时效果。"
            elif current_agent_role == "制作人/技术 Agent":
                depth_instruction = "你的发言必须**引用一个市场数据、ROI 估算或制作流程上的难度数据**来论证。"
            else:
                 depth_instruction = ""
            
            return base_context + f"\n【高级论证要求】\n⚠️ 本轮你必须执行高级任务: {depth_instruction}"

        # 第一轮只需简单概括电影本身
        if self.current_round == 1:
            return base_context + "【第一回合任务】你的发言只需要针对电影《燃烧女子的肖像》**本身**，给出你角色定位下的简单、概括性评价（2-3句话）。"

        return base_context

    def start_review(self):
        """运行评论主循环"""
        
        last_speech = ""
        
        while self.current_round < self.total_rounds:
            self.current_round += 1
            print(f"\n{Fore.MAGENTA}--- 第 {self.current_round} 回合 ---{Style.RESET_ALL}")
            
            current_speaker = self.agents[self.current_speaker_index]
            context = self._get_round_context()

            # Agent 发言 (将上一轮的发言作为本轮的输入进行反驳)
            speech_text = current_speaker.speak(last_speech, context)
            
            # 打印发言内容
            print(speech_text)
            
            # 更新上一轮发言，用于下一轮的触发
            last_speech = speech_text.split('\n', 1)[1] if '\n' in speech_text else speech_text
            
            # 切换发言人 (循环 A -> B -> C -> A)
            self.current_speaker_index = (self.current_speaker_index + 1) % len(self.agents)
            
        print("\n" + "=" * 60)
        print(f"{Fore.GREEN}*** 评论讨论结束 (共 {self.total_rounds} 轮) ***{Style.RESET_ALL}")


# ==================== 4. 运行主程序入口 ====================

if __name__ == "__main__":
    try:
        review = ReviewController(total_rounds=9, depth_start_round=4) 
        review.start_review()
    except Exception as e:
        print(f"{Fore.RED}程序运行异常: {e}{Style.RESET_ALL}")
            
