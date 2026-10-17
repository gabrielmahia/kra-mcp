"""KraMCP — Kenya Revenue Authority Tax Compliance Tools (6 tools). paye_calculator uses 2026 statutory figures (estimate); other tools are DEMO data."""
from __future__ import annotations

from typing import Annotated, Optional

from fastmcp import FastMCP
from pydantic import Field

# Annotations tell clients which tools are safe to auto-approve (read-only, no side effects).
READ_ONLY = {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False}

mcp = FastMCP(name="kra-mcp", instructions="Kenya Revenue Authority tax compliance tools. DEMO data only.")

# Statutory figures, checked 2026-10-06 against NSSF's Year-4 employer notice (Feb 2026) and KRA-aligned 2026 payroll guidance.
# Review each February (NSSF steps) and after every Finance Act. Estimates only: verify with KRA / your payroll provider.
STATUTORY_AS_OF = "2026-10"
PENDING_CHANGES = ("PROPOSED, NOT LAW: the Treasury has said it will bring a Tax Laws Amendment Bill (reported as expected around October to November 2026) that could raise the tax-free income threshold from KES 24,000 to 30,000 a month, raise personal relief above KES 2,400 and widen the PAYE bands. "
                   "The Finance Bill 2026 did not change PAYE. This tool applies current law only: re-check after any such change is enacted.")
NSSF_RATE, NSSF_UPPER_EARNINGS_LIMIT = 0.06, 108_000.0   # employee 6% of pensionable pay, capped: max KES 6,480/month from Feb 2026
SHIF_RATE, SHIF_MINIMUM = 0.0275, 300.0                   # SHIF replaced NHIF in Oct 2024: 2.75% of gross, minimum KES 300, no cap
AHL_RATE = 0.015                                          # Affordable Housing Levy: employee 1.5% of gross
PERSONAL_RELIEF_MONTHLY = 2400.0
MONTHLY_BANDS = [(24000.0, 0.10), (8333.0, 0.25), (467667.0, 0.30), (300000.0, 0.325), (float("inf"), 0.35)]
ASSUMPTIONS = [
    "Pensionable pay is taken to equal gross pay.",
    "NSSF, SHIF and the housing levy are deducted before PAYE (KRA public notice effective 27 Dec 2024; Income Tax Act s.15(2)(ac) and (ae)). The old 15% housing relief no longer exists.",
    "The Finance Act 2026 (effective 1 Jul 2026) did not change the PAYE bands (PwC tax alert, Jul 2026).",
    "Excludes insurance relief, mortgage interest, pension beyond NSSF, disability exemption and non-resident rules.",
]


def nssf_employee(monthly_gross: float) -> float:
    return round(NSSF_RATE * min(max(monthly_gross, 0.0), NSSF_UPPER_EARNINGS_LIMIT), 2)


def shif_employee(monthly_gross: float) -> float:
    return round(max(SHIF_MINIMUM, SHIF_RATE * monthly_gross), 2) if monthly_gross > 0 else 0.0


def housing_levy_employee(monthly_gross: float) -> float:
    return round(AHL_RATE * max(monthly_gross, 0.0), 2)


def compute_paye(annual_income: float) -> dict:
    """PAYE on ANNUAL TAXABLE income, computed monthly the way a payslip is: (annual / 12) through the monthly bands, times 12."""
    monthly = max(annual_income, 0.0) / 12
    tax, remaining, breakdown = 0.0, monthly, []
    for band, rate in MONTHLY_BANDS:
        taxable = min(remaining, band)
        if taxable > 0:
            breakdown.append({"band_kes_monthly": round(taxable, 2), "rate_pct": round(rate * 100, 1), "tax_kes_monthly": round(taxable * rate, 2)})
            tax += taxable * rate
            remaining -= taxable
        if remaining <= 0:
            break
    net_monthly = max(0.0, tax - PERSONAL_RELIEF_MONTHLY)
    return {"taxable_annual": round(annual_income, 2), "gross_tax": round(tax * 12, 2), "personal_relief": round(PERSONAL_RELIEF_MONTHLY * 12, 2),
            "net_paye_annual": round(net_monthly * 12, 2), "net_paye_monthly": round(net_monthly, 2), "breakdown": breakdown}


@mcp.tool(name="paye_calculator", description="Estimate Kenya PAYE and take-home pay from annual gross pay. Use when someone asks what they will take home after statutory deductions, how much PAYE they owe, or how NSSF, SHIF and the housing levy affect it. Deducts NSSF (6%, capped at KES 6,480 per month), SHIF (2.75%, minimum KES 300) and the housing levy (1.5%) before applying the PAYE bands, then KES 2,400 per month personal relief. Returns gross, each monthly deduction, taxable pay, PAYE before and after relief, net monthly pay, the effective rate, annual totals, the assumptions used and the date the statutory figures are current to (2026-10). An estimate only: verify with KRA. It applies current law; a proposed PAYE relief that is not yet law is reported in pending_changes, not applied. Read-only; no side effects.", annotations=READ_ONLY)
def paye_calculator(
    annual_gross_income_kes: Annotated[float, Field(description="Annual gross pay in Kenya shillings (KES). Negative values are treated as 0.")],
    include_nhif: Annotated[bool | None, Field(description="Deprecated and ignored: NHIF was replaced by SHIF. Kept so existing callers do not break.")] = True,
    include_nssf: Annotated[bool | None, Field(description="Deduct the employee NSSF contribution (default true).")] = True,
    include_shif: Annotated[bool | None, Field(description="Deduct the SHIF health contribution (default true).")] = True,
    include_housing_levy: Annotated[bool | None, Field(description="Deduct the affordable housing levy (default true).")] = True,
) -> dict:
    gross = max(annual_gross_income_kes, 0.0) / 12
    nssf = nssf_employee(gross) if include_nssf else 0.0
    shif = shif_employee(gross) if include_shif else 0.0   # include_nhif is accepted for old callers and ignored: NHIF no longer exists
    ahl = housing_levy_employee(gross) if include_housing_levy else 0.0
    taxable_monthly = max(gross - nssf - shif - ahl, 0.0)
    paye = compute_paye(taxable_monthly * 12)
    result = {"gross_annual": round(annual_gross_income_kes, 2), "gross_monthly": round(gross, 2),
              "deductions_monthly": {"nssf": nssf, "shif": shif, "housing_levy": ahl},
              "taxable_pay_monthly": round(taxable_monthly, 2), **paye,
              "net_pay_monthly": round(gross - nssf - shif - ahl - paye["net_paye_monthly"], 2),
              "effective_rate_pct": round(paye["net_paye_annual"] / annual_gross_income_kes * 100, 2) if annual_gross_income_kes > 0 else 0,
              "nssf_annual": round(nssf * 12, 2), "shif_annual": round(shif * 12, 2), "housing_levy_annual": round(ahl * 12, 2)}
    if include_nhif:
        result["nhif"] = "NHIF was replaced by SHIF in October 2024; see shif_annual."
    result.update({"status": "ESTIMATE", "statutory_as_of": STATUTORY_AS_OF, "pending_changes": PENDING_CHANGES, "assumptions": ASSUMPTIONS, "source": "NSSF Year-4 employer notice (Feb 2026); KRA notice on PAYE computation (Dec 2024); Finance Act 2026 analyses. Verify at itax.kra.go.ke"})
    return result

@mcp.tool(name="pin_registration_guide", description="Step-by-step guide to getting a KRA PIN (Personal Identification Number) on iTax, with the documents needed, cost and processing time. Use when someone asks how to register for a PIN. Returns steps, documents, cost, processing time and KRA contact details for an 'individual' or a 'company'; any other applicant type silently falls back to the individual guide, so check the applicant_type field in the response. Static summary labelled DEMO: confirm the steps on itax.kra.go.ke. Read-only.", annotations=READ_ONLY)
def pin_registration_guide(applicant_type: Annotated[str, Field(description="Either individual or company (case-insensitive). Any other value returns the individual guide.")] = "individual") -> dict:
    GUIDES = {
        "individual": {"steps": ["1. Go to iTax: itax.kra.go.ke", "2. New user registration",
                                 "3. Enter ID/Passport number", "4. Provide: name, DOB, contacts",
                                 "5. Upload ID scan", "6. PIN generated instantly"],
                       "documents": ["National ID or Passport", "Phone number", "Email address"],
                       "cost": "Free", "processing": "Instant"},
        "company":    {"steps": ["1. iTax portal", "2. Non-individual PIN", "3. Certificate of Incorporation",
                                 "4. CR12 (directors)", "5. Registrar confirms after 2-3 days"],
                       "documents": ["Certificate of Incorporation", "CR12", "Director IDs"],
                       "cost": "Free", "processing": "2-3 working days"},
    }
    guide = GUIDES.get(applicant_type.lower(), GUIDES["individual"])
    return {"source": "DEMO — itax.kra.go.ke", "applicant_type": applicant_type, **guide,
            "kra_portal": "itax.kra.go.ke", "kra_contact": "0800723470 (toll-free)"}

@mcp.tool(name="vat_guide", description="Kenya VAT basics: the registration threshold (KES 5 million annual taxable turnover), the standard rate and zero-rated or exempt categories, filing, refunds and government VAT withholding. Use when asked about VAT rules; for when a VAT return is due use tax_filing_calendar. Keywords in the query (registration, rate, filing, refund, withholding) select the matching entries; if none match, all entries are returned. Static summary labelled DEMO: verify at kra.go.ke. Read-only.", annotations=READ_ONLY)
def vat_guide(query: Annotated[str, Field(description="Free text such as how do I register for VAT. Keywords registration, rate, filing, refund or withholding select entries.")]) -> dict:
    INFO = {
        "registration":   "Register if annual taxable turnover > KES 5M. iTax portal. Certificate in 7 days.",
        "rate":           "Standard rate: 16%. Zero-rated: exports, basic foods, medical. Exempt: financial, educational.",
        "filing":         "Monthly by 20th of following month. iTax form VAT-3. Electronic filing mandatory.",
        "refund":         "File VAT-3 showing excess input tax. KRA may audit before refund. Takes 30-90 days.",
        "withholding_vat":"Government ministries withhold 6% VAT on supplier invoices. Supplier claims credit.",
    }
    q = query.lower()
    matched = {k: v for k, v in INFO.items() if k in q or any(w in q for w in k.split("_"))}
    return {"source": "DEMO — verify at kra.go.ke/vat", "query": query,
            "information": matched or INFO, "threshold": "KES 5M annual turnover = mandatory registration"}

@mcp.tool(name="tax_filing_calendar", description="The main recurring Kenya tax filing deadlines: individual income tax return (30 June, for the previous calendar year), company income tax return (six months after the accounting year-end), monthly PAYE (9th) and VAT (20th), and the late-filing and late-payment penalties. Use when someone asks when a return or payment is due. Takes no arguments. Not year-specific: these are standing statutory deadlines checked against KRA's published guidance on 2026-10-12, not a dated calendar for one year. Read-only.", annotations=READ_ONLY)
def tax_filing_calendar() -> dict:
    return {"source": "KRA guidance (kra.go.ke blog 'The Importance of Filing Tax Returns'), checked 2026-10-12; not year-specific",
            "key_deadlines": [
                {"deadline": "30 June", "obligation": "Individual income tax return for the previous calendar year (the filing window runs 1 January to 30 June)"},
                {"deadline": "Six months after the accounting year-end", "obligation": "Company income tax return (30 June for a 31 December year-end)"},
            ],
            "monthly": "PAYE due by the 9th and VAT by the 20th of the following month",
            "penalties": "Late filing: the higher of 5% of the tax due or KES 2,000 (individuals) / KES 20,000 (companies and other non-individuals). Late payment: 5% of the tax due plus interest of 1% per month.",
            "not_included": "Earlier versions listed an individual-return deadline of 30 April and a withholding-certificate date that did not match KRA's guidance; they were removed."}

@mcp.tool(name="withholding_tax_rates", description="Kenya withholding tax rates by payment type (dividends, bank interest, professional and management fees, royalties, commercial rent, contractor payments), resident versus non-resident. Use when working out how much tax to withhold from a payment. With payment_type it returns the matching rates, or a pointer to kra.go.ke if nothing matches; with no argument it returns all rates. Rates may be reduced by Double Tax Agreements. Static summary labelled DEMO and not verified against current law: confirm before relying. Read-only.", annotations=READ_ONLY)
def withholding_tax_rates(payment_type: Annotated[str | None, Field(description="Optional filter such as dividends, professional fees or rent. Spaces become underscores; partial matches work. Omit for all rates.")] = None) -> dict:
    RATES = {
            "dividends_resident":     "5% (final tax)",
            "dividends_non_resident": "10% (final tax)",
            "interest_bank":          "15% (final tax for resident individuals)",
            "professional_fees":      "5% (resident), 20% (non-resident)",
            "rent_commercial":        "30% (if payer is registered withholding agent)",
            "royalties_resident":     "5%",
            "royalties_non_resident": "20% (may be reduced by tax treaty)",
            "management_fees":        "5% (resident), 20% (non-resident)",
            "contractor_payments":    "3% (public sector, construction)",
    }
    if payment_type:
        pt = payment_type.lower().replace(" ", "_")
        matched = {k: v for k, v in RATES.items() if pt in k}
        return {"source": "DEMO — kra.go.ke", "payment_type": payment_type,
                "rate": matched or {"general": "Verify specific rate at kra.go.ke/withholding-tax"}}
    return {"source": "DEMO — kra.go.ke", "withholding_tax_rates": RATES,
            "note": "Rates may be reduced by Double Tax Agreements (DTAs). Verify at kra.go.ke"}

@mcp.tool(name="tax_incentives_guide", description="Kenya investment tax incentives and reliefs by sector (manufacturing, agriculture, technology, exports, pension, startup). Use when exploring tax reliefs for a business or for pension contributions. With sector it returns the matching incentives, or all sectors if none match; with no argument it returns everything. Static summary labelled DEMO and NOT verified against current law (some listed incentives are unverified): confirm with KRA or KenInvest before relying. Read-only.", annotations=READ_ONLY)
def tax_incentives_guide(sector: Annotated[str | None, Field(description="Optional keyword such as agriculture or technology; partial matches work. Omit for all sectors.")] = None) -> dict:
    INCENTIVES = {
        "manufacturing": ["100% investment deduction on plant/machinery in EPZ",
                          "10-year tax holiday in EPZ", "Reduced corporate tax 15% for SEZ"],
        "agriculture":   ["100% capital allowance on farm works", "Tax-free cooperatives",
                          "Zero VAT on agricultural inputs"],
        "technology":    ["100% investment deduction for ICT infrastructure",
                          "Preferential 10% corporate tax for registered ICT companies"],
        "exports":       ["10% corporate tax for qualifying manufacturers",
                          "Zero-rated VAT on all exports"],
        "pension":       ["Employer contributions tax-deductible up to KES 240,000/year",
                          "Employee contributions deductible up to KES 240,000/year"],
        "startup":       ["Available in Nairobi Innovation Hub — no corporate tax for 10 years",
                          "No import duty on software/ICT equipment for registered tech startups"],
    }
    s = sector.lower() if sector else None
    data = {k: v for k, v in INCENTIVES.items() if not s or k in s} or INCENTIVES
    return {"source": "DEMO — KRA and Kenya Investment Authority", "sector": sector,
            "incentives": data, "keninvest": "keninvest.go.ke for investment facilitation"}

def main() -> None:
    """Console entry point."""
    mcp.run()
