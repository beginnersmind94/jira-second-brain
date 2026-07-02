from types import SimpleNamespace
import demo
import citations_client as cc


def test_build_ticket_documents_one_block_per_nonempty_tier():
    demo._FIX = {"tickets": {"NXT-1001": {"ac": "Alpha.", "rn": "Bravo.",
                                          "rn_internal": "", "desc": "Delta."}},
                 "epics": {}}
    docs = cc.build_ticket_documents(["NXT-1001"])
    assert [d["title"] for d in docs] == ["NXT-1001:AC", "NXT-1001:RN", "NXT-1001:DESC"]
    for d in docs:
        assert d["type"] == "document"
        assert d["source"]["type"] == "text"
        assert d["citations"]["enabled"] is True
    # exactly ONE cache breakpoint (API caps breakpoints at 4/request; a section can cite >4 docs)
    assert sum("cache_control" in d for d in docs) == 1
    assert docs[-1]["cache_control"]["type"] == "ephemeral"


def test_parse_citation_response_extracts_span_and_tier():
    cit = SimpleNamespace(type="text", cited_text="Alpha.", document_title="NXT-1001:AC")
    blocks = [
        SimpleNamespace(type="text", text="<h2>Rules</h2><p>Cashier confirms PIN.", citations=[cit]),
        SimpleNamespace(type="text", text="</p>", citations=[]),
    ]
    out = cc.parse_citation_response(blocks)
    assert out["segments"][0]["cites"] == [{"span": "Alpha.", "key": "NXT-1001", "tier": "AC"}]
    assert "Cashier confirms PIN" in out["prose"]


def test_segments_to_html_namespaces_cite_ids_by_section():
    segs = [{"text": "A.", "cites": [{"span": "Alpha.", "key": "NXT-1001", "tier": "AC"}]}]
    h1, e1 = cc.segments_to_html(segs, "s1")
    h2, e2 = cc.segments_to_html(segs, "s2")
    # same content, different section -> disjoint cite-ids (no registry collision)
    assert set(e1).isdisjoint(set(e2))
    assert "[CITE:NXT-1001:AC:s1:C000]" in h1
    assert "[CITE:NXT-1001:AC:s2:C000]" in h2
    assert e1["NXT-1001:AC:s1:C000"] == {"issue": "NXT-1001", "tier": "AC", "span": "Alpha."}
