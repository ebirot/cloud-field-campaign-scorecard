"""
Insights Generator - Analyze CSV data and generate insights in Scorecard style
Replicates the Slack Skills "Health of Cloud Scorecard Builder" logic
"""
import pandas as pd
import os
from typing import Dict, List, Any
from datetime import datetime


class InsightsGenerator:
    """Generate Marketing Performance Insights from CSV data"""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data"
            )
        self.data_dir = data_dir

        # Load all CSV files
        self.regional_sales_l2_cloud = None
        self.horseman = None
        self.traffic_source = None
        self.offer_l1_l2 = None

    def load_csvs(self):
        """Load all required CSV files"""
        try:
            self.regional_sales_l2_cloud = pd.read_csv(
                os.path.join(self.data_dir, "2_regional_sales_l2_cloud.csv")
            )
            self.horseman = pd.read_csv(
                os.path.join(self.data_dir, "6_horseman.csv")
            )
            self.traffic_source = pd.read_csv(
                os.path.join(self.data_dir, "7_traffic_source.csv")
            )
            self.offer_l1_l2 = pd.read_csv(
                os.path.join(self.data_dir, "8_offer_l1_l2.csv")
            )
            return True
        except Exception as e:
            print(f"Error loading CSVs: {str(e)}")
            return False

    def generate_insights(
        self,
        cloud: str,
        ou: str = None,
        quarter: str = "All"
    ) -> Dict[str, List[str]]:
        """
        Generate insights for a specific Cloud or OU

        Args:
            cloud: Cloud name (Service, Sales, Marketing, Commerce, AI & Data)
            ou: Optional OU filter (France, UKI, North, South, Central, AMER CBS, etc.)
            quarter: Q1, Q2, Q3, Q4, or All (YTD)

        Returns:
            {
                "highlights": [...],
                "areas_to_watch": [...],
                "next_steps": [...]
            }
        """
        if not self.load_csvs():
            return self._fallback_insights()

        # Filter data
        df_regional = self._filter_regional(cloud, ou, quarter)
        df_horseman = self._filter_horseman(cloud, ou, quarter)
        df_traffic = self._filter_traffic(cloud, ou, quarter)
        df_offers = self._filter_offers(cloud, ou, quarter)

        # Calculate metrics
        metrics = self._calculate_metrics(
            df_regional, df_horseman, df_traffic, df_offers
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

    def _filter_regional(self, cloud, ou, quarter):
        """Filter regional data by cloud/ou/quarter"""
        df = self.regional_sales_l2_cloud.copy()

        # Filter by cloud
        if 'APM L1' in df.columns:
            df = df[df['APM L1'] == cloud]
        elif 'Product L1' in df.columns:
            df = df[df['Product L1'] == cloud]

        # Filter by OU
        if ou and 'OU' in df.columns:
            df = df[df['OU'] == ou]

        # Filter by quarter
        if quarter != "All" and 'Opportunity Stage 2 Date - Fiscal Quarter' in df.columns:
            df = df[df['Opportunity Stage 2 Date - Fiscal Quarter'] == quarter]

        return df

    def _filter_horseman(self, cloud, ou, quarter):
        """Filter horseman data"""
        df = self.horseman.copy()

        if 'APM L1' in df.columns:
            df = df[df['APM L1'] == cloud]
        if ou and 'OU' in df.columns:
            df = df[df['OU'] == ou]
        if quarter != "All" and 'Opportunity Stage 2 Date - Fiscal Quarter' in df.columns:
            df = df[df['Opportunity Stage 2 Date - Fiscal Quarter'] == quarter]

        return df

    def _filter_traffic(self, cloud, ou, quarter):
        """Filter traffic source data"""
        df = self.traffic_source.copy()

        if 'APM L1' in df.columns:
            df = df[df['APM L1'] == cloud]
        if ou and 'OU' in df.columns:
            df = df[df['OU'] == ou]
        if quarter != "All" and 'Opportunity Stage 2 Date - Fiscal Quarter' in df.columns:
            df = df[df['Opportunity Stage 2 Date - Fiscal Quarter'] == quarter]

        return df

    def _filter_offers(self, cloud, ou, quarter):
        """Filter offer data"""
        df = self.offer_l1_l2.copy()

        if 'APM L1' in df.columns:
            df = df[df['APM L1'] == cloud]
        if ou and 'OU' in df.columns:
            df = df[df['OU'] == ou]
        if quarter != "All" and 'Opportunity Stage 2 Date - Fiscal Quarter' in df.columns:
            df = df[df['Opportunity Stage 2 Date - Fiscal Quarter'] == quarter]

        return df

    def _calculate_metrics(self, df_regional, df_horseman, df_traffic, df_offers):
        """Calculate all required metrics"""
        metrics = {
            "total_mdp": 0,
            "yoy_change": 0,
            "contribution_rate": 0,
            "contribution_diff": 0,
            "horseman": {},
            "traffic": {},
            "offers": {},
            "ous": {}
        }

        # Total MDP
        if 'Current FY MDP' in df_regional.columns:
            metrics["total_mdp"] = df_regional['Current FY MDP'].sum()

        # YoY Change
        if '% YoY' in df_regional.columns:
            metrics["yoy_change"] = df_regional['% YoY'].mean()

        # Contribution
        if 'CFY MDP Contribution' in df_regional.columns:
            metrics["contribution_rate"] = df_regional['CFY MDP Contribution'].mean()

        if 'MDP Contr. Diff vs FY-1 (ppts)' in df_regional.columns:
            metrics["contribution_diff"] = df_regional['MDP Contr. Diff vs FY-1 (ppts)'].mean()

        # Horseman breakdown
        if not df_horseman.empty and 'Opportunity Source' in df_horseman.columns:
            for _, row in df_horseman.iterrows():
                source = row['Opportunity Source']
                if source not in ['SDR', 'Unknown']:  # Exclude SDR
                    metrics["horseman"][source] = {
                        "mdp": row.get('Current FY MDP', 0),
                        "yoy": row.get('% YoY', 0),
                        "share": row.get('% MDP Share', 0)
                    }

        # Traffic Source breakdown
        if not df_traffic.empty and 'Traffic Source Grouping L1' in df_traffic.columns:
            for _, row in df_traffic.iterrows():
                source = row['Traffic Source Grouping L1']
                metrics["traffic"][source] = {
                    "mdp": row.get('Current FY MDP', 0),
                    "yoy": row.get('% YoY', 0),
                    "share": row.get('% MDP Share', 0)
                }

        # Offers breakdown
        if not df_offers.empty and 'Offer Grouping L1' in df_offers.columns:
            for _, row in df_offers.iterrows():
                offer = row['Offer Grouping L1']
                metrics["offers"][offer] = {
                    "mdp": row.get('Current FY MDP', 0),
                    "yoy": row.get('% YoY', 0),
                    "share": row.get('% MDP Share', 0)
                }

        # OU breakdown
        if not df_regional.empty and 'OU' in df_regional.columns:
            for _, row in df_regional.iterrows():
                ou = row['OU']
                metrics["ous"][ou] = {
                    "mdp": row.get('Current FY MDP', 0),
                    "yoy": row.get('% YoY', 0),
                    "contribution": row.get('CFY MDP Contribution', 0)
                }

        return metrics

    def _generate_highlights(self, metrics, cloud, ou):
        """Generate highlights based on metrics"""
        highlights = []

        # Overall performance
        total_mdp = metrics["total_mdp"] / 1_000_000  # Convert to millions
        yoy = metrics["yoy_change"] * 100
        contrib = metrics["contribution_rate"] * 100

        if yoy > 0:
            highlights.append(
                f"{cloud} MDP at ${total_mdp:.1f}M, up {yoy:+.1f}% YoY with strong overall growth"
            )
        else:
            highlights.append(
                f"{cloud} MDP at ${total_mdp:.1f}M, {yoy:+.1f}% YoY — contribution at {contrib:.1f}%"
            )

        # Top horseman
        if metrics["horseman"]:
            top_horseman = max(
                metrics["horseman"].items(),
                key=lambda x: x[1]["yoy"]
            )
            horseman_name, horseman_data = top_horseman
            if horseman_data["yoy"] > 0:
                highlights.append(
                    f"{horseman_name} horseman surging at {horseman_data['yoy']:+.1f}% YoY, "
                    f"now {horseman_data['share']:.1f}% MDP share"
                )

        # Top traffic source
        if metrics["traffic"]:
            top_traffic = max(
                metrics["traffic"].items(),
                key=lambda x: x[1]["yoy"]
            )
            traffic_name, traffic_data = top_traffic
            if traffic_data["yoy"] > 0:
                highlights.append(
                    f"{traffic_name} channel up {traffic_data['yoy']:+.1f}% YoY, "
                    f"{traffic_data['share']:.1f}% of MDP share"
                )

        # Top OU
        if metrics["ous"]:
            top_ou = max(
                metrics["ous"].items(),
                key=lambda x: x[1]["yoy"]
            )
            ou_name, ou_data = top_ou
            if ou_data["yoy"] > 0:
                highlights.append(
                    f"{ou_name} leading growth at {ou_data['yoy']:+.1f}% YoY"
                )

        return highlights[:3]  # Limit to 3 highlights

    def _generate_areas_to_watch(self, metrics, cloud, ou):
        """Generate areas to watch based on metrics"""
        areas = []

        # Contribution floor risk
        contrib = metrics["contribution_rate"] * 100
        if contrib < 30:
            contrib_diff = metrics["contribution_diff"]
            areas.append(
                f"{cloud} contribution at {contrib:.1f}%, below the 30% floor — "
                f"{contrib_diff:+.1f}ppts vs. FY-1; urgent remediation needed"
            )
        elif contrib < 32:
            areas.append(
                f"{cloud} contribution at {contrib:.1f}%, approaching the 30% floor"
            )

        # Declining horseman
        if metrics["horseman"]:
            worst_horseman = min(
                metrics["horseman"].items(),
                key=lambda x: x[1]["yoy"]
            )
            horseman_name, horseman_data = worst_horseman
            if horseman_data["yoy"] < 0:
                areas.append(
                    f"{horseman_name} horseman declining at {horseman_data['yoy']:+.1f}% YoY, "
                    f"now {horseman_data['share']:.1f}% MDP share"
                )

        # Declining traffic
        if metrics["traffic"]:
            worst_traffic = min(
                metrics["traffic"].items(),
                key=lambda x: x[1]["yoy"]
            )
            traffic_name, traffic_data = worst_traffic
            if traffic_data["yoy"] < -10:  # Only flag significant declines
                areas.append(
                    f"{traffic_name} channel down {traffic_data['yoy']:+.1f}% YoY — "
                    f"structural weakness needs attention"
                )

        # Declining OU
        if metrics["ous"]:
            worst_ou = min(
                metrics["ous"].items(),
                key=lambda x: x[1]["yoy"]
            )
            ou_name, ou_data = worst_ou
            if ou_data["yoy"] < 0:
                areas.append(
                    f"{ou_name} declining at {ou_data['yoy']:+.1f}% YoY"
                )

        return areas[:3]  # Limit to 3 areas

    def _generate_next_steps(self, metrics, cloud, ou):
        """Generate specific next steps based on metrics"""
        next_steps = []

        # Email activation
        next_steps.append(
            f"Email: Submit {cloud} prospects into Nurture Quest; activate BOM offers in DSE; "
            f"refresh underperforming email content"
        )

        # Webinar/Events
        next_steps.append(
            f"Webinar: Drive registrations for upcoming {cloud} webinars via BASHO outreach; "
            f"promote on-demand content via paid and organic social"
        )

        # BDR TAL
        if metrics["horseman"].get("AE", {}).get("yoy", 0) < 0:
            next_steps.append(
                f"BDR TAL: Issue TAL requests for open {cloud} opps with declining AE-sourced MDP; "
                f"target hotspot accounts to compensate for AE gap"
            )

        # Paid activation
        if metrics["traffic"].get("Paid", {}).get("yoy", 0) > 0:
            next_steps.append(
                f"Paid: Continue scaling paid tactics — Content Syndication and SEM showing strong ROI; "
                f"enter leads into nurture for mid-funnel conversion"
            )

        return next_steps[:3]  # Limit to 3 actions

    def _fallback_insights(self):
        """Fallback insights if CSV loading fails"""
        return {
            "highlights": [
                "Data refresh in progress — insights will be available once CSV files are loaded",
                "Check back after the next automatic refresh (6:00 AM or 11:00 PM CET)",
                "Contact admin if this message persists"
            ],
            "areas_to_watch": [
                "CSV data files not accessible",
                "Ensure Tableau refresh has completed successfully",
                "Verify CSV files exist in backend/data/ directory"
            ],
            "next_steps": [
                "Trigger a manual CSV refresh from the Admin panel",
                "Check system logs for any errors during the last refresh",
                "Contact support if the issue continues"
            ]
        }


# Singleton
insights_generator = InsightsGenerator()
