"""Load 20 seed governance cases and run engine_only pipeline on each."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mas.db import init_db
from mas.orchestrator import Orchestrator

SEED_CASES = [
    {
        "case_id": "challenger-1986",
        "title": "Space Shuttle Challenger Disaster",
        "country": "USA",
        "year": 1986,
        "text": (
            "NASA management overruled engineers who warned that O-rings would fail in cold temperatures. "
            "Engineers sent a memo documenting concerns prior to launch. "
            "Management pressure reversed the engineers' no-launch recommendation. "
            "The shuttle broke apart 73 seconds after launch, killing all 7 crew members. "
            "The Rogers Commission investigation found groupthink and communication failure among decision-makers."
        ),
    },
    {
        "case_id": "chernobyl-1986",
        "title": "Chernobyl Nuclear Disaster",
        "country": "USSR",
        "year": 1986,
        "text": (
            "Operators at Chernobyl conducted a safety test while the reactor was in an unstable state. "
            "Warnings about reactor design flaws had been suppressed by Soviet authorities for years. "
            "Bureaucratic pressure to complete the test overrode safety protocols. "
            "The explosion released massive radiation causing a regional catastrophe. "
            "Government initially concealed the scale of the disaster from the public and international community."
        ),
    },
    {
        "case_id": "iraq-wmd-2003",
        "title": "Iraq WMD Intelligence Failure",
        "country": "USA",
        "year": 2003,
        "text": (
            "US intelligence agencies produced a National Intelligence Estimate concluding Iraq possessed WMDs. "
            "Dissenting assessments from DIA and State Department were minimized in the final report. "
            "Political pressure influenced intelligence analysis and suppressed alternative views. "
            "No weapons of mass destruction were found after the invasion of Iraq. "
            "The Senate Intelligence Committee inquiry found groupthink and absence of critical review."
        ),
    },
    {
        "case_id": "post-office-horizon-1999",
        "title": "UK Post Office Horizon IT Scandal",
        "country": "UK",
        "year": 1999,
        "text": (
            "Post Office deployed the Horizon IT system despite known accounting errors and software defects. "
            "Over 900 subpostmasters were prosecuted for false accounting based on faulty data. "
            "Post Office management repeatedly dismissed and suppressed complaints about system bugs. "
            "Whistleblowers and legal challenges were ignored for over 15 years. "
            "The Horizon Inquiry found systematic denial and cover-up by Post Office leadership."
        ),
    },
    {
        "case_id": "deepwater-horizon-2010",
        "title": "Deepwater Horizon Blowout",
        "country": "USA",
        "year": 2010,
        "text": (
            "BP management accepted risk trade-offs to reduce cost and time on the Macondo well. "
            "Engineers raised concerns about cement integrity and well control procedures. "
            "A pressure test showing a kick was misinterpreted due to schedule pressure. "
            "The blowout killed 11 workers and caused the largest marine oil spill in US history. "
            "Presidential Commission found management decisions prioritized schedule over safety."
        ),
    },
    {
        "case_id": "flint-water-2014",
        "title": "Flint Water Crisis",
        "country": "USA",
        "year": 2014,
        "text": (
            "Michigan officials switched Flint's water source to the Flint River without adequate corrosion control. "
            "EPA and state regulators received repeated complaints about lead contamination and discolored water. "
            "Agency staff raised internal concerns but senior officials delayed public warnings for months. "
            "Independent testing confirmed elevated blood lead levels in thousands of children. "
            "Investigations found bureaucratic opacity, dismissal of expert dissent, and failure to escalate known risks."
        ),
    },
    {
        "case_id": "enron-2001",
        "title": "Enron Accounting Collapse",
        "country": "USA",
        "year": 2001,
        "text": (
            "Enron executives used off-balance-sheet partnerships to hide debt and inflate reported earnings. "
            "Internal auditors and analysts who questioned the accounting structures were sidelined or reassigned. "
            "Arthur Andersen signed off on financial statements despite known irregularities. "
            "Whistleblower Sherron Watkins warned leadership that the company could implode in a wave of accounting scandals. "
            "The collapse wiped out employee pensions and triggered Sarbanes-Oxley reforms on corporate governance."
        ),
    },
    {
        "case_id": "boeing-737max-2019",
        "title": "Boeing 737 MAX Safety Failures",
        "country": "USA",
        "year": 2019,
        "text": (
            "Boeing rushed certification of the 737 MAX MCAS flight-control system to compete with Airbus. "
            "FAA delegated much of the safety review to Boeing employees with commercial incentives to approve the design. "
            "Engineers documented simulator scenarios where MCAS could force repeated nose-down commands. "
            "After two crashes killing 346 people, investigations found regulatory capture and suppressed technical dissent. "
            "Congressional reports concluded schedule and cost pressure overrode transparent safety analysis."
        ),
    },
    {
        "case_id": "hurricane-katrina-2005",
        "title": "Hurricane Katrina Response Failure",
        "country": "USA",
        "year": 2005,
        "text": (
            "FEMA and DHS received pre-landfall warnings that New Orleans levees could fail under a major hurricane. "
            "Interagency coordination broke down as state and federal authorities disputed responsibility and command. "
            "Field reports of stranded residents and overwhelmed shelters were slow to reach senior decision-makers. "
            "Media coverage exposed delayed federal deployment while local officials pleaded for resources. "
            "The bipartisan Katrina Commission cited fragmented information flow and failure to act on known vulnerabilities."
        ),
    },
    {
        "case_id": "opioid-purdue-2007",
        "title": "US Opioid Crisis — Purdue and FDA Oversight",
        "country": "USA",
        "year": 2007,
        "text": (
            "Purdue Pharma marketed OxyContin as rarely addictive while internal documents showed awareness of abuse potential. "
            "FDA reviewers raised concerns about labeling claims but approved expanded prescribing language after industry pressure. "
            "State medical boards and DEA received rising overdose signals that were not synthesized into federal action for years. "
            "Sales representatives were incentivized to downplay addiction risks to physicians. "
            "Subsequent litigation and congressional hearings found systematic suppression of contrary medical evidence."
        ),
    },
    {
        "case_id": "abu-ghraib-2004",
        "title": "Abu Ghraib Prison Abuse Scandal",
        "country": "USA",
        "year": 2004,
        "text": (
            "US military personnel abused detainees at Abu Ghraib prison in Iraq during the occupation. "
            "Internal Army reports documented harsh interrogation practices before photos became public. "
            "Chain-of-command disputes obscured who authorized stress techniques and sleep deprivation. "
            "Initial military statements minimized scope until media publication forced broader investigation. "
            "Independent reviews found failure to enforce standards, weak oversight, and delayed accountability."
        ),
    },
    {
        "case_id": "hillsborough-1989",
        "title": "Hillsborough Stadium Disaster Cover-Up",
        "country": "UK",
        "year": 1989,
        "text": (
            "Ninety-seven Liverpool fans died in a crush at Hillsborough stadium during an FA Cup semi-final. "
            "South Yorkshire Police initially blamed crowd behavior and circulated false narratives to media outlets. "
            "Survivors and bereaved families faced official obstruction when seeking records and inquest access. "
            "Internal police statements were altered to shift responsibility away from stadium management failures. "
            "The 2016 inquest verdict and subsequent inquiries found unlawful killing and decades of institutional cover-up."
        ),
    },
    {
        "case_id": "infected-blood-1970s",
        "title": "UK Contaminated Blood Scandal",
        "country": "UK",
        "year": 1978,
        "text": (
            "The NHS imported blood products from high-risk donors despite warnings about hepatitis and HIV transmission. "
            "Clinicians and haemophilia societies raised alarms that were not acted on at departmental level for years. "
            "Government continued use of commercial factor concentrates while safer heat-treated alternatives existed abroad. "
            "Patients were not informed of known infection risks linked to specific product batches. "
            "The Infected Blood Inquiry found repeated failure to disclose known hazards and protect patient safety."
        ),
    },
    {
        "case_id": "grenfell-2017",
        "title": "Grenfell Tower Fire",
        "country": "UK",
        "year": 2017,
        "text": (
            "Grenfell Tower was clad in combustible aluminum composite panels during a refurbishment overseen by the tenant management organization. "
            "Residents submitted fire safety complaints and warned that only a catastrophic event would force action. "
            "Local authority and contractor records showed cost-driven substitution of non-compliant materials. "
            "Fire service guidance on stay-put policy was not reassessed for the changed facade risk profile. "
            "The public inquiry documented regulatory gaps, ignored resident dissent, and fragmented enforcement."
        ),
    },
    {
        "case_id": "bristol-heart-1990s",
        "title": "Bristol Royal Infirmary Paediatric Heart Surgery",
        "country": "UK",
        "year": 1995,
        "text": (
            "Paediatric heart surgery at Bristol Royal Infirmary had mortality rates far above national benchmarks for years. "
            "Consultants and audit data signaling poor outcomes were not escalated to external review promptly. "
            "Hospital management prioritized maintaining the surgical program over transparent performance reporting. "
            "Families were not informed that safer treatment options existed at other centres. "
            "The Kennedy Inquiry found a club culture, weak clinical governance, and suppression of uncomfortable statistics."
        ),
    },
    {
        "case_id": "volkswagen-dieselgate-2015",
        "title": "Volkswagen Diesel Emissions Fraud",
        "country": "Germany",
        "year": 2015,
        "text": (
            "Volkswagen installed defeat-device software that reduced NOx emissions only during laboratory testing. "
            "Engineers and compliance staff knew real-world emissions exceeded legal limits by large margins. "
            "Management pursued aggressive diesel market share targets across EU and US regulatory regimes. "
            "Regulators received consumer complaints and independent tests before the EPA issued a notice of violation. "
            "Investigations found coordinated concealment of engineering workarounds and delayed disclosure to authorities."
        ),
    },
    {
        "case_id": "mad-cow-bse-1996",
        "title": "BSE / Mad Cow Disease and Public Health Response",
        "country": "UK",
        "year": 1996,
        "text": (
            "British cattle were fed rendered ruminant protein linked to bovine spongiform encephalopathy transmission. "
            "Advisory committees warned of possible human risk years before variant CJD cases were confirmed. "
            "Ministers publicly reassured consumers that beef was safe while internal briefings noted uncertainty. "
            "EU partners imposed export bans citing delayed UK notification and incomplete data sharing. "
            "The Phillips Inquiry found failure to communicate known risks and slow adaptation of precautionary policy."
        ),
    },
    {
        "case_id": "greek-debt-crisis-2010",
        "title": "Greek Sovereign Debt Crisis and EU Troika",
        "country": "EU",
        "year": 2010,
        "text": (
            "Eurostat and EU finance ministries discovered Greece had understated deficits using off-market swaps. "
            "ECB, IMF, and European Commission imposed austerity programs with limited debtor-state negotiation leverage. "
            "Independent economists warned that fiscal contraction would deepen recession and impair debt sustainability. "
            "National parliaments faced compressed timetables to approve memoranda under market pressure. "
            "Post-crisis reviews cited asymmetric information, inter-institutional conflict, and weak early-warning integration."
        ),
    },
    {
        "case_id": "fukushima-2011",
        "title": "Fukushima Daiichi Nuclear Disaster",
        "country": "Japan",
        "year": 2011,
        "text": (
            "The Tohoku earthquake and tsunami disabled cooling at Fukushima Daiichi nuclear reactors. "
            "Operator TEPCO and regulators had previously discounted tsunami heights above design basis in risk assessments. "
            "Emergency command structures struggled to obtain reliable plant status during the first critical hours. "
            "Public communications alternated between reassurance and evacuation orders as radiation releases spread. "
            "Investigation commissions found regulatory capture, ignored historical dissent, and inadequate disaster preparedness."
        ),
    },
    {
        "case_id": "rwanda-un-1994",
        "title": "Rwanda Genocide — UN Peacekeeping Failure",
        "country": "International",
        "year": 1994,
        "text": (
            "UNAMIR force commander Dallaire warned headquarters of Hutu extremist militia preparations for mass killing. "
            "Security Council members reduced troop levels despite cables describing imminent genocide risk. "
            "Peacekeepers were ordered not to intervene when weapons caches were discovered before the killing began. "
            "Media and NGO reports documented massacres while diplomatic channels debated mandate language. "
            "Subsequent UN reports found failure to act on early intelligence and bureaucratic avoidance of escalation."
        ),
    },
]


def main() -> None:
    init_db()
    orch = Orchestrator(init_llm=False)

    for case in SEED_CASES:
        print(f"  -> {case['case_id']} ...", end=" ", flush=True)
        result = orch.run_from_text(
            case_id=case["case_id"],
            raw_text=case["text"],
            title=case["title"],
            country=case["country"],
            year=case["year"],
            engine_only=True,
            verbose=False,
        )
        top = result.top_modes[0] if result.top_modes else None
        print(
            f"top={top.mode_id if top else 'none'} mu={top.mu:.3f} "
            f"cat={result.cat.catastrophe_hypothesis} "
            f"cep={result.wms.cep:.3f}"
        )

    print(f"\nDone. {len(SEED_CASES)} cases saved to DB.")


if __name__ == "__main__":
    main()
