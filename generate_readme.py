#!/usr/bin/env python3
"""Generate README.md with shields.io badges from stats.json."""

import json
import urllib.parse
from pathlib import Path


def format_tokens(n: int) -> str:
    """Format token count into human-readable string."""
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def make_badge(label: str, message: str, color: str, logo: str = "") -> str:
    """Generate a shields.io badge markdown image."""
    label_enc = urllib.parse.quote(label)
    message_enc = urllib.parse.quote(message)
    url = f"https://img.shields.io/badge/{label_enc}-{message_enc}-{color}?style=for-the-badge"
    if logo:
        url += f"&logo={urllib.parse.quote(logo)}&logoColor=white"
    return f"![{label}]({url})"


PROVIDER_LOGOS = {
    "Anthropic": "anthropic",
    "OpenAI": "openai",
    "Google": "google",
}


def main():
    stats_path = Path(__file__).parent / "stats.json"
    with open(stats_path) as f:
        data = json.load(f)

    total_input = 0
    total_output = 0
    badge_lines = []

    for model, info in data["models"].items():
        inp = info["input_tokens"]
        out = info["output_tokens"]
        total = inp + out
        total_input += inp
        total_output += out

        if total == 0:
            continue

        logo = PROVIDER_LOGOS.get(info["provider"], "")
        message = f"{format_tokens(total)} tokens"
        badge_lines.append(make_badge(model, message, info["color"], logo))

    grand_total = total_input + total_output

    # Build README
    lines = [
        f"# Hi, I'm Douglas",
        "",
        "---",
        "",
        "## LLM Token Usage",
        "",
    ]

    if grand_total == 0:
        lines.append("_No usage recorded yet. Update `stats.json` to get started!_")
    else:
        # Total badge
        total_badge = make_badge(
            "Total Tokens", format_tokens(grand_total), "8b5cf6"
        )
        input_badge = make_badge("Input", format_tokens(total_input), "6366f1")
        output_badge = make_badge("Output", format_tokens(total_output), "a78bfa")

        lines.append(total_badge + " " + input_badge + " " + output_badge)
        lines.append("")
        lines.append("### By Model")
        lines.append("")
        lines.append(" ".join(badge_lines))

    lines += [
        "",
        "---",
        "",
        f"_Last updated: {data['last_updated']}_",
        "",
    ]

    readme_path = Path(__file__).parent / "README.md"
    readme_path.write_text("\n".join(lines))
    print(f"README.md generated ({len(badge_lines)} model badges, {format_tokens(grand_total)} total tokens)")


if __name__ == "__main__":
    main()
