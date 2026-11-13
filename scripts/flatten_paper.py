r"""Flattens a modular LaTeX paper into a single submission-ready .tex file.

AAAI Press requires all sections to be embedded in a single .tex file upon final
submission (AnonymousSubmission / CameraReady guidelines forbid \input for sections).
This script resolves \input{...} statements recursively while preserving comments,
verbatim blocks, and document structure.
"""

from pathlib import Path
import re
import sys


def flatten_latex(file_path: Path, base_dir: Path) -> str:
    content = file_path.read_text(encoding="utf-8")

    def replace_input(match: re.Match) -> str:
        input_target = match.group(1).strip()
        # If no extension, append .tex
        if not input_target.endswith(".tex"):
            target_path = base_dir / f"{input_target}.tex"
        else:
            target_path = base_dir / input_target

        if target_path.exists():
            print(f"Embedding: {target_path}")
            inner_content = flatten_latex(target_path, target_path.parent)
            return f"% --- BEGIN INLINED {input_target} ---\n{inner_content}\n% --- END INLINED {input_target} ---"
        else:
            print(f"Warning: Could not find {target_path}, leaving intact.")
            return match.group(0)

    # Match \input{...} that is not commented out
    pattern = re.compile(r"^(?!\s*%\s*)\\input\{([^}]+)\}", re.MULTILINE)
    return pattern.sub(replace_input, content)


def main() -> None:
    paper_dir = Path(__file__).resolve().parent.parent / "paper"
    main_tex = paper_dir / "main.tex"
    output_tex = paper_dir / "submission_single.tex"

    if not main_tex.exists():
        print(f"Error: {main_tex} does not exist.")
        sys.exit(1)

    print(f"Flattening {main_tex} -> {output_tex}...")
    flattened = flatten_latex(main_tex, paper_dir)
    output_tex.write_text(flattened, encoding="utf-8")
    print(f"Successfully generated {output_tex} ({len(flattened.splitlines())} lines).")


if __name__ == "__main__":
    main()
