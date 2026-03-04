# -*- coding: utf-8 -*-
"""
通用工具函数：Sigmoid 归一化、置信度计算、分词等
"""
import math
import re
from typing import List, Dict, Optional, Tuple


def sigmoid_normalize(value: float, mu: float, sigma: float) -> float:
    """Sigmoid 归一化到 [0, 1]，mu=中心点，sigma=斜率控制"""
    try:
        return 1.0 / (1.0 + math.exp(-(value - mu) / max(sigma, 1e-6)))
    except OverflowError:
        return 0.0 if value < mu else 1.0


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def tokenize_mixed(text: str) -> List[str]:
    """中英文混合分词（无需jieba，基于规则）"""
    # 英文：按空格/标点分词
    en_words = re.findall(r"[a-zA-Z][a-zA-Z'-]*", text)
    # 中文：按2~4字常用词尝试匹配，退化为逐字
    zh_segments = re.findall(r'[\u4e00-\u9fff]+', text)
    zh_words = []
    for seg in zh_segments:
        # 简单的2字优先切分
        i = 0
        while i < len(seg):
            if i + 2 <= len(seg):
                zh_words.append(seg[i:i+2])
                i += 2
            else:
                zh_words.append(seg[i])
                i += 1
    return [w.lower() for w in en_words] + zh_words


def compute_shannon_diversity(counts: Dict[str, int]) -> float:
    """Shannon 多样性指数 H'，归一化到 [0,1]"""
    total = sum(counts.values())
    if total == 0 or len(counts) <= 1:
        return 0.0
    probs = [c / total for c in counts.values() if c > 0]
    h = -sum(p * math.log(p) for p in probs)
    h_max = math.log(len(counts))
    return h / h_max if h_max > 0 else 0.0


def compute_hhi(counts: Dict[str, int]) -> float:
    """赫芬达尔指数 HHI [0, 1]，1=完全集中"""
    total = sum(counts.values())
    if total == 0:
        return 1.0
    shares = [c / total for c in counts.values()]
    return sum(s * s for s in shares)


def compute_cv(values: List[float]) -> float:
    """变异系数 CV"""
    if not values or len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    if mean == 0:
        return 0.0
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(variance) / mean


def classify_dimension(score: float, threshold: float = 0.5, temperature: float = 0.1) -> Tuple[str, float, float]:
    """
    将连续得分二分为极性 A 或 B
    返回: (pole='A'/'B', confidence, probability_B)
    """
    prob_b = 1.0 / (1.0 + math.exp(-(score - threshold) / max(temperature, 1e-6)))
    pole = 'B' if prob_b >= 0.5 else 'A'
    confidence = max(prob_b, 1 - prob_b)
    return pole, confidence, prob_b
