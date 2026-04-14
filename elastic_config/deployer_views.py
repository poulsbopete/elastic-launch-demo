"""DataViewsMixin — data view deploy methods."""

from __future__ import annotations

import urllib.parse

import httpx

from elastic_config.deployer_base import _kibana_headers, ProgressCallback


class DataViewsMixin:

    def _deploy_data_views(self, client: httpx.Client, notify: ProgressCallback):
        step = self._step(11)
        step.status = "running"
        notify(self.progress)

        views = [
            # Custom view for exec dashboard panels (broad match, no hyphen)
            {
                "data_view": {
                    "id": "logs*",
                    "title": "logs*",
                    "name": f"{self.scenario.scenario_name} Logs",
                    "timeFieldName": "@timestamp",
                },
                "override": True,
            },
            # OTel-standard views — required by shipped [OTel] dashboards
            {
                "data_view": {
                    "id": "logs-*",
                    "title": "logs-*",
                    "name": "logs-*",
                    "timeFieldName": "@timestamp",
                },
                "override": True,
            },
            {
                "data_view": {
                    "id": "traces-*",
                    "title": "traces-*",
                    "name": f"{self.scenario.scenario_name} Traces",
                    "timeFieldName": "@timestamp",
                },
                "override": True,
            },
            {
                "data_view": {
                    "id": "metrics-*",
                    "title": "metrics-*",
                    "name": f"{self.scenario.scenario_name} Metrics",
                    "timeFieldName": "@timestamp",
                },
                "override": True,
            },
            # Required by [OTel] Host Details dashboards
            {
                "data_view": {
                    "id": "metrics-hostmetricsreceiver.otel-*",
                    "title": "metrics-hostmetricsreceiver.otel-*",
                    "name": "metrics-hostmetricsreceiver.otel-*",
                    "timeFieldName": "@timestamp",
                },
                "override": True,
            },
        ]

        step.items_total = len(views)
        created = 0
        for view in views:
            resp = client.post(
                f"{self.kibana_url}/api/data_views/data_view",
                headers=_kibana_headers(self.api_key),
                json=view,
            )
            if resp.status_code < 300:
                created += 1
                step.items_done = created
                notify(self.progress)

        step.status = "ok"
        step.detail = f"Created {created} data views"
        notify(self.progress)

    def _cleanup_data_views(self, client: httpx.Client) -> int:
        """Delete data views belonging to this scenario (matched by name prefix)."""
        scenario_prefix = f"{self.scenario.scenario_name} "
        deleted = 0
        try:
            resp = client.get(
                f"{self.kibana_url}/api/data_views",
                headers=_kibana_headers(self.api_key),
            )
            if resp.status_code < 300:
                for view in resp.json().get("data_view", []):
                    if view.get("name", "").startswith(scenario_prefix):
                        view_id = view.get("id", "")
                        if view_id:
                            encoded_id = urllib.parse.quote(view_id, safe="")
                            r = client.delete(
                                f"{self.kibana_url}/api/data_views/data_view/{encoded_id}",
                                headers=_kibana_headers(self.api_key),
                            )
                            if r.status_code < 300:
                                deleted += 1
        except Exception:
            pass
        return deleted
