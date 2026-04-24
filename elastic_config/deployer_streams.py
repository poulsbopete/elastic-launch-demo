"""StreamsMixin — stream fork, significant events deploy and cleanup methods."""

from __future__ import annotations

import logging

import httpx

from elastic_config.deployer_base import _kibana_headers, ProgressCallback

logger = logging.getLogger("deployer")


class StreamsMixin:

    @property
    def _stream_name(self) -> str:
        return f"logs.otel.{self.ns}"

    def _create_stream(self, client: httpx.Client) -> None:
        """Fork logs.otel into a scenario-specific child stream."""
        resp = client.post(
            f"{self.kibana_url}/api/streams/logs.otel/_fork",
            headers=_kibana_headers(self.api_key),
            json={
                "where": {
                    "field": "resource.attributes.service.namespace",
                    "eq": self.ns,
                },
                "status": "enabled",
                "stream": {
                    "name": self._stream_name,
                },
            },
        )
        if resp.status_code >= 300:
            logger.warning("Stream fork failed (HTTP %s): %s", resp.status_code, resp.text[:500])

    def _deploy_significant_events(self, client: httpx.Client, notify: ProgressCallback):
        step = self._step(10)
        step.status = "running"
        notify(self.progress)

        # Delete any existing stream then recreate it clean
        self._delete_stream(client)
        self._create_stream(client)

        # Build bulk operations
        operations = []
        registry = self.scenario.channel_registry
        for ch_num, ch_data in sorted(registry.items()):
            num_str = f"{int(ch_num):02d}"
            error_type = ch_data["error_type"]
            esql_query = (
                f"FROM {self._stream_name},{self._stream_name}.* METADATA _id, _source"
                f' | WHERE body.text LIKE "*{error_type}*" AND severity_text == "ERROR"'
            )
            operations.append({
                "index": {
                    "id": f"{self.ns}-se-ch{num_str}",
                    "title": f"{self.scenario.scenario_name}: SE CH {num_str}: {ch_data['name']}",
                    "description": f"{ch_data.get('subsystem', 'system')} — {error_type}",
                    "esql": {"query": esql_query},
                }
            })

        step.items_total = len(operations)

        if operations:
            resp = client.post(
                f"{self.kibana_url}/api/streams/{self._stream_name}/queries/_bulk",
                headers=_kibana_headers(self.api_key),
                json={"operations": operations},
            )
            if resp.status_code < 300:
                step.items_done = len(operations)
                step.detail = f"Created {len(operations)} stream queries on {self._stream_name}"
            else:
                logger.warning("Significant events bulk create failed: %s", resp.text[:500])
                step.detail = f"Bulk create failed (HTTP {resp.status_code})"

        step.status = "ok" if step.items_done > 0 else "failed"
        notify(self.progress)

    def _delete_stream(self, client: httpx.Client) -> None:
        """Delete the scenario-specific stream (also removes its significant events)."""
        try:
            resp = client.delete(
                f"{self.kibana_url}/api/streams/{self._stream_name}",
                headers=_kibana_headers(self.api_key),
            )
            if resp.status_code == 404:
                return  # already gone
            if resp.status_code >= 300:
                logger.warning(
                    "Failed to delete stream %s: HTTP %s", self._stream_name, resp.status_code,
                )
        except Exception as exc:
            logger.warning("Exception deleting stream %s: %s", self._stream_name, exc)
