"""
Data API Endpoints
Serve parsed CSV data with filtering
"""
from fastapi import APIRouter, Query
from typing import Optional, List
from pathlib import Path
import os

# Use safe parser if CSV files don't exist (Heroku deployment)
csv_dir = Path(__file__).parent.parent.parent.parent / 'data' / 'csv'
if not csv_dir.exists() or not any(csv_dir.glob('*.csv')):
    print("⚠️ CSV files not found - Using SafeCSVParser (empty data mode)")
    from app.services.csv_parser_safe import SafeCSVParser
    csv_parser = SafeCSVParser()
else:
    from app.services.csv_parser import csv_parser

router = APIRouter()


@router.get("/summary")
async def get_summary():
    """Get summary statistics"""
    return csv_parser.get_summary_stats()


@router.get("/regional")
async def get_regional_data(
    cloud: Optional[str] = Query(None, description="Filter by cloud (e.g., Service, Sales)"),
    leader: Optional[str] = Query(None, description="Filter by leader name"),
    quarters: Optional[str] = Query('Q2', description="Quarters to include (comma-separated, e.g., 'Q2' or 'Q1,Q2')")
):
    """
    Get regional MDP data by leader and cloud

    Returns MDP breakdown by region and cloud with YoY growth
    """
    # Parse quarters parameter
    quarters_list = [q.strip() for q in quarters.split(',')] if quarters else ['Q2']

    data = csv_parser.parse_regional_cloud_view(quarters=quarters_list, fiscal_year='FY 2027')

    # Apply filters
    if cloud:
        data = [item for item in data if item.get('cloud') == cloud]

    if leader:
        data = [item for item in data if leader.lower() in item.get('leader', '').lower()]

    return {
        "count": len(data),
        "data": data
    }


@router.get("/horseman")
async def get_horseman_data(
    cloud: Optional[str] = Query(None, description="Filter by cloud (e.g., Service, Sales)"),
    quarters: Optional[str] = Query('Q2', description="Quarters to include (comma-separated)"),
    leaders: Optional[str] = Query(None, description="Comma-separated list of leader names to filter")
):
    """
    Get MDP breakdown by Horseman (AE, BDR, Specialist, etc.)

    Returns opportunity source distribution filtered by cloud and leaders
    """
    # Parse quarters parameter
    quarters_list = [q.strip() for q in quarters.split(',')] if quarters else ['Q2']

    # Parse leaders parameter
    leaders_list = [l.strip() for l in leaders.split(',')] if leaders else None

    # Parse with cloud and leaders filter
    data = csv_parser.parse_horseman(cloud_filter=cloud, leaders_filter=leaders_list, quarters=quarters_list, fiscal_year='FY 2027')

    # Calculate total
    total_mdp = sum(metrics.get('mdp', 0) or 0 for source, metrics in data.items() if source not in ['All', 'SDR'])

    return {
        "total": {"mdp": total_mdp},
        "breakdown": {k: v for k, v in data.items() if k not in ['All', 'SDR']}
    }


@router.get("/traffic")
async def get_traffic_data(
    cloud: Optional[str] = Query(None, description="Filter by cloud (e.g., Service, Sales)"),
    quarters: Optional[str] = Query('Q2', description="Quarters to include (comma-separated)"),
    leaders: Optional[str] = Query(None, description="Comma-separated list of leader names to filter")
):
    """
    Get MDP breakdown by Traffic Source

    Returns distribution across Email, Paid, Organic, Events filtered by cloud and leaders
    """
    # Parse quarters parameter
    quarters_list = [q.strip() for q in quarters.split(',')] if quarters else ['Q2']

    # Parse leaders parameter
    leaders_list = [l.strip() for l in leaders.split(',')] if leaders else None

    data = csv_parser.parse_traffic_source(cloud_filter=cloud, leaders_filter=leaders_list, quarters=quarters_list, fiscal_year='FY 2027')

    # Calculate total
    total_mdp = sum(metrics.get('mdp', 0) or 0 for source, metrics in data.items() if source and source != 'All')

    return {
        "total": {"mdp": total_mdp},
        "breakdown": {k: v for k, v in data.items() if k and k != 'All'}
    }


@router.get("/clouds")
async def get_cloud_breakdown():
    """
    Get MDP breakdown by Cloud

    Aggregates data across all regions per cloud
    """
    regional_data = csv_parser.parse_regional_cloud_view()

    # Aggregate by cloud
    cloud_totals = {}
    for item in regional_data:
        cloud = item.get('cloud')
        mdp = item.get('mdp', 0) or 0

        if cloud not in cloud_totals:
            cloud_totals[cloud] = {
                'cloud': cloud,
                'mdp': 0,
                'count': 0,
                'yoy_changes': []
            }

        cloud_totals[cloud]['mdp'] += mdp
        cloud_totals[cloud]['count'] += 1

        if item.get('yoy_change') is not None:
            cloud_totals[cloud]['yoy_changes'].append(item['yoy_change'])

    # Calculate average YoY
    formatted = []
    for cloud, data in cloud_totals.items():
        yoy_changes = data['yoy_changes']
        avg_yoy = sum(yoy_changes) / len(yoy_changes) if yoy_changes else None

        formatted.append({
            'cloud': cloud,
            'mdp': data['mdp'],
            'avg_yoy_change': avg_yoy,
            'leaders_count': data['count']
        })

    # Sort by MDP
    formatted.sort(key=lambda x: x['mdp'], reverse=True)

    return {
        "clouds": formatted,
        "total_clouds": len(formatted)
    }


@router.get("/offer")
async def get_offer_data(
    cloud: Optional[str] = Query(None, description="Filter by cloud (e.g., Service, Sales)"),
    quarters: Optional[str] = Query('Q2', description="Quarters to include (comma-separated)"),
    leaders: Optional[str] = Query(None, description="Comma-separated list of leader names to filter")
):
    """
    Get MDP breakdown by Offer L2

    Returns distribution across offer types filtered by cloud and leaders
    """
    # Parse quarters parameter
    quarters_list = [q.strip() for q in quarters.split(',')] if quarters else ['Q2']

    # Parse leaders parameter
    leaders_list = [l.strip() for l in leaders.split(',')] if leaders else None

    data = csv_parser.parse_offer(cloud_filter=cloud, leaders_filter=leaders_list, quarters=quarters_list, fiscal_year='FY 2027')

    # Calculate total - sum L1 MDP only (L1 already includes L2 breakdown)
    total_mdp = 0
    for offer_l1, metrics in data.items():
        # Add L1 MDP (this already includes all L2 children)
        total_mdp += metrics.get('mdp', 0) or 0

    return {
        "total": {"mdp": total_mdp},
        "breakdown": data
    }


@router.get("/webinar")
async def get_webinar_data(
    cloud: Optional[str] = Query(None, description="Filter by cloud (e.g., Service, Sales, Marketing)"),
    quarters: Optional[str] = Query('Q2', description="Quarters to include (comma-separated)"),
    leaders: Optional[str] = Query(None, description="Comma-separated list of leader names to filter")
):
    """
    Get webinar MDP data by Cloud

    Returns webinar metrics filtered by cloud and leaders
    """
    # Parse quarters parameter
    quarters_list = [q.strip() for q in quarters.split(',')] if quarters else ['Q2']

    # Parse leaders parameter
    leaders_list = [l.strip() for l in leaders.split(',')] if leaders else None

    data = csv_parser.parse_webinar(cloud_filter=cloud, leaders_filter=leaders_list, quarters=quarters_list)

    # Calculate total
    total_mdp = sum(metrics.get('mdp', 0) or 0 for cloud, metrics in data.items())
    total_previous_mdp = sum(metrics.get('previous_mdp', 0) or 0 for cloud, metrics in data.items())

    # Calculate overall YoY
    overall_yoy = None
    if total_previous_mdp > 0:
        overall_yoy = (total_mdp - total_previous_mdp) / total_previous_mdp

    return {
        "total": {
            "mdp": total_mdp,
            "previous_mdp": total_previous_mdp,
            "yoy_change": overall_yoy
        },
        "breakdown": data
    }


@router.get("/last_refresh")
async def get_last_refresh():
    """Get last data refresh timestamp from Tableau's Data Freshness CSV"""
    import csv
    from datetime import datetime

    try:
        # Read from centralized data/csv folder
        freshness_file = Path(__file__).parent.parent.parent.parent / "data" / "csv" / "10_data_freshness.csv"

        if freshness_file.exists():
            with open(freshness_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    raw_timestamp = row.get('Last Refresh Date', '').strip()
                    if raw_timestamp:
                        # Parse the timestamp (format: "6/9/2026 8:33:18 PM")
                        try:
                            dt = datetime.strptime(raw_timestamp, "%m/%d/%Y %I:%M:%S %p")
                            formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
                            return {
                                "last_refresh": formatted,
                                "success": True
                            }
                        except:
                            # Return raw if parsing fails
                            return {
                                "last_refresh": raw_timestamp,
                                "success": True
                            }

        # Fallback: check old location
        old_file = Path(__file__).parent.parent.parent / "data" / "last_refresh.txt"
        if old_file.exists():
            with open(old_file, 'r') as f:
                timestamp = f.read().strip()
            return {
                "last_refresh": timestamp,
                "success": True
            }

        return {
            "last_refresh": None,
            "success": False,
            "message": "No refresh timestamp found"
        }
    except Exception as e:
        return {
            "last_refresh": None,
            "success": False,
            "error": str(e)
        }


@router.get("/health-check")
async def data_health_check():
    """Check data availability"""
    try:
        regional = csv_parser.parse_regional_cloud_view()
        horseman = csv_parser.parse_horseman()
        traffic = csv_parser.parse_traffic_source()

        return {
            "status": "healthy",
            "data_points": {
                "regional": len(regional),
                "horseman": len(horseman),
                "traffic": len(traffic)
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
