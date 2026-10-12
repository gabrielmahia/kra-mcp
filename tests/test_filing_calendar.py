from kra_mcp import server

fn = server.tax_filing_calendar.fn if hasattr(server.tax_filing_calendar, "fn") else server.tax_filing_calendar


def test_the_calendar_matches_kras_published_deadlines_and_is_not_stamped_with_a_stale_year():
    """It said year 2025, an individual-return deadline of 30 April and a company return on 30 June for non-December year-ends. KRA: individuals file by 30 June;
    companies within six months after the accounting year-end; late filing is the higher of 5% or KES 2,000 (individuals) / KES 20,000 (companies)."""
    r = fn()
    text = str(r)
    assert "year" not in r and "2025" not in text and "Apr 30" not in str(r["key_deadlines"])
    assert any(d["deadline"] == "30 June" and "Individual" in d["obligation"] for d in r["key_deadlines"])
    assert any("Six months" in d["deadline"] and "Company" in d["obligation"] for d in r["key_deadlines"])
    assert "KES 2,000" in r["penalties"] and "KES 20,000" in r["penalties"]
