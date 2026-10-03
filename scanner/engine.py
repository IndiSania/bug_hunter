import ast
from pathlib import Path

SEVERITY_WEIGHT = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}

def finding(rule, severity, message, path, line, suggestion):
    return {
        "rule": rule,
        "severity": severity,
        "message": message,
        "file": str(path),
        "line": line or 1,
        "suggestion": suggestion
    }

class Analyzer(ast.NodeVisitor):
    def __init__(self, source, path):
        self.source = source
        self.path = path
        self.findings = []
        self.lines = source.splitlines()

    def add(self, rule, severity, message, node, suggestion):
        self.findings.append(finding(rule, severity, message, self.path, getattr(node, "lineno", 1), suggestion))

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
            self.add("BH001", "critical", f"Penggunaan {node.func.id}() dapat mengeksekusi kode secara dinamis.", node,
                     "Hindari eksekusi kode dinamis; gunakan parser atau whitelist input.")
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            self.add("BH006", "info", "print() ditemukan di source code.", node,
                     "Gunakan logging untuk aplikasi yang akan diproduksikan.")
        if isinstance(node.func, ast.Attribute) and node.func.attr in {"run", "Popen", "call", "check_output"}:
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    self.add("BH002", "high", "subprocess dipanggil dengan shell=True.", node,
                             "Hindari shell=True atau validasi input dengan ketat dan gunakan argumen terpisah.")
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        if node.type is None:
            self.add("BH003", "medium", "Bare except menangkap semua exception tanpa spesifikasi.", node,
                     "Tangkap exception yang spesifik dan jangan menyembunyikan kesalahan.")
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if len(node.args.defaults) > 0:
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    self.add("BH004", "high", "Mutable object digunakan sebagai default argument.", node,
                             "Gunakan None sebagai default lalu buat object baru di dalam fungsi.")
        end = getattr(node, "end_lineno", node.lineno)
        if end - node.lineno + 1 > 60:
            self.add("BH008", "medium", f"Fungsi '{node.name}' memiliki lebih dari 60 baris.", node,
                     "Pecah fungsi besar menjadi beberapa fungsi yang lebih kecil.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if any(alias.name == "*" for alias in node.names):
            self.add("BH005", "medium", "Wildcard import (*) membuat dependensi kode sulit dilacak.", node,
                     "Import hanya nama yang benar-benar digunakan.")
        self.generic_visit(node)

    def visit_Assert(self, node):
        self.add("BH007", "low", "assert ditemukan pada source code.", node,
                 "Untuk validasi runtime, gunakan exception handling eksplisit.")
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store) and len(node.id) == 1 and node.id not in {"i", "j", "k", "_"}:
            self.add("BH009", "info", f"Nama variabel '{node.id}' terlalu singkat.", node,
                     "Gunakan nama variabel yang lebih deskriptif.")
        self.generic_visit(node)

def scan_file(path):
    path = Path(path)
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"error": str(e), "findings": [], "files_scanned": 0, "lines": 0}

    findings = []
    try:
        tree = ast.parse(source)
        analyzer = Analyzer(source, path.name)
        analyzer.visit(tree)
        findings.extend(analyzer.findings)
    except SyntaxError as e:
        findings.append(finding("BH000", "critical", f"SyntaxError: {e.msg}", path.name, e.lineno or 1,
                                "Perbaiki kesalahan sintaks pada baris yang ditunjukkan."))

    text_upper = source.upper()
    for marker in ("TODO", "FIXME"):
        for idx, line in enumerate(source.splitlines(), 1):
            if marker in line.upper():
                findings.append(finding("BH010", "low", f"Komentar {marker} ditemukan.", path.name, idx,
                                        "Tinjau kembali pekerjaan yang masih tertunda sebelum rilis."))

    return build_result(findings, 1, len(source.splitlines()))

def scan_project(root):
    findings, files, lines = [], 0, 0
    root = Path(root)
    for path in root.rglob("*.py"):
        if any(part in {".venv", "venv", "__pycache__", ".git", "node_modules"} for part in path.parts):
            continue
        result = scan_file(path)
        files += 1
        lines += result.get("lines", 0)
        for item in result.get("findings", []):
            try:
                item["file"] = str(Path(item["file"]))
            except Exception:
                pass
            findings.append(item)
    return build_result(findings, files, lines)

def build_result(findings, files, lines):
    counts = {s: 0 for s in ("critical", "high", "medium", "low", "info")}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    score = max(0, 100 - sum(SEVERITY_WEIGHT[f["severity"]] for f in findings) * 3)
    return {
        "files_scanned": files,
        "lines": lines,
        "findings": findings,
        "counts": counts,
        "total": len(findings),
        "score": score
    }
