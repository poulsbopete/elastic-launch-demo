"""Digital Marketplace service — AWS us-east-1b. E-commerce platform for physical and digital cards."""

from __future__ import annotations

import random

from app.services.base_service import BaseService
from scenarios.executive_kpis import emit_executive_business_metrics_if_eligible


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

        table_full = any(
            self._channel_registry.get(ch, {}).get("fault_kind") == "table_full_vs_disk"
            for ch in active_channels
        )

        # -- Transaction metrics --
        active_users = random.randint(800, 3500)
        transactions_per_sec = round(random.uniform(8.0, 25.0), 1) if table_full else round(random.uniform(45.0, 120.0), 1)
        cart_conversion = round(random.uniform(0.4, 1.8), 2) if table_full else round(random.uniform(2.5, 6.8), 2)
        avg_response_ms = round(random.uniform(2500.0, 9000.0), 1) if table_full else round(random.uniform(35.0, 120.0), 1)

        self.emit_metric("marketplace.active_users", float(active_users), "users")
        self.emit_metric(
            "marketplace.transactions_per_sec", transactions_per_sec, "tps"
        )
        self.emit_metric("marketplace.cart_conversion_pct", cart_conversion, "%")
        self.emit_metric("marketplace.avg_response_ms", avg_response_ms, "ms")

        # Amazon Bedrock listing-assistant — always-on LLM observability
        bedrock_latency_ms = round(random.uniform(1800.0, 7000.0), 1) if table_full else round(random.uniform(90.0, 420.0), 1)
        input_tokens = float(random.randint(180, 1400))
        output_tokens = float(random.randint(0, 40) if table_full else random.randint(40, 650))
        self.emit_metric("gen_ai.client.operation.duration", bedrock_latency_ms, "ms")
        self.emit_metric("gen_ai.client.token.usage.input", input_tokens, "{token}")
        self.emit_metric("gen_ai.client.token.usage.output", output_tokens, "{token}")

        emit_executive_business_metrics_if_eligible(self)

        self.emit_log(
            "INFO",
            f"marketplace.health active_users={active_users} tps={transactions_per_sec} "
            f"cart_conversion={cart_conversion}% response_ms={avg_response_ms} "
            f"bedrock_model=anthropic.claude-3-5-sonnet-20241022-v2:0 "
            f"bedrock_latency_ms={bedrock_latency_ms} "
            f"bedrock_tokens_in={int(input_tokens)} bedrock_tokens_out={int(output_tokens)}",
            {
                "operation": "marketplace_health",
                "marketplace.active_users": active_users,
                "marketplace.tps": transactions_per_sec,
                "marketplace.conversion": cart_conversion,
                "marketplace.response_ms": avg_response_ms,
                "gen_ai.provider.name": "aws.bedrock",
                "gen_ai.request.model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "gen_ai.client.operation.duration": bedrock_latency_ms,
            },
        )

        # Catalog sync status
        catalog_items = random.randint(120000, 180000)
        self.emit_log(
            "INFO",
            f"marketplace.catalog_sync status=nominal items_indexed={catalog_items}",
            {"operation": "catalog_sync", "catalog.item_count": catalog_items},
        )
