from typing import Any

from app.agents.prompts import DISCLAIMER
from app.api.schemas import LegalSource


def generate_general_reference_answer(
    message: str,
    facts: dict[str, Any],
    region: str | None,
) -> str:
    region_note = "当前问题可能受地区规则或当地实践影响, 建议核实当地主管机关、法院规则或律师意见。" if region else ""
    return (
        "一、当前依据状态\n"
        "当前法规库尚未检索到可支撑具体法律结论的可靠来源, 以下仅为一般处理思路, 不引用具体法条、案例或 URL。\n\n"
        "二、一般处理思路\n"
        "可以先梳理双方关系、争议发生经过、关键时间点、沟通记录和已经采取的措施, 再判断是否需要协商、投诉、调解、仲裁或诉讼等路径。"
        f"{region_note}\n\n"
        "三、建议补充的信息\n"
        "建议补充双方身份关系、争议发生时间、金额或标的、是否有书面材料、是否已经通知对方以及希望达到的结果。\n\n"
        "四、建议整理的证据\n"
        f"{evidence_tips(facts.get('legal_domain', 'unknown'))}\n\n"
        "五、免责声明\n"
        f"{DISCLAIMER}"
    )


def generate_completed_answer(
    message: str,
    facts: dict[str, Any],
    sources: list[LegalSource],
    region: str | None,
) -> str:
    source_lines = []
    for index, source in enumerate(sources, start=1):
        source_lines.append(
            f"[{index}] 标题: {source.title}\n"
            f"来源: {source.source or ''}\n"
            f"URL: {source.url or ''}\n"
            f"权威等级: {source.authority_level}\n"
            f"现行有效性: {source.effective_status}\n"
            f"引用片段: {source.quote_text or source.snippet or ''}\n"
            f"用途: {source.used_for or ''}"
        )
    return (
        "一、结论摘要\n"
        "基于当前检索来源, 可作初步法律信息分析, 但仍需结合完整证据核实。\n\n"
        "二、事实归纳\n"
        f"{'; '.join(facts.get('key_facts', [])) or message}\n\n"
        "三、争议焦点\n"
        "需要判断对方行为、证据完整性、责任承担方式和处理路径。\n\n"
        "四、法律依据\n"
        "以下依据仅限已列明来源, 不扩展引用未检索到的法条或案例。\n\n"
        "五、法律分析\n"
        "应将用户陈述事实与来源内容逐项对应, 对证据不足或事实未明部分保持保守判断。\n\n"
        "六、可采取措施\n"
        "可先固定证据并沟通协商; 协商不成时, 结合争议类型选择投诉、调解、仲裁或诉讼等程序。\n\n"
        "七、证据清单\n"
        f"{evidence_tips(facts.get('legal_domain', 'unknown'))}\n\n"
        "八、风险提示\n"
        "具体结论可能受证据完整性、时效、地区司法实践和对方抗辩影响; 涉及金额较大或事实复杂时建议咨询律师。\n\n"
        "九、免责声明\n"
        f"{DISCLAIMER}\n\n"
        "十、引用来源\n"
        + "\n\n".join(source_lines)
    )


def evidence_tips(domain: str) -> str:
    tips = {
        "labor": "劳动合同、工资流水、考勤记录、社保记录、工作聊天记录、辞退或离职通知、欠薪沟通记录。",
        "contract": "合同文本、补充协议、付款凭证、发票、交付记录、催告记录、违约沟通记录。",
        "marriage_family": "结婚证、财产凭证、债务凭证、子女抚养情况、收入证明、报警或就医记录。",
        "tort": "现场照片、视频、报警记录、医疗票据、鉴定意见、证人证言、沟通记录。",
        "private_lending": "借条、转账记录、聊天记录、还款记录、催收记录、担保材料。",
        "housing_lease": "租赁合同、押金收据、付款记录、房屋照片、维修记录、退租沟通记录。",
        "consumer_rights": "订单记录、付款凭证、商品照片、检测报告、客服聊天记录、投诉记录。",
    }
    return tips.get(domain, "合同、付款记录、聊天记录、通知材料、照片视频、证人材料和其他能证明关键事实的资料。")

