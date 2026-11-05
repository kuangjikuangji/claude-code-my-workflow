#!/usr/bin/env python3
"""
Quality Scoring System for Academic Research Project (Python + Stata + paper)

Calculates objective quality scores (0-100) based on defined rubrics.
Enforces quality gates: 80 (commit), 90 (submission candidate), 95 (excellence).

Usage:
    python scripts/quality_score.py code/python/00_clean_pollution.py
    python scripts/quality_score.py code/stata/01_main_did.do
    python scripts/quality_score.py paper/main.tex
    python scripts/quality_score.py paper/main.tex --summary
    python scripts/quality_score.py code/python/*.py
"""

import sys
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import re
import json

# ==============================================================================
# SCORING RUBRIC (from .claude/rules/quality-gates.md)
# ==============================================================================

QUARTO_RUBRIC = {
    'critical': {
        'compilation_failure': {'points': 100, 'auto_fail': True},
        'equation_overflow': {'points': 20},
        'broken_citation': {'points': 15},
        'typo_in_equation': {'points': 10},
        'missing_plotly_chart': {'points': 10},
    },
    'major': {
        'text_overflow': {'points': 5},
        'tikz_label_overlap': {'points': 5},
        'notation_inconsistency': {'points': 3},
        'missing_box_separation': {'points': 2},
        'color_contrast_low': {'points': 3},
    },
    'minor': {
        'font_size_reduction': {'points': 1},
        'missing_forward_ref': {'points': 1},
        'missing_framing_sentence': {'points': 1},
    }
}

R_SCRIPT_RUBRIC = {
    'critical': {
        'syntax_error': {'points': 100, 'auto_fail': True},
        'hardcoded_path': {'points': 20},
        'missing_library': {'points': 10},
    },
    'major': {
        'missing_set_seed': {'points': 10},
        'missing_figure': {'points': 5},
        'missing_rds': {'points': 5},
    },
    'minor': {
        'style_violation': {'points': 1},
        'missing_roxygen': {'points': 1},
    }
}

BEAMER_RUBRIC = {
    'critical': {
        'compilation_failure': {'points': 100, 'auto_fail': True},
        'undefined_citation': {'points': 15},
        'overfull_hbox': {'points': 10},
    },
    'major': {
        'text_overflow': {'points': 5},
        'notation_inconsistency': {'points': 3},
    },
    'minor': {
        'font_size_reduction': {'points': 1},
    }
}

# ==============================================================================
# RESEARCH PROJECT RUBRICS (Python + Stata + paper, per quality-gates.md)
# ==============================================================================

PYTHON_RUBRIC = {
    'critical': {
        'syntax_error': {'points': 100, 'auto_fail': True},
        'raw_data_modification': {'points': 30},
        'hardcoded_path': {'points': 20},
    },
    'major': {
        'missing_seed': {'points': 10},
        'missing_header_docstring': {'points': 5},
        'figure_single_format': {'points': 5},
    },
    'minor': {
        'long_line': {'points': 1},
    }
}

STATA_DO_RUBRIC = {
    'critical': {
        'log_error': {'points': 100, 'auto_fail': True},
        'bare_capture_regression': {'points': 30},
        'hardcoded_path': {'points': 20},
    },
    'major': {
        'missing_version': {'points': 10},
        'missing_path_block': {'points': 10},
        'missing_sample_check': {'points': 10},
        'missing_seed': {'points': 10},
        'missing_table_export': {'points': 5},
    },
    'minor': {
        'chinese_comment': {'points': 1},
    }
}

PAPER_TEX_RUBRIC = {
    'critical': {
        'structure_error': {'points': 100, 'auto_fail': True},
        'untraceable_numbers': {'points': 20},
        'undefined_citation': {'points': 15},
    },
    'major': {
        'table_missing_notes': {'points': 5},
    },
    'minor': {
        'long_line': {'points': 1},
    }
}

THRESHOLDS = {
    'commit': 80,
    'pr': 90,
    'excellence': 95
}

# ==============================================================================
# ISSUE DETECTION (Lightweight checks - full agents run separately)
# ==============================================================================

class IssueDetector:
    """Detect common issues for quality scoring."""

    @staticmethod
    def check_quarto_compilation(filepath: Path) -> Tuple[bool, str]:
        """Check if Quarto file compiles successfully."""
        try:
            result = subprocess.run(
                ['quarto', 'render', str(filepath), '--to', 'html'],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=filepath.parent
            )
            if result.returncode != 0:
                return False, result.stderr
            return True, ""
        except subprocess.TimeoutExpired:
            return False, "Compilation timeout (>2min)"
        except FileNotFoundError:
            return False, "Quarto not installed"

    @staticmethod
    def check_equation_overflow(content: str) -> List[int]:
        """Detect displayed equations with single lines likely to overflow.

        Flags equations only when a SINGLE LINE within a math block exceeds
        120 characters. Multi-line equations properly broken across lines
        are not flagged even if the total block is long.

        Checks:
        - $$ ... $$ blocks (Quarto/LaTeX)
        - \\begin{equation} ... \\end{equation} blocks
        - \\begin{align} ... \\end{align} blocks
        - \\begin{gather} ... \\end{gather} blocks
        """
        overflows = []
        lines = content.split('\n')
        in_math = False
        math_start = 0
        math_delim = None  # Track which delimiter opened the block

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Check for $$ delimiter (toggle)
            if '$$' in stripped and math_delim != 'env':
                if not in_math:
                    in_math = True
                    math_start = i
                    math_delim = '$$'
                    # Handle single-line $$ ... $$ (both delimiters on same line)
                    if stripped.count('$$') >= 2:
                        inner = stripped.split('$$')[1]
                        if len(inner.strip()) > 120:
                            overflows.append(i)
                        in_math = False
                        math_delim = None
                    continue
                else:
                    in_math = False
                    math_delim = None
                    continue

            # Check for \begin{equation/align/gather/...}
            env_begin = re.match(
                r'\\begin\{(equation|align|gather|multline|eqnarray)\*?\}', stripped
            )
            if env_begin and not in_math:
                in_math = True
                math_start = i
                math_delim = 'env'
                continue

            # Check for \end{equation/align/gather/...}
            if re.match(r'\\end\{(equation|align|gather|multline|eqnarray)\*?\}', stripped):
                in_math = False
                math_delim = None
                continue

            # Inside a math block: check individual line length
            if in_math:
                # Strip LaTeX comments before measuring
                code_part = line.split('%')[0] if '%' in line else line
                if len(code_part.strip()) > 120:
                    overflows.append(i)

        return overflows

    @staticmethod
    def check_broken_citations(content: str, bib_file: Path) -> List[str]:
        """Check for LaTeX citation keys not in bibliography.

        Matches \\cite{}, \\citep{}, \\citet{}, \\citeauthor{}, \\citeyear{}, etc.
        """
        cite_pattern = r'\\cite[a-z]*\{([^}]+)\}'
        cited_keys = set()
        for match in re.finditer(cite_pattern, content):
            keys = match.group(1).split(',')
            cited_keys.update(k.strip() for k in keys)

        if not bib_file.exists():
            return list(cited_keys)

        bib_content = bib_file.read_text(encoding='utf-8')
        bib_keys = set(re.findall(r'@\w+\{([^,]+),', bib_content))

        broken = cited_keys - bib_keys
        return list(broken)

    @staticmethod
    def check_plotly_widgets(html_file: Path, expected: int = None) -> Tuple[int, bool]:
        """Check if plotly charts rendered in HTML."""
        if not html_file.exists():
            return 0, False

        html_content = html_file.read_text(encoding='utf-8')
        actual_count = html_content.count('htmlwidget')

        if expected is None:
            return actual_count, True

        return actual_count, (actual_count >= expected)

    @staticmethod
    def check_r_syntax(filepath: Path) -> Tuple[bool, str]:
        """Check R script for syntax errors."""
        try:
            result = subprocess.run(
                ['Rscript', '-e', f'parse("{filepath}")'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                return False, result.stderr
            return True, ""
        except subprocess.TimeoutExpired:
            return False, "Syntax check timeout"
        except FileNotFoundError:
            return False, "Rscript not installed"

    @staticmethod
    def check_hardcoded_paths(content: str) -> List[int]:
        """Detect absolute paths in R scripts."""
        issues = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if re.search(r'["\'][/\\]|["\'][A-Za-z]:[/\\]', line):
                if not re.search(r'http:|https:|file://|/tmp/', line):
                    issues.append(i)

        return issues

    @staticmethod
    def check_latex_syntax(content: str) -> List[Dict]:
        """Check for common LaTeX syntax issues without compiling.

        Looks for:
        - Unmatched braces
        - Unclosed environments
        - Common typos in commands
        """
        issues = []
        lines = content.split('\n')

        # Track open environments
        env_stack = []
        for i, line in enumerate(lines, 1):
            # Skip comments
            stripped = line.split('%')[0] if '%' in line else line

            # Check for \begin{env}
            for match in re.finditer(r'\\begin\{(\w+)\}', stripped):
                env_stack.append((match.group(1), i))

            # Check for \end{env}
            for match in re.finditer(r'\\end\{(\w+)\}', stripped):
                env_name = match.group(1)
                if env_stack and env_stack[-1][0] == env_name:
                    env_stack.pop()
                elif env_stack:
                    issues.append({
                        'line': i,
                        'description': f'Mismatched environment: \\end{{{env_name}}} '
                                       f'but expected \\end{{{env_stack[-1][0]}}} '
                                       f'(opened at line {env_stack[-1][1]})',
                    })
                else:
                    issues.append({
                        'line': i,
                        'description': f'\\end{{{env_name}}} without matching \\begin',
                    })

        # Report unclosed environments
        for env_name, line_num in env_stack:
            issues.append({
                'line': line_num,
                'description': f'Unclosed environment: \\begin{{{env_name}}} never closed',
            })

        return issues

    @staticmethod
    def check_overfull_hbox_risk(content: str) -> List[int]:
        """Detect lines in LaTeX source likely to cause overfull hbox.

        Checks for very long lines inside text and math environments
        that are likely to overflow the slide width.
        """
        issues = []
        lines = content.split('\n')
        in_frame = False

        for i, line in enumerate(lines, 1):
            stripped = line.split('%')[0] if '%' in line else line

            # Track frame environments for context
            if r'\begin{frame}' in stripped:
                in_frame = True
            elif r'\end{frame}' in stripped:
                in_frame = False

            # Flag very long content lines inside frames
            # Strip leading whitespace and LaTeX commands for length check
            if in_frame and len(stripped.strip()) > 120:
                # Skip lines that are just comments or common long commands
                if stripped.strip().startswith('%'):
                    continue
                # Skip includegraphics, input, and similar path-based commands
                if re.match(r'\s*\\(includegraphics|input|bibliography|usepackage)', stripped):
                    continue
                issues.append(i)

        return issues

    @staticmethod
    def check_python_syntax(filepath: Path) -> Tuple[bool, str]:
        """Check Python script for syntax errors using py_compile."""
        try:
            result = subprocess.run(
                ['/opt/anaconda3/bin/python3', '-m', 'py_compile', str(filepath)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                return False, result.stderr
            return True, ""
        except subprocess.TimeoutExpired:
            return False, "Syntax check timeout"
        except FileNotFoundError:
            return False, "python3 not found"

    @staticmethod
    def check_raw_data_modification(content: str) -> List[int]:
        """Detect writes targeting data/raw/ (SSOT violation).

        Heuristic: write-style calls (to_csv, to_stata, to_parquet, open(..., 'w'),
        savefig, shutil.copy) whose path argument mentions data/raw.
        """
        issues = []
        lines = content.split('\n')
        write_call = re.compile(
            r'(to_csv|to_stata|to_parquet|to_excel|savefig|open|copy|move|write_text|'
            r'write_bytes|write_)\s*\('
        )
        for i, line in enumerate(lines, 1):
            if write_call.search(line) and 'data/raw' in line:
                issues.append(i)
        return issues

    @staticmethod
    def check_python_paths(content: str) -> List[int]:
        """Detect hardcoded absolute paths in Python scripts.

        Allows the documented ROOT resolution block (Path(__file__).resolve().parents).
        """
        issues = []
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if re.search(r'["\'][/\\]|["\'][A-Za-z]:[/\\]', line):
                if re.search(r'http:|https:|file://|/tmp/', line):
                    continue
                if '__file__' in line or 'parents' in line:
                    continue
                issues.append(i)
        return issues

    @staticmethod
    def check_python_headers(content: str) -> bool:
        """Check file starts with a docstring header (title/purpose)."""
        first_lines = content.strip().split('\n')[:5]
        joined = '\n'.join(first_lines).lower()
        return ('"""' in joined or "'''" in joined) and any(
            kw in joined for kw in ('purpose', 'input', 'output', 'title', '用途', '输入')
        )

    @staticmethod
    def check_figure_dual_output(content: str) -> Tuple[int, int]:
        """Count savefig-style calls lacking both png and pdf suffixes."""
        png = content.count('.png')
        pdf = content.count('.pdf')
        missing = 0
        for m in re.finditer(r'savefig\s*\(', content):
            window = content[m.end():m.end() + 300]
            if '.png' not in window or '.pdf' not in window:
                missing += 1
        return missing, (png, pdf)

    @staticmethod
    def check_stata_version(content: str) -> bool:
        """Check do file declares version."""
        return bool(re.search(r'^\s*version\s+\d+', content, re.MULTILINE))

    @staticmethod
    def check_stata_path_block(content: str) -> bool:
        """Check do file has the header path block (cd + global root)."""
        return ('global root' in content) and bool(
            re.search(r'^\s*cd\s+"', content, re.MULTILINE)
        )

    @staticmethod
    def check_stata_paths(content: str) -> List[int]:
        """Detect absolute paths in do files OUTSIDE the header path block.

        The header block (first ~15 non-empty lines) may contain the machine-specific
        cd/global root paths; everything else must use $root or relative paths.
        """
        issues = []
        lines = content.split('\n')
        # Find the end of the header path block: last line with cd "..." or global root
        # within the first 15 non-empty lines.
        non_empty = [(i, ln) for i, ln in enumerate(lines) if ln.strip()]
        header_end = 0
        for i, ln in non_empty[:15]:
            if re.search(r'^\s*(cd\s+"|global root\s+)', ln):
                header_end = max(header_end, i + 1)
        for i, line in enumerate(lines, 1):
            if i <= header_end:
                continue
            if re.search(r'["\'][/\\]|["\'][A-Za-z]:[/\\]', line):
                if re.search(r'http:|https:', line):
                    continue
                issues.append(i)
        return issues

    @staticmethod
    def check_bare_capture(content: str) -> List[int]:
        """Detect capture wrapping critical regression commands without _rc check."""
        issues = []
        lines = content.split('\n')
        regression_cmd = re.compile(r'\b(reg|regress|reghdfe|ivreg|areg|xtreg|logit|probit|oprobit)\b')
        for i, line in enumerate(lines, 1):
            if 'capture' in line and regression_cmd.search(line):
                # Check the next ~5 lines for a _rc check
                following = '\n'.join(lines[i:i + 5])
                if '_rc' not in following:
                    issues.append(i)
        return issues

    @staticmethod
    def check_sample_check(content: str) -> Tuple[bool, bool]:
        """Check regressions are followed by e(N)/assert sample checks (heuristic)."""
        has_regression = bool(re.search(
            r'^\s*(reg|regress|reghdfe|ivreg|areg|xtreg|logit|probit|oprobit)\b',
            content, re.MULTILINE))
        has_check = ('e(N)' in content) or ('assert ' in content)
        return has_regression, has_check

    @staticmethod
    def check_table_export(content: str) -> bool:
        """Check esttab/export of tables when regressions exist."""
        has_regression = bool(re.search(
            r'^\s*(reg|regress|reghdfe|ivreg|areg|xtreg|logit|probit|oprobit)\b',
            content, re.MULTILINE))
        if not has_regression:
            return True  # nothing to export
        return bool(re.search(r'esttab|estout|outreg2|export delimited', content))

    @staticmethod
    def check_chinese_comments(content: str) -> List[int]:
        """Detect CJK characters in comment lines (encoding discipline)."""
        issues = []
        for i, line in enumerate(content.split('\n'), 1):
            stripped = line.strip()
            if stripped.startswith('*') or stripped.startswith('//'):
                if re.search(r'[\u4e00-\u9fff]', line):
                    issues.append(i)
        return issues

    @staticmethod
    def check_stata_log(log_file: Path) -> Tuple[bool, str]:
        """Check a Stata batch log for error codes."""
        if not log_file.exists():
            return True, ""  # no log yet — nothing to fail
        content = log_file.read_text(encoding='utf-8', errors='replace')
        errors = re.findall(r'r\((\d+)\)', content)
        if errors:
            return False, f"log contains error code(s): r({', r('.join(errors)})"
        return True, ""

    @staticmethod
    def check_decimal_numbers_unreferenced(content: str, repo_root: Path) -> bool:
        """Heuristic for SSOT number reconciliation.

        If the paper contains decimal-looking numbers but the repo has NO
        tables/*.tex|csv and NO code/stata/*.log artifacts to trace them to,
        flag as untraceable. (Precise reconciliation is done by verifier.)
        """
        if not re.search(r'\d\.\d{2,3}', content):
            return False
        artifacts = list((repo_root / 'tables').glob('*')) + \
                    list((repo_root / 'code' / 'stata').glob('*.log'))
        return len(artifacts) == 0

    @staticmethod
    def check_table_notes(content: str) -> int:
        """Count table environments lacking a Notes row (heuristic)."""
        missing = 0
        for m in re.finditer(r'\\begin\{table\}', content):
            window = content[m.end():m.end() + 3000]
            end = re.search(r'\\end\{table\}', window)
            if end:
                window = window[:end.end()]
            if not re.search(r'\\multicolumn.*Notes|Notes:', window, re.IGNORECASE):
                missing += 1
        return missing

    @staticmethod
    def check_quarto_citations(content: str, bib_file: Path) -> List[str]:
        """Check Quarto-style citation keys against bibliography.

        Supports patterns: @key, [@key], [@key1; @key2]
        """
        cited_keys = set()

        # Pattern 1: [@key] or [@key1; @key2; ...]
        bracket_pattern = r'\[([^\]]*@[^\]]+)\]'
        for match in re.finditer(bracket_pattern, content):
            inner = match.group(1)
            # Extract individual @key references from within brackets
            for key_match in re.finditer(r'@([\w:.#$%&\-+?<>~/]+)', inner):
                cited_keys.add(key_match.group(1))

        # Pattern 2: standalone @key (not inside brackets, not email addresses)
        # Match @key that is preceded by start-of-line or whitespace or punctuation
        # but NOT preceded by characters that indicate an email address
        standalone_pattern = r'(?<![.\w])@([\w:.#$%&\-+?<>~/]+)'
        for match in re.finditer(standalone_pattern, content):
            key = match.group(1)
            # Skip if it looks like a Quarto directive or special syntax
            if key.startswith('{') or key in ('fig', 'tbl', 'sec', 'eq', 'lst'):
                continue
            cited_keys.add(key)

        if not cited_keys:
            return []

        if not bib_file.exists():
            return list(cited_keys)

        bib_content = bib_file.read_text(encoding='utf-8')
        bib_keys = set(re.findall(r'@\w+\{([^,]+),', bib_content))

        broken = cited_keys - bib_keys
        return list(broken)

# ==============================================================================
# QUALITY SCORER
# ==============================================================================

class QualityScorer:
    """Calculate quality scores for course materials."""

    def __init__(self, filepath: Path, verbose: bool = False):
        self.filepath = filepath
        self.verbose = verbose
        self.score = 100
        self.issues = {
            'critical': [],
            'major': [],
            'minor': []
        }
        self.auto_fail = False

    def score_quarto(self) -> Dict:
        """Score Quarto lecture slides."""
        content = self.filepath.read_text(encoding='utf-8')

        # Check compilation
        compiles, error = IssueDetector.check_quarto_compilation(self.filepath)
        if not compiles:
            self.auto_fail = True
            self.issues['critical'].append({
                'type': 'compilation_failure',
                'description': 'Quarto compilation failed',
                'details': error[:200],
                'points': 100
            })
            self.score = 0
            return self._generate_report()

        # Check equation overflow (heuristic)
        equation_overflows = IssueDetector.check_equation_overflow(content)
        for line in equation_overflows:
            self.issues['critical'].append({
                'type': 'equation_overflow',
                'description': f'Potential equation overflow at line {line}',
                'details': 'Single equation line >120 chars may overflow slide',
                'points': 20
            })
            self.score -= 20

        # Check broken citations (LaTeX-style \cite patterns)
        bib_file = self.filepath.parent.parent / 'Bibliography_base.bib'
        broken_citations = IssueDetector.check_broken_citations(content, bib_file)

        # Also check Quarto-style @key citations
        quarto_broken = IssueDetector.check_quarto_citations(content, bib_file)
        # Merge both sets, avoiding duplicates
        all_broken = set(broken_citations) | set(quarto_broken)
        for key in all_broken:
            self.issues['critical'].append({
                'type': 'broken_citation',
                'description': f'Citation key not in bibliography: {key}',
                'details': 'Add to Bibliography_base.bib or fix key',
                'points': 15
            })
            self.score -= 15

        # Check plotly widgets (if HTML exists)
        html_file = self.filepath.parent.parent / 'docs' / 'slides' / self.filepath.with_suffix('.html').name
        if html_file.exists():
            widget_count, _ = IssueDetector.check_plotly_widgets(html_file)
            expected_plotly = content.count('plotly::plot_ly')
            if expected_plotly > 0 and widget_count < expected_plotly:
                missing = expected_plotly - widget_count
                self.issues['critical'].append({
                    'type': 'missing_plotly_chart',
                    'description': f'{missing} plotly chart(s) failed to render',
                    'details': f'Expected {expected_plotly}, found {widget_count}',
                    'points': 10 * missing
                })
                self.score -= 10 * missing

        self.score = max(0, self.score)
        return self._generate_report()

    def score_r_script(self) -> Dict:
        """Score R script quality."""
        content = self.filepath.read_text(encoding='utf-8')

        # Check syntax
        is_valid, error = IssueDetector.check_r_syntax(self.filepath)
        if not is_valid:
            self.auto_fail = True
            self.issues['critical'].append({
                'type': 'syntax_error',
                'description': 'R syntax error',
                'details': error[:200],
                'points': 100
            })
            self.score = 0
            return self._generate_report()

        # Check hardcoded paths
        path_issues = IssueDetector.check_hardcoded_paths(content)
        for line in path_issues:
            self.issues['critical'].append({
                'type': 'hardcoded_path',
                'description': f'Hardcoded absolute path at line {line}',
                'details': 'Use relative paths or here::here()',
                'points': 20
            })
            self.score -= 20

        # Check for set.seed() if randomness detected
        has_random = any(fn in content for fn in ['rnorm', 'runif', 'sample', 'rbinom', 'rnbinom'])
        has_seed = 'set.seed' in content
        if has_random and not has_seed:
            self.issues['major'].append({
                'type': 'missing_set_seed',
                'description': 'Missing set.seed() for reproducibility',
                'details': 'Add set.seed(YYYYMMDD) after library() calls',
                'points': 10
            })
            self.score -= 10

        self.score = max(0, self.score)
        return self._generate_report()

    def score_beamer(self) -> Dict:
        """Score Beamer/LaTeX lecture slides."""
        content = self.filepath.read_text(encoding='utf-8')

        # Check for LaTeX syntax issues (without compiling)
        syntax_issues = IssueDetector.check_latex_syntax(content)
        if syntax_issues:
            # Mismatched environments are treated as compilation risk
            for issue in syntax_issues:
                self.issues['critical'].append({
                    'type': 'compilation_failure',
                    'description': f'LaTeX syntax issue at line {issue["line"]}',
                    'details': issue['description'],
                    'points': 100
                })
            self.auto_fail = True
            self.score = 0
            return self._generate_report()

        # Check for undefined/broken citations (\cite, \citep, \citet patterns)
        bib_file = self.filepath.parent.parent / 'Bibliography_base.bib'
        if not bib_file.exists():
            # Also check same directory
            bib_file = self.filepath.parent / 'Bibliography_base.bib'
        broken_citations = IssueDetector.check_broken_citations(content, bib_file)
        for key in broken_citations:
            self.issues['critical'].append({
                'type': 'undefined_citation',
                'description': f'Citation key not in bibliography: {key}',
                'details': 'Add to Bibliography_base.bib or fix key',
                'points': 15
            })
            self.score -= 15

        # Check for lines likely to cause overfull hbox
        overfull_lines = IssueDetector.check_overfull_hbox_risk(content)
        for line in overfull_lines:
            self.issues['critical'].append({
                'type': 'overfull_hbox',
                'description': f'Potential overfull hbox at line {line}',
                'details': 'Line >120 chars inside frame may overflow slide width',
                'points': 10
            })
            self.score -= 10

        # Check equation overflow (same heuristic as Quarto)
        equation_overflows = IssueDetector.check_equation_overflow(content)
        for line_num in equation_overflows:
            self.issues['critical'].append({
                'type': 'overfull_hbox',
                'description': f'Potential equation overflow at line {line_num}',
                'details': 'Single equation line >120 chars likely to overflow',
                'points': 10
            })
            self.score -= 10

        self.score = max(0, self.score)
        return self._generate_report()

    def score_python(self) -> Dict:
        """Score Python script quality (code/python/, scripts/)."""
        content = self.filepath.read_text(encoding='utf-8')

        # Syntax check
        is_valid, error = IssueDetector.check_python_syntax(self.filepath)
        if not is_valid:
            self.auto_fail = True
            self.issues['critical'].append({
                'type': 'syntax_error',
                'description': 'Python syntax error',
                'details': error[:200],
                'points': 100
            })
            self.score = 0
            return self._generate_report()

        # Raw data modification (SSOT violation)
        for line in IssueDetector.check_raw_data_modification(content):
            self.issues['critical'].append({
                'type': 'raw_data_modification',
                'description': f'Possible write to data/raw/ at line {line}',
                'details': 'Raw data is read-only; write only to data/processed/',
                'points': 30
            })
            self.score -= 30

        # Hardcoded absolute paths
        for line in IssueDetector.check_python_paths(content):
            self.issues['critical'].append({
                'type': 'hardcoded_path',
                'description': f'Hardcoded absolute path at line {line}',
                'details': 'Resolve via Path(__file__).resolve().parents[N]',
                'points': 20
            })
            self.score -= 20

        # Seed when randomness detected
        has_random = any(fn in content for fn in ['default_rng', 'random', 'shuffle', 'choice', 'normal'])
        has_seed = ('default_rng' in content and 'SEED' in content) or 'np.random.seed' in content
        if has_random and not has_seed:
            self.issues['major'].append({
                'type': 'missing_seed',
                'description': 'Randomness without SEED constant / default_rng',
                'details': 'Define SEED = 20251105 and use np.random.default_rng(SEED)',
                'points': 10
            })
            self.score -= 10

        # Header docstring
        if not IssueDetector.check_python_headers(content):
            self.issues['major'].append({
                'type': 'missing_header_docstring',
                'description': 'Missing header docstring (title/inputs/outputs)',
                'details': 'Add module docstring describing purpose, inputs, outputs',
                'points': 5
            })
            self.score -= 5

        # Figure dual output
        missing_dual, _ = IssueDetector.check_figure_dual_output(content)
        for _ in range(missing_dual):
            self.issues['major'].append({
                'type': 'figure_single_format',
                'description': 'savefig without PNG+PDF dual output',
                'details': 'Export both .png (300 DPI) and .pdf',
                'points': 5
            })
            self.score -= 5

        # Long lines (>100, math exceptions tolerated via comment)
        for i, line in enumerate(content.split('\n'), 1):
            if len(line) > 100 and not line.strip().startswith('#'):
                self.issues['minor'].append({
                    'type': 'long_line',
                    'description': f'Line {i} exceeds 100 chars',
                    'details': 'Split or document as math exception',
                    'points': 1
                })
                self.score -= 1

        self.score = max(0, self.score)
        return self._generate_report()

    def score_stata(self) -> Dict:
        """Score Stata do file quality (code/stata/)."""
        content = self.filepath.read_text(encoding='utf-8')

        # Log error check (if a corresponding -b log exists)
        log_file = self.filepath.with_suffix('.log')
        log_ok, log_error = IssueDetector.check_stata_log(log_file)
        if not log_ok:
            self.auto_fail = True
            self.issues['critical'].append({
                'type': 'log_error',
                'description': 'Stata log contains error codes',
                'details': log_error,
                'points': 100
            })
            self.score = 0
            return self._generate_report()

        # Bare capture around regressions
        for line in IssueDetector.check_bare_capture(content):
            self.issues['critical'].append({
                'type': 'bare_capture_regression',
                'description': f'capture wraps regression without _rc check (line {line})',
                'details': 'Remove capture or check _rc and fail loudly',
                'points': 30
            })
            self.score -= 30

        # Hardcoded paths outside header block
        for line in IssueDetector.check_stata_paths(content):
            self.issues['critical'].append({
                'type': 'hardcoded_path',
                'description': f'Absolute path outside header block at line {line}',
                'details': 'Use $root or relative paths; absolute paths only in header cd/global root',
                'points': 20
            })
            self.score -= 20

        # version declaration
        if not IssueDetector.check_stata_version(content):
            self.issues['major'].append({
                'type': 'missing_version',
                'description': 'Missing version declaration',
                'details': 'Add "version 19.5" at top (StataNow 19.5)',
                'points': 10
            })
            self.score -= 10

        # Header path block
        if not IssueDetector.check_stata_path_block(content):
            self.issues['major'].append({
                'type': 'missing_path_block',
                'description': 'Missing header path block (cd + global root)',
                'details': 'macOS Stata does not inherit shell cwd — add cd + global root header',
                'points': 10
            })
            self.score -= 10

        # Sample checks after regressions
        has_reg, has_check = IssueDetector.check_sample_check(content)
        if has_reg and not has_check:
            self.issues['major'].append({
                'type': 'missing_sample_check',
                'description': 'Regressions without e(N)/assert sample checks',
                'details': 'Add assert e(N) == expected after key regressions',
                'points': 10
            })
            self.score -= 10

        # Seed when stochastic
        has_random = any(fn in content for fn in ['sample ', 'bsample', 'simulate', 'rnormal', 'runiform', 'bootstrap'])
        if has_random and 'set seed' not in content:
            self.issues['major'].append({
                'type': 'missing_seed',
                'description': 'Stochastic commands without set seed',
                'details': 'Add "set seed 20251105"',
                'points': 10
            })
            self.score -= 10

        # Table export
        if not IssueDetector.check_table_export(content):
            self.issues['major'].append({
                'type': 'missing_table_export',
                'description': 'Regressions without esttab/export',
                'details': 'Export tables via esttab to tables/ (booktabs + notes)',
                'points': 5
            })
            self.score -= 5

        # Chinese comments (encoding discipline)
        for line in IssueDetector.check_chinese_comments(content):
            self.issues['minor'].append({
                'type': 'chinese_comment',
                'description': f'Chinese characters in comment at line {line}',
                'details': 'Keep Stata comments in English (locale/encoding risk)',
                'points': 1
            })
            self.score -= 1

        self.score = max(0, self.score)
        return self._generate_report()

    def score_paper(self) -> Dict:
        """Score paper .tex (structural checks only — no local compilation)."""
        content = self.filepath.read_text(encoding='utf-8')

        # Structure check (unclosed/mismatched environments)
        syntax_issues = IssueDetector.check_latex_syntax(content)
        if syntax_issues:
            for issue in syntax_issues:
                self.issues['critical'].append({
                    'type': 'structure_error',
                    'description': f'LaTeX structure issue at line {issue["line"]}',
                    'details': issue['description'],
                    'points': 100
                })
            self.auto_fail = True
            self.score = 0
            return self._generate_report()

        # Undefined citations
        bib_file = self.filepath.parent.parent / 'Bibliography_base.bib'
        broken_citations = IssueDetector.check_broken_citations(content, bib_file)
        for key in broken_citations:
            self.issues['critical'].append({
                'type': 'undefined_citation',
                'description': f'Citation key not in bibliography: {key}',
                'details': 'Add to Bibliography_base.bib or fix key',
                'points': 15
            })
            self.score -= 15

        # Number reconciliation heuristic (SSOT)
        if IssueDetector.check_decimal_numbers_unreferenced(content, self.filepath.parent.parent):
            self.issues['critical'].append({
                'type': 'untraceable_numbers',
                'description': 'Decimal numbers in paper but no traceable artifacts (tables/ or .log)',
                'details': 'Generate tables via Stata and reconcile every number (SSOT)',
                'points': 20
            })
            self.score -= 20

        # Tables without notes
        missing_notes = IssueDetector.check_table_notes(content)
        for _ in range(missing_notes):
            self.issues['major'].append({
                'type': 'table_missing_notes',
                'description': 'Table environment lacking Notes row',
                'details': 'Add notes (SE in parentheses, star conventions)',
                'points': 5
            })
            self.score -= 5

        # Long lines
        for i, line in enumerate(content.split('\n'), 1):
            stripped = line.strip()
            if len(line) > 100 and not stripped.startswith('%'):
                self.issues['minor'].append({
                    'type': 'long_line',
                    'description': f'Line {i} exceeds 100 chars',
                    'details': 'Split (math exception requires inline comment)',
                    'points': 1
                })
                self.score -= 1

        self.score = max(0, self.score)
        return self._generate_report()

    def _generate_report(self) -> Dict:
        """Generate quality score report."""
        if self.auto_fail:
            status = 'FAIL'
            threshold = 'None (auto-fail)'
        elif self.score >= THRESHOLDS['excellence']:
            status = 'EXCELLENCE'
            threshold = 'excellence'
        elif self.score >= THRESHOLDS['pr']:
            status = 'PR_READY'
            threshold = 'pr'
        elif self.score >= THRESHOLDS['commit']:
            status = 'COMMIT_READY'
            threshold = 'commit'
        else:
            status = 'BLOCKED'
            threshold = 'None (below commit)'

        critical_count = len(self.issues['critical'])
        major_count = len(self.issues['major'])
        minor_count = len(self.issues['minor'])
        total_count = critical_count + major_count + minor_count

        return {
            'filepath': str(self.filepath),
            'score': self.score,
            'status': status,
            'threshold': threshold,
            'auto_fail': self.auto_fail,
            'issues': {
                'critical': self.issues['critical'],
                'major': self.issues['major'],
                'minor': self.issues['minor'],
                'counts': {
                    'critical': critical_count,
                    'major': major_count,
                    'minor': minor_count,
                    'total': total_count
                }
            },
            'thresholds': THRESHOLDS
        }

    def print_report(self, summary_only: bool = False) -> None:
        """Print formatted quality report."""
        report = self._generate_report()

        print(f"\n# Quality Score: {self.filepath.name}\n")

        status_emoji = {
            'EXCELLENCE': '[EXCELLENCE]',
            'PR_READY': '[PASS]',
            'COMMIT_READY': '[PASS]',
            'BLOCKED': '[BLOCKED]',
            'FAIL': '[FAIL]'
        }

        print(f"## Overall Score: {report['score']}/100 {status_emoji.get(report['status'], '')}")

        if report['status'] == 'BLOCKED':
            print(f"\n**Status:** BLOCKED - Cannot commit (score < {THRESHOLDS['commit']})")
        elif report['status'] == 'COMMIT_READY':
            print(f"\n**Status:** Ready for commit (score >= {THRESHOLDS['commit']})")
            gap_to_pr = THRESHOLDS['pr'] - report['score']
            print(f"**Next milestone:** Submission candidate ({THRESHOLDS['pr']}+)")
            print(f"**Gap analysis:** Need +{gap_to_pr} points to reach submission quality")
        elif report['status'] == 'PR_READY':
            print(f"\n**Status:** Submission candidate (score >= {THRESHOLDS['pr']})")
            gap_to_excellence = THRESHOLDS['excellence'] - report['score']
            if gap_to_excellence > 0:
                print(f"**Next milestone:** Excellence ({THRESHOLDS['excellence']})")
                print(f"**Gap analysis:** +{gap_to_excellence} points to excellence")
        elif report['status'] == 'EXCELLENCE':
            print(f"\n**Status:** Excellence achieved! (score >= {THRESHOLDS['excellence']})")
        elif report['status'] == 'FAIL':
            print(f"\n**Status:** Auto-fail (compilation/syntax error)")

        if summary_only:
            print(f"\n**Total issues:** {report['issues']['counts']['total']} "
                  f"({report['issues']['counts']['critical']} critical, "
                  f"{report['issues']['counts']['major']} major, "
                  f"{report['issues']['counts']['minor']} minor)")
            return

        # Detailed issues
        print(f"\n## Critical Issues (MUST FIX): {report['issues']['counts']['critical']}")
        if report['issues']['counts']['critical'] == 0:
            print("No critical issues - safe to commit\n")
        else:
            for i, issue in enumerate(report['issues']['critical'], 1):
                print(f"{i}. **{issue['description']}** (-{issue['points']} points)")
                print(f"   - {issue['details']}\n")

        if report['issues']['counts']['major'] > 0:
            print(f"## Major Issues (SHOULD FIX): {report['issues']['counts']['major']}")
            for i, issue in enumerate(report['issues']['major'], 1):
                print(f"{i}. **{issue['description']}** (-{issue['points']} points)")
                print(f"   - {issue['details']}\n")

        if report['issues']['counts']['minor'] > 0 and self.verbose:
            print(f"## Minor Issues (NICE-TO-HAVE): {report['issues']['counts']['minor']}")
            for i, issue in enumerate(report['issues']['minor'], 1):
                print(f"{i}. {issue['description']} (-{issue['points']} points)\n")

        # Recommendations
        if report['status'] == 'BLOCKED':
            print("## Recommended Actions")
            print("1. Fix all critical issues above")
            print(f"2. Re-run quality score (target: >={THRESHOLDS['commit']})")
            print("3. Commit after reaching threshold\n")
        elif report['status'] == 'COMMIT_READY' and report['score'] < THRESHOLDS['pr']:
            print("## Recommended Actions to Reach PR Threshold")
            points_needed = THRESHOLDS['pr'] - report['score']
            print(f"Need +{points_needed} points to reach {THRESHOLDS['pr']}/100")
            if report['issues']['counts']['major'] > 0:
                print("Fix major issues listed above to improve score")
            print(f"\n**Estimated time:** 10-20 minutes\n")

# ==============================================================================
# CLI INTERFACE
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Calculate quality scores for research project files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Score a Python script
  python scripts/quality_score.py code/python/00_clean_pollution.py

  # Score a Stata do file
  python scripts/quality_score.py code/stata/01_main_did.do

  # Score the paper (structural check only — no local TeX)
  python scripts/quality_score.py paper/main.tex

  # Summary only (no detailed issues)
  python scripts/quality_score.py paper/main.tex --summary

  # Verbose output (include minor issues)
  python scripts/quality_score.py code/python/*.py --verbose

Quality Thresholds:
  80/100 = Commit threshold (blocks if below)
  90/100 = Submission candidate (warning if below)
  95/100 = Excellence (aspirational)

Exit Codes:
  0 = Score >= 80 (commit allowed)
  1 = Score < 80 (commit blocked)
  2 = Auto-fail (syntax/log error)
        """
    )

    parser.add_argument('filepaths', type=Path, nargs='+', help='Path(s) to file(s) to score')
    parser.add_argument('--summary', action='store_true', help='Show summary only')
    parser.add_argument('--verbose', action='store_true', help='Show all issues including minor')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    results = []
    exit_code = 0

    for filepath in args.filepaths:
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            exit_code = 1
            continue

        try:
            scorer = QualityScorer(filepath, verbose=args.verbose)

            if filepath.suffix == '.qmd':
                report = scorer.score_quarto()
            elif filepath.suffix == '.R':
                report = scorer.score_r_script()
            elif filepath.suffix == '.py':
                report = scorer.score_python()
            elif filepath.suffix == '.do':
                report = scorer.score_stata()
            elif filepath.suffix == '.tex':
                report = scorer.score_paper()
            else:
                print(f"Error: Unsupported file type: {filepath.suffix}")
                continue

            results.append(report)

            if not args.json:
                scorer.print_report(summary_only=args.summary)

            if report['auto_fail']:
                exit_code = max(exit_code, 2)
            elif report['score'] < THRESHOLDS['commit']:
                exit_code = max(exit_code, 1)

        except Exception as e:
            print(f"Error scoring {filepath}: {e}")
            import traceback
            traceback.print_exc()
            exit_code = 1

    if args.json:
        print(json.dumps(results, indent=2))

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
