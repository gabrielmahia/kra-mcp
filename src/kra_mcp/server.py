"""KraMCP — Kenya Revenue Authority Tax Compliance Tools (6 tools). All data DEMO."""
from __future__ import annotations
from typing import Optional
from fastmcp import FastMCP
mcp = FastMCP(name="kra-mcp", description="Kenya Revenue Authority tax compliance tools. DEMO data only.")

TAX_BRACKETS_2025 = [
    (24000, 0.10), (8333, 0.25), (467667, 0.30), (300000, 0.325), (float("inf"), 0.35)
]

def compute_paye(annual_income: float) -> dict:
    """Compute PAYE tax for Kenya 2025 (simplified)."""
    tax = 0.0
    remaining = annual_income
    breakdown = []
    cumulative = 0
    for band, rate in TAX_BRACKETS_2025:
        monthly_band = band
        annual_band = monthly_band * 12
        taxable = min(remaining, annual_band)
        band_tax = taxable * rate
        if taxable > 0:
            breakdown.append({"band_kes": round(taxable, 0), "rate_pct": rate*100, "tax_kes": round(band_tax, 0)})
        tax += band_tax
        remaining -= taxable
        cumulative += annual_band
        if remaining <= 0:
            break
    personal_relief = 28800
    net_tax = max(0, tax - personal_relief)
    return {"gross_annual": annual_income, "gross_tax": round(tax, 2),
            "personal_relief": personal_relief, "net_paye_annual": round(net_tax, 2),
            "net_paye_monthly": round(net_tax/12, 2), "breakdown": breakdown,
            "effective_rate_pct": round(net_tax/annual_income*100, 2) if annual_income > 0 else 0}

@mcp.tool(name="paye_calculator", description="Compute Kenya PAYE income tax for 2025 tax year. DEMO.")
def paye_calculator(annual_gross_income_kes: float, include_nhif: Optional[bool] = True,
                    include_nssf: Optional[bool] = True) -> dict:
    result = compute_paye(annual_gross_income_kes)
    if include_nhif:
        nhif = min(1700 * 12, annual_gross_income_kes * 0.015 * 12)
        result["nhif_annual"] = round(nhif, 2)
    if include_nssf:
        result["nssf_annual"] = round(min(720 * 12, annual_gross_income_kes * 0.06), 2)
    result["source"] = "DEMO — verify at itax.kra.go.ke"
    result["note"] = "Personal relief: KES 28,800/year. AHL levy, insurance relief may apply."
    return result

@mcp.tool(name="pin_registration_guide", description="Guide to registering for Kenya Revenue Authority PIN. DEMO.")
def pin_registration_guide(applicant_type: str = "individual") -> dict:
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

@mcp.tool(name="vat_guide", description="Kenya VAT registration, rates, and filing guidance. DEMO.")
def vat_guide(query: str) -> dict:
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

@mcp.tool(name="tax_filing_calendar", description="Kenya tax filing deadlines and calendar. DEMO.")
def tax_filing_calendar() -> dict:
    return {"source": "DEMO — kra.go.ke", "year": 2025,
            "key_deadlines": [
                {"deadline": "Jan 20", "obligation": "VAT return — December transactions"},
                {"deadline": "Feb 9",  "obligation": "PAYE return — January payroll"},
                {"deadline": "Apr 30", "obligation": "Individual tax return (simple income)"},
                {"deadline": "Jun 30", "obligation": "Corporate tax return (non-December year-end)"},
                {"deadline": "Dec 31", "obligation": "Withholding tax certificate issuance"},
            ],
            "monthly": "PAYE and VAT due by 9th and 20th respectively each month",
            "penalties": "5% of tax due for late filing. 1% interest per month on late payment."}

@mcp.tool(name="withholding_tax_rates", description="Kenya withholding tax rates by payment type. DEMO.")
def withholding_tax_rates(payment_type: Optional[str] = None) -> dict:
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

@mcp.tool(name="tax_incentives_guide", description="Kenya investment tax incentives and reliefs. DEMO.")
def tax_incentives_guide(sector: Optional[str] = None) -> dict:
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
