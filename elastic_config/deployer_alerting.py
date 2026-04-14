"""AlertingMixin — alerting deploy and cleanup methods."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

import httpx

from elastic_config.deployer_base import _kibana_headers, ProgressCallback

if TYPE_CHECKING:
    from scenarios.base import BaseScenario

logger = logging.getLogger("deployer")


class AlertingMixin:
    # Attributes supplied by ScenarioDeployer at runtime — declared here for type checkers.
    if TYPE_CHECKING:
        kibana_url: str
        api_key: str
        ns: str
        scenario: BaseScenario
        _workflow_ids: dict[str, str]

    def _deploy_alerting(self, client: httpx.Client, notify: ProgressCallback):
        step = self._step(13)
        step.status = "running"
        notify(self.progress)

        # Find notification workflow ID
        notification_wf_id = ""
        for name_frag, wf_id in self._workflow_ids.items():
            if "notification" in name_frag or "significant" in name_frag:
                notification_wf_id = wf_id
                break

        if not notification_wf_id:
            # Search for it
            try:
                items = self._wf_search(client)
                for item in items:
                    if "Notification" in item.get("name", "") or "Significant" in item.get("name", ""):
                        notification_wf_id = item["id"]
                        break
            except Exception:
                pass

        if not notification_wf_id:
            step.status = "failed"
            step.detail = "Notification workflow not found"
            notify(self.progress)
            return

        # Clean old rules
        self._cleanup_alerts(client)

        # Create 20 alert rules
        registry = self.scenario.channel_registry
        step.items_total = len(registry)

        for ch_num, ch_data in sorted(registry.items()):
            num_str = f"{int(ch_num):02d}"
            error_type = ch_data["error_type"]
            name = ch_data["name"]
            subsystem = ch_data.get("subsystem", "")

            # Determine severity
            ch_int = int(ch_num)
            if ch_int >= 19:
                severity = "critical"
            elif ch_int <= 6:
                severity = "high"
            else:
                severity = "medium"

            rule_name = f"{self.scenario.scenario_name} CH{num_str}: {name}"

            es_query = json.dumps({
                "query": {
                    "bool": {
                        "filter": [
                            {"range": {"@timestamp": {"gte": "now-1m"}}},
                            {"match_phrase": {"body.text": error_type}},
                            {"term": {"severity_text": "ERROR"}},
                        ]
                    }
                }
            })

            rule = {
                "name": rule_name,
                "rule_type_id": ".es-query",
                "consumer": "alerts",
                "tags": [self.ns, error_type],
                "schedule": {"interval": "1m"},
                "params": {
                    "searchType": "esQuery",
                    "esQuery": es_query,
                    "index": ["logs*"],
                    "timeField": "@timestamp",
                    "threshold": [0],
                    "thresholdComparator": ">",
                    "size": 100,
                    "timeWindowSize": 1,
                    "timeWindowUnit": "m",
                },
                "actions": [{
                    "group": "query matched",
                    "id": "system-connector-.workflows",
                    "frequency": {
                        "summary": False,
                        "notify_when": "onActiveAlert",
                        "throttle": None,
                    },
                    "params": {
                        "subAction": "run",
                        "subActionParams": {
                            "workflowId": notification_wf_id,
                            "inputs": {
                                "channel": ch_int,
                                "error_type": error_type,
                                "subsystem": subsystem,
                                "severity": severity,
                            },
                        },
                    },
                }],
            }

            resp = client.post(
                f"{self.kibana_url}/api/alerting/rule",
                headers=_kibana_headers(self.api_key),
                json=rule,
            )
            if resp.status_code < 300:
                step.items_done += 1
            else:
                logger.warning("Alert rule %s failed: %s", rule_name, resp.text[:200])
            notify(self.progress)

        step.status = "ok" if step.items_done > 0 else "failed"
        step.detail = f"Created {step.items_done}/{step.items_total} alert rules"
        notify(self.progress)

    def _cleanup_alerts(self, client: httpx.Client) -> int:
        """Delete alert rules belonging to this scenario.

        Primary: name-based search (new-style rules named "{scenario_name} CH…").
        Fallback: tag-based search (old-style rules tagged with namespace).
        """
        deleted = 0
        deleted_ids: set[str] = set()
        scenario_name = self.scenario.scenario_name

        # Primary: name-based (new-style rules named "{scenario_name} CH…")
        try:
            for page in range(1, 11):
                resp = client.get(
                    f"{self.kibana_url}/api/alerting/rules/_find",
                    params={"per_page": 100, "page": page, "search_fields": "name", "search": scenario_name},
                    headers=_kibana_headers(self.api_key),
                )
                if resp.status_code >= 300:
                    break
                rules = resp.json().get("data", [])
                if not rules:
                    break
                for rule in rules:
                    if scenario_name not in rule.get("name", ""):
                        continue
                    rule_id = rule.get("id", "")
                    if rule_id and rule_id not in deleted_ids:
                        client.delete(
                            f"{self.kibana_url}/api/alerting/rule/{rule_id}",
                            headers=_kibana_headers(self.api_key),
                        )
                        deleted_ids.add(rule_id)
                        deleted += 1
        except Exception:
            pass

        # Fallback: tag-based (old-style rules tagged with namespace)
        try:
            for page in range(1, 11):
                resp = client.get(
                    f"{self.kibana_url}/api/alerting/rules/_find?per_page=100&page={page}"
                    f"&filter=alert.attributes.tags:{self.ns}",
                    headers=_kibana_headers(self.api_key),
                )
                if resp.status_code >= 300:
                    break
                rules = resp.json().get("data", [])
                if not rules:
                    break
                for rule in rules:
                    rule_id = rule.get("id", "")
                    if rule_id and rule_id not in deleted_ids:
                        client.delete(
                            f"{self.kibana_url}/api/alerting/rule/{rule_id}",
                            headers=_kibana_headers(self.api_key),
                        )
                        deleted_ids.add(rule_id)
                        deleted += 1
        except Exception:
            pass

        # Migration cleanup: pre-refactor rules named "Channel XX: {name}" with no scenario prefix.
        # Build exact expected names from this scenario's channel registry.
        old_names: set[str] = set()
        for ch_num, ch_data in self.scenario.channel_registry.items():
            num_str = f"{int(ch_num):02d}"
            old_names.add(f"Channel {num_str}: {ch_data['name']}")

        if old_names:
            try:
                for page in range(1, 11):
                    resp = client.get(
                        f"{self.kibana_url}/api/alerting/rules/_find?per_page=100&page={page}",
                        headers=_kibana_headers(self.api_key),
                    )
                    if resp.status_code >= 300:
                        break
                    rules = resp.json().get("data", [])
                    if not rules:
                        break
                    for rule in rules:
                        rule_id = rule.get("id", "")
                        if rule.get("name", "") in old_names and rule_id and rule_id not in deleted_ids:
                            client.delete(
                                f"{self.kibana_url}/api/alerting/rule/{rule_id}",
                                headers=_kibana_headers(self.api_key),
                            )
                            deleted_ids.add(rule_id)
                            deleted += 1
            except Exception:
                pass

        return deleted
