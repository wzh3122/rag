import re

from app.agents.prompts import DISCLAIMER
from app.api.schemas import LegalSource, ReviewResult

COMPLETED_SECTIONS = ["一、", "二、", "三、", "四、", "五、", "六、", "七、", "八、", "九、", "十、"]
GENERAL_SECTIONS = ["一、", "二、", "三、", "四、", "五、"]


def review_answer(status: str, answer: str, sources: list[LegalSource], retry_count: int = 0) -> ReviewResult:
    issues: list[str] = []
    if DISCLAIMER not in answer:
        issues.append("缺少免责声明")
    if status == "completed":
        for section in COMPLETED_SECTIONS:
            if section not in answer:
                issues.append("completed 回答缺少十段式结构")
                break
        if not sources:
            issues.append("completed 状态缺少 sources")
    if status == "general_reference":
        for section in GENERAL_SECTIONS:
            if section not in answer:
                issues.append("general_reference 回答缺少五段式结构")
                break
        if sources:
            issues.append("general_reference 不应包含 sources")
        if re.search(r"第[一二三四五六七八九十百千万\d]+条|《[^》]+》", answer):
            issues.append("无 sources 时不得引用具体法条或法规名称")
    if any(source.authority_level == "D" or source.effective_status == "obsolete" for source in sources):
        issues.append("包含低权威或失效来源")
    return ReviewResult(passed=not issues, issues=issues, retry_count=retry_count)

