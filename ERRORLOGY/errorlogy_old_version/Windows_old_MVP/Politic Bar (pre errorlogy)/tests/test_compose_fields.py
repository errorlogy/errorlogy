"""Step-2 fix: deterministic composers for residual_uncertainty / analyst_notes.

Free LLM text from the Compiler agent must NOT enter the published card.
These two fields are now built from counter_arguments, verifications,
and run metadata only — see politic_bar/compose.py.
"""

from __future__ import annotations

import inspect

from politic_bar import __version__
from politic_bar.compose import compose_analyst_notes, compose_residual_uncertainty
from politic_bar.models import CounterArgument, VerificationResult


# ---------------------------------------------------------------------------
# residual_uncertainty
# ---------------------------------------------------------------------------

def test_residual_with_no_inputs_emits_explicit_null_statement():
    """Silence is not neutrality — empty inputs must produce a positive
    statement so the field is never just '' on a published card."""
    text = compose_residual_uncertainty([], [])
    assert "No surviving counter-arguments" in text
    assert "asserts what its citations support" in text


def test_residual_lists_surviving_and_defeated_counters():
    counters = [
        CounterArgument(targets="CB-019", target_kind="classification",
                        strongest_counter="alternative procedural reading",
                        does_it_survive=True,
                        tests_run=["5a_lower_layer"]),
        CounterArgument(targets="MP-005", target_kind="classification",
                        strongest_counter="defeated by S4 applicability",
                        does_it_survive=False,
                        tests_run=["5d_S3_downward", "5d_S4_applicability"]),
    ]
    text = compose_residual_uncertainty(counters, [])

    # Survivors
    assert "1 counter-argument(s) survived" in text
    assert "[classification:CB-019]" in text
    assert "alternative procedural reading" in text

    # Defeats — count, target, and applied tests
    assert "1 claim(s) dropped" in text
    assert "classification:MP-005" in text
    assert "5d_S3_downward" in text
    assert "5d_S4_applicability" in text


def test_residual_includes_only_verifier_notes_with_content():
    verifs = [
        VerificationResult(source_id="rogers_v1", excerpt="...",
                           resolves=True, quote_matches=True,
                           notes="locator imprecise — verified to ±2 paragraphs"),
        VerificationResult(source_id="house_99_1016", excerpt="...",
                           resolves=True, quote_matches=True),  # no notes
    ]
    text = compose_residual_uncertainty([], verifs)
    assert "Verifier notes carried forward" in text
    assert "[rogers_v1]" in text
    assert "house_99_1016" not in text


# ---------------------------------------------------------------------------
# analyst_notes — fixed template, no free-text leakage
# ---------------------------------------------------------------------------

def test_analyst_notes_template_shape():
    notes = compose_analyst_notes(
        case_id="TEST-CASE-01",
        counters=[
            CounterArgument(targets="CB-019", does_it_survive=True),
            CounterArgument(targets="SF-009", does_it_survive=False),
        ],
        classifications=[1, 2, 3],
        asymmetry_vectors=[1, 2],
        propagation_links=[1],
    )

    # Stable template anchors — these strings are part of the contract.
    assert f"politic_bar v{__version__}" in notes
    assert "3 classification(s)" in notes
    assert "2 asymmetry vector(s)" in notes
    assert "1 propagation link(s)" in notes
    assert "1 claim(s) dropped" in notes
    assert "cases/TEST-CASE-01/_pipeline/" in notes


def test_analyst_notes_signature_does_not_take_agent_text():
    """Hard contract: only structural inputs. A future regression that
    re-introduces free LLM text would have to add a parameter — and would
    fail this test at code review time."""
    sig = inspect.signature(compose_analyst_notes)
    params = set(sig.parameters)
    assert params == {
        "case_id", "counters", "classifications",
        "asymmetry_vectors", "propagation_links",
    }
