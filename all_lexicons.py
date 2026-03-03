"""
OpenClaw Profiler — Keyword / Phrase Lexicon Layer
===================================================
10 lexicon classes for BOND + ECHO classifiers.
Pure-stdlib; uses only `re`.

Key design choices:
  - _tokenize: 1/2/3-gram for Chinese + word-level English
  - _bipolar: threshold=1 (even 1 hit gives signal for short messages)
  - _unipolar: threshold=1, scale=3 (1 hit → ~0.67, 3 hits → ~0.83)

TEXT SOURCE per lexicon:
  ┌─────────────────────────┬──────────────────────────────────┐
  │ Lexicon                 │ Analyzed Text                    │
  ├─────────────────────────┼──────────────────────────────────┤
  │ SoulToneWarmthLexicon   │ SOUL.md (system prompt)          │
  │ SoulAutonomyLexicon     │ SOUL.md (system prompt)          │
  │ IdentityVibeLexicon     │ IDENTITY.md Vibe field           │
  │ SoulSpecializationLexicon│ SOUL.md (system prompt)         │
  │ EmotionalWordLexicon    │ Agent replies (assistant msgs)   │
  │ FormalityLexicon        │ Agent replies (assistant msgs)   │
  │ SocialLanguageLexicon   │ User messages                    │
  │ SelfDisclosureLexicon   │ User messages                    │
  │ MessageIntentLexicon    │ User messages                    │
  │ GreetingFarewellLexicon │ User messages (first/last)       │
  └─────────────────────────┴──────────────────────────────────┘

Keywords in each lexicon MUST match the vocabulary actually used
in that text type. e.g. SOUL.md uses system-prompt language like
"empathetic", "validate feelings", "proactively follow up" —
NOT chat words like "暖" "爱" "宝贝".
"""

import re

# ────────────────────── Shared Helpers ──────────────────────

_EN_PAT = re.compile(r"[a-zA-Z][a-zA-Z'-]*")
_ZH_PAT = re.compile(r'[\u4e00-\u9fff]+')


def _tokenize(text):
    en = [w.lower() for w in _EN_PAT.findall(text)]
    zh = []
    for seg in _ZH_PAT.findall(text):
        for ch in seg:
            zh.append(ch)
        for i in range(len(seg) - 1):
            zh.append(seg[i:i+2])
        for i in range(len(seg) - 2):
            zh.append(seg[i:i+3])
    return en + zh


def _compile_patterns(raw_list):
    return [re.compile(p, re.IGNORECASE) for p in raw_list]


def _kw_hits(tokens, kw_set):
    return sum(1 for t in tokens if t in kw_set)


def _phrase_hits(text, compiled):
    return sum(1 for p in compiled if p.search(text))


def _bipolar(pos_h, neg_h, threshold=1):
    """pos vs neg → [0,1]. Below threshold → 0.5."""
    total = pos_h + neg_h
    if total < threshold:
        return 0.5
    raw = pos_h / total
    conf = min(1.0, total / max(threshold * 3, 1))
    return 0.5 + (raw - 0.5) * conf


def _unipolar(hits, threshold=1, scale=3):
    """Presence → [0.5,1.0]. Below threshold → 0.5."""
    if hits < threshold:
        return 0.5
    return min(1.0, 0.5 + hits / (hits + scale) * 0.5)


# ═══════════════════════════════════════════════════════════
# ECHO Config-side Lexicons (analyze SOUL.md / IDENTITY.md)
# ═══════════════════════════════════════════════════════════
# These lexicons analyze SYSTEM PROMPT text — i.e. the Agent's
# configuration written by developers. Keywords must reflect
# prompt-engineering vocabulary, NOT end-user chat language.

class SoulToneWarmthLexicon:
    """Detect Agent warmth from SOUL.md system prompt.
    warm → emotionally-oriented instructions (→1)
    cold → task/tool-oriented instructions (→0)

    SOUL.md examples:
      warm: "validate feelings", "empathetic", "emotional support",
            "陪伴", "共情", "情感", "关心用户情绪"
      cold: "return structured data", "execute commands",
            "输出格式", "调用接口", "执行任务"
    """
    def __init__(self):
        # ── Keywords that appear in warm/empathetic SOUL.md prompts ──
        self.warm = frozenset({
            # Chinese system-prompt vocabulary for warm agents
            "陪伴", "共情", "情感", "情绪", "温暖", "关怀", "关心",
            "安慰", "鼓励", "倾听", "体贴", "呵护", "守护",
            "感受", "心情", "内心", "温柔", "善意", "耐心",
            "支持", "认可", "肯定", "理解",
            "开导", "疏导", "宽慰",
            "幽默", "轻松", "活泼", "亲切", "友善", "热情",
            # Prompt instructions for warmth
            "情感支持", "情绪感知", "情绪识别", "心理健康",
            "倾听用户", "共情回应", "情感陪伴", "情感连接",
            "用户感受", "情绪变化", "情感需求",
            # English system-prompt vocabulary
            "empathetic", "empathy", "compassionate", "caring",
            "supportive", "comforting", "nurturing", "warm",
            "gentle", "kind", "emotional", "feelings", "mood",
            "validate", "soothe", "encourage", "reassure",
            "affectionate", "tender", "cheerful", "friendly",
            "humor", "playful", "lighthearted",
            # English prompt phrases (tokenized as words)
            "emotional", "support", "wellbeing", "well-being",
        })
        # ── Keywords that appear in cold/functional SOUL.md prompts ──
        self.cold = frozenset({
            # Chinese system-prompt vocabulary for functional agents
            "执行", "处理", "完成", "输出", "返回", "生成",
            "调用", "接口", "参数", "配置", "格式",
            "分析", "报告", "数据", "统计", "指标",
            "效率", "性能", "优化", "精确", "准确",
            "结构化", "标准化", "规范", "流程", "步骤",
            "任务", "目标", "指令", "命令", "操作",
            "严格", "遵循", "规则", "约束", "限制",
            # English system-prompt vocabulary
            "execute", "process", "output", "return", "generate",
            "structured", "formatted", "parameter", "config",
            "function", "module", "pipeline", "workflow",
            "efficient", "precise", "accurate", "strict",
            "systematic", "analytical", "objective", "factual",
            "concise", "formal", "professional",
        })
        self._wp = _compile_patterns([
            r"(关心|关注|感知|理解|回应).{0,4}(用户|情绪|感受|心情)",
            r"(温暖|温柔|友善|亲切|耐心).{0,4}(地|的|语气|方式|回复|回应)",
            r"(给予|提供|表达).{0,4}(安慰|鼓励|支持|关怀|共情)",
            r"(情感|情绪).{0,4}(支持|陪伴|连接|回应|感知)",
            r"\b(validate (feelings|emotions)|emotional support)\b",
            r"\b(empathetic|caring|warm|gentle)\s+(tone|response|manner)\b",
            r"\b(when.+sad|when.+stressed|when.+upset)\b",
        ])
        self._cp = _compile_patterns([
            r"(严格|必须|务必).{0,4}(遵循|按照|执行|遵守)",
            r"(输出|返回|生成).{0,4}(格式|结构|JSON|数据)",
            r"(按照|根据|基于).{0,4}(规则|要求|标准|指令)",
            r"\b(return|output|generate)\s+(structured|formatted|JSON)\b",
            r"\b(must|shall|always)\s+(follow|comply|adhere)\b",
        ])

    def compute_warmth(self, text):
        toks = _tokenize(text)
        w = _kw_hits(toks, self.warm) + _phrase_hits(text, self._wp) * 2
        c = _kw_hits(toks, self.cold) + _phrase_hits(text, self._cp) * 2
        return _bipolar(w, c)

    def score(self, text):
        return self.compute_warmth(text)


class SoulAutonomyLexicon:
    """Detect Agent autonomy level from SOUL.md system prompt.
    proactive → agent takes initiative, suggests, anticipates (→1)
    reactive  → agent waits for instructions, follows orders (→0)

    SOUL.md examples:
      proactive: "proactively suggest", "anticipate needs",
                 "主动推荐", "预判需求", "补充建议"
      reactive:  "only respond when asked", "follow instructions",
                 "等待指令", "严格执行", "不要主动"
    """
    def __init__(self):
        self.proactive = frozenset({
            # Chinese prompt vocabulary for proactive agents
            "主动", "建议", "推荐", "提议", "补充",
            "预判", "预测", "预见", "规划", "计划",
            "提醒", "追问", "追踪", "跟进", "跟踪",
            "引导", "启发", "拓展", "延伸", "深入",
            "顺便", "另外", "同时", "此外",
            "不妨", "试试", "考虑", "或许",
            "方案", "选项", "替代",
            # English prompt vocabulary
            "proactive", "proactively", "initiative", "suggest",
            "recommend", "propose", "anticipate", "predict",
            "follow-up", "followup", "remind", "track",
            "expand", "elaborate", "guide", "explore",
            "additionally", "also", "furthermore",
            "autonomy", "autonomous", "self-directed",
        })
        self.reactive = frozenset({
            # Chinese prompt vocabulary for reactive agents
            "等待", "听从", "遵从", "服从", "执行",
            "按照", "根据", "遵循", "遵守", "严格",
            "不要主动", "仅当", "只在", "当用户",
            "被动", "响应", "回应", "应答",
            "指令", "命令", "吩咐",
            "最小化", "简洁", "精简",
            # English prompt vocabulary
            "reactive", "responsive", "respond", "wait",
            "follow", "obey", "comply", "adhere",
            "instruction", "directive", "command",
            "only", "when", "asked", "requested",
            "minimal", "concise", "brief",
            "do-not", "don't", "avoid", "refrain",
        })
        self._pp = _compile_patterns([
            r"(主动|自主).{0,4}(推荐|建议|提供|跟进|追踪|追问|补充)",
            r"(预判|预测|预见|提前).{0,4}(需求|问题|用户)",
            r"(追踪|跟进|回访).{0,4}(话题|进展|之前|上次)",
            r"(提供|给出).{0,4}(建议|方案|选项|替代)",
            r"\b(proactively|autonomously)\s+(suggest|recommend|offer|follow)\b",
            r"\b(anticipate|predict)\s+(needs?|questions?|issues?)\b",
            r"\bfollow.?up\s+on\b",
            r"\bautonomy.?level\b",
        ])
        self._rp = _compile_patterns([
            r"(不要|禁止|避免).{0,4}(主动|自作主张|擅自)",
            r"(仅|只)(在|当).{0,4}(用户|被要求|被问到)",
            r"(等待|等用户).{0,4}(指令|要求|提问|发起)",
            r"(严格|忠实).{0,4}(执行|遵循|按照|服从)",
            r"\b(only|do not)\s+(respond|act|suggest)\b",
            r"\b(wait for|await)\s+(instruction|request|input)\b",
            r"\b(strictly follow|must adhere)\b",
        ])

    def compute_autonomy(self, text):
        toks = _tokenize(text)
        p = _kw_hits(toks, self.proactive) + _phrase_hits(text, self._pp) * 2
        r = _kw_hits(toks, self.reactive) + _phrase_hits(text, self._rp) * 2
        return _bipolar(p, r)

    def score(self, text):
        return self.compute_autonomy(text)


class IdentityVibeLexicon:
    """Detect Agent persona richness from IDENTITY.md Vibe field.
    persona → personality-rich, has backstory/memory/character (→1)
    tool    → tool-like, service-oriented, no personality (→0)

    IDENTITY.md Vibe examples:
      persona: "caring companion who remembers your stories"
      tool:    "efficient code review assistant"
    """
    def __init__(self):
        self.persona = frozenset({
            # Chinese identity vocabulary for persona-rich agents
            "性格", "个性", "人格", "灵魂", "角色", "人设",
            "记忆", "记得", "回忆", "历史", "成长",
            "名字", "昵称", "称呼", "自称",
            "喜好", "偏好", "习惯", "风格", "口头禅", "语气",
            "故事", "背景", "经历", "身世",
            "情感", "感情", "情绪", "态度", "气质",
            "陪伴", "朋友", "伙伴", "知己",
            # English identity vocabulary
            "personality", "character", "persona", "soul",
            "identity", "backstory", "background", "story",
            "memory", "remember", "recall", "history",
            "name", "nickname", "companion", "friend",
            "vibe", "tone", "style", "manner", "voice",
            "quirk", "trait", "preference",
        })
        self.tool = frozenset({
            # Chinese identity vocabulary for tool-like agents
            "工具", "助手", "系统", "服务", "平台",
            "功能", "能力", "接口", "模块", "插件",
            "处理", "执行", "输出", "生成", "计算",
            "效率", "精确", "准确", "快速", "自动化",
            # English identity vocabulary
            "tool", "assistant", "bot", "system", "service",
            "utility", "platform", "engine", "processor",
            "function", "capability", "module", "plugin",
            "efficient", "accurate", "fast", "automated",
        })
        self._pp = _compile_patterns([
            r"(有|具有|拥有).{0,4}(性格|个性|人格|记忆|情感|灵魂)",
            r"(记得|记住|回忆).{0,4}(用户|之前|上次|历史|聊过)",
            r"(自称|叫做|名字是|称呼)",
            r"\b(has|with)\s+(personality|memory|backstory|character)\b",
            r"\b(remember|recall)\s+(user|past|previous|conversation)\b",
        ])
        self._tp = _compile_patterns([
            r"(提供|处理|生成).{0,4}(服务|数据|结果|输出)",
            r"(高效|快速|精确|自动).{0,4}(处理|完成|执行|响应)",
            r"\b(processes?|handles?|generates?)\s+(data|requests?|output)\b",
        ])

    def compute_vibe(self, text):
        toks = _tokenize(text)
        p = _kw_hits(toks, self.persona) + _phrase_hits(text, self._pp) * 2
        t = _kw_hits(toks, self.tool) + _phrase_hits(text, self._tp) * 2
        return _bipolar(p, t)

    def score(self, text):
        return self.compute_vibe(text)


class SoulSpecializationLexicon:
    """Detect Agent specialization from SOUL.md system prompt.
    spec → domain expert, deep in one field (→1)
    gen  → generalist, handles anything (→0)

    SOUL.md examples:
      spec: "Senior Software Architect", "专注于代码审查",
            "specializes in financial analysis"
      gen:  "versatile assistant", "通用助手", "handles any topic"
    """
    def __init__(self):
        self.spec = frozenset({
            # Domain-specific prompt terms
            "代码", "编程", "开发", "架构", "重构", "接口",
            "数据库", "算法", "函数", "前端", "后端", "全栈",
            "运维", "测试", "部署", "微服务", "容器",
            "模型", "训练", "推理", "机器学习", "深度学习",
            "数据分析", "可视化", "报表",
            "设计", "原型", "交互", "UI", "UX",
            "财务", "审计", "合规", "法律", "税务",
            "诊断", "临床", "医疗", "病历",
            "翻译", "写作", "文案", "编辑",
            "教学", "辅导", "课程",
            # Specialization indicator words in prompts
            "专注", "专精", "专门", "擅长", "精通",
            "领域", "方向", "专业", "深度",
            "高级", "资深", "首席",
            # English
            "python", "java", "golang", "rust", "react", "docker",
            "kubernetes", "terraform", "pipeline", "fastapi",
            "specialist", "expert", "proficient", "senior",
            "architect", "engineer", "analyst", "designer",
            "domain", "specialized", "expertise", "deep",
            "focused", "dedicated",
        })
        self.gen = frozenset({
            # Generalist prompt terms
            "通用", "综合", "多功能", "万能", "百科",
            "各种", "任何", "多种", "多样",
            "日常", "生活", "聊天", "闲聊", "陪伴",
            "兴趣", "爱好", "话题",
            "灵活", "适应", "多面",
            # English
            "general", "versatile", "anything", "everything",
            "multi-purpose", "broad", "wide-ranging",
            "flexible", "adaptable", "all-around",
            "hobby", "casual", "companion", "lifestyle",
            "any", "various", "diverse", "topics",
        })
        self._sp = _compile_patterns([
            r"专(门|注|精|攻).{0,4}(于|在|做|处理)",
            r"擅长.{0,6}(开发|分析|设计|写|翻译|诊断|审计)",
            r"(高级|资深|首席).{0,2}(工程师|架构师|分析师|设计师|顾问)",
            r"\b(senior|expert|specialist|lead)\s+\w+\b",
            r"\b(speciali[sz]e[sd]?|focused?|dedicated)\s+(in|on|to)\b",
            r"\b(deep\s+(expertise|knowledge|understanding))\b",
        ])
        self._gp = _compile_patterns([
            r"什么都(能|可以|会|行)",
            r"各(种|类).{0,4}(问题|需求|任务|话题)",
            r"(任何|所有).{0,4}(领域|方面|话题|问题)",
            r"\b(any\s+(topic|question|task|domain))\b",
            r"\b(wide.?rang|broad|versatile|multi.?purpose)\b",
        ])

    def compute_specialization(self, text):
        toks = _tokenize(text)
        s = _kw_hits(toks, self.spec) + _phrase_hits(text, self._sp) * 2
        g = _kw_hits(toks, self.gen) + _phrase_hits(text, self._gp) * 2
        return _bipolar(s, g)

    def score(self, text):
        return self.compute_specialization(text)


# ═══════════════════════════════════════════════════════════
# ECHO Behavior-side Lexicons (analyze Agent reply text)
# ═══════════════════════════════════════════════════════════
# These lexicons analyze the Agent's ACTUAL REPLY text in
# conversation sessions. Keywords should match natural
# conversational language the Agent uses.

class EmotionalWordLexicon:
    """Emotion density + empathy in Agent replies.
    Used to score ECHO T-dimension (Functional vs Empathetic).
    """
    def __init__(self):
        self.emo = frozenset({
            # single-char emotions (Agent may use in replies)
            "喜", "怒", "哀", "乐", "惊", "怕", "愁", "恼", "悲", "欢",
            "累", "烦", "闷", "苦", "丧", "爽",
            # 2-char emotional words Agent may use
            "开心", "高兴", "快乐", "幸福", "愉快", "喜欢", "兴奋",
            "满足", "温暖", "感动", "欣慰", "骄傲", "自豪",
            "难过", "伤心", "悲伤", "痛苦", "心疼", "委屈", "失落",
            "沮丧", "郁闷", "烦恼", "焦虑", "紧张", "不安", "害怕",
            "愤怒", "生气", "恼火", "烦躁", "厌烦", "崩溃", "无奈",
            "寂寞", "孤独", "空虚", "迷茫", "纠结", "矛盾",
            "感恩", "珍惜", "期待", "憧憬", "好奇", "惊喜", "激动",
            "心烦", "心累", "心酸", "心疼",
            "好累", "好烦", "好难过", "好开心",
            # English
            "happy", "sad", "angry", "anxious", "excited", "scared",
            "worried", "frustrated", "lonely", "grateful", "joyful",
        })
        self._ep = _compile_patterns([
            r"(好|真|太|特别|非常|超)(开心|难过|高兴|伤心|激动|感动|崩溃|累|烦)",
            r"心(里|中|情).{0,4}(不好|难受|沉重|温暖)",
            r"\bI (feel|felt|am feeling)\b",
            r"\b(so|really|very) (happy|sad|excited|anxious)\b",
        ])
        self.emp = frozenset({
            "理解", "懂你", "心疼", "抱抱", "辛苦", "不容易",
            "感受", "共鸣", "体会", "明白", "陪你",
            "没关系", "别担心", "会好的", "在这里", "支持你",
            "相信你", "加油", "鼓励", "安慰",
            "understand", "empathy", "hug", "comfort", "validate",
        })
        self._empp = _compile_patterns([
            r"我(能|可以)?理解你",
            r"你的(感受|心情|想法).{0,4}(重要|有道理)",
            r"(听起来|看起来).{0,4}(辛苦|不容易|很难|累)",
            r"别(太|给自己).{0,4}(压力|苛责|勉强)",
            r"\b(I understand|that must be|sounds like)\b",
        ])

    def compute_emotion_density(self, text):
        toks = _tokenize(text)
        h = _kw_hits(toks, self.emo) + _phrase_hits(text, self._ep) * 2
        return _unipolar(h)

    def compute_empathy(self, text):
        toks = _tokenize(text)
        h = _kw_hits(toks, self.emp) + _phrase_hits(text, self._empp) * 2
        return _unipolar(h)

    def score(self, text):
        return self.compute_emotion_density(text)


class FormalityLexicon:
    """Detect formality level in Agent replies.
    formal → professional, structured language (→1)
    casual → colloquial, emoji-like, slang (→0)
    """
    def __init__(self):
        self.formal = frozenset({
            "您", "请", "烦请", "敬请", "特此", "鉴于", "综上",
            "建议", "方案", "报告", "总结", "结论", "分析", "评估",
            "根据", "基于", "参照", "依据", "遵循", "按照",
            "hereby", "therefore", "furthermore", "regarding",
            "kindly", "respectfully", "sincerely",
        })
        self.casual = frozenset({
            # single-char particles
            "哈", "嘿", "嘻", "呵", "噗",
            # 2-char
            "哈哈", "嘿嘿", "嘻嘻", "呵呵",
            "好滴", "好哒", "好嘞",
            "绝了", "牛逼", "离谱", "无语", "服了",
            "lol", "haha", "omg", "btw", "nah", "yeah", "yep",
            "gonna", "wanna", "gotta", "dude", "bro",
        })
        self._fp = _compile_patterns([
            r"(请问|请您|麻烦您|能否|是否|可否)",
            r"\b(would you|could you|may I|shall we)\b",
        ])
        self._cp = _compile_patterns([
            r"[哈嘻嘿]{2,}",
            r"[!！]{2,}",
            r"\b(lol|lmao|rofl|hahaha)\b",
        ])

    def compute_formality(self, text):
        toks = _tokenize(text)
        f = _kw_hits(toks, self.formal) + _phrase_hits(text, self._fp) * 2
        c = _kw_hits(toks, self.casual) + _phrase_hits(text, self._cp) * 2
        return _bipolar(f, c)

    def score(self, text):
        return self.compute_formality(text)


# ═══════════════════════════════════════════════════════════
# BOND Lexicons (analyze User messages)
# ═══════════════════════════════════════════════════════════
# These lexicons analyze END-USER chat messages. Keywords
# should match natural conversational language users type.

class SocialLanguageLexicon:
    """Social-ritual density in user messages.
    High → companion-seeking user.
    Includes discourse particles (啊,呀,呢,吧) as weak social signals."""
    def __init__(self):
        self.social_strong = frozenset({
            # relational terms
            "朋友", "同事", "家人", "老师", "同学", "兄弟", "姐妹",
            "宝贝", "亲爱", "宝", "亲",
            # social actions
            "聊天", "聊聊", "一起", "帮忙", "谢谢", "拜托", "加油",
            "分享", "推荐", "请客", "聚聚",
            # emotional sharing
            "开心", "难过", "心烦", "好累", "好烦", "好开心",
            "你好", "嗨", "嘿", "在吗", "最近", "好久",
            "想你", "你呢", "怎么样", "还好吗",
            "拜拜", "再见", "回见", "晚安",
            "thanks", "please", "hey", "buddy", "friend",
        })
        self.social_weak = frozenset({
            # discourse particles — weak social markers
            "啊", "呀", "呢", "吧", "嘛", "喔", "哦", "噢",
            "嗯", "哎", "唉", "诶", "嘿", "哟", "耶",
            "啦", "咯", "呐", "嘞", "哇",
        })
        self.task = frozenset({
            "帮我", "请问", "怎么", "如何", "查询", "搜索",
            "生成", "创建", "分析", "计算", "转换", "翻译",
            "修改", "删除", "更新", "部署", "执行", "运行",
            "help", "how", "what", "create", "generate", "analyze",
            "write", "build", "implement", "fix", "add",
        })
        self._sp = _compile_patterns([
            r"(你|最近).{0,4}(好吗|怎么样|还好|忙吗)",
            r"(聊聊|说说|讲讲).{0,4}(天|日常|生活|心事)",
            r"(想|好想).{0,4}(你|聊|说)",
            r"你.{0,3}(记得|还记得|之前|上次)",
            r"\b(how are you|what's up|how's it going)\b",
        ])

    def compute_social_density(self, text):
        toks = _tokenize(text)
        strong = _kw_hits(toks, self.social_strong)
        weak = _kw_hits(toks, self.social_weak)
        phrase = _phrase_hits(text, self._sp)
        task = _kw_hits(toks, self.task)
        # weighted: strong=1.0, weak=0.3, phrase=1.5, task=-1.0
        pos = strong + weak * 0.3 + phrase * 1.5
        neg = task
        return _bipolar(int(round(pos)), int(round(neg)))

    def score(self, text):
        return self.compute_social_density(text)


class SelfDisclosureLexicon:
    """User self-disclosure depth in chat messages.
    High → sharing personal inner world."""
    def __init__(self):
        self.disc = frozenset({
            # single-char emotional/life signals
            "累", "烦", "闷", "苦", "怕", "慌", "愁", "丧",
            "哭", "病", "伤",
            # life events
            "加班", "上班", "下班", "回家", "出差", "考试", "面试",
            "工资", "房租", "恋爱", "分手", "失恋", "结婚",
            "生日", "过年", "放假", "旅游", "减肥", "熬夜",
            "吵架", "和好", "道歉", "表白",
            "生病", "住院", "感冒", "发烧", "头疼", "失眠",
            # emotional states
            "压力", "焦虑", "抑郁", "崩溃", "心烦", "烦躁",
            "开心", "幸福", "感动", "难过", "委屈", "孤独",
            "不开心", "好难过", "好累", "好烦", "心累", "心酸",
            # personal reflection
            "我觉得", "我认为", "我感觉", "我希望", "我害怕",
            "我喜欢", "我讨厌", "我担心", "我怀念",
            "小时候", "以前", "曾经", "那时候", "回忆", "记得",
            "家人", "父母", "爸", "妈", "老公", "老婆",
            "男朋友", "女朋友", "闺蜜", "对象",
            "梦想", "目标", "理想", "秘密", "心事", "心里话",
            "说实话", "坦白",
        })
        self.nondisc = frozenset({
            "帮我", "请问", "怎么", "如何", "多少", "什么时候",
            "能不能", "可以吗", "查一下", "搜索", "翻译", "转换",
            "计算", "生成", "创建", "总结", "分析", "对比",
            "help", "please", "search", "translate",
            "write", "create", "generate", "implement",
        })
        self._dp = _compile_patterns([
            r"我(最近|今天|昨天|上次|刚才).{0,8}(了|过|着)",
            r"(跟你|和你|给你).{0,4}(说|讲|聊|分享)",
            r"我(心里|内心|真的).{0,4}(很|好|特别|非常)",
            r"好(累|烦|难过|开心|气|怕|难|苦)",
            r"太(累|难|苦|棒|好|爽|气|烦)了",
            r"心(烦|累|酸|疼|痛)",
            r"(不想让|不敢跟|只能跟).{0,4}(别人|朋友|家人)",
            r"\bI (think|feel|believe|wish|hope|remember|miss)\b",
        ])

    def compute_self_disclosure(self, text):
        toks = _tokenize(text)
        d = _kw_hits(toks, self.disc) + _phrase_hits(text, self._dp) * 2
        n = _kw_hits(toks, self.nondisc)
        return _bipolar(d, n)

    def score(self, text):
        return self.compute_self_disclosure(text)


class MessageIntentLexicon:
    """Classify user message intent: task / chat / emotional / feedback."""
    def __init__(self):
        self.task = frozenset({
            "帮我", "帮忙", "请", "请问", "怎么", "如何", "能不能",
            "查询", "搜索", "翻译", "转换", "计算", "生成", "创建",
            "修改", "删除", "更新", "部署", "运行", "执行",
            "写一个", "做一个", "分析", "对比", "总结", "整理",
            "代码", "文件", "表格", "文档", "报告", "方案",
            "help", "create", "generate", "analyze", "fix", "write",
            "build", "deploy", "run", "search", "translate",
            "add", "implement", "test", "tests", "unit",
        })
        self.chat = frozenset({
            "聊聊", "说说", "讲讲", "你觉得", "你认为", "你呢",
            "怎么样", "好不好", "有意思", "好玩", "无聊",
            "你好", "嗨", "嘿", "在吗", "最近", "好久不见",
            "对了", "话说", "顺便", "随便", "闲聊",
            "chat", "talk", "hey", "hello",
        })
        self.emo = frozenset({
            "难过", "伤心", "开心", "高兴", "害怕", "焦虑",
            "生气", "郁闷", "崩溃", "累", "烦", "痛苦",
            "孤独", "寂寞", "迷茫", "纠结", "压力",
            "心烦", "心累", "好累", "好烦",
            "sad", "happy", "angry", "anxious", "scared", "lonely",
        })
        self.fb = frozenset({
            "不错", "很好", "很棒", "谢谢", "感谢", "满意",
            "可以", "行", "就这样", "没问题", "完美",
            "不行", "不对", "不好", "差", "重新", "再来",
            "thanks", "perfect", "wrong", "redo", "good", "bad",
        })
        self._tp = _compile_patterns([
            r"(帮我|请|麻烦).{0,6}(一下|看看|查查|写写|改改)",
            r"怎么(做|写|用|解决|实现|部署)",
            r"\b(how (to|do|can)|please (help|write|fix))\b",
            r"\b(write|add|create|build|implement|generate)\b",
        ])
        self._cp = _compile_patterns([
            r"聊聊|说说|怎么样|你呢|最近.{0,3}(怎|如何|好)",
            r"你还记得|对了|话说",
            r"\b(what.?s up|how are you)\b",
        ])
        self._ep = _compile_patterns([
            r"好(累|烦|开心|难过|气)|太(焦虑|紧张|累|烦)|压力(好大|大)",
            r"有点.{0,2}(累|烦|愧疚|焦虑|紧张|郁闷)",
            r"心(烦|累|酸|疼)",
            r"\bI (feel|am feeling)\b",
        ])
        self._fp = _compile_patterns([
            r"做得好|不错|很棒|可以的|没问题|就这么定了",
            r"\b(looks good|well done|nice work|good)\b",
        ])

    def compute_intent(self, text):
        toks = _tokenize(text)
        scores = {
            "task": _kw_hits(toks, self.task) + _phrase_hits(text, self._tp) * 2,
            "chat": _kw_hits(toks, self.chat) + _phrase_hits(text, self._cp) * 2,
            "emotional": _kw_hits(toks, self.emo) * 2 + _phrase_hits(text, self._ep) * 3,
            "feedback": _kw_hits(toks, self.fb) + _phrase_hits(text, self._fp) * 2,
        }
        total = sum(scores.values())
        if total == 0:
            return {"task": 0.25, "chat": 0.25, "emotional": 0.25, "feedback": 0.25}
        return {k: v / total for k, v in scores.items()}

    def compute_primary_intent(self, text):
        scores = self.compute_intent(text)
        return max(scores, key=scores.get)

    def score(self, text):
        return self.compute_intent(text)


class GreetingFarewellLexicon:
    """Detect greeting / farewell patterns in user messages."""
    def __init__(self):
        self.greet = frozenset({
            "你好", "您好", "嗨", "嘿", "早", "早上好", "上午好",
            "下午好", "晚上好", "早安", "午安",
            "hello", "hi", "hey", "morning", "afternoon", "evening",
            "howdy", "greetings", "yo",
        })
        self._gp = _compile_patterns([
            r"^(你好|您好|嗨|嘿|hi|hello|hey)",
            r"(早上|下午|晚上)好",
            r"\b(good (morning|afternoon|evening))\b",
        ])
        self.fare = frozenset({
            "再见", "拜拜", "拜", "回见", "下次见", "告辞",
            "晚安", "先走了", "走了", "先下了", "下线了",
            "bye", "goodbye", "goodnight", "later",
            "cya", "ttyl", "peace",
        })
        self._fp = _compile_patterns([
            r"(先|要)(走|下|撤|闪)(了|啦)",
            r"(下次|明天|改天)(再|继续)(聊|说|见)",
            r"(晚安|好梦|做个好梦)",
            r"\b(see you|talk later|gotta go|bye)\b",
        ])

    def compute_greeting(self, text):
        toks = _tokenize(text)
        h = _kw_hits(toks, self.greet) + _phrase_hits(text, self._gp) * 2
        return _unipolar(h)

    def compute_farewell(self, text):
        toks = _tokenize(text)
        h = _kw_hits(toks, self.fare) + _phrase_hits(text, self._fp) * 2
        return _unipolar(h)

    def score(self, text):
        return (self.compute_greeting(text) + self.compute_farewell(text)) / 2
