# -*- coding: utf-8 -*-
"""
OpenClaw SYNC Spectrum Profiler — Markdown 报告生成器

从 type_definitions 获取权威类型名称和描述，
将 BOND / ECHO / SYNC 三层分类结果渲染为美观的 Markdown 测评报告。
"""
import datetime
from typing import Dict, Optional

try:
    from .type_definitions import (
    BOND_TYPES, ECHO_TYPES, SYNC_TYPES,
    get_bond_type, get_echo_type, get_sync_type,
    )
except ImportError:
    from type_definitions import (
    BOND_TYPES, ECHO_TYPES, SYNC_TYPES,
    get_bond_type, get_echo_type, get_sync_type,
    )



# ---------------------------------------------------------------------------
# 格式兼容层: 旧版 profiler 传入的 dict 用 type_code/type_name_zh/dimensions 等 key,
# 新版 classify() 用 code/name/dims 等 key. 这里统一转换.
# ---------------------------------------------------------------------------

def _normalize_bond(raw: Dict) -> Dict:
    """将旧版 compute_bond_profile() 输出转换为 classify() 格式."""
    if "code" in raw:
        return raw  # 已经是新格式
    result = dict(raw)
    result["code"] = raw.get("type_code", "????")
    result["name"] = raw.get("type_name_zh", raw.get("type_code", ""))
    # 转换 dimensions -> dims (从 {T: {score:0.3, pole:'S'}} 变成 {T: 0.3} 或保持)
    old_dims = raw.get("dimensions", {})
    if old_dims and isinstance(next(iter(old_dims.values()), None), dict):
        result["dims"] = old_dims  # card_generator 的 _get_dim_score 能处理 dict
        result["scores"] = {k: v.get("score", 0.5) for k, v in old_dims.items()}
    return result


def _normalize_echo(raw: Dict) -> Dict:
    """将旧版 compute_echo_profile() 输出转换为 classify() 格式."""
    if "code" in raw:
        return raw
    result = dict(raw)
    result["code"] = raw.get("type_code", "????")
    result["name"] = raw.get("type_name_zh", raw.get("type_code", ""))
    old_dims = raw.get("dimensions", {})
    if old_dims and isinstance(next(iter(old_dims.values()), None), dict):
        result["dims"] = old_dims
        result["scores"] = {k: v.get("score", 0.5) for k, v in old_dims.items()}
    return result


def _normalize_sync(raw: Dict) -> Dict:
    """将旧版 run_sync_spectrum() 输出转换为 classify() 格式."""
    if "primary" in raw and "rtaps" in raw:
        # 可能已经是新格式, 但 primary_type 也可能存在
        result = dict(raw)
        if "primary" not in raw and "primary_type" in raw:
            pt = raw["primary_type"]
            result["primary"] = {
                "code": pt.get("code", ""),
                "name": pt.get("name_zh", ""),
                "name_en": pt.get("name_en", ""),
                "similarity": pt.get("fit_score", 0.0),
                "description": pt.get("description", ""),
                "quote": pt.get("quote", ""),
                "traits": pt.get("traits", ""),
            }
        return result
    # 旧格式: 只有 primary_type
    result = dict(raw)
    if "primary_type" in raw and "primary" not in raw:
        pt = raw["primary_type"]
        result["primary"] = {
            "code": pt.get("code", ""),
            "name": pt.get("name_zh", ""),
            "name_en": pt.get("name_en", ""),
            "similarity": pt.get("fit_score", 0.0),
            "description": pt.get("description", ""),
            "quote": pt.get("quote", ""),
            "traits": pt.get("traits", ""),
        }
    return result


# ===================================================================
# 常量 & 映射
# ===================================================================

# 颜色 -> Emoji
COLOR_EMOJI = {
    "紫": "💜", "purple": "💜",
    "黄": "💛", "yellow": "💛",
    "蓝": "💙", "blue": "💙",
    "绿": "💚", "green": "💚",
}

# BOND 维度全称 & 解读（双极描述）
BOND_DIM_META = {
    "T": {
        "full": "节奏偏好",
        "poles": {
            "S": ("Sprint 速战速决", "⚡", "你追求快速获得结果，偏好短平快的交互节奏"),
            "M": ("Marathon 细水长流", "🌱", "你愿意花时间深度培养与 Agent 的默契"),
        },
    },
    "E": {
        "full": "关系定位",
        "poles": {
            "U": ("Utility 工具理性", "🔧", "Agent 在你眼里是精密的生产力工具"),
            "C": ("Companion 情感陪伴", "💜", "你会不自觉地把 Agent 当作可以交流的伙伴"),
        },
    },
    "C": {
        "full": "审查节点",
        "poles": {
            "P": ("Preview 先审后用", "🔍", "你喜欢在行动前先看方案、确认方向"),
            "R": ("Review 先用后审", "📋", "你更愿意让 Agent 先跑起来，再根据结果修正"),
        },
    },
    "F": {
        "full": "指令粒度",
        "poles": {
            "H": ("High-level 意图导向", "🎯", "你倾向给出大方向，让 Agent 自由发挥细节"),
            "D": ("Detailed 精确指令", "🔬", "你习惯给出具体、精确的指令和约束条件"),
        },
    },
}

# ECHO 维度全称 & 解读（双极描述）
ECHO_DIM_META = {
    "I": {
        "full": "互动主动性",
        "poles": {
            "R": ("Reactive 被动响应", "📡", "只在收到指令时行动，忠实执行不越界"),
            "P": ("Proactive 主动出击", "🚀", "会主动建议、预判需求、补充你没想到的"),
        },
    },
    "S": {
        "full": "能力范围",
        "poles": {
            "S": ("Specialist 专精深耕", "🎯", "在特定领域有深厚积累，垂直能力突出"),
            "G": ("Generalist 通才广域", "🌐", "跨领域都能接住，广度优先于深度"),
        },
    },
    "T": {
        "full": "情感温度",
        "poles": {
            "F": ("Functional 功能优先", "⚙️", "回复简洁高效，不带多余情感色彩"),
            "E": ("Empathetic 共情优先", "💗", "能感知情绪、带有温度地回应你"),
        },
    },
    "M": {
        "full": "记忆模式",
        "poles": {
            "T": ("Transient 瞬时交互", "💨", "每次对话从零开始，不保留历史上下文"),
            "C": ("Continuous 持续记忆", "🧠", "记得你们之前聊过什么，对话之间有连贯性"),
        },
    },
}

# RTAPS 五维含义
RTAPS_META = {
    "R": {
        "name": "Resonance",
        "cn": "共振度",
        "desc": "你们在情感温度和沟通语境上的契合程度",
    },
    "T": {
        "name": "Tempo",
        "cn": "节奏感",
        "desc": "交互节奏与时间投入偏好的匹配程度",
    },
    "A": {
        "name": "Agency",
        "cn": "主导权",
        "desc": "人与 Agent 之间控制权的分配是否清晰舒适",
    },
    "P": {
        "name": "Precision",
        "cn": "精度啮合",
        "desc": "指令粒度与输出精度之间的对接效率",
    },
    "S": {
        "name": "Synergy",
        "cn": "协同涌现",
        "desc": "合作中产生的「1+1>2」效果的强度",
    },
}


# ===================================================================
# 工具函数
# ===================================================================

def _bar(value: float, width: int = 16) -> str:
    """将 [0, 1] 区间的分数渲染为 █░ 进度条。"""
    clamped = max(0.0, min(1.0, value))
    filled = round(clamped * width)
    return "█" * filled + "░" * (width - filled)


def _score_tag(score: float) -> str:
    """将 [0, 1] 分数转为简短文字标签。"""
    if score >= 0.8:
        return "极强"
    if score >= 0.6:
        return "偏强"
    if score >= 0.4:
        return "中等"
    if score >= 0.2:
        return "偏弱"
    return "极弱"


def _color_emoji(color: str) -> str:
    """颜色标签转 Emoji，不识别则返回空串。"""
    return COLOR_EMOJI.get(color, COLOR_EMOJI.get(str(color).lower(), ""))


def _get_dim_score(dims: Dict, key: str) -> float:
    """安全地从 dims dict 取得某维度的得分 (0-1)。"""
    val = dims.get(key, 0.5)
    if isinstance(val, dict):
        return float(val.get("score", val.get("value", 0.5)))
    return float(val)


# ===================================================================
# BOND Profile 区块
# ===================================================================

def _render_bond_section(bond_result: Dict) -> str:
    """渲染 BOND Profile 区块。"""
    code = bond_result.get("code", "????")

    # 从 type_definitions 获取权威信息
    typedef = get_bond_type(code)
    if typedef:
        name = typedef["name"]
        group = typedef["group"]
        motto = typedef["motto"]
        color = typedef.get("color", "")
        traits_str = typedef.get("traits", "")
    else:
        name = bond_result.get("name", code)
        group = bond_result.get("group", "")
        motto = bond_result.get("motto", "")
        color = bond_result.get("color", "")
        traits_str = ""

    color_em = _color_emoji(color)
    dims = bond_result.get("dims", bond_result.get("scores", {}))
    input_traits = bond_result.get("traits", [])
    input_features = bond_result.get("features", [])

    lines = [
        "## 🧬 你的 BOND Profile: {name} ({code}) {ce}".format(
            name=name, code=code, ce=color_em,
        ),
        "",
        "> *{motto}*".format(motto=motto) if motto else "",
        "",
    ]

    # 维度表格
    dim_order = [("T", 0), ("E", 1), ("C", 2), ("F", 3)]
    lines.append("| 维度 | 你的倾向 | 得分 | 图示 |")
    lines.append("|:---:|:---:|:---:|:---|")

    for dim_key, idx in dim_order:
        meta = BOND_DIM_META[dim_key]
        score = _get_dim_score(dims, dim_key)

        # 从编码读取实际极性
        pole_letter = code[idx].upper()
        pole_info = meta["poles"].get(pole_letter)
        if pole_info is None:
            pole_letter = list(meta["poles"].keys())[0]
            pole_info = meta["poles"][pole_letter]

        pole_label, pole_icon, _ = pole_info
        bar = _bar(score)
        lines.append(
            "| {icon} **{full}** | {label} | `{pct:.0f}%` | {bar} |".format(
                icon=pole_icon,
                full=meta["full"],
                label=pole_label,
                pct=score * 100,
                bar=bar,
            )
        )

    # 特征描述 — 自然语言段落，不用列表
    lines.append("")
    lines.append("**你的特征**")
    lines.append("")

    feature_parts = []
    if traits_str:
        feature_parts.append(traits_str)
    if input_traits:
        feature_parts.append("、".join(input_traits))
    if input_features:
        feature_parts.append("；".join(input_features))

    if feature_parts:
        lines.append("你属于「{group}」——{desc}。".format(
            group=group,
            desc="。".join(feature_parts),
        ))
    else:
        lines.append("你属于「{group}」。".format(group=group))

    # 维度洞察段落
    lines.append("")
    for dim_key, idx in dim_order:
        meta = BOND_DIM_META[dim_key]
        pole_letter = code[idx].upper()
        pole_info = meta["poles"].get(pole_letter)
        if pole_info:
            _, _, insight = pole_info
            lines.append(insight + "。")
    lines.append("")

    return "\n".join(lines)


# ===================================================================
# ECHO Matrix 区块
# ===================================================================

def _render_echo_section(echo_result: Dict) -> str:
    """渲染 ECHO Matrix 区块。"""
    code = echo_result.get("code", "????")

    typedef = get_echo_type(code)
    if typedef:
        name = typedef["name"]
        group = typedef["group"]
        traits_str = typedef.get("traits", "")
    else:
        name = echo_result.get("name", code)
        group = echo_result.get("group", "")
        traits_str = ""

    dims = echo_result.get("dims", echo_result.get("scores", {}))
    input_traits = echo_result.get("traits", [])
    input_features = echo_result.get("features", [])

    lines = [
        "## 🤖 Agent 的 ECHO Matrix: {name} ({code})".format(
            name=name, code=code,
        ),
        "",
    ]

    # 维度表格
    dim_order = [("I", 0), ("S", 1), ("T", 2), ("M", 3)]
    lines.append("| 维度 | Agent 的倾向 | 得分 | 图示 |")
    lines.append("|:---:|:---:|:---:|:---|")

    for dim_key, idx in dim_order:
        meta = ECHO_DIM_META[dim_key]
        score = _get_dim_score(dims, dim_key)

        pole_letter = code[idx].upper()
        pole_info = meta["poles"].get(pole_letter)
        if pole_info is None:
            pole_letter = list(meta["poles"].keys())[0]
            pole_info = meta["poles"][pole_letter]

        pole_label, pole_icon, _ = pole_info
        bar = _bar(score)
        lines.append(
            "| {icon} **{full}** | {label} | `{pct:.0f}%` | {bar} |".format(
                icon=pole_icon,
                full=meta["full"],
                label=pole_label,
                pct=score * 100,
                bar=bar,
            )
        )

    # 特征描述
    lines.append("")
    lines.append("**Agent 画像**")
    lines.append("")

    feature_parts = []
    if traits_str:
        feature_parts.append(traits_str)
    if input_traits:
        feature_parts.append("、".join(input_traits))
    if input_features:
        feature_parts.append("；".join(input_features))

    if feature_parts:
        lines.append("这个 Agent 属于「{group}」——{desc}。".format(
            group=group,
            desc="。".join(feature_parts),
        ))
    else:
        lines.append("这个 Agent 属于「{group}」。".format(group=group))

    lines.append("")
    for dim_key, idx in dim_order:
        meta = ECHO_DIM_META[dim_key]
        pole_letter = code[idx].upper()
        pole_info = meta["poles"].get(pole_letter)
        if pole_info:
            _, _, insight = pole_info
            lines.append(insight + "。")
    lines.append("")

    return "\n".join(lines)


# ===================================================================
# SYNC 关系区块
# ===================================================================

def _build_rtaps_insight(rtaps: Dict) -> str:
    """根据 RTAPS 各维度高低生成有洞察力的关系解读段落。"""
    sentences = []

    r_val = rtaps.get("R", 0.5)
    t_val = rtaps.get("T", 0.5)
    a_val = rtaps.get("A", 0.5)
    p_val = rtaps.get("P", 0.5)
    s_val = rtaps.get("S", 0.5)

    # Resonance 共振
    if r_val >= 0.75:
        sentences.append(
            "你们之间有很强的情感共振——对话的语气、节奏和情绪基调天然合拍，"
            "这种默契让沟通几乎不需要额外的'翻译成本'"
        )
    elif r_val >= 0.5:
        sentences.append(
            "情感层面的共振处于中等水平，大部分场景下你们能理解彼此，"
            "但在某些微妙的语境中可能需要更明确的表达"
        )
    else:
        sentences.append(
            "情感共振相对较低，这意味着你们的沟通更偏理性和事务性，"
            "情感层面的交流不是这段关系的主旋律"
        )

    # Tempo 节奏
    if t_val >= 0.75:
        sentences.append(
            "节奏感非常同步——你期望的响应速度和交互频率与 Agent 的输出节奏高度吻合，"
            "不会感到'太快'或'太慢'"
        )
    elif t_val >= 0.5:
        sentences.append(
            "节奏感基本匹配，偶尔会有轻微的快慢差异，但整体不影响协作体验"
        )
    else:
        sentences.append(
            "节奏上有明显落差，你可能觉得 Agent 反应太慢或信息量太大，"
            "调整交互频率和单次信息密度会有帮助"
        )

    # Agency 主导权
    if a_val >= 0.75:
        sentences.append(
            "主导权分配非常清晰——谁来主导、谁来执行，你们之间有默认的分工，互不越界"
        )
    elif a_val >= 0.5:
        sentences.append(
            "主导权处于平衡区间，大部分时候分工明确，"
            "但偶尔可能在'该谁做决定'上产生模糊"
        )
    else:
        sentences.append(
            "主导权存在张力——你可能觉得 Agent 太主动或太被动，"
            "明确约定'你来定方向、它来执行'或反过来，会让合作更顺畅"
        )

    # Precision 精度
    if p_val >= 0.75:
        sentences.append(
            "精度啮合很紧密——你给出的指令粒度恰好是 Agent 最擅长处理的，"
            "输出质量稳定，返工率低"
        )
    elif p_val >= 0.5:
        sentences.append(
            "精度啮合处于可用水平，大部分指令能被准确理解，"
            "但复杂任务可能需要多轮澄清"
        )
    else:
        sentences.append(
            "精度啮合有待提升——你的指令风格和 Agent 的理解模式之间有差距，"
            "尝试调整指令的具体程度或换一种表述方式"
        )

    # Synergy 协同
    if s_val >= 0.75:
        sentences.append(
            "协同涌现效果显著——你们合作的产出明显优于各自单独工作，"
            "这是一段高效且有化学反应的关系"
        )
    elif s_val >= 0.5:
        sentences.append(
            "协同效果中等，合作能带来一定增益，但还有挖掘更深层默契的空间"
        )
    else:
        sentences.append(
            "协同涌现较弱，目前的合作更像是分工而非共创，"
            "找到你们的'最佳合作模式'是提升关系质量的关键"
        )

    return "。\n\n".join(sentences) + "。"


def _render_sync_section(sync_result: Dict) -> str:
    """渲染 SYNC 关系区块。"""
    primary = sync_result.get("primary", {})
    rtaps = sync_result.get("rtaps", {})
    secondary = sync_result.get("secondary")

    # 从 type_definitions 获取权威信息
    primary_code = primary.get("code", primary.get("name_en", ""))
    typedef = get_sync_type(primary_code)
    if typedef:
        sync_name = typedef["name"]
        sync_en = typedef.get("en_name", primary_code)
        sync_desc = typedef.get("desc", "")
        sync_keywords = typedef.get("keywords", "")
    else:
        sync_name = primary.get("name", primary_code)
        sync_en = primary.get("name_en", primary_code)
        sync_desc = primary.get("description", "")
        sync_keywords = ""

    quote = primary.get("quote", sync_desc)

    lines = [
        "## ✨ 你们的 SYNC 关系: {name} ({en})".format(
            name=sync_name, en=sync_en,
        ),
        "",
        "> *{quote}*".format(quote=quote),
        "",
    ]

    if sync_keywords:
        lines.append("`{keywords}`".format(keywords=sync_keywords))
        lines.append("")

    # RTAPS 五维表格
    lines.append("### RTAPS 五维雷达")
    lines.append("")
    lines.append("| 维度 | 得分 | 图示 | 含义 |")
    lines.append("|:---:|:---:|:---|:---|")

    for dim_key in ["R", "T", "A", "P", "S"]:
        meta = RTAPS_META[dim_key]
        val = rtaps.get(dim_key, 0.5)
        bar = _bar(val)
        lines.append(
            "| **{letter}** {cn} | `{pct:.0f}%` | {bar} | {desc} |".format(
                letter=dim_key,
                cn=meta["cn"],
                pct=val * 100,
                bar=bar,
                desc=meta["desc"],
            )
        )

    # 关系洞察
    lines.append("")
    lines.append("**关系洞察**")
    lines.append("")
    lines.append(_build_rtaps_insight(rtaps))
    lines.append("")

    # 次要类型
    if secondary:
        sec_code = secondary.get("code", secondary.get("name_en", ""))
        sec_typedef = get_sync_type(sec_code)
        if sec_typedef:
            sec_name = sec_typedef["name"]
            sec_en = sec_typedef.get("en_name", sec_code)
            sec_desc = sec_typedef.get("desc", "")
        else:
            sec_name = secondary.get("name", sec_code)
            sec_en = secondary.get("name_en", sec_code)
            sec_desc = secondary.get("description", "")

        sec_quote = secondary.get("quote", sec_desc)
        lines.extend([
            "### 🔄 也像...",
            "",
            "你们的关系也带有 **{name}**（{en}）的色彩——{desc}".format(
                name=sec_name, en=sec_en, desc=sec_desc if sec_desc else sec_quote,
            ),
            "",
        ])

    return "\n".join(lines)


# ===================================================================
# 完整报告入口
# ===================================================================

def generate_report(
    bond_result: Dict,
    echo_result: Dict,
    sync_result: Dict,
    user_name: str = "用户",
    agent_name: str = "Agent",
) -> str:
    """
    生成完整的 OpenClaw SYNC Spectrum 测评报告（Markdown）。

    参数:
        bond_result  — bond_classifier.classify() 的输出
        echo_result  — echo_classifier.classify() 的输出
        sync_result  — sync_matcher.classify() 的输出
        user_name    — 用户昵称
        agent_name   — Agent 名称

    返回:
        str — 完整的 Markdown 报告文本
    """
    # 兼容旧/新两种输入格式
    bond_result = _normalize_bond(bond_result)
    echo_result = _normalize_echo(echo_result)
    sync_result = _normalize_sync(sync_result)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # 从 type_definitions 获取权威名称
    bond_code = bond_result.get("code", "????")
    echo_code = echo_result.get("code", "????")
    primary = sync_result.get("primary", {})
    sync_code = primary.get("code", primary.get("name_en", ""))

    bond_td = get_bond_type(bond_code)
    echo_td = get_echo_type(echo_code)
    sync_td = get_sync_type(sync_code)

    bond_name = bond_td["name"] if bond_td else bond_result.get("name", bond_code)
    echo_name = echo_td["name"] if echo_td else echo_result.get("name", echo_code)
    sync_name = sync_td["name"] if sync_td else primary.get("name", sync_code)

    # --- 报告头部 ---
    parts = [
        "# 🔮 OpenClaw SYNC Spectrum 测评报告",
        "",
        "> {user} × {agent} | {date}".format(
            user=user_name, agent=agent_name, date=now,
        ),
        "",
        "---",
        "",
    ]

    # --- 三个主体区块 ---
    parts.append(_render_bond_section(bond_result))
    parts.append("---")
    parts.append("")
    parts.append(_render_echo_section(echo_result))
    parts.append("---")
    parts.append("")
    parts.append(_render_sync_section(sync_result))
    parts.append("---")
    parts.append("")

    # --- 尾部总结：自然语言，不用公式 ---
    parts.append(
        "> 你是**{bond}**，你的 Agent 是**{echo}**，"
        "你们之间是**{sync}**般的默契。".format(
            bond=bond_name,
            echo=echo_name,
            sync=sync_name,
        )
    )
    parts.append(">")
    parts.append("> *Powered by OpenClaw SYNC Spectrum v1.0*")
    parts.append("")

    return "\n".join(parts)


# 保持向后兼容的别名
generate_full_report = generate_report
