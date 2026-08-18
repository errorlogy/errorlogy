"""
Demo: STS-51L Challenger disaster (1986)
Run: python examples/run_challenger.py
Requires: ANTHROPIC_API_KEY in environment or .env file
"""
import json
import sys
from pathlib import Path

if sys.platform == "win32":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent.parent))

from mas.orchestrator import Orchestrator
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

CHALLENGER_SOURCE = """
The Space Shuttle Challenger (STS-51L) broke apart 73 seconds into its flight on January 28, 1986,
killing all seven crew members. The immediate physical cause was the failure of O-ring seals in
the right solid rocket booster (SRB), which allowed hot gases to escape and ignite the external
fuel tank.

Key documented facts:
- Engineers at Morton Thiokol (O-ring manufacturer) had raised concerns about O-ring performance
  in cold temperatures since 1977. Internal memos documented the risk repeatedly.
- The night before launch (January 27), Thiokol engineers held an emergency teleconference with
  NASA managers. Engineers recommended delaying the launch due to temperatures forecast at 18°F,
  far below any previous launch temperature (53°F was the coldest prior launch).
- NASA managers challenged the engineers' recommendation, inverting the normal burden of proof
  by asking engineers to "prove it was unsafe to fly" rather than "prove it was safe."
- Thiokol management overruled their own engineers after NASA pressure, approving the launch.
  One manager, Jerald Mason, told fellow engineer Roger Boisjoly: "Take off your engineering
  hat and put on your management hat."
- The Rogers Commission investigation found NASA's decision-making process was flawed and that
  the organizational culture suppressed safety concerns in favor of schedule pressure.
- Launch had already been delayed multiple times; there was external pressure to proceed
  (President Reagan was scheduled to mention the mission in the State of the Union address).
- O-ring concerns had been discussed in 13 prior flight readiness reviews without being resolved
  as a critical launch constraint (classified as "Criticality 1" — loss of crew and vehicle).
- Information about O-ring erosion in previous flights was not consistently communicated up
  the management chain; the data existed but was not aggregated in a way that conveyed the pattern.
- NASA's internal safety culture had shifted following Apollo's success; schedule pressure and
  cost concerns had grown significantly by the mid-1980s.
- The accident investigation found evidence of "groupthink" in NASA's decision-making culture,
  where dissenting voices were systematically marginalized over time.
"""


def main():
    engine_only = "--engine-only" in sys.argv

    console.print(Panel.fit(
        "[bold]Errorlogy MAS — Demo Run[/bold]\n"
        "Case: [cyan]US-NASA-1986-CHALLENGER-01[/cyan]\n"
        "STS-51L Space Shuttle Challenger"
        + ("\n[dim]mode: engine_only (no LLM)[/dim]" if engine_only else ""),
        border_style="cyan"
    ))

    orchestrator = Orchestrator(init_llm=not engine_only)

    label = "engine-only analytics" if engine_only else "full pipeline"
    console.print(f"\n[bold yellow]Running {label}...[/bold yellow]\n")

    analysis = orchestrator.run_from_text(
        case_id="US-NASA-1986-CHALLENGER-01",
        raw_text=CHALLENGER_SOURCE,
        title="STS-51L Space Shuttle Challenger Disaster",
        country="USA",
        year=1986,
        verbose=not engine_only,
        engine_only=engine_only,
    )

    console.print("\n" + "-" * 60)
    console.print("[bold green]Pipeline complete.[/bold green]\n")

    # Summary table
    console.print("[bold]Top 5 activated modes (after alpha-propagation):[/bold]")
    for m in analysis.top_modes[:5]:
        bar = "#" * int(m.mu * 20)
        console.print(f"  {m.mode_id:10} mu={m.mu:.2f} [{bar:<20}] {m.name}")

    console.print(f"\n[bold]PNO regime:[/bold] {analysis.pno.dominant_pno}")
    console.print(f"[bold]Max contribution cluster:[/bold] {analysis.acc.max_contribution_cluster.cluster_id} — {analysis.acc.max_contribution_cluster.name}")
    console.print(f"[bold]CAT hypothesis:[/bold] {analysis.cat.catastrophe_hypothesis}")
    console.print(f"[bold]FPD horizon:[/bold] {analysis.fpd.horizon}, confidence={analysis.fpd.confidence:.2f}")

    if analysis.red_team_notes:
        console.print("\n[bold yellow]Red Team flags:[/bold yellow]")
        for note in analysis.red_team_notes:
            console.print(f"  ⚑ {note}")

    if analysis.neutrality_flags:
        console.print("\n[bold red]Neutrality flags:[/bold red]")
        for flag in analysis.neutrality_flags:
            console.print(f"  ⚠ {flag}")

    if analysis.public_explanation:
        console.print("\n[bold]Public Card:[/bold]")
        console.print(Panel(Markdown(analysis.public_explanation), border_style="green"))
    elif engine_only:
        console.print("\n[dim]Public card skipped (engine_only).[/dim]")

    # Save output
    output_path = Path(__file__).parent / "challenger_output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis.model_dump(), f, indent=2, ensure_ascii=False)
    console.print(f"\n[dim]Full analysis saved → {output_path}[/dim]")


if __name__ == "__main__":
    main()
