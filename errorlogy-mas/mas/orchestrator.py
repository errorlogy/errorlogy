from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from contextlib import nullcontext
from typing import Callable

from .engine import ENGINE_VERSION
from .engine.types import EngineWarnings, FuzzyContext
from .engine.wms_vocabulary import ingest_metadata_to_signals, merge_weak_signals
from . import metrics as pipeline_metrics
from . import db as case_db
from .schemas.case import GovernanceCase, WeakSignal
from .schemas.analysis import CaseAnalysis, LBIResult
from .agents import (
    ScoutAgent, FuzzyClassifierAgent, AlphaPropagationAgent,
    WMSAgent, PNOAgent, ACCAgent, EGDAgent, T4DAgent,
    CATAgent, FPDAgent, LBIAgent, RedTeamAgent,
    NeutralityAuditorAgent, CardCompilerAgent,
)
from .agents.base import set_router
from .providers import build_router
from .config import Config

console = Console()


def _step_context(on_step: Callable | None):
    if on_step:
        return _StepListener(on_step)
    return nullcontext()


class _StepListener:
    def __init__(self, on_step: Callable) -> None:
        self._on_step = on_step

    def __enter__(self):
        pipeline_metrics.set_step_listener(self._on_step)
        return self

    def __exit__(self, *args):
        pipeline_metrics.set_step_listener(None)
        return False

class Orchestrator:
    """
    Runs the full Errorlogy pipeline for a governance case:
    DATA → WMS → μ → α → ACC → PNO → FPD → LBI → public card
    """

    def __init__(self, *, init_llm: bool = True) -> None:
        if init_llm:
            cfg = Config()
            router = build_router(cfg)
            set_router(router)
            console.print(f"  [dim]providers online: {', '.join(router.available)}[/dim]")
        self.scout = ScoutAgent()
        self.wms = WMSAgent()
        self.classifier = FuzzyClassifierAgent()
        self.alpha = AlphaPropagationAgent()
        self.pno = PNOAgent()
        self.acc = ACCAgent()
        self.egd = EGDAgent()
        self.t4d = T4DAgent()
        self.cat = CATAgent()
        self.fpd = FPDAgent()
        self.lbi = LBIAgent()
        self.red_team = RedTeamAgent()
        self.neutrality = NeutralityAuditorAgent()
        self.card = CardCompilerAgent()

    def _run_analytics(
        self,
        case: GovernanceCase,
        warnings: EngineWarnings,
        verbose: bool,
        progress=None,
        steps: list[str] | None = None,
    ):
        def step(name: str):
            if progress and steps:
                progress.update(progress.task_ids[0], description=f"[{steps.index(name)+1}/{len(steps)}] {name}")
                progress.advance(progress.task_ids[0])

        step("WMS — detecting weak signals")
        with pipeline_metrics.track_engine("wms"):
            wms_result = self.wms.run(case)
        _log(verbose, "wms", f"MSI={wms_result.msi:.2f} CEP={wms_result.cep:.2f}")

        step("Classifier — fuzzy mode scoring")
        ctx = FuzzyContext(wms_msi=wms_result.msi)
        with pipeline_metrics.track_engine("classifier"):
            top_modes = self.classifier.run(case, ctx=ctx, warnings=warnings)
        top_label = top_modes[0].mode_id if top_modes else "none"
        top_mu = top_modes[0].mu if top_modes else 0.0
        _log(verbose, "classifier", f"{len(top_modes)} modes scored, top={top_label} mu={top_mu:.2f}")

        step("Alpha — propagating μ through graph")
        with pipeline_metrics.track_engine("alpha"):
            alpha_result = self.alpha.run(top_modes, warnings=warnings)
        _log(verbose, "alpha", f"{len(alpha_result.activated_edges)} edges activated")

        step("PNO — scoring system regime")
        with pipeline_metrics.track_engine("pno"):
            pno_result = self.pno.run(
                alpha_result.top_modes,
                case.description,
                propagated_mu=alpha_result.propagated_mu,
            )
        _log(verbose, "pno", f"dominant={pno_result.dominant_pno}")

        step("ACC — identifying contribution clusters")
        with pipeline_metrics.track_engine("acc"):
            acc_result = self.acc.run(alpha_result.propagated_mu, case.description, case=case)
        _log(verbose, "acc", f"max cluster={acc_result.max_contribution_cluster.cluster_id}")

        step("EGD — echo-room dynamics")
        with pipeline_metrics.track_engine("egd"):
            egd_result = self.egd.run(case, alpha_result.top_modes, warnings=warnings)
        _log(verbose, "egd", f"echo_pressure={egd_result.echo_room_pressure:.2f}")

        step("T4D — building temporal worldline")
        with pipeline_metrics.track_engine("t4d"):
            t4d_result = self.t4d.run(case, wms_result)
        ctx_boost = FuzzyContext(
            wms_msi=wms_result.msi,
            t4d_latency_risk=t4d_result.warning_to_action_latency_risk,
        )
        _log(verbose, "t4d", f"{len(t4d_result.worldline)} worldline points")

        step("CAT — catastrophe hypothesis")
        with pipeline_metrics.track_engine("cat"):
            cat_result = self.cat.run(wms_result, t4d_result, pno_result, acc_result)
        _log(verbose, "cat", f"hypothesis={cat_result.catastrophe_hypothesis}")

        step("FPD — fuzzy forecast")
        with pipeline_metrics.track_engine("fpd"):
            fpd_result = self.fpd.run(alpha_result, wms_result, pno_result, cat_result)
        _log(verbose, "fpd", f"horizon={fpd_result.horizon}")

        return wms_result, alpha_result, pno_result, acc_result, egd_result, t4d_result, cat_result, fpd_result, ctx_boost

    def run_engine_from_case(
        self, case: GovernanceCase, verbose: bool = False, on_step: Callable | None = None,
    ) -> CaseAnalysis:
        """Deterministic analytics path — no LLM calls."""
        with _step_context(on_step):
            pipeline_metrics.start_run(case.case_id, engine_only=True)
            warnings = EngineWarnings()
            try:
                (
                    wms_result, alpha_result, pno_result, acc_result,
                    egd_result, t4d_result, cat_result, fpd_result, _,
                ) = self._run_analytics(case, warnings, verbose)

                result = CaseAnalysis(
                    case_id=case.case_id,
                    top_modes=alpha_result.top_modes,
                    wms=wms_result,
                    alpha=alpha_result,
                    pno=pno_result,
                    acc=acc_result,
                    egd=egd_result,
                    t4d=t4d_result,
                    cat=cat_result,
                    fpd=fpd_result,
                    lbi=LBIResult(alternatives=[]),
                    public_explanation="",
                    red_team_notes=[],
                    neutrality_flags=[],
                    metadata=_build_metadata(warnings, engine_only=True),
                )
                pipeline_metrics.finish_run(status="ok")
                _persist_result(case, result, engine_only=True)
                return result
            except Exception:
                pipeline_metrics.finish_run(status="error")
                raise

    def run_from_text(
        self,
        case_id: str,
        raw_text: str,
        title: str = "",
        country: str = "",
        year: int = 0,
        verbose: bool = True,
        engine_only: bool = False,
        structure_only: bool = False,
        ingest_metadata: dict | None = None,
        enrich_sources: bool = False,
        discover_num_results: int = 3,
        on_step: Callable | None = None,
    ) -> CaseAnalysis:
        with _step_context(on_step):
            discovery_meta: dict | None = None
            if enrich_sources:
                from .ingest.source_discovery import enrich_source_bundle

                raw_text, hits, provider = enrich_source_bundle(
                    raw_text,
                    title=title,
                    country=country,
                    year=year,
                    num_results=discover_num_results,
                )
                discovery_meta = {
                    "provider": provider,
                    "hits": len(hits),
                    "urls": [h.get("url", "") for h in hits if h.get("url")],
                }
                _log(verbose, "discover", f"{len(hits)} supplemental sources via {provider or 'none'}")

            ingest_signals = ingest_metadata_to_signals(ingest_metadata)
            if engine_only and not structure_only:
                case = GovernanceCase(
                    case_id=case_id,
                    title=title or case_id,
                    description=raw_text[:500],
                    country=country,
                    domain="governance",
                    year=year,
                    source_text=raw_text,
                    weak_signals=merge_weak_signals(
                        _heuristic_weak_signals(raw_text),
                        ingest_signals,
                    ),
                )
                result = self.run_engine_from_case(case, verbose=verbose, on_step=on_step)
                if discovery_meta:
                    meta = dict(result.metadata or {})
                    meta["source_discovery"] = discovery_meta
                    result.metadata = meta
                return result

            if engine_only and structure_only:
                return self._run_structure_then_engine(
                    case_id, raw_text, title, country, year, verbose=verbose,
                    ingest_signals=ingest_signals, discovery_meta=discovery_meta,
                    on_step=on_step,
                )

            steps = [
                "Scout — extracting case structure",
                "WMS — detecting weak signals",
                "Classifier — fuzzy mode scoring",
                "Alpha — propagating μ through graph",
                "PNO — scoring system regime",
                "ACC — identifying contribution clusters",
                "EGD — echo-room dynamics",
                "T4D — building temporal worldline",
                "CAT — catastrophe hypothesis",
                "FPD — fuzzy forecast",
                "LBI — betterment alternatives",
                "Red Team — adversarial review",
                "Card Compiler — generating public card",
                "Neutrality Audit — language check",
            ]

            warnings = EngineWarnings()
            pipeline_metrics.start_run(case_id, engine_only=False)

            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold cyan]{task.description}"),
                    transient=True,
                    disable=not verbose,
                ) as progress:
                    task = progress.add_task("", total=len(steps))

                    def step(name: str):
                        progress.update(task, description=f"[{steps.index(name)+1}/{len(steps)}] {name}")
                        progress.advance(task)

                    step("Scout — extracting case structure")
                    case = self.scout.run(case_id, raw_text, title, country, year)
                    if ingest_signals:
                        case = case.model_copy(
                            update={"weak_signals": merge_weak_signals(case.weak_signals, ingest_signals)}
                        )
                    _log(verbose, "scout", f"{len(case.weak_signals)} weak signals extracted")

                    (
                        wms_result, alpha_result, pno_result, acc_result,
                        egd_result, t4d_result, cat_result, fpd_result, _,
                    ) = self._run_analytics(case, warnings, verbose, progress, steps)

                    step("LBI — betterment alternatives")
                    lbi_result = self.lbi.run(case, pno_result, acc_result, cat_result)
                    _log(verbose, "lbi", f"{len(lbi_result.alternatives)} alternatives")

                    step("Red Team — adversarial review")
                    red_notes = self.red_team.run(case, alpha_result.top_modes, pno_result, acc_result)
                    red_notes = list(red_notes) + warnings.flags
                    _log(verbose, "red_team", f"{len(red_notes)} issues flagged")

                    step("Card Compiler — generating public card")
                    public_card = self.card.run(
                        case, alpha_result.top_modes, wms_result, pno_result,
                        acc_result, t4d_result, cat_result, fpd_result, lbi_result,
                    )

                    step("Neutrality Audit — language check")
                    neutrality_flags = self.neutrality.run(public_card)
                    _log(verbose, "neutrality", f"{len(neutrality_flags)} language flags")

                    meta = _build_metadata(warnings, engine_only=False)
                    if discovery_meta:
                        meta["source_discovery"] = discovery_meta
                    result = CaseAnalysis(
                        case_id=case_id,
                        top_modes=alpha_result.top_modes,
                        wms=wms_result,
                        alpha=alpha_result,
                        pno=pno_result,
                        acc=acc_result,
                        egd=egd_result,
                        t4d=t4d_result,
                        cat=cat_result,
                        fpd=fpd_result,
                        lbi=lbi_result,
                        public_explanation=public_card,
                        red_team_notes=red_notes,
                        neutrality_flags=neutrality_flags,
                        metadata=meta,
                    )
                    pipeline_metrics.finish_run(status="ok")
                    _persist_result(case, result, engine_only=False)
                    return result
            except Exception:
                pipeline_metrics.finish_run(status="error")
                raise

    def run_dual(
        self,
        case_id: str,
        raw_text: str,
        title: str = "",
        country: str = "",
        year: int = 0,
        verbose: bool = False,
        on_step: Callable | None = None,
    ) -> CaseAnalysis:
        """Run engine_only then full pipeline; attach diff in metadata."""
        from .dual_run import apply_dual_run_flags, compute_dual_run_diff

        engine_result = self.run_from_text(
            case_id=case_id,
            raw_text=raw_text,
            title=title,
            country=country,
            year=year,
            verbose=verbose,
            engine_only=True,
            on_step=on_step,
        )
        full_result = self.run_from_text(
            case_id=case_id,
            raw_text=raw_text,
            title=title,
            country=country,
            year=year,
            verbose=verbose,
            engine_only=False,
            on_step=on_step,
        )
        diff = compute_dual_run_diff(engine_result, full_result)
        full_result = apply_dual_run_flags(full_result, diff)
        meta = dict(full_result.metadata or {})
        meta["dual_run_diff"] = diff
        meta["engine_only_snapshot"] = {
            "top_modes": [m.model_dump() for m in engine_result.top_modes[:5]],
            "dominant_pno": engine_result.pno.dominant_pno,
            "cat": engine_result.cat.catastrophe_hypothesis,
        }
        full_result.metadata = meta
        case_db.save_case(
            case_id=case_id,
            title=title or case_id,
            country=country,
            year=year,
            engine_only=False,
            result=full_result.model_dump(),
        )
        return full_result

    def _run_structure_then_engine(
        self,
        case_id: str,
        raw_text: str,
        title: str,
        country: str,
        year: int,
        verbose: bool,
        ingest_signals: list[WeakSignal] | None = None,
        discovery_meta: dict | None = None,
        on_step: Callable | None = None,
    ) -> CaseAnalysis:
        """LightweightScout: one LLM call for structure, then deterministic engine."""
        with _step_context(on_step):
            pipeline_metrics.start_run(case_id, engine_only=True)
            warnings = EngineWarnings()
            try:
                case = self.scout.run(case_id, raw_text, title, country, year)
                if ingest_signals:
                    case = case.model_copy(
                        update={"weak_signals": merge_weak_signals(case.weak_signals, ingest_signals)}
                    )
                _log(verbose, "scout", f"{len(case.weak_signals)} weak signals (structure_only)")
                (
                    wms_result, alpha_result, pno_result, acc_result,
                    egd_result, t4d_result, cat_result, fpd_result, _,
                ) = self._run_analytics(case, warnings, verbose)
                meta = _build_metadata(warnings, engine_only=True, structure_only=True)
                if discovery_meta:
                    meta["source_discovery"] = discovery_meta
                result = CaseAnalysis(
                    case_id=case_id,
                    top_modes=alpha_result.top_modes,
                    wms=wms_result,
                    alpha=alpha_result,
                    pno=pno_result,
                    acc=acc_result,
                    egd=egd_result,
                    t4d=t4d_result,
                    cat=cat_result,
                    fpd=fpd_result,
                    lbi=LBIResult(alternatives=[]),
                    public_explanation="",
                    red_team_notes=[],
                    neutrality_flags=[],
                    metadata=meta,
                )
                pipeline_metrics.finish_run(status="ok")
                _persist_result(case, result, engine_only=True)
                return result
            except Exception:
                pipeline_metrics.finish_run(status="error")
                raise

    def run_from_case(self, case: GovernanceCase, verbose: bool = True, engine_only: bool = False) -> CaseAnalysis:
        if engine_only:
            return self.run_engine_from_case(case, verbose=verbose)
        return self.run_from_text(
            case_id=case.case_id,
            raw_text=case.source_text,
            title=case.title,
            country=case.country,
            year=case.year,
            verbose=verbose,
        )


def _persist_result(case: GovernanceCase, result: CaseAnalysis, *, engine_only: bool) -> None:
    try:
        case_db.save_case(
            case_id=case.case_id,
            title=case.title,
            country=case.country,
            year=case.year,
            engine_only=engine_only,
            result=result.model_dump(),
        )
    except Exception:
        pass


def _build_metadata(
    warnings: EngineWarnings,
    *,
    engine_only: bool,
    structure_only: bool = False,
) -> dict:
    run = pipeline_metrics.last_run()
    meta: dict = {
        "engine": ENGINE_VERSION,
        "engine_warnings": warnings.flags,
        "pipeline_metrics": pipeline_metrics.run_to_dict(run) if run else None,
    }
    if engine_only:
        meta["engine_only"] = True
    if structure_only:
        meta["structure_only"] = True
    return meta


def _heuristic_weak_signals(text: str) -> list[WeakSignal]:
    """Fallback weak-signal extraction when Scout/LLM is skipped."""
    signals = []
    rules = [
        ("WMS-003", ("dissent", "overruled", "engineers opposed")),
        ("WMS-006", ("schedule", "pressure", "launch")),
        ("WMS-011", ("not conveyed", "not transmitted", "opacity")),
        ("WMS-013", ("ignored", "warning", "memo")),
    ]
    lower = text.lower()
    for wms_id, kws in rules:
        if any(k in lower for k in kws):
            signals.append(
                WeakSignal(
                    signal_type=wms_id,
                    description=f"Heuristic detection of {wms_id}",
                    source_environment="media_investigative",
                    strength=0.6,
                    reliability=0.5,
                    temporal_relevance=0.7,
                )
            )
    return signals


def _log(verbose: bool, agent: str, msg: str) -> None:
    if verbose:
        console.print(f"  [green]ok[/green] [dim]{agent}[/dim]: {msg}")
