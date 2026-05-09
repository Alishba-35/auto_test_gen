"""
parser.py — Python AST Parser (v2 — production rebuild)

New in v2:
  • RaiseTrigger: analyses if-conditions to extract REAL triggering values
  • ClassInfo:    introspects __init__ so fixtures are instantiated correctly
  • __init__      is flagged is_init=True — excluded from test generation
  • _extract_raise_message: pulls literal string out of raise Exc("msg")
  • _condition_to_trigger: handles ==, <, <=, >, >=, is None, not x,
    len(x)==0, BoolOp(and/or) chains
"""

import ast
from dataclasses import dataclass, field
from typing import Optional, List, Dict


# ─────────────────────────────────────────────────────────────────────────────
#  Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ParamInfo:
    name: str
    annotation: Optional[str] = None
    default: Optional[str]    = None
    has_default: bool          = False
    sample_value: str          = '"test_value"'
    alt_value: str             = '"alt_value"'   # second distinct value for parametrize
    kind: str                  = "other"         # numeric|string|list|dict|bool|other


@dataclass
class RaiseTrigger:
    exc_name: str              # "ValueError"
    exc_message: Optional[str] # literal string from raise Exc("msg"), or None
    param_name: str            # which param to override
    trigger_value: str         # concrete value that triggers the raise
    condition_desc: str        # human-readable: "amount <= 0"


@dataclass
class FunctionInfo:
    name: str
    params: List[ParamInfo]              = field(default_factory=list)
    return_annotation: Optional[str]     = None
    docstring: Optional[str]             = None
    raises: List[str]                    = field(default_factory=list)
    raise_triggers: List[RaiseTrigger]   = field(default_factory=list)
    is_method: bool      = False
    class_name: Optional[str] = None
    line_no: int         = 0
    is_static: bool      = False
    is_classmethod: bool = False
    is_async: bool       = False
    is_init: bool        = False   # __init__ — skipped in test generation


@dataclass
class ClassInfo:
    name: str
    constructor_params: List[ParamInfo] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
#  Low-level helpers
# ─────────────────────────────────────────────────────────────────────────────

def _annotation_str(node) -> Optional[str]:
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return None


def _default_str(node) -> Optional[str]:
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return None


def _extract_raise_message(exc_node) -> Optional[str]:
    """Return the first string arg of raise Exc("msg"), or None."""
    if exc_node is None:
        return None
    if isinstance(exc_node, ast.Call) and exc_node.args:
        first = exc_node.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value
    return None


def _collect_raises(func_node) -> List[str]:
    seen, result = set(), []
    for child in ast.walk(func_node):
        if isinstance(child, ast.Raise) and child.exc is not None:
            try:
                cls_name = ast.unparse(child.exc).split("(")[0].strip()
                if cls_name and cls_name not in seen:
                    seen.add(cls_name)
                    result.append(cls_name)
            except Exception:
                pass
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  Sample / alt value inference
# ─────────────────────────────────────────────────────────────────────────────

def _infer_sample(annotation: Optional[str], name: str):
    """Return (sample, alt, kind) for a param."""
    n = name.lower()

    if annotation:
        a = annotation.lower().replace(" ", "")
        if a in ("int", "integer"):
            return "1", "100", "numeric"
        if a == "float":
            return "1.5", "99.9", "numeric"
        if a in ("str", "string"):
            return '"hello"', '"world"', "string"
        if a in ("bool", "boolean"):
            return "True", "False", "bool"
        if a.startswith("list") or a == "list":
            return "[1, 2, 3]", "[10, 20]", "list"
        if a.startswith("dict") or a == "dict":
            return '{"key": "value"}', '{"x": 1}', "dict"
        if a.startswith("tuple") or a == "tuple":
            return "(1, 2)", "(3, 4)", "other"
        if a.startswith("set") or a == "set":
            return "{1, 2}", "{3, 4}", "other"
        if "optional" in a:
            return "None", "None", "other"
        if "bytes" in a:
            return 'b"hello"', 'b"world"', "other"
        if "callable" in a or "function" in a:
            return "lambda x: x", "lambda x: x * 2", "other"

    if any(k in n for k in ["num", "count", "size", "length", "age",
                              "index", "limit", "offset", "page", "score",
                              "qty", "quantity", "total"]):
        return "5", "10", "numeric"
    if "id" in n:
        return "1", "42", "numeric"
    if any(k in n for k in ["max", "min"]):
        return "10", "100", "numeric"
    if any(k in n for k in ["price", "rate", "amount", "percent", "ratio",
                              "weight", "height", "width", "lat", "lon", "balance"]):
        return "9.99", "100.0", "numeric"
    if any(k in n for k in ["name", "text", "msg", "message", "label",
                              "title", "desc", "content", "body", "subject",
                              "query", "keyword", "url", "path", "email",
                              "username", "tag"]):
        return '"hello"', '"world"', "string"
    if "key" in n:
        return '"my_key"', '"other_key"', "string"
    if any(k in n for k in ["owner", "user", "author", "sender"]):
        return '"alice"', '"bob"', "string"
    if n.startswith("is_") or n.startswith("has_") or any(
            k in n for k in ["flag", "enabled", "active", "valid",
                              "visible", "hidden", "checked", "selected"]):
        return "True", "False", "bool"
    if any(k in n for k in ["items", "elements", "values", "numbers",
                              "strings", "arr", "array", "lst", "rows",
                              "entries", "results"]):
        return "[1, 2, 3]", "[10, 20]", "list"
    if any(k in n for k in ["config", "options", "settings", "headers",
                              "data", "payload", "info", "meta", "attrs",
                              "attributes", "params", "kwargs"]):
        return '{"key": "value"}', '{"x": 1}', "dict"
    if any(k in n for k in ["callback", "func", "fn", "handler"]):
        return "lambda x: x", "lambda x: x * 2", "other"

    return '"test_value"', '"other_value"', "other"


def _falsy_value(p: ParamInfo) -> str:
    mapping = {
        "string":  '""',
        "list":    "[]",
        "dict":    "{}",
        "numeric": "0",
        "bool":    "False",
    }
    return mapping.get(p.kind, "None")


# ─────────────────────────────────────────────────────────────────────────────
#  Raise-condition analyser
# ─────────────────────────────────────────────────────────────────────────────

def _op_symbol(op) -> str:
    return {
        ast.Eq: "==", ast.NotEq: "!=",
        ast.Lt: "<",  ast.LtE: "<=",
        ast.Gt: ">",  ast.GtE: ">=",
        ast.Is: "is", ast.IsNot: "is not",
    }.get(type(op), "?")


def _condition_to_trigger(
    test_node,
    param_map: Dict[str, "ParamInfo"],
    exc_name: str,
    exc_msg: Optional[str],
) -> Optional[RaiseTrigger]:
    """
    Given the test node of an ast.If that wraps a raise, return a
    RaiseTrigger with the concrete value that satisfies that condition.

    Patterns:
        name == val      → val
        name != val      → (skip — can't infer without context)
        name < val       → val - 1
        name <= val      → val
        name > val       → val + 1
        name >= val      → val
        name is None     → None
        not name         → falsy value based on kind
        len(name) == 0   → [] / "" / {}
        BoolOp(and/or)   → first resolvable sub-condition
    """

    # ── Compare ───────────────────────────────────────────────────────────────
    if isinstance(test_node, ast.Compare) and len(test_node.ops) == 1:
        left = test_node.left
        op   = test_node.ops[0]
        comp = test_node.comparators[0]

        # name op constant
        if isinstance(left, ast.Name) and left.id in param_map:
            pname = left.id
            p     = param_map[pname]
            try:
                cval_str = ast.unparse(comp)
                cval_lit = ast.literal_eval(comp)
            except Exception:
                return None

            sym  = _op_symbol(op)
            desc = f"{pname} {sym} {cval_str}"

            if isinstance(op, ast.Eq):
                return RaiseTrigger(exc_name, exc_msg, pname, cval_str, desc)

            if isinstance(op, ast.LtE):
                try:
                    trig = str(int(cval_lit)) if p.kind == "numeric" else cval_str
                except Exception:
                    trig = cval_str
                return RaiseTrigger(exc_name, exc_msg, pname, trig, desc)

            if isinstance(op, ast.Lt):
                try:
                    trig = str(int(cval_lit) - 1) if p.kind == "numeric" else cval_str
                except Exception:
                    trig = cval_str
                return RaiseTrigger(exc_name, exc_msg, pname, trig, desc)

            if isinstance(op, ast.GtE):
                try:
                    trig = str(int(cval_lit)) if p.kind == "numeric" else cval_str
                except Exception:
                    trig = cval_str
                return RaiseTrigger(exc_name, exc_msg, pname, trig, desc)

            if isinstance(op, ast.Gt):
                try:
                    trig = str(int(cval_lit) + 1) if p.kind == "numeric" else cval_str
                except Exception:
                    trig = cval_str
                return RaiseTrigger(exc_name, exc_msg, pname, trig, desc)

            # name is None
            if isinstance(op, ast.Is) and isinstance(comp, ast.Constant) and comp.value is None:
                return RaiseTrigger(exc_name, exc_msg, pname, "None", f"{pname} is None")

        # len(name) == 0
        if (
            isinstance(op, ast.Eq)
            and isinstance(comp, ast.Constant) and comp.value == 0
            and isinstance(left, ast.Call)
            and isinstance(left.func, ast.Name) and left.func.id == "len"
            and left.args
            and isinstance(left.args[0], ast.Name)
            and left.args[0].id in param_map
        ):
            pname = left.args[0].id
            trig  = _falsy_value(param_map[pname])
            return RaiseTrigger(exc_name, exc_msg, pname, trig, f"len({pname}) == 0")

    # ── not name ──────────────────────────────────────────────────────────────
    if isinstance(test_node, ast.UnaryOp) and isinstance(test_node.op, ast.Not):
        operand = test_node.operand
        if isinstance(operand, ast.Name) and operand.id in param_map:
            pname = operand.id
            trig  = _falsy_value(param_map[pname])
            return RaiseTrigger(exc_name, exc_msg, pname, trig, f"not {pname}")

    # ── BoolOp ────────────────────────────────────────────────────────────────
    if isinstance(test_node, ast.BoolOp):
        for val in test_node.values:
            r = _condition_to_trigger(val, param_map, exc_name, exc_msg)
            if r:
                return r

    return None


def _analyse_raise_triggers(
    func_node,
    param_map: Dict[str, ParamInfo],
) -> List[RaiseTrigger]:
    triggers: List[RaiseTrigger] = []
    seen_exc: set = set()

    for node in ast.walk(func_node):
        if not isinstance(node, ast.If):
            continue
        for stmt in node.body:
            if not isinstance(stmt, ast.Raise) or stmt.exc is None:
                continue
            try:
                exc_name = ast.unparse(stmt.exc).split("(")[0].strip()
            except Exception:
                continue
            exc_msg = _extract_raise_message(stmt.exc)
            trigger = _condition_to_trigger(node.test, param_map, exc_name, exc_msg)
            if trigger and exc_name not in seen_exc:
                seen_exc.add(exc_name)
                triggers.append(trigger)

    return triggers


# ─────────────────────────────────────────────────────────────────────────────
#  Core: FunctionDef → FunctionInfo
# ─────────────────────────────────────────────────────────────────────────────

def _parse_func_node(node, class_name: Optional[str] = None) -> FunctionInfo:
    args       = node.args
    num_args   = len(args.args)
    num_defs   = len(args.defaults)
    defs_start = num_args - num_defs

    params: List[ParamInfo] = []

    for i, arg in enumerate(args.args):
        if arg.arg in ("self", "cls"):
            continue
        has_default = i >= defs_start
        default_val = _default_str(args.defaults[i - defs_start]) if has_default else None
        annotation  = _annotation_str(arg.annotation)
        sample, alt, kind = _infer_sample(annotation, arg.arg)
        if has_default and default_val is not None:
            sample = default_val
        params.append(ParamInfo(
            name         = arg.arg,
            annotation   = annotation,
            default      = default_val,
            has_default  = has_default,
            sample_value = sample,
            alt_value    = alt,
            kind         = kind,
        ))

    if args.vararg:
        params.append(ParamInfo(
            name="*" + args.vararg.arg,
            annotation=_annotation_str(args.vararg.annotation),
            sample_value="1, 2, 3",
            alt_value="10, 20",
            kind="other",
        ))

    for i, arg in enumerate(args.kwonlyargs):
        kw_def     = args.kw_defaults[i]
        annotation = _annotation_str(arg.annotation)
        sample, alt, kind = _infer_sample(annotation, arg.arg)
        params.append(ParamInfo(
            name         = arg.arg,
            annotation   = annotation,
            default      = _default_str(kw_def),
            has_default  = kw_def is not None,
            sample_value = _default_str(kw_def) or sample,
            alt_value    = alt,
            kind         = kind,
        ))

    param_map = {p.name: p for p in params}

    is_static      = any(isinstance(d, ast.Name) and d.id == "staticmethod"  for d in node.decorator_list)
    is_classmethod = any(isinstance(d, ast.Name) and d.id == "classmethod"   for d in node.decorator_list)
    is_init        = node.name == "__init__"

    return FunctionInfo(
        name              = node.name,
        params            = params,
        return_annotation = _annotation_str(node.returns),
        docstring         = ast.get_docstring(node),
        raises            = _collect_raises(node),
        raise_triggers    = _analyse_raise_triggers(node, param_map),
        is_method         = class_name is not None,
        class_name        = class_name,
        line_no           = node.lineno,
        is_static         = is_static,
        is_classmethod    = is_classmethod,
        is_async          = isinstance(node, ast.AsyncFunctionDef),
        is_init           = is_init,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────────────────────────────

def parse_source(source_code: str):
    """
    Returns (List[FunctionInfo], Dict[str, ClassInfo]).
    Raises ValueError on syntax errors.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError as exc:
        raise ValueError(f"Syntax error: {exc}") from exc

    functions: List[FunctionInfo]    = []
    classes:   Dict[str, ClassInfo]  = {}

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(_parse_func_node(node))

        elif isinstance(node, ast.ClassDef):
            cname       = node.name
            ctor_params: List[ParamInfo] = []

            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    fn = _parse_func_node(item, class_name=cname)
                    functions.append(fn)
                    if item.name == "__init__":
                        ctor_params = fn.params

            classes[cname] = ClassInfo(name=cname, constructor_params=ctor_params)

    return functions, classes