from app.agents.answer_generator import generate_general_reference_answer
from app.agents.prompts import DISCLAIMER
from app.agents.reviewer import review_answer
from app.api.schemas import LegalSource


def test_general_reference_with_no_sources_passes_without_law_articles():
    answer = generate_general_reference_answer("公司拖欠工资三个月怎么办", {"legal_domain": "labor"}, "广东")
    result = review_answer("general_reference", answer, [])
    assert result.passed
    assert "第" not in answer or "第九" not in answer
    assert DISCLAIMER in answer


def test_general_reference_rejects_specific_article_without_sources():
    answer = "一、当前依据状态\n根据《劳动合同法》第三十八条处理。\n二、一般处理思路\n三、建议补充的信息\n四、建议整理的证据\n五、免责声明\n" + DISCLAIMER
    result = review_answer("general_reference", answer, [])
    assert not result.passed
    assert any("无 sources" in issue for issue in result.issues)


def test_completed_rejects_missing_sources():
    answer = "\n".join([f"{section}x" for section in ["一、", "二、", "三、", "四、", "五、", "六、", "七、", "八、", "九、", "十、"]]) + DISCLAIMER
    result = review_answer("completed", answer, [])
    assert not result.passed
    assert "completed 状态缺少 sources" in result.issues


def test_rejects_obsolete_source():
    source = LegalSource(title="旧规定", authority_level="S", effective_status="obsolete")
    result = review_answer("completed", "一、二、三、四、五、六、七、八、九、十、" + DISCLAIMER, [source])
    assert not result.passed

