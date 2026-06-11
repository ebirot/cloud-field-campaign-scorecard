#!/usr/bin/env python3
"""
Test all 9 OU Scorecards
Verify data consistency for each Operating Unit
"""
import urllib.request
import json
from urllib.parse import quote


API_BASE = "http://localhost:8000/api/data"

# OU to Leader mapping
OU_MAPPING = {
    'CENTRAL': 'Alexander Wallner',
    'NORTH': 'Bob Vanstraelen',
    'FRANCE': 'Emilie Sidiqian',
    'SOUTH': 'Marco Hernansanz',
    'UKI': 'Zahra Bahrololoumi',
    'AMER REG': 'Mark Sullivan',
    'TMT': 'Lenore Lang',
    'PACE & AFD360': 'Connor Marsden',
    'CBS': 'Scot Blocker'
}


def test_ou_scorecard(ou_name, leader_name):
    """Test one OU scorecard"""
    print(f"\n{'='*60}")
    print(f"Testing: {ou_name} ({leader_name})")
    print(f"{'='*60}")

    try:
        leader_param = quote(leader_name)

        # Test Regional (all clouds for this leader)
        regional_resp = urllib.request.urlopen(
            f"{API_BASE}/regional?quarters=Q2",
            timeout=5
        )
        regional_data = json.loads(regional_resp.read())['data']

        # Filter to this leader
        ou_regional = [r for r in regional_data if r['leader'] == leader_name]

        if not ou_regional:
            print(f"  WARNING: No regional data found for {leader_name}")
            return False

        regional_total = sum(r['mdp'] for r in ou_regional)
        clouds_count = len(ou_regional)

        print(f"  Regional: {clouds_count} clouds, ${regional_total/1e6:.1f}M total")
        for r in ou_regional:
            print(f"    - {r['cloud']}: ${r['mdp']/1e6:.1f}M")

        # Test Horseman (aggregated across all clouds)
        horseman_resp = urllib.request.urlopen(
            f"{API_BASE}/horseman?quarters=Q2&leaders={leader_param}",
            timeout=5
        )
        horseman = json.loads(horseman_resp.read())
        horseman_total = horseman['total']['mdp']
        print(f"  Horseman: ${horseman_total/1e6:.1f}M")

        # Test Traffic
        traffic_resp = urllib.request.urlopen(
            f"{API_BASE}/traffic?quarters=Q2&leaders={leader_param}",
            timeout=5
        )
        traffic = json.loads(traffic_resp.read())
        traffic_total = traffic['total']['mdp']
        print(f"  Traffic: ${traffic_total/1e6:.1f}M")

        # Test Offer
        offer_resp = urllib.request.urlopen(
            f"{API_BASE}/offer?quarters=Q2&leaders={leader_param}",
            timeout=5
        )
        offer = json.loads(offer_resp.read())
        offer_total = offer['total']['mdp']
        print(f"  Offer: ${offer_total/1e6:.1f}M")

        # Check consistency
        tolerance = 0.5e6  # $0.5M tolerance
        match_horseman = abs(regional_total - horseman_total) < tolerance
        match_traffic = abs(regional_total - traffic_total) < tolerance
        match_offer = abs(regional_total - offer_total) < tolerance

        all_match = match_horseman and match_traffic and match_offer

        if all_match:
            print(f"  ✓ PASS: All totals match (±$0.5M)")
            return True
        else:
            print(f"  X FAIL: Totals do not match!")
            if not match_horseman:
                diff = (horseman_total - regional_total) / 1e6
                print(f"    - Horseman diff: ${diff:.1f}M")
            if not match_traffic:
                diff = (traffic_total - regional_total) / 1e6
                print(f"    - Traffic diff: ${diff:.1f}M")
            if not match_offer:
                diff = (offer_total - regional_total) / 1e6
                print(f"    - Offer diff: ${diff:.1f}M")
            return False

    except Exception as e:
        print(f"  X ERROR: {e}")
        return False


def main():
    print("="*60)
    print("OPERATING UNITS SCORECARD - COMPREHENSIVE TEST")
    print("="*60)
    print(f"\nTesting {len(OU_MAPPING)} Operating Units...")
    print(f"Quarter: Q2")
    print(f"Checking: Regional, Horseman, Traffic, Offer consistency")

    results = {}
    for ou_name, leader_name in OU_MAPPING.items():
        results[ou_name] = test_ou_scorecard(ou_name, leader_name)

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nResults by OU:")
    for ou_name, passed_test in results.items():
        status = "PASS" if passed_test else "FAIL"
        print(f"  {status}: {ou_name}")

    print(f"\nTotal: {passed}/{total} OUs passed")

    if passed == total:
        print("\nAll OU Scorecards are working correctly!")
        return 0
    else:
        print(f"\n{total - passed} OU(s) failed. Check logs above.")
        return 1


if __name__ == "__main__":
    exit(main())
