#!/usr/bin/env python3
"""
Quick test script to verify all fixes
Run: python TEST_ALL.py
"""
import urllib.request
import json
from urllib.parse import quote


API_BASE = "http://localhost:8000/api/data"
ANALYTICS_BASE = "http://localhost:8000/api/analytics"


def test_api(name, url, expected_total=None):
    """Test an API endpoint"""
    try:
        resp = urllib.request.urlopen(url, timeout=5)
        data = json.loads(resp.read())

        if 'total' in data and 'mdp' in data['total']:
            total = data['total']['mdp']
            print(f"✅ {name}: ${total/1e6:.1f}M", end='')

            if expected_total:
                diff = abs(total - expected_total)
                if diff < 1e6:  # Within $1M tolerance
                    print(" (PASS)")
                    return True
                else:
                    print(f" (FAIL - expected ${expected_total/1e6:.1f}M)")
                    return False
            else:
                print()
                return True
        else:
            print(f"✅ {name}: OK")
            return True

    except Exception as e:
        print(f"❌ {name}: {e}")
        return False


def main():
    print("=" * 60)
    print("CLOUD FIELD CAMPAIGN SCORECARD - TEST SUITE")
    print("=" * 60)
    print()

    # Test 1: Service Q2 EMEA (5 leaders)
    print("TEST 1: Service Q2 EMEA ($38.9M expected)")
    print("-" * 60)
    emea_leaders = quote("Alexander Wallner,Bob Vanstraelen,Emilie Sidiqian,Marco Hernansanz,Zahra Bahrololoumi")

    t1_horseman = test_api(
        "Horseman",
        f"{API_BASE}/horseman?cloud=Service&quarters=Q2&leaders={emea_leaders}",
        38.9e6
    )
    t1_traffic = test_api(
        "Traffic",
        f"{API_BASE}/traffic?cloud=Service&quarters=Q2&leaders={emea_leaders}",
        38.9e6
    )
    t1_offer = test_api(
        "Offer",
        f"{API_BASE}/offer?cloud=Service&quarters=Q2&leaders={emea_leaders}",
        38.9e6
    )
    print()

    # Test 2: Service Q2 EMEA + AMER (9 leaders)
    print("TEST 2: Service Q2 EMEA + AMER ($149.5M expected)")
    print("-" * 60)
    all_leaders = quote("Alexander Wallner,Bob Vanstraelen,Emilie Sidiqian,Marco Hernansanz,Zahra Bahrololoumi,Mark Sullivan,Lenore Lang,Connor Marsden,Scot Blocker")

    t2_horseman = test_api(
        "Horseman",
        f"{API_BASE}/horseman?cloud=Service&quarters=Q2&leaders={all_leaders}",
        149.5e6
    )
    t2_traffic = test_api(
        "Traffic",
        f"{API_BASE}/traffic?cloud=Service&quarters=Q2&leaders={all_leaders}",
        149.5e6
    )
    t2_offer = test_api(
        "Offer",
        f"{API_BASE}/offer?cloud=Service&quarters=Q2&leaders={all_leaders}",
        149.5e6
    )
    print()

    # Test 3: Analytics API
    print("TEST 3: Analytics API")
    print("-" * 60)
    t3_stats = test_api("Stats", f"{ANALYTICS_BASE}/stats")
    t3_events = test_api("Events", f"{ANALYTICS_BASE}/events?limit=10")
    t3_users = test_api("Active Users", f"{ANALYTICS_BASE}/active-users?minutes=5")
    print()

    # Test 4: Frontend pages
    print("TEST 4: Frontend Pages")
    print("-" * 60)
    try:
        urllib.request.urlopen("http://localhost:8000/", timeout=5)
        print("✅ Main page: OK")
        t4_main = True
    except Exception as e:
        print(f"❌ Main page: {e}")
        t4_main = False

    try:
        urllib.request.urlopen("http://localhost:8000/admin", timeout=5)
        print("✅ Admin page: OK")
        t4_admin = True
    except Exception as e:
        print(f"❌ Admin page: {e}")
        t4_admin = False
    print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_tests = [
        ("Service Q2 EMEA", t1_horseman and t1_traffic and t1_offer),
        ("Service Q2 BOTH", t2_horseman and t2_traffic and t2_offer),
        ("Analytics API", t3_stats and t3_events and t3_users),
        ("Frontend Pages", t4_main and t4_admin),
    ]

    passed = sum(1 for _, result in all_tests if result)
    total = len(all_tests)

    for name, result in all_tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print()
    print(f"TOTAL: {passed}/{total} tests passed")

    if passed == total:
        print()
        print("🎉 ALL TESTS PASSED! App is ready!")
        print()
        print("Next steps:")
        print("1. Open http://localhost:8000 in browser")
        print("2. Hard refresh (CTRL + SHIFT + R)")
        print("3. Test Service Q2 with different region filters")
        print("4. Check Admin page at http://localhost:8000/admin")
        return 0
    else:
        print()
        print("⚠️  SOME TESTS FAILED!")
        print("Check backend logs and try restarting the server.")
        return 1


if __name__ == "__main__":
    exit(main())
