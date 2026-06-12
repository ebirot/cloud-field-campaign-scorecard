"""
Insights Generator - Analyze CSV data and generate insights in Scorecard style
Uses the SAME csv_parser as the frontend to ensure data consistency
"""
from typing import Dict, List, Any
from app.services.csv_parser import csv_parser


class InsightsGenerator:
    """Generate Marketing Performance Insights from parsed CSV data"""

    def __init__(self):
        # Use the existing CSV parser that the frontend uses
        self.parser = csv_parser

    def generate_insights(
        self,
        cloud: str,
        ou: str = None,
        quarter: str = "Q2"
    ) -> Dict[str, List[str]]:
        """
        Generate insights for a specific Cloud or OU
        Uses THE SAME data that the frontend scorecard displays

        Args:
            cloud: Cloud name (Service, Sales, Marketing, Commerce, AI & Data, Analytics)
            ou: Optional OU filter (France, UKI, North, South, Central, AMER CBS, etc.)
            quarter: Q1, Q2, Q3, Q4 (default Q2)

        Returns:
            {
                "highlights": [...],
                "areas_to_watch": [...],
                "next_steps": [...]
            }
        """
        try:
            # Parse data using the SAME parser as frontend
            quarters = [quarter] if quarter != "All" else ["Q1", "Q2", "Q3", "Q4"]

            regional_data = self.parser.parse_regional_cloud_view(quarters=quarters)
            horseman_data = self.parser.parse_horseman(quarters=quarters)
            traffic_data = self.parser.parse_traffic_source(quarters=quarters)
            offer_data = self.parser.parse_offer(quarters=quarters)

            # Filter by cloud and ou
            filtered_regional = self._filter_by_cloud_ou(regional_data, cloud, ou)
            filtered_horseman = self._filter_by_cloud_ou(horseman_data, cloud, ou)
            filtered_traffic = self._filter_by_cloud_ou(traffic_data, cloud, ou)
            filtered_offers = self._filter_by_cloud_ou(offer_data, cloud, ou)

            # Calculate aggregate metrics
            metrics = self._calculate_metrics(
                filtered_regional,
                filtered_horseman,
                filtered_traffic,
                filtered_offers,
                cloud,
                ou
            )

            # Generate insights
            highlights = self._generate_highlights(metrics, cloud, ou)
            areas_to_watch = self._generate_areas_to_watch(metrics, cloud, ou)
            next_steps = self._generate_next_steps(metrics, cloud, ou)

            return {
                "highlights": highlights,
                "areas_to_watch": areas_to_watch,
                "next_steps": next_steps
            }

        except Exception as e:
            print(f"Error generating insights: {str(e)}")
            return self._fallback_insights(cloud, ou)

    def _filter_by_cloud_ou(self, data, cloud, ou):
        """Filter parsed data by cloud and/or OU"""
        if not data:
            return [] if isinstance(data, list) else {}

        # Handle list format (regional data)
        if isinstance(data, list):
            filtered = []
            for item in data:
                # Filter by cloud
                if cloud and item.get('cloud') != cloud:
                    continue

                # Filter by OU if specified
                if ou and item.get('leader') != ou:
                    continue

                filtered.append(item)
            return filtered

        # Handle dict format (horseman, traffic, offers)
        # Already aggregated - just return as-is
        return data

    def _calculate_metrics(self, regional, horseman, traffic, offers, cloud, ou):
        """Calculate aggregate metrics from filtered data"""
        metrics = {
            "cloud": cloud,
            "ou": ou,
            "total_mdp": 0,
            "avg_yoy": 0,
            "avg_contribution": 0,
            "avg_contribution_diff": 0,
            "horseman_breakdown": {},
            "traffic_breakdown": {},
            "offer_breakdown": {},
            "ou_breakdown": {}
        }

        # Regional aggregates
        if regional:
            total_mdp = sum(item.get('mdp', 0) for item in regional if item.get('mdp'))
            yoys = [item.get('yoy_change') for item in regional if item.get('yoy_change') is not None]
            contribs = [item.get('contribution') for item in regional if item.get('contribution') is not None]
            contrib_diffs = [item.get('contribution_diff') for item in regional if item.get('contribution_diff') is not None]

            metrics["total_mdp"] = total_mdp
            metrics["avg_yoy"] = sum(yoys) / len(yoys) if yoys else 0
            metrics["avg_contribution"] = sum(contribs) / len(contribs) if contribs else 0
            metrics["avg_contribution_diff"] = sum(contrib_diffs) / len(contrib_diffs) if contrib_diffs else 0

            # OU breakdown
            for item in regional:
                leader = item.get('leader', 'Unknown')
                if leader not in metrics["ou_breakdown"]:
                    metrics["ou_breakdown"][leader] = {
                        "mdp": 0,
                        "yoy": None,
                        "contribution": None
                    }
                metrics["ou_breakdown"][leader]["mdp"] += item.get('mdp', 0)
                if item.get('yoy_change') is not None:
                    metrics["ou_breakdown"][leader]["yoy"] = item.get('yoy_change')
                if item.get('contribution') is not None:
                    metrics["ou_breakdown"][leader]["contribution"] = item.get('contribution')

        # Horseman breakdown (already a dict from parser)
        if horseman and isinstance(horseman, dict):
            for source, data in horseman.items():
                metrics["horseman_breakdown"][source] = {
                    "mdp": data.get('mdp', 0),
                    "yoy": data.get('yoy_change'),
                    "share": data.get('mdp_share')
                }

        # Traffic breakdown (already a dict from parser)
        if traffic and isinstance(traffic, dict):
            for source_key, data in traffic.items():
                # Traffic parser returns nested dict with L1 -> L2 structure
                if isinstance(data, dict) and 'total_mdp' in data:
                    metrics["traffic_breakdown"][source_key] = {
                        "mdp": data.get('total_mdp', 0),
                        "yoy": data.get('yoy_change'),
                        "share": data.get('mdp_share')
                    }

        # Offer breakdown (already a dict from parser)
        if offers and isinstance(offers, dict):
            for offer_key, data in offers.items():
                # Offer parser returns nested dict with L1 -> L2 structure
                if isinstance(data, dict) and 'total_mdp' in data:
                    metrics["offer_breakdown"][offer_key] = {
                        "mdp": data.get('total_mdp', 0),
                        "yoy": data.get('yoy_change'),
                        "share": data.get('mdp_share')
                    }

        return metrics

    def _generate_highlights(self, metrics, cloud, ou):
        """Generate highlights - positive trends and standout performers"""
        highlights = []

        # Overall performance
        total_mdp_m = metrics["total_mdp"] / 1_000_000
        yoy_pct = metrics["avg_yoy"] * 100
        contrib_pct = metrics["avg_contribution"] * 100

        scope = f"{ou} - {cloud}" if ou else cloud

        if yoy_pct > 10:
            highlights.append(
                f"{scope} MDP at ${total_mdp_m:.1f}M, up {yoy_pct:+.1f}% YoY with strong overall growth — "
                f"contribution at {contrib_pct:.1f}%"
            )
        elif yoy_pct > 0:
            highlights.append(
                f"{scope} MDP at ${total_mdp_m:.1f}M, {yoy_pct:+.1f}% YoY — "
                f"contribution at {contrib_pct:.1f}%"
            )
        else:
            highlights.append(
                f"{scope} MDP at ${total_mdp_m:.1f}M, {yoy_pct:+.1f}% YoY — "
                f"contribution at {contrib_pct:.1f}%, {metrics['avg_contribution_diff']:+.1f}ppts vs. FY-1"
            )

        # Best horseman
        if metrics["horseman_breakdown"]:
            sorted_horseman = sorted(
                [(k, v) for k, v in metrics["horseman_breakdown"].items() if v["yoy"] is not None],
                key=lambda x: x[1]["yoy"],
                reverse=True
            )
            if sorted_horseman and sorted_horseman[0][1]["yoy"] > 0:
                name, data = sorted_horseman[0]
                highlights.append(
                    f"{name} horseman surging at {data['yoy']*100:+.1f}% YoY, "
                    f"now {data['share']*100:.1f}% MDP share" if data["share"] else
                    f"{name} horseman up {data['yoy']*100:+.1f}% YoY"
                )

        # Best traffic source
        if metrics["traffic_breakdown"]:
            sorted_traffic = sorted(
                [(k, v) for k, v in metrics["traffic_breakdown"].items() if v["yoy"] is not None],
                key=lambda x: x[1]["yoy"],
                reverse=True
            )
            if sorted_traffic and sorted_traffic[0][1]["yoy"] > 0:
                name, data = sorted_traffic[0]
                highlights.append(
                    f"{name} channel up {data['yoy']*100:+.1f}% YoY, "
                    f"{data['share']*100:.1f}% of MDP share" if data["share"] else
                    f"{name} channel growing {data['yoy']*100:+.1f}% YoY"
                )

        # Best OU (if global view)
        if not ou and metrics["ou_breakdown"]:
            sorted_ous = sorted(
                [(k, v) for k, v in metrics["ou_breakdown"].items() if v["yoy"] is not None],
                key=lambda x: x[1]["yoy"],
                reverse=True
            )
            if sorted_ous and sorted_ous[0][1]["yoy"] > 0:
                name, data = sorted_ous[0]
                highlights.append(
                    f"{name} leading growth at {data['yoy']*100:+.1f}% YoY"
                )

        return highlights[:3]

    def _generate_areas_to_watch(self, metrics, cloud, ou):
        """Generate areas to watch - declining metrics and risks"""
        areas = []

        contrib_pct = metrics["avg_contribution"] * 100
        scope = f"{ou} - {cloud}" if ou else cloud

        # Contribution floor risk
        if contrib_pct < 28:
            areas.append(
                f"{scope} contribution at {contrib_pct:.1f}%, well below the 30% floor — "
                f"{metrics['avg_contribution_diff']:+.1f}ppts vs. FY-1; urgent remediation needed"
            )
        elif contrib_pct < 30:
            areas.append(
                f"{scope} contribution at {contrib_pct:.1f}%, approaching the 30% floor — "
                f"{metrics['avg_contribution_diff']:+.1f}ppts vs. FY-1"
            )

        # Worst horseman
        if metrics["horseman_breakdown"]:
            sorted_horseman = sorted(
                [(k, v) for k, v in metrics["horseman_breakdown"].items() if v["yoy"] is not None],
                key=lambda x: x[1]["yoy"]
            )
            if sorted_horseman and sorted_horseman[0][1]["yoy"] < -5:
                name, data = sorted_horseman[0]
                areas.append(
                    f"{name} horseman declining at {data['yoy']*100:+.1f}% YoY — "
                    f"only horseman in significant decline"
                )

        # Worst traffic
        if metrics["traffic_breakdown"]:
            sorted_traffic = sorted(
                [(k, v) for k, v in metrics["traffic_breakdown"].items() if v["yoy"] is not None],
                key=lambda x: x[1]["yoy"]
            )
            if sorted_traffic and sorted_traffic[0][1]["yoy"] < -15:
                name, data = sorted_traffic[0]
                areas.append(
                    f"{name} channel down {data['yoy']*100:+.1f}% YoY — structural weakness needs attention"
                )

        # Worst OU
        if not ou and metrics["ou_breakdown"]:
            sorted_ous = sorted(
                [(k, v) for k, v in metrics["ou_breakdown"].items() if v["yoy"] is not None],
                key=lambda x: x[1]["yoy"]
            )
            if sorted_ous and sorted_ous[0][1]["yoy"] < -10:
                name, data = sorted_ous[0]
                areas.append(
                    f"{name} declining at {data['yoy']*100:+.1f}% YoY — needs targeted support"
                )

        return areas[:3]

    def _generate_next_steps(self, metrics, cloud, ou):
        """Generate specific next steps based on metrics"""
        next_steps = []

        # Always include email/webinar as baseline tactics
        next_steps.append(
            f"Email & Webinar: Activate BOM offers in DSE; submit {cloud} prospects into Nurture Quest; "
            f"drive registrations for upcoming webinars via BASHO outreach"
        )

        # BDR TAL if AE declining
        ae_data = metrics["horseman_breakdown"].get("AE")
        if ae_data and ae_data["yoy"] and ae_data["yoy"] < -0.05:
            next_steps.append(
                f"BDR TAL: Issue TAL requests for open {cloud} opps with declining AE-sourced MDP "
                f"({ae_data['yoy']*100:.1f}% YoY); target hotspot accounts"
            )

        # Paid if performing well
        paid_data = metrics["traffic_breakdown"].get("Paid")
        if paid_data and paid_data["yoy"] and paid_data["yoy"] > 0.1:
            next_steps.append(
                f"Paid: Continue scaling paid tactics — Content Syndication and SEM showing strong ROI "
                f"({paid_data['yoy']*100:+.1f}% YoY); enter leads into nurture for conversion"
            )

        # Organic if declining
        organic_data = metrics["traffic_breakdown"].get("Organic")
        if organic_data and organic_data["yoy"] and organic_data["yoy"] < -0.2:
            next_steps.append(
                f"Organic: Address organic channel decline ({organic_data['yoy']*100:.1f}% YoY); "
                f"audit SEO, review content strategy, activate organic social"
            )

        return next_steps[:3]

    def _fallback_insights(self, cloud, ou):
        """Fallback insights if generation fails"""
        scope = f"{ou} - {cloud}" if ou else cloud
        return {
            "highlights": [
                f"Data refresh in progress for {scope}",
                "Insights will be available once CSV files are fully loaded",
                "Check back after the next automatic refresh (6:00 AM or 11:00 PM CET)"
            ],
            "areas_to_watch": [
                "CSV data files not accessible or empty",
                "Ensure Tableau refresh has completed successfully",
                "Verify data quality in admin panel"
            ],
            "next_steps": [
                "Trigger a manual CSV refresh from the Admin panel",
                "Check system logs for any errors during the last refresh",
                "Contact support if the issue persists"
            ]
        }


# Singleton
insights_generator = InsightsGenerator()
