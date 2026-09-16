from __future__ import annotations

import argparse
import json
from pathlib import Path

from feedbackos_api.main import app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="将 FastAPI OpenAPI 契约导出为确定性 JSON 文件",
    )
    parser.add_argument("output", type=Path, help="OpenAPI JSON 输出路径")
    return parser.parse_args()


def main() -> None:
    output = parse_args().output
    content = json.dumps(
        app.openapi(),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(f"{content}\n", encoding="utf-8")


if __name__ == "__main__":
    main()
