"""Numbers, not just imports. Expected values are hand-computed from the 2026 bands; vectors 1 and 2 also match two independent public worked examples
(taxable pay 44,875 for a 50,000 salary; PAYE before relief 21,708.35 for 100,000)."""
import pytest

from kra_mcp import server as s

paye = s.paye_calculator.fn if hasattr(s.paye_calculator, "fn") else s.paye_calculator


def monthly(gross, **kw):
    return paye(gross * 12, **kw)


def test_50k_salary_matches_the_independent_example():
    r = monthly(50_000)
    assert r["deductions_monthly"] == {"nssf": 3000.0, "shif": 1375.0, "housing_levy": 750.0}
    assert r["taxable_pay_monthly"] == 44_875.0
    # 2,400 + 8,333*25% + (44,875-32,333)*30% = 8,245.85 before relief
    assert r["net_paye_monthly"] == pytest.approx(8_245.85 - 2_400, abs=0.02)


def test_100k_salary_matches_the_independent_example():
    r = monthly(100_000)
    assert r["taxable_pay_monthly"] == 89_750.0
    assert r["gross_tax"] / 12 == pytest.approx(21_708.35, abs=0.02)
    assert r["net_paye_monthly"] == pytest.approx(19_308.35, abs=0.02)


def test_nssf_is_capped_at_the_2026_upper_limit():
    """The old kazi-mcp / kra-mcp logic charged 6% of everything: 12,000 on a 200,000 salary. The maximum is 6,480."""
    r = monthly(200_000)
    assert r["deductions_monthly"]["nssf"] == 6480.0
    assert r["taxable_pay_monthly"] == 185_020.0
    assert r["net_paye_monthly"] == pytest.approx(50_289.35 - 2_400, abs=0.02)


def test_low_income_pays_no_paye_and_relief_never_goes_negative():
    r = monthly(20_000)
    assert r["net_paye_monthly"] == 0 and r["net_pay_monthly"] > 0


def test_shif_has_a_300_minimum():
    assert monthly(8_000)["deductions_monthly"]["shif"] == 300.0


def test_nhif_is_gone():
    r = monthly(60_000)
    assert "nhif_annual" not in r and "SHIF" in r["nhif"]
    assert "nhif" not in monthly(60_000, include_nhif=False)


def test_the_assumptions_are_stated():
    r = monthly(60_000)
    assert r["status"] == "ESTIMATE" and r["statutory_as_of"] == "2026-10" and any("housing levy" in a for a in r["assumptions"])


def test_zero_income_is_all_zeros_not_an_error():
    r = paye(0)
    assert r["net_paye_annual"] == 0 and r["effective_rate_pct"] == 0


def test_top_band_applies_above_800k_a_month():
    r = s.compute_paye(900_000 * 12)
    assert r["breakdown"][-1]["rate_pct"] == 35.0
