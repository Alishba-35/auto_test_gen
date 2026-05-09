"""
generator.py — Test & Conftest Generator (v2)

Returns both a pytest test file and a conftest.py.
All Jinja2 filter functions are defined ABOVE generate_tests()
so they are resolvable when env.filters is populated.
"""

import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .parser import parse_source, FunctionInfo, ClassInfo
from typing import List, Tuple, Dict


# ─────────────────────────────────────────────────────────────────────────────
#  Jinja2 filter helpers  (must be defined before generate_tests)
# ─────────────────────────────────────────────────────────────────────────────

def _title(name: str) -> str:
    """snake_case → TitleCase for class names."""
    return "".join(part.capitalize() for part in name.split("_"))


def _safe_exc(exc: str) -> str:
    """ValueError → value_error  (for test method names)."""
    base = exc.split("(")[0].strip()
    out = []
    for i, ch in enumerate(base):
        if ch.isupper() and i > 0:
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


def _firstline(s: str) -> str:
    """Return only the first line of a docstring (avoids multi-line in comments)."""
    return (s or "").splitlines()[0][:120] if s else ""


def _fixture_val(p) -> str:
    """
    For fixture construction, prefer alt_value when sample_value is a
    trivially falsy literal (0, 0.0, '', [], {}, False, None).

    Why: a fixture built with a falsy default (e.g. BankAccount(balance=0.0))
    will immediately fail tests that require state — withdraw(9.99) raises
    'Insufficient funds' before the test body even runs.
    Using alt_value (e.g. 99.9) gives the fixture realistic starting state.
    """
    falsy_literals = {"0", "0.0", '""', "''", "[]", "{}", "False", "None"}
    return p.alt_value if p.sample_value in falsy_literals else p.sample_value


# ─────────────────────────────────────────────────────────────────────────────
#  Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def generate_tests(
    source_code: str,
    module_name: str,
    template_dir: str,
) -> Tuple[str, str, List[FunctionInfo], dict]:
    """
    Parse source_code and render a pytest test file + conftest.py.

    Returns:
        (test_code, conftest_code, all_functions, stats_dict)
    """
    functions, classes = parse_source(source_code)

    # __init__ is excluded from test generation (no return value to assert on)
    testable = [f for f in functions if not f.is_init]

    top_level_funcs = [f.name for f in testable if not f.is_method]
    class_names     = list(dict.fromkeys(
        f.class_name for f in testable if f.is_method
    ))
    has_async = any(f.is_async for f in testable)

    stats = {
        "total_functions":   len(functions),
        "testable":          len(testable),
        "top_level":         len(top_level_funcs),
        "methods":           len(testable) - len(top_level_funcs),
        "with_type_hints":   sum(
            1 for f in testable
            if f.return_annotation or any(p.annotation for p in f.params)
        ),
        "with_raises":       sum(1 for f in testable if f.raises),
        "triggers_resolved": sum(1 for f in testable if f.raise_triggers),
        "async_functions":   sum(1 for f in testable if f.is_async),
        "classes":           len(class_names),
    }

    env = Environment(
        loader            = FileSystemLoader(template_dir),
        autoescape        = select_autoescape([]),
        trim_blocks       = True,
        lstrip_blocks     = True,
        keep_trailing_newline = True,
    )

    # Register all filters — every filter used in .j2 templates must appear here
    env.filters["title_name"]  = _title
    env.filters["safe_exc"]    = _safe_exc
    env.filters["firstline"]   = _firstline
    env.filters["fixture_val"] = _fixture_val

    ctx = dict(
        module_name     = module_name,
        functions       = testable,
        top_level_funcs = top_level_funcs,
        class_names     = class_names,
        classes         = classes,
        has_functions   = bool(top_level_funcs),
        has_classes     = bool(class_names),
        has_async       = has_async,
    )

    test_code     = env.get_template("test_template.j2").render(**ctx)
    conftest_code = env.get_template("conftest_template.j2").render(**ctx)

    return test_code, conftest_code, functions, stats