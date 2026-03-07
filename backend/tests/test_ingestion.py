from app.services.ingestion import _extract_pdf_from_article, _find_monthly_article_links, extract_metrics, normalize_unit


def test_extract_metrics_and_normalization():
    text = "猪肉批发价格为20.30元/公斤，28种蔬菜平均价格为4.20元/公斤，6种水果平均价格为7.10元/公斤。"
    metrics = extract_metrics(text)
    assert ("猪肉", "畜牧水产", 20.3, "元/公斤") in metrics
    assert ("28种蔬菜", "蔬菜类", 4.2, "元/公斤") in metrics
    assert normalize_unit("元/千克") == "元/公斤"


def test_monthly_article_and_pdf_parsing():
    article_list_html = """
    <html><body>
      <a href="./202602/t20260210_6481483.htm">2026年2月中国农产品供需形势分析（CASDE-No.116）</a>
    </body></html>
    """
    article_links = _find_monthly_article_links(article_list_html)
    assert article_links
    assert article_links[0][1] == "https://scs.moa.gov.cn/jcyj/202602/t20260210_6481483.htm"

    article_html = """
    <html><body>
      <a href="./P020260210539899311012.pdf">2026年2月中国农产品供需形势分析（CASDE—No.116）.pdf</a>
    </body></html>
    """
    title, pdf_url = _extract_pdf_from_article(article_html, article_links[0][1])
    assert title.endswith(".pdf")
    assert pdf_url.endswith(".pdf")
