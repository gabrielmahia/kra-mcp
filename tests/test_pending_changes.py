from kra_mcp import server

_fn = lambda name: (getattr(server, name).fn if hasattr(getattr(server, name), "fn") else getattr(server, name))


def test_the_paye_estimate_says_a_relief_is_proposed_not_law():
    """The Treasury's proposed KES 30,000 tax-free threshold was left out of the Finance Bill 2026; the tool must say it is only proposed."""
    r = _fn("paye_calculator")(1_200_000)
    assert r["pending_changes"].startswith("PROPOSED, NOT LAW") and "Finance Bill 2026 did not change PAYE" in r["pending_changes"]


def test_current_law_is_still_applied_and_the_proposal_is_not():
    """KES 100,000 a month: taxable 89,750 after NSSF 6,000, SHIF 2,750 and levy 1,500; PAYE 2,400 + 2,083.25 + 17,225.10 = 21,708.35 less relief 2,400 = 19,308.35.
    A proposed relief of 3,000 a month (36,000 a year) must not be the one used."""
    r = _fn("paye_calculator")(1_200_000)
    assert r["taxable_pay_monthly"] == 89750.0 and r["personal_relief"] == 28800.0 and r["net_paye_monthly"] == 19308.35
