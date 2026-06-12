"""
Claude Code Insights Generator
This script is called BY YOU (Claude Code) to generate insights from CSV data
"""
import sys
import json
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.insights_generator import insights_generator


def main():
    """
    Generate insights for a specific request
    Usage: python claude_generate_insights.py <cloud> <ou> <quarter>
    """
    if len(sys.argv) < 2:
        print("Usage: python claude_generate_insights.py <cloud> [ou] [quarter]")
        print("Example: python claude_generate_insights.py Service UKI Q2")
        print("Example: python claude_generate_insights.py Sales")
        sys.exit(1)

    cloud = sys.argv[1]
    ou = sys.argv[2] if len(sys.argv) > 2 else None
    quarter = sys.argv[3] if len(sys.argv) > 3 else "All"

    print("\n*** CLAUDE CODE - INSIGHTS GENERATION ***")
    print("=" * 60)
    print(f"Cloud: {cloud}")
    print(f"OU: {ou or 'All OUs'}")
    print(f"Quarter: {quarter}")
    print("=" * 60)

    # Generate insights
    insights = insights_generator.generate_insights(
        cloud=cloud,
        ou=ou,
        quarter=quarter
    )

    # Display results
    print("\n[+] HIGHLIGHTS:")
    for i, highlight in enumerate(insights["highlights"], 1):
        print(f"{i}. {highlight}")

    print("\n[-] AREAS TO WATCH:")
    for i, area in enumerate(insights["areas_to_watch"], 1):
        print(f"{i}. {area}")

    print("\n[>] NEXT STEPS:")
    for i, step in enumerate(insights["next_steps"], 1):
        print(f"{i}. {step}")

    # Save to JSON for API consumption
    output_dir = Path(__file__).parent.parent / "data" / "insights"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"insights_{cloud}_{ou or 'global'}_{quarter}.json"

    output_data = {
        "cloud": cloud,
        "ou": ou,
        "quarter": quarter,
        "generated_at": str(Path(__file__).stat().st_mtime),
        "insights": insights
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n[OK] Insights saved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
