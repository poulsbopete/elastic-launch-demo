"""Synthetic `business.*` OTLP gauges for the Kibana Executive dashboard (all scenarios)."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.base_service import BaseService


def emit_executive_business_metrics_if_eligible(service: "BaseService") -> None:
    """Emit leadership KPI gauges once per telemetry cycle from the scenario-designated service."""
    ctx = getattr(service, "_ctx", None)
    if not ctx:
        return
    want = getattr(ctx.scenario, "executive_kpi_emitter_service_name", None)
    if not want or want != service.SERVICE_NAME:
        return

    emit = service.emit_metric

    ad_revenue = round(random.uniform(85_000.0, 520_000.0), 1)
    fill_rate = round(random.uniform(82.0, 98.4), 2)
    betting_handle = round(random.uniform(180_000.0, 2_200_000.0), 1)
    hold_pct = round(random.uniform(6.5, 14.2), 2)
    emit("business.ad_revenue_usd_per_min", ad_revenue, "USD/min")
    emit("business.programmatic_fill_rate_pct", fill_rate, "%")
    emit("business.betting_handle_usd_per_min", betting_handle, "USD/min")
    emit("business.betting_hold_pct", hold_pct, "%")

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

    emit("business.live_concurrent_viewers", live_ccv, "viewers")
    emit("business.video_minutes_engaged_per_min", video_minutes_1m, "min/min")
    emit("business.page_views_per_min", page_views_1m, "views/min")
    emit("business.app_sessions_per_min", app_sessions_1m, "sessions/min")
    emit("business.subscription_mrr_usd_per_min", subscription_mrr_1m, "USD/min")
    emit("business.merch_gmv_usd_per_min", merch_gmv_1m, "USD/min")
    emit("business.live_event_ticketing_usd_per_min", live_ticketing_1m, "USD/min")
    emit("business.partner_sponsorship_usd_per_min", partner_sponsor_1m, "USD/min")
    emit("business.fantasy_active_entries", fantasy_entries_active, "entries")
    emit("business.sponsored_inventory_seconds_per_min", sponsored_inv_1m, "s/min")
    emit("business.premium_tier_arpu_usd", premium_arpu, "USD")
    emit("business.content_completion_rate_pct", content_completion_pct, "%")
    emit("business.push_notification_ctr_pct", push_ctr_pct, "%")
    emit("business.newsletter_open_rate_pct", newsletter_open_pct, "%")
    emit("business.loyalty_points_redeemed_per_min", loyalty_redeem_1m, "pts/min")
    emit("business.api_data_partner_revenue_usd_per_min", api_b2b_revenue_1m, "USD/min")
    emit("business.churn_risk_index_0_100", churn_risk_index, "index")
    emit("business.net_satisfaction_proxy_nps", nps_proxy, "score")
    emit("business.social_clip_shares_per_min", clip_shares_1m, "shares/min")
    emit("business.betting_gross_win_usd_per_min", betting_gross_win_1m, "USD/min")
