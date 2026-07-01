# kra-mcp

[![kra-mcp Glama score](https://glama.ai/mcp/servers/gabrielmahia/kra-mcp/badges/score.svg)](https://glama.ai/mcp/servers/gabrielmahia/kra-mcp)
[![smithery badge](https://smithery.ai/badge/@gabrielmahia/kra-mcp)](https://smithery.ai/server/@gabrielmahia/kra-mcp)


---
**Compatible with `claude-sonnet-5`** (released 2026-06-30) — Anthropic's most agentic
Sonnet yet. Runs multi-step tool chains end-to-end without stopping short.
Install: `pip install kra-mcp` · Use with any MCP client.

---


> Kenya Revenue Authority tax compliance via MCP — PAYE calculator, VAT guide, PIN registration, tax incentives

[![PyPI](https://img.shields.io/badge/PyPI-v0.1.0-blue)](https://github.com/gabrielmahia/kra-mcp)
[![License](https://img.shields.io/badge/License-MIT-green)](https://github.com/gabrielmahia/kra-mcp)
[![Layer](https://img.shields.io/badge/Layer-Economic-orange)](https://github.com/gabrielmahia/kra-mcp)

## Install

```bash
pip install kra-mcp
```

## What it does

6 MCP tools covering Kenya tax compliance. 1st world equivalent: **TurboTax / HMRC**.

| Tool | Description |
|------|-------------|
| `paye_calculator` | Kenya PAYE tax for 2025 — 7 brackets + personal relief |
| `pin_registration_guide` | Step-by-step KRA PIN registration (individual and company) |
| `vat_guide` | VAT registration threshold, rates, filing deadlines |
| `tax_filing_calendar` | All Kenya tax deadlines in one place |
| `withholding_tax_rates` | Rates by payment type: dividends, royalties, professional fees |
| `tax_incentives_guide` | EPZ, SEZ, tech, pension, startup tax incentives |

## Usage

```bash
# Run as standalone MCP server
kra-mcp

# Or add to Claude Desktop / any MCP client
# Add to your MCP config: {"command": "kra-mcp"}
```

## Part of the Kenya Coordination Infrastructure Stack

This is one of 23 MCP servers covering the full coordination infrastructure of East Africa:

**Economic:** mpesa · mkopo · bima · soko · sifa · remit · kra · faida  
**Physical:** wapimaji · nishati · usafiri · ardhi  
**Social:** afya · afya-ya-akili · elimu · kazi · haki-ya-kazi · kilimo · jumuia  
**Civic:** nyumba · habari · mazingira · civic-agent-kit  

→ [The Nairobi Stack](https://gabrielmahia.github.io/nairobi-stack)  
→ [Full Portfolio](https://gabrielmahia.github.io)

## Trust Integrity

All data in this server is **clearly labeled DEMO** where synthetic. Verify all operational data with the relevant Kenyan government authority before use.

## License

MIT © Gabriel Mahia | [AI-KungFU](https://github.com/gabrielmahia) | contact@aikungfu.dev

> *Decision infrastructure for East Africa*

## Part of the East Africa Coordination Stack

This MCP server is one of 32 tools in the Kenya coordination infrastructure.
Connect it to [`africa-coord-bus`](https://github.com/gabrielmahia/africa-coord-bus) —
the coordination event bus that routes signals between domains automatically.

```bash
pip install africa-coord-bus
```

All 32 servers: [pypi.org/user/gmahia](https://pypi.org/user/gmahia/)
Live demo: [coord-cascade-demo](https://github.com/gabrielmahia/coord-cascade-demo)