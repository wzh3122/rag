import re
from typing import Any

from app.agents.prompts import CLARIFICATION_QUESTIONS

DOMAIN_KEYWORDS = {
    "labor": ["工资", "劳动", "公司", "离职", "社保", "加班", "辞退", "劳动合同"],
    "contract": ["合同", "违约", "交付", "定金", "订单", "协议"],
    "marriage_family": ["离婚", "夫妻", "抚养", "彩礼", "婚姻", "共同财产"],
    "tort": ["侵权", "受伤", "赔偿", "事故", "医疗费", "人身损害"],
    "private_lending": ["借钱", "借款", "欠款", "还钱", "利息", "借条"],
    "housing_lease": ["租房", "房租", "押金", "退租", "房东", "租赁"],
    "consumer_rights": ["消费", "退款", "商家", "客服", "质量", "退货"],
}

OUT_OF_SCOPE_KEYWORDS = ["香港", "澳门", "台湾", "美国", "欧盟", "日本", "新加坡", "涉外"]
GENERIC_QUESTIONS = ["怎么办", "能起诉吗", "违法吗", "能赔多少", "怎么处理"]


def extract_facts(
    message: str,
    legal_domain: str | None,
    region: str | None,
    previous_facts: dict[str, Any],
) -> dict[str, Any]:
    domain = legal_domain or infer_domain(message)
    facts: dict[str, Any] = dict(previous_facts)
    facts.update(
        {
            "legal_domain": domain,
            "region": region or previous_facts.get("region"),
            "key_facts": compact_key_facts(message),
            "claims": infer_claims(message),
            "evidence": infer_evidence(message),
        }
    )
    if any(word in message for word in ["拖欠", "欠薪", "没发工资"]):
        facts["wage_payment_status"] = "可能存在工资拖欠"
    if any(word in message for word in ["已经发了", "工资发了", "已支付工资"]):
        facts["wage_payment_status"] = "工资可能已支付"
    return facts


def infer_domain(message: str) -> str:
    scores = {
        domain: sum(1 for keyword in keywords if keyword in message)
        for domain, keywords in DOMAIN_KEYWORDS.items()
    }
    best_domain, best_score = max(scores.items(), key=lambda item: item[1])
    return best_domain if best_score > 0 else "unknown"


def compact_key_facts(message: str) -> list[str]:
    parts = re.split(r"[。！？!?；;\n]+", message)
    return [part.strip() for part in parts if part.strip()][:6]


def infer_claims(message: str) -> list[str]:
    claims = []
    if "赔" in message or "补偿" in message:
        claims.append("要求赔偿或补偿")
    if "离职" in message or "解除" in message:
        claims.append("解除或离职处理")
    if "退款" in message:
        claims.append("退款")
    return claims


def infer_evidence(message: str) -> list[str]:
    evidence = []
    for word in ["合同", "聊天记录", "工资流水", "转账", "发票", "照片", "录音"]:
        if word in message:
            evidence.append(word)
    return evidence


def needs_clarification(message: str, domain: str) -> tuple[bool, list[str], list[str]]:
    normalized = message.strip()
    too_generic = len(normalized) <= 12 or normalized in GENERIC_QUESTIONS
    has_behavior = bool(re.search(r"(拖欠|借|租|离婚|退款|受伤|违约|辞退|欠|打|赔|解除|签)", normalized))
    missing = []
    if domain == "unknown":
        missing.append("legal_domain")
    if not has_behavior:
        missing.append("specific_behavior")
    if too_generic or (domain == "unknown" and not has_behavior):
        return True, CLARIFICATION_QUESTIONS, missing
    return False, [], missing


def detect_out_of_scope(message: str) -> bool:
    return any(keyword in message for keyword in OUT_OF_SCOPE_KEYWORDS)


def detect_conflicts(previous_facts: dict[str, Any], facts: dict[str, Any]) -> list[dict[str, str]]:
    conflicts: list[dict[str, str]] = []
    previous_wage = previous_facts.get("wage_payment_status")
    current_wage = facts.get("wage_payment_status")
    if previous_wage and current_wage and previous_wage != current_wage:
        conflicts.append(
            {
                "field": "wage_payment_status",
                "previous_fact": str(previous_wage),
                "new_fact": str(current_wage),
                "question": "请确认当前争议是仍存在基本工资拖欠, 还是只涉及其他款项或工资已经支付?",
            }
        )
    return conflicts

