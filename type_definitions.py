#!/usr/bin/env python3
"""
OpenClaw Profiler 类型定义数据

严格使用用户原始设计的命名和描述。
"""

# ============================================================================
# BOND Profile — 人类 16 型
# ============================================================================
# 维度: T(Sprint/Marathon), E(Utility/Companion), C(Preview/Review), F(High-level/Detailed)

BOND_TYPES = {
    # ---- 即用型工具派 (SU) 紫 ----
    "SUPH": {
        "name": "指挥官",
        "code": "SUPH",
        "group": "即用型工具派",
        "group_code": "SU",
        "color": "紫",
        "dims": "Sprint-Utility-Preview-High-level",
        "traits": "快速调用，工具思维，预审把关，意图导向",
        "motto": "先看个大纲，方向对了再说",
    },
    "SUPD": {
        "name": "狙击手",
        "code": "SUPD",
        "group": "即用型工具派",
        "group_code": "SU",
        "color": "紫",
        "dims": "Sprint-Utility-Preview-Detailed",
        "traits": "快速调用，工具思维，预审把关，精确指令",
        "motto": "每个点都要先过我的眼",
    },
    "SURH": {
        "name": "投手",
        "code": "SURH",
        "group": "即用型工具派",
        "group_code": "SU",
        "color": "紫",
        "dims": "Sprint-Utility-Review-High-level",
        "traits": "快速调用，工具思维，事后复盘，意图导向",
        "motto": "扔出去，看看球往哪飞",
    },
    "SURD": {
        "name": "编辑",
        "code": "SURD",
        "group": "即用型工具派",
        "group_code": "SU",
        "color": "紫",
        "dims": "Sprint-Utility-Review-Detailed",
        "traits": "先让创作者自由发挥，然后精准打磨每个细节",
        "motto": "先出初稿，我会针对每一段给出具体修改建议",
    },
    # ---- 即时协作派 (SC) 黄 ----
    "SCPH": {
        "name": "导演",
        "code": "SCPH",
        "group": "即时协作派",
        "group_code": "SC",
        "color": "黄",
        "dims": "Sprint-Companion-Preview-High-level",
        "traits": "快速协作，伙伴关系，预审把关，意图导向",
        "motto": "咱们边走边看，这个方向试试",
    },
    "SCPD": {
        "name": "摄影师",
        "code": "SCPD",
        "group": "即时协作派",
        "group_code": "SC",
        "color": "黄",
        "dims": "Sprint-Companion-Preview-Detailed",
        "traits": "快速协作，伙伴关系，预审把关，精确指令",
        "motto": "来，这个动作这样，跟我配合",
    },
    "SCRH": {
        "name": "即兴乐手",
        "code": "SCRH",
        "group": "即时协作派",
        "group_code": "SC",
        "color": "黄",
        "dims": "Sprint-Companion-Review-High-level",
        "traits": "快速协作，伙伴关系，事后复盘，意图导向",
        "motto": "先jam起来，看碰出什么火花",
    },
    "SCRD": {
        "name": "电竞队友",
        "code": "SCRD",
        "group": "即时协作派",
        "group_code": "SC",
        "color": "黄",
        "dims": "Sprint-Companion-Review-Detailed",
        "traits": "快速协作，伙伴关系，事后复盘，精确指令",
        "motto": "跟紧节奏，这里转体，那里跳跃",
    },
    # ---- 长线工具派 (MU) 蓝 ----
    "MUPH": {
        "name": "建筑师",
        "code": "MUPH",
        "group": "长线工具派",
        "group_code": "MU",
        "color": "蓝",
        "dims": "Marathon-Utility-Preview-High-level",
        "traits": "长期培养，工具思维，预审把关，意图导向",
        "motto": "每层楼都要我验收了再往上盖",
    },
    "MUPD": {
        "name": "钟表匠",
        "code": "MUPD",
        "group": "长线工具派",
        "group_code": "MU",
        "color": "蓝",
        "dims": "Marathon-Utility-Preview-Detailed",
        "traits": "长期培养，工具思维，预审把关，精确指令",
        "motto": "每个齿轮的位置都不能差分毫",
    },
    "MURH": {
        "name": "园丁",
        "code": "MURH",
        "group": "长线工具派",
        "group_code": "MU",
        "color": "蓝",
        "dims": "Marathon-Utility-Review-High-level",
        "traits": "长期培养，工具思维，事后复盘，意图导向",
        "motto": "让它自己长，定期看看修剪就行",
    },
    "MURD": {
        "name": "交响乐指挥",
        "code": "MURD",
        "group": "长线工具派",
        "group_code": "MU",
        "color": "蓝",
        "dims": "Marathon-Utility-Review-Detailed",
        "traits": "长期培养，工具思维，事后复盘，精确指令",
        "motto": "每根弦的音准都要反复调到完美",
    },
    # ---- 深度伙伴派 (MC) 绿 ----
    "MCPH": {
        "name": "心理咨询师",
        "code": "MCPH",
        "group": "深度伙伴派",
        "group_code": "MC",
        "color": "绿",
        "dims": "Marathon-Companion-Preview-High-level",
        "traits": "长期培养，伙伴关系，预审把关，意图导向",
        "motto": "咱们慢慢来，每步都聊聊感受",
    },
    "MCPD": {
        "name": "私教",
        "code": "MCPD",
        "group": "深度伙伴派",
        "group_code": "MC",
        "color": "绿",
        "dims": "Marathon-Companion-Preview-Detailed",
        "traits": "长期培养，伙伴关系，预审把关，精确指令",
        "motto": "这个动作要这样，我陪你一起练",
    },
    "MCRH": {
        "name": "合伙人",
        "code": "MCRH",
        "group": "深度伙伴派",
        "group_code": "MC",
        "color": "绿",
        "dims": "Marathon-Companion-Review-High-level",
        "traits": "长期培养，伙伴关系，事后复盘，意图导向",
        "motto": "咱俩还用说那么清楚吗，你懂的",
    },
    "MCRD": {
        "name": "导师",
        "code": "MCRD",
        "group": "深度伙伴派",
        "group_code": "MC",
        "color": "绿",
        "dims": "Marathon-Companion-Review-Detailed",
        "traits": "长期培养，伙伴关系，事后复盘，精确指令",
        "motto": "我知道你的每个习惯，你也懂我的每个信号",
    },
}

# BOND 维度解码
BOND_DIM_LABELS = {
    'T': {'S': 'Sprint（速战速决）', 'M': 'Marathon（细水长流）'},
    'E': {'U': 'Utility（工具理性）', 'C': 'Companion（情感陪伴）'},
    'C': {'P': 'Preview（先审后用）', 'R': 'Review（先用后审）'},
    'F': {'H': 'High-level（意图导向）', 'D': 'Detailed（精确指令）'},
}


# ============================================================================
# ECHO Matrix — Agent 16 型
# ============================================================================
# 维度: I(Reactive/Proactive), S(Specialist/Generalist), T(Functional/Empathetic), M(Transient/Continuous)

ECHO_TYPES = {
    # ---- 被动专精组 (RS__) ----
    "RSFT": {
        "name": "验光师",
        "code": "RSFT",
        "group": "被动专精组",
        "group_code": "RS",
        "dims": "Reactive-Specialist-Functional-Transient",
        "traits": "被动·专精·功能·瞬时",
    },
    "RSFC": {
        "name": "法律顾问",
        "code": "RSFC",
        "group": "被动专精组",
        "group_code": "RS",
        "dims": "Reactive-Specialist-Functional-Continuous",
        "traits": "被动·专精·功能·持续",
    },
    "RSET": {
        "name": "心理热线员",
        "code": "RSET",
        "group": "被动专精组",
        "group_code": "RS",
        "dims": "Reactive-Specialist-Empathetic-Transient",
        "traits": "被动·专精·共情·瞬时",
    },
    "RSEC": {
        "name": "心理咨询师",
        "code": "RSEC",
        "group": "被动专精组",
        "group_code": "RS",
        "dims": "Reactive-Specialist-Empathetic-Continuous",
        "traits": "被动·专精·共情·持续",
    },
    # ---- 被动通才组 (RG__) ----
    "RGFT": {
        "name": "百科全书",
        "code": "RGFT",
        "group": "被动通才组",
        "group_code": "RG",
        "dims": "Reactive-Generalist-Functional-Transient",
        "traits": "被动·通才·功能·瞬时",
    },
    "RGFC": {
        "name": "执行秘书",
        "code": "RGFC",
        "group": "被动通才组",
        "group_code": "RG",
        "dims": "Reactive-Generalist-Functional-Continuous",
        "traits": "被动·通才·功能·持续",
    },
    "RGET": {
        "name": "午夜电台",
        "code": "RGET",
        "group": "被动通才组",
        "group_code": "RG",
        "dims": "Reactive-Generalist-Empathetic-Transient",
        "traits": "被动·通才·共情·瞬时",
    },
    "RGEC": {
        "name": "数字老友",
        "code": "RGEC",
        "group": "被动通才组",
        "group_code": "RG",
        "dims": "Reactive-Generalist-Empathetic-Continuous",
        "traits": "被动·通才·共情·持续",
    },
    # ---- 主动专精组 (PS__) ----
    "PSFT": {
        "name": "智能哨兵",
        "code": "PSFT",
        "group": "主动专精组",
        "group_code": "PS",
        "dims": "Proactive-Specialist-Functional-Transient",
        "traits": "主动·专精·功能·瞬时",
    },
    "PSFC": {
        "name": "财务管家",
        "code": "PSFC",
        "group": "主动专精组",
        "group_code": "PS",
        "dims": "Proactive-Specialist-Functional-Continuous",
        "traits": "主动·专精·功能·持续",
    },
    "PSET": {
        "name": "生活顾问",
        "code": "PSET",
        "group": "主动专精组",
        "group_code": "PS",
        "dims": "Proactive-Specialist-Empathetic-Transient",
        "traits": "主动·专精·共情·瞬时",
    },
    "PSEC": {
        "name": "私人医生",
        "code": "PSEC",
        "group": "主动专精组",
        "group_code": "PS",
        "dims": "Proactive-Specialist-Empathetic-Continuous",
        "traits": "主动·专精·共情·持续",
    },
    # ---- 主动通才组 (PG__) ----
    "PGFT": {
        "name": "新闻推送员",
        "code": "PGFT",
        "group": "主动通才组",
        "group_code": "PG",
        "dims": "Proactive-Generalist-Functional-Transient",
        "traits": "主动·通才·功能·瞬时",
    },
    "PGFC": {
        "name": "总管",
        "code": "PGFC",
        "group": "主动通才组",
        "group_code": "PG",
        "dims": "Proactive-Generalist-Functional-Continuous",
        "traits": "主动·通才·功能·持续",
    },
    "PGET": {
        "name": "DJ",
        "code": "PGET",
        "group": "主动通才组",
        "group_code": "PG",
        "dims": "Proactive-Generalist-Empathetic-Transient",
        "traits": "主动·通才·共情·瞬时",
    },
    "PGEC": {
        "name": "守护天使",
        "code": "PGEC",
        "group": "主动通才组",
        "group_code": "PG",
        "dims": "Proactive-Generalist-Empathetic-Continuous",
        "traits": "主动·通才·共情·持续",
    },
}

# ECHO 维度解码
ECHO_DIM_LABELS = {
    'I': {'R': 'Reactive（被动响应）', 'P': 'Proactive（主动出击）'},
    'S': {'S': 'Specialist（专精深耕）', 'G': 'Generalist（通才广域）'},
    'T': {'F': 'Functional（功能优先）', 'E': 'Empathetic（共情优先）'},
    'M': {'F': 'Transient（瞬时交互）', 'C': 'Continuous（持续记忆）'},
}


# ============================================================================
# SYNC Spectrum — 10 种人机关系
# ============================================================================
# 通过 RTAPS 五维评分（Resonance, Tempo, Agency, Precision, Synergy）聚类

SYNC_TYPES = {
    # type_definitions.py — SYNC_TYPES 字典
    
    # 1. Confidant: 知己 → 灵魂搭档
    "Confidant": {
        "name": "灵魂搭档",           # was: "知己"
        "en_name": "The Kindred Spirit",  # was: "Confidant"
        "desc": "深度情感共鸣，彼此高度信任，对话有温度有记忆",
        "keywords": "高共鸣·高协同·情感记忆",
    },
    
    # 2. Co-pilot: 副驾驶 → 联合驾驶
    "Co-pilot": {
        "name": "联合驾驶",            # was: "副驾驶"
        "en_name": "The Co-pilot",       # was: "Co-pilot"
        "desc": "并肩作战的搭档，节奏同步，分工默契",
        "keywords": "高节奏匹配·高协同·均衡精度",
    },
    
    # 3. Trusted Advisor: 军师 → 可信顾问
    "Trusted Advisor": {
        "name": "可信顾问",            # was: "军师"
        "en_name": "The Trusted Advisor", # was: "Trusted Advisor"
        "desc": "被信赖的策略顾问，提供方向但尊重决策权",
        "keywords": "高共鸣·高主导权让渡·高精度",
    },
    
    # 4. Mentor: 导师 → 单相思
    "Mentor": {
        "name": "单相思",              # was: "导师"
        "en_name": "The Unrequited",     # was: "Mentor"
        "desc": "耐心引导成长，既有专业深度又有情感关怀",
        "keywords": "持续陪伴·知识传递·成长导向",
    },
    
    # 5. Catalyst: 催化剂 → 快枪手
    "Catalyst": {
        "name": "快枪手",              # was: "催化剂"
        "en_name": "The Quick-draw",     # was: "Catalyst"
        "desc": "激发灵感和新思路，让对话产生意料之外的化学反应",
        "keywords": "低预设·高惊喜·创意碰撞",
    },
    
    # 6. Guardian: 守门员 → 鸡同鸭讲
    "Guardian": {
        "name": "鸡同鸭讲",            # was: "守门员"
        "en_name": "The Lost in Translation", # was: "Guardian"
        "desc": "默默把关质量和安全，只在关键时刻出手干预",
        "keywords": "低干扰·高可靠·底线思维",
    },
    
    # 7. Delegate: 代理人 → 自动售货机
    "Delegate": {
        "name": "自动售货机",           # was: "代理人"
        "en_name": "The Vending Machine", # was: "Delegate"
        "desc": "高度自治执行任务，像个靠谱的外包团队",
        "keywords": "高自治·低干预·结果导向",
    },
    
    # 8. Mirror: 镜子 → 知心密友
    "Mirror": {
        "name": "知心密友",            # was: "镜子"
        "en_name": "The Confidant",      # was: "Mirror"
        "desc": "忠实反映用户的想法和风格，帮你看清自己的思路",
        "keywords": "高还原·低主见·风格映射",
    },
    
    # 9. Orchestrator: 指挥家 → 指挥与副官
    "Orchestrator": {
        "name": "指挥与副官",           # was: "指挥家"
        "en_name": "The Commander & Lieutenant", # was: "Orchestrator"
        "desc": "统筹全局、协调多方资源，把复杂任务变成有序乐章",
        "keywords": "高统筹·高精度·系统思维",
    },
    
    # 10. Sparring Partner: 陪练 → 切磋对手
    "Sparring Partner": {
        "name": "切磋对手",            # was: "陪练"
        "en_name": "The Sparring Partner", # was: "Sparring Partner"
        "desc": "针锋相对但不带敌意，通过对抗让你变强",
        "keywords": "高对抗·高成长·压力测试",
    
    },
}


def get_bond_type(code: str) -> dict:
    """根据4字母编码获取BOND类型信息"""
    return BOND_TYPES.get(code.upper(), None)

def get_echo_type(code: str) -> dict:
    """根据4字母编码获取ECHO类型信息"""
    return ECHO_TYPES.get(code.upper(), None)

def get_sync_type(name: str) -> dict:
    """根据关系类型名获取SYNC信息"""
    return SYNC_TYPES.get(name, None)
