"""Digital Marketplace service — AWS us-east-1b. E-commerce platform for physical and digital cards."""

from __future__ import annotations

import random

from app.services.base_service import BaseService


class DigitalMarketplaceService(BaseService):
    SERVICE_NAME = "digital-marketplace"

    def generate_telemetry(self) -> None:
        # -- Fault injection --
        active_channels = self.get_active_channels_for_service()
        for ch in active_channels:
            self.emit_fault_logs(ch)

        cascade_channels = self.get_cascade_channels_for_service()
        for ch in cascade_channels:
            self.emit_cascade_logs(ch)

        # -- Transaction metrics --
        active_users = random.randint(800, 3500)
        transactions_per_sec = round(random.uniform(45.0, 120.0), 1)
        cart_conversion = round(random.uniform(2.5, 6.8), 2)
        avg_response_ms = round(random.uniform(35.0, 120.0), 1)

        self.emit_metric("marketplace.active_users", float(active_users), "users")
        self.emit_metric(
            "marketplace.transactions_per_sec", transactions_per_sec, "tps"
        )
        self.emit_metric("marketplace.cart_conversion_pct", cart_conversion, "%")
        self.emit_metric("marketplace.avg_response_ms", avg_response_ms, "ms")

        # Synthetic executive KPIs — sports media + marketplace + wagering (Kibana Executive dashboard)
        ad_revenue = round(random.uniform(85_000.0, 520_000.0), 1)
        fill_rate = round(random.uniform(82.0, 98.4), 2)
        betting_handle = round(random.uniform(180_000.0, 2_200_000.0), 1)
        hold_pct = round(random.uniform(6.5, 14.2), 2)
        self.emit_metric("business.ad_revenue_usd_per_min", ad_revenue, "USD/min")
        self.emit_metric("business.programmatic_fill_rate_pct", fill_rate, "%")
        self.emit_metric("business.betting_handle_usd_per_min", betting_handle, "USD/min")
        self.emit_metric("business.betting_hold_pct", hold_pct, "%")

        live_ccv = float(random.randint(78_000, 520_000))
        video_minutes_1m = round(random.uniform(120_000.0, 980_000.0), 1)
        page_views_1m = float(random.randint(180_000, 2_400_000))
        app_sessions_1m = float(random.randint(900, 12_000))
        subscription_mrr_1m = round(random.uniform(18_000.0, 185_000.0), 1)
        merch_gmv_1m = round(random.uniform(28_000.0, 310_000.0), 1)
        live_ticketing_1m = round(random.uniform(4_500.0, 98_000.0), 1)
        partner_sponsor_1m = round(random.uniform(15_000.0, 195_000.0), 1)
        fantasy_entries_active = float(random.randint(9_000, 220_000))
        sponsored_inv_1m = float(random.randint(400, 12_000))
        premium_arpu = round(random.uniform(8.2, 34.9), 2)
        content_completion_pct = round(random.uniform(38.0, 82.0), 2)
        push_ctr_pct = round(random.uniform(2.0, 11.5), 2)
        newsletter_open_pct = round(random.uniform(16.0, 38.0), 2)
        loyalty_redeem_1m = float(random.randint(25_000, 380_000))
        api_b2b_revenue_1m = round(random.uniform(6_000.0, 72_000.0), 1)
        churn_risk_index = round(random.uniform(11.0, 52.0), 1)
        nps_proxy = round(random.uniform(-8.0, 68.0), 1)
        clip_shares_1m = float(random.randint(3_000, 95_000))
        betting_gross_win_1m = round(random.uniform(12_000.0, 210_000.0), 1)

        self.emit_metric("business.live_concurrent_viewers", live_ccv, "viewers")
        self.emit_metric("business.video_minutes_engaged_per_min", video_minutes_1m, "min/min")
        self.emit_metric("business.page_views_per_min", page_views_1m, "views/min")
        self.emit_metric("business.app_sessions_per_min", app_sessions_1m, "sessions/min")
        self.emit_metric("business.subscription_mrr_usd_per_min", subscription_mrr_1m, "USD/min")
        self.emit_metric("business.merch_gmv_usd_per_min", merch_gmv_1m, "USD/min")
        self.emit_metric("business.live_event_ticketing_usd_per_min", live_ticketing_1m, "USD/min")
        self.emit_metric("business.partner_sponsorship_usd_per_min", partner_sponsor_1m, "USD/min")
        self.emit_metric("business.fantasy_active_entries", fantasy_entries_active, "entries")
        self.emit_metric("business.sponsored_inventory_seconds_per_min", sponsored_inv_1m, "s/min")
        self.emit_metric("business.premium_tier_arpu_usd", premium_arpu, "USD")
        self.emit_metric("business.content_completion_rate_pct", content_completion_pct, "%")
        self.emit_metric("business.push_notification_ctr_pct", push_ctr_pct, "%")
        self.emit_metric("business.newsletter_open_rate_pct", newsletter_open_pct, "%")
        self.emit_metric("business.loyalty_points_redeemed_per_min", loyalty_redeem_1m, "pts/min")
        self.emit_metric("business.api_data_partner_revenue_usd_per_min", api_b2b_revenue_1m, "USD/min")
        self.emit_metric("business.churn_risk_index_0_100", churn_risk_index, "index")
        self.emit_metric("business.net_satisfaction_proxy_nps", nps_proxy, "score")
        self.emit_metric("business.social_clip_shares_per_min", clip_shares_1m, "shares/min")
        self.emit_metric("business.betting_gross_win_usd_per_min", betting_gross_win_1m, "USD/min")

        self.emit_log(
            "INFO",
            f"marketplace.health active_users={active_users} tps={transactions_per_sec} "
            f"cart_conversion={cart_conversion}% response_ms={avg_response_ms}",
            {
                "operation": "marketplace_health",
                "marketplace.active_users": active_users,
                "marketplace.tps": transactions_per_sec,
                "marketplace.conversion": cart_conversion,
                "marketplace.response_ms": avg_response_ms,
            },
        )

        # Catalog sync status
        catalog_items = random.randint(120000, 180000)
        self.emit_log(
            "INFO",
            f"marketplace.catalog_sync status=nominal items_indexed={catalog_items}",
            {"operation": "catalog_sync", "catalog.item_count": catalog_items},
        )
