"""KraMCP — Kenya Revenue Authority Tax Compliance Tools (6 tools). paye_calculator uses 2026 statutory figures (estimate); other tools are DEMO data."""
from __future__ import annotations

from typing import Optional

from fastmcp import FastMCP

mcp = FastMCP(name="kra-mcp", instructions="Kenya Revenue Authority tax compliance tools. DEMO data only.")

# Statutory figures, checked 2026-10-06 against NSSF's Year-4 employer notice (Feb 2026) and KRA-aligned 2026 payroll guidance.
# Review each February (NSSF steps) and after every Finance Act. Estimates only: verify with KRA / your payroll provider.
STATUTORY_AS_OF = "2026-10"
NSSF_RATE, NSSF_UPPER_EARNINGS_LIMIT = 0.06, 108_000.0   # employee 6% of pensionable pay, capped: max KES 6,480/month from Feb 2026
SHIF_RATE, SHIF_MINIMUM = 0.0275, 300.0                   # SHIF replaced NHIF in Oct 2024: 2.75% of gross, minimum KES 300, no cap
AHL_RATE = 0.015                                          # Affordable Housing Levy: employee 1.5% of gross
PERSONAL_RELIEF_MONTHLY = 2400.0
MONTHLY_BANDS = [(24000.0, 0.10), (8333.0, 0.25), (467667.0, 0.30), (300000.0, 0.325), (float("inf"), 0.35)]
ASSUMPTIONS = [
    "Pensionable pay is taken to equal gross pay.",
    "NSSF, SHIF and the housing levy are deducted before PAYE (most 2026 sources agree; one older source says the housing levy is not deductible: verify with KRA).",
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


@mcp.tool(name="paye_calculator", description="Estimate Kenya PAYE and take-home pay from annual gross pay: NSSF (6%, capped at KES 6,480/month), SHIF (2.75%, min KES 300), housing levy (1.5%) deducted before PAYE bands, then KES 2,400/month personal relief. Statutory figures as of 2026-10. Estimate only; verify with KRA.")
def paye_calculator(annual_gross_income_kes: float, include_nhif: bool | None = True,
                    include_nssf: bool | None = True, include_shif: bool | None = True,
                    include_housing_levy: bool | None = True) -> dict:
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
    result.update({"status": "ESTIMATE", "statutory_as_of": STATUTORY_AS_OF, "assumptions": ASSUMPTIONS, "source": "NSSF Year-4 employer notice (Feb 2026); KRA-aligned 2026 payroll guidance. Verify at itax.kra.go.ke"})
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
def withholding_tax_rates(payment_type: str | None = None) -> dict:
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
def tax_incentives_guide(sector: str | None = None) -> dict:
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
