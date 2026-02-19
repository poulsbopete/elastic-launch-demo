"""Google Cloud Network Operations scenario — GCP-native networking across 3 regions."""

from __future__ import annotations

import random
from typing import Any

from scenarios.base import BaseScenario, CountdownConfig, UITheme


class GCPScenario(BaseScenario):
    """GCP-native network operations across us-central1, us-east1, europe-west1."""

    # ── Identity ──────────────────────────────────────────────────────

    @property
    def scenario_id(self) -> str:
        return "gcp"

    @property
    def scenario_name(self) -> str:
        return "Google Cloud Network Operations"

    @property
    def scenario_description(self) -> str:
        return (
            "GCP-native network operations across three regions: us-central1, "
            "us-east1, and europe-west1. Covers VPC, Cloud Armor, Cloud NAT, "
            "Cloud DNS, Interconnect, VPN, CDN, and Load Balancing services "
            "running on Google Kubernetes Engine."
        )

    @property
    def namespace(self) -> str:
        return "gcpnet"

    # ── Services ──────────────────────────────────────────────────────

    @property
    def services(self) -> dict[str, dict[str, Any]]:
        return {
            # ── us-central1 — Core Network ──
            "vpc-network-manager": {
                "cloud_provider": "gcp",
                "cloud_region": "us-central1",
                "cloud_platform": "gcp_compute_engine",
                "cloud_availability_zone": "us-central1-a",
                "subsystem": "core_network",
                "language": "go",
            },
            "cloud-load-balancer": {
                "cloud_provider": "gcp",
                "cloud_region": "us-central1",
                "cloud_platform": "gcp_compute_engine",
                "cloud_availability_zone": "us-central1-b",
                "subsystem": "traffic_management",
                "language": "java",
            },
            "cloud-cdn-service": {
                "cloud_provider": "gcp",
                "cloud_region": "us-central1",
                "cloud_platform": "gcp_compute_engine",
                "cloud_availability_zone": "us-central1-c",
                "subsystem": "content_delivery",
                "language": "python",
            },
            # ── us-east1 — Security & Access ──
            "cloud-armor-waf": {
                "cloud_provider": "gcp",
                "cloud_region": "us-east1",
                "cloud_platform": "gcp_compute_engine",
                "cloud_availability_zone": "us-east1-b",
                "subsystem": "security",
                "language": "rust",
            },
            "cloud-nat-gateway": {
                "cloud_provider": "gcp",
                "cloud_region": "us-east1",
                "cloud_platform": "gcp_compute_engine",
                "cloud_availability_zone": "us-east1-c",
                "subsystem": "network_access",
                "language": "go",
                "generates_traces": False,
            },
            "cloud-dns-resolver": {
                "cloud_provider": "gcp",
                "cloud_region": "us-east1",
                "cloud_platform": "gcp_compute_engine",
                "cloud_availability_zone": "us-east1-d",
                "subsystem": "dns",
                "language": "cpp",
                "generates_traces": False,
            },
            # ── europe-west1 — Connectivity & Monitoring ──
            "cloud-interconnect": {
                "cloud_provider": "gcp",
                "cloud_region": "europe-west1",
                "cloud_platform": "gcp_compute_engine",
                "cloud_availability_zone": "europe-west1-b",
                "subsystem": "connectivity",
                "language": "java",
            },
            "cloud-vpn-gateway": {
                "cloud_provider": "gcp",
                "cloud_region": "europe-west1",
                "cloud_platform": "gcp_compute_engine",
                "cloud_availability_zone": "europe-west1-c",
                "subsystem": "vpn",
                "language": "rust",
                "generates_traces": False,
            },
            "network-intelligence": {
                "cloud_provider": "gcp",
                "cloud_region": "europe-west1",
                "cloud_platform": "gcp_compute_engine",
                "cloud_availability_zone": "europe-west1-d",
                "subsystem": "monitoring",
                "language": "python",
            },
        }

    # ── Channel Registry ──────────────────────────────────────────────

    @property
    def channel_registry(self) -> dict[int, dict[str, Any]]:
        return {
            1: {
                "name": "VPC Peering Route Limit",
                "subsystem": "core_network",
                "vehicle_section": "vpc_routing",
                "error_type": "VPC-ROUTE-LIMIT-EXCEEDED",
                "sensor_type": "route_table",
                "affected_services": ["vpc-network-manager", "cloud-load-balancer"],
                "cascade_services": ["cloud-nat-gateway"],
                "description": "VPC peering route table exceeding maximum advertised route limit",
                "error_message": (
                    'level=error ts={{timestamp}} caller=vpc_manager.go:312 '
                    'msg="VPC-ROUTE-LIMIT-EXCEEDED" project={gcp_project} '
                    "peering={vpc_peering_name} routes={route_count}/{route_max} "
                    "network={vpc_network} region={gcp_region} "
                    "dropped_prefixes={dropped_prefixes}"
                ),
                "stack_trace": (
                    "goroutine 234 [running]:\n"
                    "runtime/debug.Stack()\n"
                    "\t/usr/local/go/src/runtime/debug/stack.go:24 +0x5e\n"
                    "cloud.google.com/go/compute/apiv1.(*RoutesClient).AggregatedList(0xc000518000, "
                    "{{0xc000a12480}}, {{0xc000a124c0}})\n"
                    "\t/app/internal/vpc/route_manager.go:312 +0x3a2\n"
                    "  VPC Network: {vpc_network}\n"
                    "  Peering: {vpc_peering_name}\n"
                    "  Routes: {route_count}/{route_max}\n"
                    "  Dropped Prefixes: {dropped_prefixes}\n"
                    "  Action: Consolidate routes or request quota increase"
                ),
            },
            2: {
                "name": "Subnet IP Exhaustion",
                "subsystem": "core_network",
                "vehicle_section": "vpc_subnets",
                "error_type": "VPC-SUBNET-IP-EXHAUSTION",
                "sensor_type": "subnet_usage",
                "affected_services": ["vpc-network-manager", "cloud-nat-gateway"],
                "cascade_services": ["cloud-load-balancer", "cloud-cdn-service"],
                "description": "VPC subnet running out of available IP addresses",
                "error_message": (
                    'level=error ts={{timestamp}} caller=subnet_monitor.go:189 '
                    'msg="VPC-SUBNET-IP-EXHAUSTION" project={gcp_project} '
                    "subnet={subnet_name} cidr={subnet_cidr} "
                    "used={subnet_used_ips}/{subnet_total_ips} "
                    "utilization={subnet_util_pct}% region={gcp_region}"
                ),
                "stack_trace": (
                    "goroutine 156 [running]:\n"
                    "cloud.google.com/go/compute/apiv1.(*SubnetworksClient).Get(0xc000420000)\n"
                    "\t/app/internal/vpc/subnet_monitor.go:189 +0x1b8\n"
                    "  Subnet: {subnet_name} ({subnet_cidr})\n"
                    "  Used IPs: {subnet_used_ips}/{subnet_total_ips} ({subnet_util_pct}%)\n"
                    "  Region: {gcp_region}\n"
                    "  Action: Expand CIDR range or create secondary range"
                ),
            },
            3: {
                "name": "Firewall Rule Conflict",
                "subsystem": "core_network",
                "vehicle_section": "vpc_firewall",
                "error_type": "VPC-FIREWALL-RULE-CONFLICT",
                "sensor_type": "firewall_policy",
                "affected_services": ["vpc-network-manager", "cloud-armor-waf"],
                "cascade_services": ["cloud-interconnect"],
                "description": "Conflicting VPC firewall rules causing unexpected traffic drops",
                "error_message": (
                    'level=error ts={{timestamp}} caller=fw_policy_engine.go:445 '
                    'msg="VPC-FIREWALL-RULE-CONFLICT" project={gcp_project} '
                    "rule_a={fw_rule_a} rule_b={fw_rule_b} "
                    "priority_a={fw_priority_a} priority_b={fw_priority_b} "
                    "network={vpc_network} dropped_packets={fw_dropped_packets}/s"
                ),
                "stack_trace": (
                    "goroutine 312 [running]:\n"
                    "cloud.google.com/go/compute/apiv1.(*FirewallsClient).List(0xc000518000)\n"
                    "\t/app/internal/vpc/fw_policy_engine.go:445 +0x2f1\n"
                    "  Conflicting Rules:\n"
                    "    Rule A: {fw_rule_a} (priority {fw_priority_a}, ALLOW)\n"
                    "    Rule B: {fw_rule_b} (priority {fw_priority_b}, DENY)\n"
                    "  Network: {vpc_network}\n"
                    "  Dropped: {fw_dropped_packets} packets/s\n"
                    "  Action: Adjust rule priorities or merge conflicting rules"
                ),
            },
            4: {
                "name": "DDoS Alert Triggered",
                "subsystem": "security",
                "vehicle_section": "ddos_protection",
                "error_type": "ARMOR-DDOS-ALERT",
                "sensor_type": "ddos_detector",
                "affected_services": ["cloud-armor-waf", "cloud-load-balancer"],
                "cascade_services": ["vpc-network-manager", "cloud-cdn-service"],
                "description": "Cloud Armor detecting and mitigating a volumetric DDoS attack",
                "error_message": (
                    "[CloudArmor] ARMOR-DDOS-ALERT policy={armor_policy} "
                    "attack_type={ddos_attack_type} volume={ddos_volume_gbps}Gbps "
                    "source_regions={ddos_source_regions} "
                    "mitigated={ddos_mitigated_pct}% backend={armor_backend} "
                    "rule={armor_rule_name}"
                ),
                "stack_trace": (
                    "Cloud Armor DDoS Mitigation Report\n"
                    "------------------------------------\n"
                    "Policy:         {armor_policy}\n"
                    "Attack Type:    {ddos_attack_type}\n"
                    "Volume:         {ddos_volume_gbps} Gbps\n"
                    "Source Regions: {ddos_source_regions}\n"
                    "Mitigated:      {ddos_mitigated_pct}%\n"
                    "Backend:        {armor_backend}\n"
                    "Rule Matched:   {armor_rule_name}\n"
                    "Duration:       ongoing\n"
                    "Action:         Adaptive protection engaged, monitoring escalation"
                ),
            },
            5: {
                "name": "WAF False Positive Surge",
                "subsystem": "security",
                "vehicle_section": "waf_engine",
                "error_type": "ARMOR-FALSE-POSITIVE",
                "sensor_type": "waf_rules",
                "affected_services": ["cloud-armor-waf", "cloud-cdn-service"],
                "cascade_services": ["cloud-load-balancer"],
                "description": "Cloud Armor WAF rules generating excessive false positive blocks",
                "error_message": (
                    "[CloudArmor] ARMOR-FALSE-POSITIVE policy={armor_policy} "
                    "rule={waf_rule_id} blocked_requests={waf_blocked_count}/m "
                    "false_positive_rate={waf_fp_rate}% "
                    "affected_paths={waf_affected_paths} "
                    "sensitivity={waf_sensitivity_level}"
                ),
                "stack_trace": (
                    "Cloud Armor WAF Analysis\n"
                    "-------------------------\n"
                    "Policy:              {armor_policy}\n"
                    "Rule:                {waf_rule_id}\n"
                    "Blocked/min:         {waf_blocked_count}\n"
                    "False Positive Rate: {waf_fp_rate}%\n"
                    "Affected Paths:      {waf_affected_paths}\n"
                    "Sensitivity:         {waf_sensitivity_level}\n"
                    "Legitimate traffic pattern: API JSON payloads triggering SQLi detection\n"
                    "Action: Adjust rule sensitivity or add path exception"
                ),
            },
            6: {
                "name": "Security Policy Sync Failure",
                "subsystem": "security",
                "vehicle_section": "policy_management",
                "error_type": "ARMOR-POLICY-SYNC-FAILURE",
                "sensor_type": "policy_sync",
                "affected_services": ["cloud-armor-waf", "vpc-network-manager"],
                "cascade_services": ["cloud-load-balancer"],
                "description": "Cloud Armor security policy failing to sync across backend services",
                "error_message": (
                    "[CloudArmor] ARMOR-POLICY-SYNC-FAILURE policy={armor_policy} "
                    "version={policy_version} backends_synced={backends_synced}/{backends_total} "
                    "last_sync={policy_last_sync_sec}s ago "
                    "error=\"{policy_sync_error}\""
                ),
                "stack_trace": (
                    "Cloud Armor Policy Sync Diagnostic\n"
                    "-------------------------------------\n"
                    "Policy:           {armor_policy}\n"
                    "Version:          {policy_version}\n"
                    "Synced Backends:  {backends_synced}/{backends_total}\n"
                    "Last Sync:        {policy_last_sync_sec}s ago\n"
                    "Error:            {policy_sync_error}\n"
                    "Stale Backends:   Running policy version {policy_version} - 1\n"
                    "Action: Force policy push or check backend health"
                ),
            },
            7: {
                "name": "NAT Port Exhaustion",
                "subsystem": "network_access",
                "vehicle_section": "nat_gateway",
                "error_type": "NAT-PORT-EXHAUSTION",
                "sensor_type": "nat_ports",
                "affected_services": ["cloud-nat-gateway", "vpc-network-manager"],
                "cascade_services": ["cloud-load-balancer", "cloud-dns-resolver"],
                "description": "Cloud NAT gateway running out of available source ports",
                "error_message": (
                    "cloudnat: NAT-PORT-EXHAUSTION gateway={nat_gateway_name} "
                    "region={gcp_region} ports_used={nat_ports_used}/{nat_ports_total} "
                    "utilization={nat_port_util_pct}% "
                    "dropped_connections={nat_dropped_conns}/s "
                    "top_vm={nat_top_vm}"
                ),
                "stack_trace": (
                    "Cloud NAT Port Allocation Report\n"
                    "----------------------------------\n"
                    "Gateway:      {nat_gateway_name}\n"
                    "Region:       {gcp_region}\n"
                    "Ports Used:   {nat_ports_used}/{nat_ports_total} ({nat_port_util_pct}%)\n"
                    "Dropped/s:    {nat_dropped_conns}\n"
                    "Top Consumer: {nat_top_vm}\n"
                    "Min Ports/VM: 64\n"
                    "Action: Increase minPortsPerVm or add NAT IP addresses"
                ),
            },
            8: {
                "name": "NAT Endpoint Mapping Failure",
                "subsystem": "network_access",
                "vehicle_section": "nat_gateway",
                "error_type": "NAT-ENDPOINT-MAPPING-FAILURE",
                "sensor_type": "nat_mapping",
                "affected_services": ["cloud-nat-gateway", "cloud-load-balancer"],
                "cascade_services": ["cloud-cdn-service"],
                "description": "Cloud NAT endpoint-independent mapping failing for new connections",
                "error_message": (
                    "cloudnat: NAT-ENDPOINT-MAPPING-FAILURE gateway={nat_gateway_name} "
                    "mapping_type={nat_mapping_type} failures={nat_mapping_failures}/m "
                    "nat_ip={nat_external_ip} subnet={subnet_name} "
                    "protocol={nat_protocol}"
                ),
                "stack_trace": (
                    "Cloud NAT Mapping Diagnostic\n"
                    "------------------------------\n"
                    "Gateway:      {nat_gateway_name}\n"
                    "Mapping Type: {nat_mapping_type}\n"
                    "Failures/min: {nat_mapping_failures}\n"
                    "NAT IP:       {nat_external_ip}\n"
                    "Subnet:       {subnet_name}\n"
                    "Protocol:     {nat_protocol}\n"
                    "Action: Check NAT IP allocation and endpoint mapping config"
                ),
            },
            9: {
                "name": "NAT IP Allocation Error",
                "subsystem": "network_access",
                "vehicle_section": "nat_gateway",
                "error_type": "NAT-IP-ALLOCATION-ERROR",
                "sensor_type": "nat_ip_pool",
                "affected_services": ["cloud-nat-gateway", "vpc-network-manager"],
                "cascade_services": ["cloud-interconnect"],
                "description": "Cloud NAT unable to allocate external IP addresses for outbound traffic",
                "error_message": (
                    "cloudnat: NAT-IP-ALLOCATION-ERROR gateway={nat_gateway_name} "
                    "region={gcp_region} allocated_ips={nat_allocated_ips}/{nat_max_ips} "
                    "pending_allocations={nat_pending_allocs} "
                    "error=\"{nat_alloc_error}\""
                ),
                "stack_trace": (
                    "Cloud NAT IP Allocation Report\n"
                    "---------------------------------\n"
                    "Gateway:     {nat_gateway_name}\n"
                    "Region:      {gcp_region}\n"
                    "Allocated:   {nat_allocated_ips}/{nat_max_ips}\n"
                    "Pending:     {nat_pending_allocs}\n"
                    "Error:       {nat_alloc_error}\n"
                    "Quota:       EXTERNAL_IP_ADDRESS — check project quota\n"
                    "Action: Release unused IPs or request quota increase"
                ),
            },
            10: {
                "name": "DNSSEC Validation Failure",
                "subsystem": "dns",
                "vehicle_section": "dns_security",
                "error_type": "DNS-DNSSEC-VALIDATION-FAILURE",
                "sensor_type": "dnssec_validator",
                "affected_services": ["cloud-dns-resolver", "vpc-network-manager"],
                "cascade_services": ["cloud-armor-waf", "network-intelligence"],
                "description": "DNSSEC signature validation failing for managed DNS zones",
                "error_message": (
                    "cloud-dns: DNS-DNSSEC-VALIDATION-FAILURE zone={dns_zone} "
                    "record={dns_record_name} type={dns_record_type} "
                    "rrsig_expiry={dnssec_rrsig_expiry} "
                    "ds_status={dnssec_ds_status} "
                    "validation_errors={dnssec_error_count}/m"
                ),
                "stack_trace": (
                    "Cloud DNS DNSSEC Validation Report\n"
                    "------------------------------------\n"
                    "Zone:              {dns_zone}\n"
                    "Record:            {dns_record_name} ({dns_record_type})\n"
                    "RRSIG Expiry:      {dnssec_rrsig_expiry}\n"
                    "DS Record Status:  {dnssec_ds_status}\n"
                    "Validation Errors: {dnssec_error_count}/min\n"
                    "DNSKEY Algorithm:  RSASHA256\n"
                    "Action: Rotate DNSSEC keys or update DS record at registrar"
                ),
            },
            11: {
                "name": "DNS Zone Propagation Delay",
                "subsystem": "dns",
                "vehicle_section": "dns_propagation",
                "error_type": "DNS-ZONE-PROPAGATION-DELAY",
                "sensor_type": "dns_propagation",
                "affected_services": ["cloud-dns-resolver", "cloud-load-balancer"],
                "cascade_services": ["cloud-cdn-service", "network-intelligence"],
                "description": "DNS record changes taking abnormally long to propagate across Cloud DNS servers",
                "error_message": (
                    "cloud-dns: DNS-ZONE-PROPAGATION-DELAY zone={dns_zone} "
                    "change_id={dns_change_id} record={dns_record_name} "
                    "propagation_time={dns_prop_time_sec}s (SLA {dns_prop_sla_sec}s) "
                    "servers_updated={dns_servers_updated}/{dns_servers_total}"
                ),
                "stack_trace": (
                    "Cloud DNS Propagation Report\n"
                    "------------------------------\n"
                    "Zone:               {dns_zone}\n"
                    "Change ID:          {dns_change_id}\n"
                    "Record:             {dns_record_name}\n"
                    "Propagation Time:   {dns_prop_time_sec}s (SLA: {dns_prop_sla_sec}s)\n"
                    "Servers Updated:    {dns_servers_updated}/{dns_servers_total}\n"
                    "Status:             PENDING\n"
                    "Action: Wait for propagation or flush DNS cache"
                ),
            },
            12: {
                "name": "Interconnect Circuit Down",
                "subsystem": "connectivity",
                "vehicle_section": "dedicated_interconnect",
                "error_type": "INTERCONNECT-CIRCUIT-DOWN",
                "sensor_type": "circuit_status",
                "affected_services": ["cloud-interconnect", "vpc-network-manager"],
                "cascade_services": ["cloud-vpn-gateway", "network-intelligence"],
                "description": "Dedicated Interconnect circuit losing link, failing over to backup path",
                "error_message": (
                    "[Interconnect] INTERCONNECT-CIRCUIT-DOWN attachment={interconnect_name} "
                    "circuit_id={circuit_id} location={interconnect_location} "
                    "link_status=DOWN since {circuit_down_sec}s "
                    "bandwidth={interconnect_bw_gbps}Gbps failover={failover_status}"
                ),
                "stack_trace": (
                    "Cloud Interconnect Circuit Report\n"
                    "-----------------------------------\n"
                    "Attachment:   {interconnect_name}\n"
                    "Circuit ID:   {circuit_id}\n"
                    "Location:     {interconnect_location}\n"
                    "Link Status:  DOWN\n"
                    "Down Since:   {circuit_down_sec}s\n"
                    "Bandwidth:    {interconnect_bw_gbps} Gbps\n"
                    "Failover:     {failover_status}\n"
                    "LACP State:   DETACHED\n"
                    "Action: Contact colo provider, verify cross-connect"
                ),
            },
            13: {
                "name": "BGP Session Flap",
                "subsystem": "connectivity",
                "vehicle_section": "bgp_routing",
                "error_type": "INTERCONNECT-BGP-FLAP",
                "sensor_type": "bgp_session",
                "affected_services": ["cloud-interconnect", "cloud-vpn-gateway"],
                "cascade_services": ["vpc-network-manager", "cloud-nat-gateway"],
                "description": "Cloud Router BGP session repeatedly flapping on interconnect attachment",
                "error_message": (
                    "[CloudRouter] INTERCONNECT-BGP-FLAP router={cloud_router} "
                    "peer={bgp_peer_ip} peer_asn={bgp_peer_asn} "
                    "flaps={bgp_flap_count} window={bgp_flap_window}s "
                    "state={bgp_state} advertised_routes={bgp_advertised_routes}"
                ),
                "stack_trace": (
                    "Cloud Router BGP Session Report\n"
                    "----------------------------------\n"
                    "Router:            {cloud_router}\n"
                    "Peer IP:           {bgp_peer_ip}\n"
                    "Peer ASN:          {bgp_peer_asn}\n"
                    "Flap Count:        {bgp_flap_count} in {bgp_flap_window}s\n"
                    "Current State:     {bgp_state}\n"
                    "Advertised Routes: {bgp_advertised_routes}\n"
                    "BFD Status:        DOWN\n"
                    "Action: Check peer configuration and physical link"
                ),
            },
            14: {
                "name": "CDN Cache Miss Spike",
                "subsystem": "content_delivery",
                "vehicle_section": "cdn_cache",
                "error_type": "CDN-CACHE-MISS-SPIKE",
                "sensor_type": "cache_hit_ratio",
                "affected_services": ["cloud-cdn-service", "cloud-load-balancer"],
                "cascade_services": ["vpc-network-manager"],
                "description": "Cloud CDN cache hit ratio dropping significantly, overwhelming origin servers",
                "error_message": (
                    "[CloudCDN] CDN-CACHE-MISS-SPIKE backend={cdn_backend} "
                    "hit_ratio={cdn_hit_ratio}% (SLA {cdn_hit_sla}%) "
                    "miss_rate={cdn_miss_rate}/s origin_latency={cdn_origin_latency_ms}ms "
                    "cache_fill={cdn_cache_fill_pct}%"
                ),
                "stack_trace": (
                    "Cloud CDN Cache Analysis\n"
                    "--------------------------\n"
                    "Backend:          {cdn_backend}\n"
                    "Hit Ratio:        {cdn_hit_ratio}% (SLA: {cdn_hit_sla}%)\n"
                    "Miss Rate:        {cdn_miss_rate}/s\n"
                    "Origin Latency:   {cdn_origin_latency_ms}ms\n"
                    "Cache Fill:       {cdn_cache_fill_pct}%\n"
                    "Top Missed Paths: /api/v2/assets, /media/images\n"
                    "Action: Review cache key policy and TTL configuration"
                ),
            },
            15: {
                "name": "CDN Origin Unreachable",
                "subsystem": "content_delivery",
                "vehicle_section": "cdn_origin",
                "error_type": "CDN-ORIGIN-UNREACHABLE",
                "sensor_type": "origin_health",
                "affected_services": ["cloud-cdn-service", "cloud-load-balancer"],
                "cascade_services": ["cloud-armor-waf"],
                "description": "Cloud CDN unable to reach origin backend, serving stale content",
                "error_message": (
                    "[CloudCDN] CDN-ORIGIN-UNREACHABLE backend={cdn_backend} "
                    "origin={cdn_origin_host} status_code={cdn_origin_status} "
                    "failures={cdn_origin_failures}/m "
                    "serving_stale={cdn_stale_pct}% ttl_remaining={cdn_stale_ttl_sec}s"
                ),
                "stack_trace": (
                    "Cloud CDN Origin Health Report\n"
                    "--------------------------------\n"
                    "Backend:       {cdn_backend}\n"
                    "Origin:        {cdn_origin_host}\n"
                    "Status Code:   {cdn_origin_status}\n"
                    "Failures/min:  {cdn_origin_failures}\n"
                    "Serving Stale: {cdn_stale_pct}%\n"
                    "Stale TTL:     {cdn_stale_ttl_sec}s remaining\n"
                    "Action: Check origin backend health and network path"
                ),
            },
            16: {
                "name": "Backend Unhealthy",
                "subsystem": "traffic_management",
                "vehicle_section": "load_balancing",
                "error_type": "LB-BACKEND-UNHEALTHY",
                "sensor_type": "health_check",
                "affected_services": ["cloud-load-balancer", "vpc-network-manager"],
                "cascade_services": ["cloud-cdn-service", "cloud-armor-waf"],
                "description": "Load balancer backend instances failing health checks",
                "error_message": (
                    "[CloudLB] LB-BACKEND-UNHEALTHY forwarding_rule={lb_forwarding_rule} "
                    "backend_service={lb_backend_service} "
                    "unhealthy={lb_unhealthy_count}/{lb_total_backends} "
                    "health_check={lb_health_check} "
                    "failed_checks={lb_failed_checks} region={gcp_region}"
                ),
                "stack_trace": (
                    "Cloud Load Balancer Health Report\n"
                    "-----------------------------------\n"
                    "Forwarding Rule:  {lb_forwarding_rule}\n"
                    "Backend Service:  {lb_backend_service}\n"
                    "Unhealthy:        {lb_unhealthy_count}/{lb_total_backends}\n"
                    "Health Check:     {lb_health_check}\n"
                    "Failed Checks:    {lb_failed_checks} consecutive\n"
                    "Region:           {gcp_region}\n"
                    "Action: Investigate backend instance logs and health check config"
                ),
            },
            17: {
                "name": "SSL Certificate Expiry",
                "subsystem": "traffic_management",
                "vehicle_section": "ssl_termination",
                "error_type": "LB-SSL-CERT-EXPIRY",
                "sensor_type": "certificate",
                "affected_services": ["cloud-load-balancer", "cloud-cdn-service"],
                "cascade_services": ["cloud-armor-waf"],
                "description": "Google-managed SSL certificate approaching or past expiration",
                "error_message": (
                    "[CloudLB] LB-SSL-CERT-EXPIRY certificate={ssl_cert_name} "
                    "domain={ssl_domain} expires_in={ssl_days_remaining}d "
                    "managed_status={ssl_managed_status} "
                    "forwarding_rules={ssl_affected_rules}"
                ),
                "stack_trace": (
                    "SSL Certificate Status Report\n"
                    "-------------------------------\n"
                    "Certificate:      {ssl_cert_name}\n"
                    "Domain:           {ssl_domain}\n"
                    "Days Remaining:   {ssl_days_remaining}\n"
                    "Managed Status:   {ssl_managed_status}\n"
                    "Forwarding Rules: {ssl_affected_rules}\n"
                    "Provisioning:     FAILED_NOT_VISIBLE\n"
                    "Action: Verify DNS authorization and domain ownership"
                ),
            },
            18: {
                "name": "VPN Tunnel Down",
                "subsystem": "vpn",
                "vehicle_section": "vpn_tunnels",
                "error_type": "VPN-TUNNEL-DOWN",
                "sensor_type": "tunnel_status",
                "affected_services": ["cloud-vpn-gateway", "cloud-interconnect"],
                "cascade_services": ["vpc-network-manager", "network-intelligence"],
                "description": "Cloud VPN tunnel losing connectivity to remote peer",
                "error_message": (
                    "[CloudVPN] VPN-TUNNEL-DOWN tunnel={vpn_tunnel_name} "
                    "gateway={vpn_gateway_name} peer={vpn_peer_ip} "
                    "status=DOWN since {vpn_down_sec}s "
                    "ike_version={vpn_ike_version} "
                    "last_handshake={vpn_last_handshake_sec}s ago"
                ),
                "stack_trace": (
                    "Cloud VPN Tunnel Report\n"
                    "-------------------------\n"
                    "Tunnel:          {vpn_tunnel_name}\n"
                    "Gateway:         {vpn_gateway_name}\n"
                    "Peer IP:         {vpn_peer_ip}\n"
                    "Status:          DOWN\n"
                    "Down Since:      {vpn_down_sec}s\n"
                    "IKE Version:     {vpn_ike_version}\n"
                    "Last Handshake:  {vpn_last_handshake_sec}s ago\n"
                    "Action: Verify peer gateway and IKE configuration"
                ),
            },
            19: {
                "name": "IKE Negotiation Failure",
                "subsystem": "vpn",
                "vehicle_section": "ike_protocol",
                "error_type": "VPN-IKE-NEGOTIATION-FAILURE",
                "sensor_type": "ike_session",
                "affected_services": ["cloud-vpn-gateway", "cloud-interconnect"],
                "cascade_services": ["cloud-nat-gateway"],
                "description": "IKE phase negotiation failing between Cloud VPN and remote peer",
                "error_message": (
                    "[CloudVPN] VPN-IKE-NEGOTIATION-FAILURE tunnel={vpn_tunnel_name} "
                    "gateway={vpn_gateway_name} peer={vpn_peer_ip} "
                    "ike_phase={ike_phase} error=\"{ike_error}\" "
                    "retries={ike_retry_count}/{ike_max_retries}"
                ),
                "stack_trace": (
                    "Cloud VPN IKE Negotiation Report\n"
                    "----------------------------------\n"
                    "Tunnel:      {vpn_tunnel_name}\n"
                    "Gateway:     {vpn_gateway_name}\n"
                    "Peer IP:     {vpn_peer_ip}\n"
                    "IKE Phase:   {ike_phase}\n"
                    "Error:       {ike_error}\n"
                    "Retries:     {ike_retry_count}/{ike_max_retries}\n"
                    "Cipher:      AES-256-CBC\n"
                    "Auth:        SHA-256\n"
                    "Action: Verify pre-shared key and cipher suite compatibility"
                ),
            },
            20: {
                "name": "Connectivity Test Failure",
                "subsystem": "monitoring",
                "vehicle_section": "network_intelligence",
                "error_type": "NI-CONNECTIVITY-TEST-FAILURE",
                "sensor_type": "connectivity_test",
                "affected_services": ["network-intelligence", "vpc-network-manager"],
                "cascade_services": ["cloud-vpn-gateway", "cloud-interconnect"],
                "description": "Network Intelligence Center connectivity test detecting unreachable endpoints",
                "error_message": (
                    "[NIC] NI-CONNECTIVITY-TEST-FAILURE test={ni_test_name} "
                    "src={ni_src_ip} dst={ni_dst_ip} protocol={ni_protocol} "
                    "result={ni_test_result} "
                    "hops_completed={ni_hops_completed}/{ni_hops_total} "
                    "blocking_resource={ni_blocking_resource}"
                ),
                "stack_trace": (
                    "Network Intelligence Connectivity Test\n"
                    "-----------------------------------------\n"
                    "Test Name:         {ni_test_name}\n"
                    "Source:            {ni_src_ip}\n"
                    "Destination:       {ni_dst_ip}\n"
                    "Protocol:          {ni_protocol}\n"
                    "Result:            {ni_test_result}\n"
                    "Hops Completed:    {ni_hops_completed}/{ni_hops_total}\n"
                    "Blocking Resource: {ni_blocking_resource}\n"
                    "Action: Review firewall rules and routing for blocking resource"
                ),
            },
        }

    # ── Topology ──────────────────────────────────────────────────────

    @property
    def service_topology(self) -> dict[str, list[tuple[str, str, str]]]:
        return {
            "vpc-network-manager": [
                ("cloud-load-balancer", "/api/v1/lb/backend-health", "GET"),
                ("cloud-load-balancer", "/api/v1/lb/forwarding-rules", "GET"),
                ("cloud-nat-gateway", "/api/v1/nat/port-allocation", "GET"),
                ("cloud-armor-waf", "/api/v1/armor/policy-status", "GET"),
                ("cloud-dns-resolver", "/api/v1/dns/zone-health", "GET"),
            ],
            "cloud-load-balancer": [
                ("cloud-cdn-service", "/api/v1/cdn/cache-status", "GET"),
                ("cloud-cdn-service", "/api/v1/cdn/invalidate", "POST"),
                ("cloud-armor-waf", "/api/v1/armor/request-filter", "POST"),
                ("vpc-network-manager", "/api/v1/vpc/health-check-config", "GET"),
            ],
            "cloud-cdn-service": [
                ("cloud-load-balancer", "/api/v1/lb/origin-fetch", "GET"),
                ("vpc-network-manager", "/api/v1/vpc/route-to-origin", "GET"),
            ],
            "cloud-armor-waf": [
                ("cloud-load-balancer", "/api/v1/lb/block-request", "POST"),
                ("vpc-network-manager", "/api/v1/vpc/firewall-sync", "POST"),
            ],
            "cloud-nat-gateway": [
                ("vpc-network-manager", "/api/v1/vpc/subnet-info", "GET"),
                ("cloud-dns-resolver", "/api/v1/dns/external-resolve", "POST"),
            ],
            "cloud-dns-resolver": [
                ("vpc-network-manager", "/api/v1/vpc/peering-dns", "GET"),
            ],
            "cloud-interconnect": [
                ("vpc-network-manager", "/api/v1/vpc/route-advertise", "POST"),
                ("cloud-vpn-gateway", "/api/v1/vpn/failover-status", "GET"),
                ("network-intelligence", "/api/v1/ni/latency-report", "GET"),
            ],
            "cloud-vpn-gateway": [
                ("cloud-interconnect", "/api/v1/interconnect/backup-path", "GET"),
                ("vpc-network-manager", "/api/v1/vpc/tunnel-routes", "POST"),
            ],
            "network-intelligence": [
                ("vpc-network-manager", "/api/v1/vpc/topology-map", "GET"),
                ("cloud-vpn-gateway", "/api/v1/vpn/tunnel-metrics", "GET"),
                ("cloud-interconnect", "/api/v1/interconnect/circuit-status", "GET"),
            ],
        }

    @property
    def entry_endpoints(self) -> dict[str, list[tuple[str, str]]]:
        return {
            "vpc-network-manager": [
                ("/api/v1/vpc/networks", "GET"),
                ("/api/v1/vpc/subnets", "GET"),
                ("/api/v1/vpc/firewall-rules", "GET"),
            ],
            "cloud-load-balancer": [
                ("/api/v1/lb/status", "GET"),
                ("/api/v1/lb/backends", "GET"),
                ("/api/v1/lb/configure", "POST"),
            ],
            "cloud-cdn-service": [
                ("/api/v1/cdn/analytics", "GET"),
                ("/api/v1/cdn/purge", "POST"),
            ],
            "cloud-armor-waf": [
                ("/api/v1/armor/policies", "GET"),
                ("/api/v1/armor/events", "GET"),
                ("/api/v1/armor/rule-update", "POST"),
            ],
            "cloud-nat-gateway": [
                ("/api/v1/nat/status", "GET"),
                ("/api/v1/nat/mappings", "GET"),
            ],
            "cloud-dns-resolver": [
                ("/api/v1/dns/query", "POST"),
                ("/api/v1/dns/zones", "GET"),
                ("/api/v1/dns/health", "GET"),
            ],
            "cloud-interconnect": [
                ("/api/v1/interconnect/attachments", "GET"),
                ("/api/v1/interconnect/diagnostics", "GET"),
            ],
            "cloud-vpn-gateway": [
                ("/api/v1/vpn/tunnels", "GET"),
                ("/api/v1/vpn/status", "GET"),
            ],
            "network-intelligence": [
                ("/api/v1/ni/tests", "GET"),
                ("/api/v1/ni/topology", "GET"),
                ("/api/v1/ni/run-test", "POST"),
            ],
        }

    @property
    def db_operations(self) -> dict[str, list[tuple[str, str, str]]]:
        return {
            "vpc-network-manager": [
                ("SELECT", "vpc_networks", "SELECT network_id, name, subnet_mode, peering_count, route_count FROM vpc_networks WHERE project = ? AND status = 'ACTIVE'"),
                ("SELECT", "firewall_rules", "SELECT rule_id, name, priority, direction, action, target_tags FROM firewall_rules WHERE network_id = ? ORDER BY priority"),
                ("UPDATE", "vpc_routes", "UPDATE vpc_routes SET status = ?, updated_at = NOW() WHERE network_id = ? AND dest_range = ?"),
            ],
            "cloud-load-balancer": [
                ("SELECT", "forwarding_rules", "SELECT rule_id, ip_address, port_range, target, region FROM forwarding_rules WHERE project = ? AND status = 'ACTIVE'"),
                ("SELECT", "backend_services", "SELECT service_id, name, protocol, health_check_id, backends FROM backend_services WHERE forwarding_rule_id = ?"),
                ("UPDATE", "health_checks", "UPDATE health_checks SET last_check = NOW(), status = ? WHERE health_check_id = ?"),
            ],
            "cloud-cdn-service": [
                ("SELECT", "cdn_backends", "SELECT backend_id, origin_host, cache_mode, ttl_sec, hit_ratio FROM cdn_backends WHERE enabled = true"),
                ("INSERT", "cache_invalidations", "INSERT INTO cache_invalidations (backend_id, path_pattern, requested_at, status) VALUES (?, ?, NOW(), 'pending')"),
            ],
            "cloud-armor-waf": [
                ("SELECT", "security_policies", "SELECT policy_id, name, rule_count, backend_count, last_updated FROM security_policies WHERE project = ?"),
                ("SELECT", "waf_events", "SELECT timestamp, rule_id, action, src_ip, request_path, matched_pattern FROM waf_events WHERE policy_id = ? AND timestamp > NOW() - INTERVAL 1 HOUR ORDER BY timestamp DESC LIMIT 100"),
            ],
            "cloud-dns-resolver": [
                ("SELECT", "dns_zones", "SELECT zone_id, dns_name, visibility, dnssec_state, record_count FROM dns_zones WHERE project = ?"),
                ("SELECT", "dns_records", "SELECT name, type, ttl, rrdatas FROM dns_records WHERE zone_id = ? AND type = ?"),
            ],
            "cloud-interconnect": [
                ("SELECT", "interconnect_attachments", "SELECT attachment_id, name, region, bandwidth, vlan_tag, state FROM interconnect_attachments WHERE interconnect_id = ?"),
            ],
            "network-intelligence": [
                ("SELECT", "connectivity_tests", "SELECT test_id, name, source, destination, protocol, result, last_run FROM connectivity_tests WHERE project = ? ORDER BY last_run DESC"),
                ("INSERT", "test_results", "INSERT INTO test_results (test_id, result, hops, blocking_resource, tested_at) VALUES (?, ?, ?, ?, NOW())"),
            ],
        }

    # ── Infrastructure ────────────────────────────────────────────────

    @property
    def hosts(self) -> list[dict[str, Any]]:
        return [
            {
                "host.name": "gcpnet-host-central1",
                "host.id": "4801234567890123456",
                "host.arch": "amd64",
                "host.type": "n2-standard-4",
                "host.image.id": "projects/cos-cloud/global/images/cos-113-18244-85-29",
                "host.cpu.model.name": "Intel(R) Xeon(R) CPU @ 2.80GHz",
                "host.cpu.vendor.id": "GenuineIntel",
                "host.cpu.family": "6",
                "host.cpu.model.id": "106",
                "host.cpu.stepping": "7",
                "host.cpu.cache.l2.size": 1310720,
                "host.ip": ["10.128.0.10", "10.128.0.11"],
                "host.mac": ["42:01:0a:80:00:0a", "42:01:0a:80:00:0b"],
                "os.type": "linux",
                "os.description": "Container-Optimized OS 113",
                "cloud.provider": "gcp",
                "cloud.platform": "gcp_compute_engine",
                "cloud.region": "us-central1",
                "cloud.availability_zone": "us-central1-a",
                "cloud.account.id": "gcpnet-prod-project",
                "cloud.instance.id": "4801234567890123456",
                "cpu_count": 4,
                "memory_total_bytes": 16 * 1024 * 1024 * 1024,
                "disk_total_bytes": 100 * 1024 * 1024 * 1024,
            },
            {
                "host.name": "gcpnet-host-east1",
                "host.id": "5912345678901234567",
                "host.arch": "amd64",
                "host.type": "n2-standard-4",
                "host.image.id": "projects/cos-cloud/global/images/cos-113-18244-85-29",
                "host.cpu.model.name": "Intel(R) Xeon(R) CPU @ 2.80GHz",
                "host.cpu.vendor.id": "GenuineIntel",
                "host.cpu.family": "6",
                "host.cpu.model.id": "106",
                "host.cpu.stepping": "7",
                "host.cpu.cache.l2.size": 1310720,
                "host.ip": ["10.142.0.10", "10.142.0.11"],
                "host.mac": ["42:01:0a:8e:00:0a", "42:01:0a:8e:00:0b"],
                "os.type": "linux",
                "os.description": "Container-Optimized OS 113",
                "cloud.provider": "gcp",
                "cloud.platform": "gcp_compute_engine",
                "cloud.region": "us-east1",
                "cloud.availability_zone": "us-east1-b",
                "cloud.account.id": "gcpnet-prod-project",
                "cloud.instance.id": "5912345678901234567",
                "cpu_count": 4,
                "memory_total_bytes": 16 * 1024 * 1024 * 1024,
                "disk_total_bytes": 100 * 1024 * 1024 * 1024,
            },
            {
                "host.name": "gcpnet-host-europe1",
                "host.id": "6023456789012345678",
                "host.arch": "amd64",
                "host.type": "n2-standard-4",
                "host.image.id": "projects/cos-cloud/global/images/cos-113-18244-85-29",
                "host.cpu.model.name": "Intel(R) Xeon(R) CPU @ 2.80GHz",
                "host.cpu.vendor.id": "GenuineIntel",
                "host.cpu.family": "6",
                "host.cpu.model.id": "106",
                "host.cpu.stepping": "7",
                "host.cpu.cache.l2.size": 1310720,
                "host.ip": ["10.132.0.10", "10.132.0.11"],
                "host.mac": ["42:01:0a:84:00:0a", "42:01:0a:84:00:0b"],
                "os.type": "linux",
                "os.description": "Container-Optimized OS 113",
                "cloud.provider": "gcp",
                "cloud.platform": "gcp_compute_engine",
                "cloud.region": "europe-west1",
                "cloud.availability_zone": "europe-west1-b",
                "cloud.account.id": "gcpnet-prod-project",
                "cloud.instance.id": "6023456789012345678",
                "cpu_count": 4,
                "memory_total_bytes": 16 * 1024 * 1024 * 1024,
                "disk_total_bytes": 100 * 1024 * 1024 * 1024,
            },
        ]

    @property
    def k8s_clusters(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "gcpnet-gke-central1",
                "provider": "gcp",
                "platform": "gcp_gke",
                "region": "us-central1",
                "zones": ["us-central1-a", "us-central1-b", "us-central1-c"],
                "os_description": "Container-Optimized OS",
                "services": ["vpc-network-manager", "cloud-load-balancer", "cloud-cdn-service"],
            },
            {
                "name": "gcpnet-gke-east1",
                "provider": "gcp",
                "platform": "gcp_gke",
                "region": "us-east1",
                "zones": ["us-east1-b", "us-east1-c", "us-east1-d"],
                "os_description": "Container-Optimized OS",
                "services": ["cloud-armor-waf", "cloud-nat-gateway", "cloud-dns-resolver"],
            },
            {
                "name": "gcpnet-gke-europe1",
                "provider": "gcp",
                "platform": "gcp_gke",
                "region": "europe-west1",
                "zones": ["europe-west1-b", "europe-west1-c", "europe-west1-d"],
                "os_description": "Container-Optimized OS",
                "services": ["cloud-interconnect", "cloud-vpn-gateway", "network-intelligence"],
            },
        ]

    # ── Dashboard Override (region-based columns) ─────────────────────

    @property
    def dashboard_cloud_groups(self) -> list[dict[str, Any]]:
        """Override to group by GCP region instead of cloud provider."""
        region_order = ["us-central1", "us-east1", "europe-west1"]
        x_starts = [0, 16, 33]
        col_widths = [15, 16, 15]
        groups = []
        for i, region in enumerate(region_order):
            svcs = [
                name for name, cfg in self.services.items()
                if cfg["cloud_region"] == region
            ]
            cluster = next(
                (c for c in self.k8s_clusters if c["region"] == region), {}
            )
            groups.append({
                "label": f"**GCP** {region}",
                "services": svcs,
                "x_start": x_starts[i],
                "col_width": col_widths[i],
                "cluster": cluster.get("name", ""),
            })
        return groups

    # ── Theme ─────────────────────────────────────────────────────────

    @property
    def theme(self) -> UITheme:
        return UITheme(
            bg_primary="#0d1117",
            bg_secondary="#161b22",
            bg_tertiary="#21262d",
            accent_primary="#4285F4",       # Google Blue
            accent_secondary="#34A853",     # Google Green
            text_primary="#e6edf3",
            text_secondary="#8b949e",
            text_accent="#4285F4",          # Google Blue
            status_nominal="#34A853",       # Google Green
            status_warning="#FBBC04",       # Google Yellow
            status_critical="#EA4335",      # Google Red
            status_info="#4285F4",          # Google Blue
            font_family="'Google Sans', 'Inter', system-ui, sans-serif",
            grid_background=True,
            dashboard_title="Network Operations Center",
            chaos_title="Incident Simulator",
            landing_title="Google Cloud Network Operations",
        )

    @property
    def countdown_config(self) -> CountdownConfig:
        return CountdownConfig(enabled=False)

    # ── Agent Config ──────────────────────────────────────────────────

    @property
    def agent_config(self) -> dict[str, Any]:
        return {
            "id": "gcp-network-analyst",
            "name": "Google Cloud Network Analyst",
            "assessment_tool_name": "network_health_assessment",
            "system_prompt": (
                "You are the Google Cloud Network Analyst, an expert AI assistant "
                "for GCP network operations. You help network engineers investigate "
                "incidents, analyze telemetry data, and provide root cause analysis "
                "for fault conditions across 9 GCP networking services spanning 3 regions "
                "(us-central1, us-east1, europe-west1). "
                "You have deep expertise in Google Cloud VPC networking, Cloud Armor WAF "
                "and DDoS protection, Cloud NAT gateway management, Cloud DNS (including DNSSEC), "
                "Dedicated Interconnect and BGP routing, Cloud VPN (IKE/IPsec), "
                "Cloud CDN caching and origin management, Cloud Load Balancing (L4/L7), "
                "and Network Intelligence Center connectivity testing. "
                "When investigating incidents, search for these GCP-specific identifiers in logs: "
                "VPC errors (VPC-ROUTE-LIMIT-EXCEEDED, VPC-SUBNET-IP-EXHAUSTION, VPC-FIREWALL-RULE-CONFLICT), "
                "Cloud Armor events (ARMOR-DDOS-ALERT, ARMOR-FALSE-POSITIVE, ARMOR-POLICY-SYNC-FAILURE), "
                "NAT faults (NAT-PORT-EXHAUSTION, NAT-ENDPOINT-MAPPING-FAILURE, NAT-IP-ALLOCATION-ERROR), "
                "DNS issues (DNS-DNSSEC-VALIDATION-FAILURE, DNS-ZONE-PROPAGATION-DELAY), "
                "Interconnect faults (INTERCONNECT-CIRCUIT-DOWN, INTERCONNECT-BGP-FLAP), "
                "CDN errors (CDN-CACHE-MISS-SPIKE, CDN-ORIGIN-UNREACHABLE), "
                "LB faults (LB-BACKEND-UNHEALTHY, LB-SSL-CERT-EXPIRY), "
                "VPN errors (VPN-TUNNEL-DOWN, VPN-IKE-NEGOTIATION-FAILURE), "
                "and NIC events (NI-CONNECTIVITY-TEST-FAILURE). "
                "Log messages are in body.text — NEVER search the body field alone."
            ),
        }

    @property
    def assessment_tool_config(self) -> dict[str, Any]:
        return {
            "id": "network_health_assessment",
            "description": (
                "Comprehensive network health assessment. Evaluates all "
                "GCP networking services against operational readiness criteria. "
                "Returns data for health evaluation across VPC, Cloud Armor, "
                "NAT, DNS, Interconnect, VPN, CDN, and Load Balancing systems. "
                "Log message field: body.text (never use 'body' alone)."
            ),
        }

    @property
    def knowledge_base_docs(self) -> list[dict[str, Any]]:
        return []  # Populated by deployer from channel_registry

    # ── Service Classes ───────────────────────────────────────────────

    def get_service_classes(self) -> list[type]:
        from scenarios.gcp.services.vpc_network_manager import VpcNetworkManagerService
        from scenarios.gcp.services.cloud_load_balancer import CloudLoadBalancerService
        from scenarios.gcp.services.cloud_cdn_service import CloudCdnService
        from scenarios.gcp.services.cloud_armor_waf import CloudArmorWafService
        from scenarios.gcp.services.cloud_nat_gateway import CloudNatGatewayService
        from scenarios.gcp.services.cloud_dns_resolver import CloudDnsResolverService
        from scenarios.gcp.services.cloud_interconnect import CloudInterconnectService
        from scenarios.gcp.services.cloud_vpn_gateway import CloudVpnGatewayService
        from scenarios.gcp.services.network_intelligence import NetworkIntelligenceService

        return [
            VpcNetworkManagerService,
            CloudLoadBalancerService,
            CloudCdnService,
            CloudArmorWafService,
            CloudNatGatewayService,
            CloudDnsResolverService,
            CloudInterconnectService,
            CloudVpnGatewayService,
            NetworkIntelligenceService,
        ]

    # ── Fault Parameters ──────────────────────────────────────────────

    def get_fault_params(self, channel: int) -> dict[str, Any]:
        return {
            # ── VPC / Core Network (channels 1-3) ──
            "gcp_project": random.choice(["gcpnet-prod-001", "gcpnet-prod-002", "gcpnet-staging"]),
            "gcp_region": random.choice(["us-central1", "us-east1", "europe-west1"]),
            "vpc_network": random.choice(["gcpnet-vpc-prod", "gcpnet-vpc-staging", "gcpnet-vpc-shared"]),
            "vpc_peering_name": random.choice(["peer-to-shared-vpc", "peer-to-onprem", "peer-to-partner"]),
            "route_count": random.randint(240, 250),
            "route_max": 250,
            "dropped_prefixes": random.randint(5, 30),
            "subnet_name": random.choice([
                "gcpnet-subnet-central1", "gcpnet-subnet-east1",
                "gcpnet-subnet-europe1", "gcpnet-subnet-services",
            ]),
            "subnet_cidr": random.choice(["10.128.0.0/20", "10.142.0.0/20", "10.132.0.0/20"]),
            "subnet_used_ips": random.randint(3900, 4090),
            "subnet_total_ips": 4094,
            "subnet_util_pct": round(random.uniform(95.0, 100.0), 1),
            "fw_rule_a": random.choice(["allow-internal-all", "allow-health-checks", "allow-iap-ssh"]),
            "fw_rule_b": random.choice(["deny-egress-default", "deny-all-ingress", "deny-suspicious-ips"]),
            "fw_priority_a": random.choice([1000, 1100, 1200]),
            "fw_priority_b": random.choice([900, 950, 1000]),
            "fw_dropped_packets": random.randint(100, 5000),

            # ── Cloud Armor / Security (channels 4-6) ──
            "armor_policy": random.choice(["gcpnet-waf-policy", "gcpnet-ddos-policy", "gcpnet-edge-policy"]),
            "armor_backend": random.choice(["backend-lb-central1", "backend-lb-east1", "backend-lb-europe1"]),
            "armor_rule_name": random.choice(["rate-limit-global", "geo-block-sanctioned", "sqli-detection", "xss-prevention"]),
            "ddos_attack_type": random.choice(["SYN_FLOOD", "UDP_AMPLIFICATION", "HTTP_FLOOD", "DNS_AMPLIFICATION"]),
            "ddos_volume_gbps": round(random.uniform(5.0, 120.0), 1),
            "ddos_source_regions": random.choice(["CN,RU,BR", "RU,UA,KZ", "multiple (>20 countries)"]),
            "ddos_mitigated_pct": round(random.uniform(92.0, 99.9), 1),
            "waf_rule_id": random.choice(["owasp-crs-v030301-id942100", "sqli-v33-stable", "xss-v33-stable", "rce-v33-stable"]),
            "waf_blocked_count": random.randint(100, 5000),
            "waf_fp_rate": round(random.uniform(15.0, 60.0), 1),
            "waf_affected_paths": random.choice(["/api/v2/search", "/api/v1/upload", "/graphql", "/api/v1/webhook"]),
            "waf_sensitivity_level": random.choice(["1 (High)", "2 (Medium)", "3 (Low)"]),
            "policy_version": random.randint(10, 50),
            "backends_synced": random.randint(1, 3),
            "backends_total": random.randint(4, 8),
            "policy_last_sync_sec": random.randint(120, 600),
            "policy_sync_error": random.choice([
                "backend not responding to policy push",
                "version conflict with pending update",
                "timeout waiting for backend acknowledgment",
            ]),

            # ── Cloud NAT (channels 7-9) ──
            "nat_gateway_name": random.choice(["gcpnet-nat-central1", "gcpnet-nat-east1", "gcpnet-nat-europe1"]),
            "nat_ports_used": random.randint(60000, 64000),
            "nat_ports_total": 64512,
            "nat_port_util_pct": round(random.uniform(92.0, 99.5), 1),
            "nat_dropped_conns": random.randint(50, 500),
            "nat_top_vm": random.choice(["gke-node-pool-a-001", "gke-node-pool-b-002", "gke-node-pool-c-003"]),
            "nat_mapping_type": random.choice(["ENDPOINT_INDEPENDENT", "ADDRESS_DEPENDENT"]),
            "nat_mapping_failures": random.randint(100, 2000),
            "nat_external_ip": f"34.{random.randint(64,127)}.{random.randint(0,255)}.{random.randint(1,254)}",
            "nat_protocol": random.choice(["TCP", "UDP", "TCP+UDP"]),
            "nat_allocated_ips": random.randint(8, 10),
            "nat_max_ips": 10,
            "nat_pending_allocs": random.randint(2, 8),
            "nat_alloc_error": random.choice([
                "QUOTA_EXCEEDED: EXTERNAL_IP_ADDRESS",
                "IP_ALREADY_IN_USE by another NAT",
                "REGION_QUOTA_EXCEEDED for static IPs",
            ]),

            # ── Cloud DNS (channels 10-11) ──
            "dns_zone": random.choice(["gcpnet-internal", "gcpnet-prod-zone", "gcpnet-services"]),
            "dns_record_name": random.choice([
                "api.gcpnet.internal", "lb.gcpnet.prod",
                "cdn.gcpnet.internal", "vpn.gcpnet.internal",
            ]),
            "dns_record_type": random.choice(["A", "AAAA", "CNAME", "MX"]),
            "dnssec_rrsig_expiry": random.choice(["EXPIRED", "2h remaining", "30m remaining"]),
            "dnssec_ds_status": random.choice(["MISSING", "STALE", "MISMATCHED_ALGORITHM"]),
            "dnssec_error_count": random.randint(50, 500),
            "dns_change_id": f"change-{random.randint(10000, 99999)}",
            "dns_prop_time_sec": random.randint(120, 600),
            "dns_prop_sla_sec": 60,
            "dns_servers_updated": random.randint(1, 3),
            "dns_servers_total": random.randint(4, 8),

            # ── Interconnect (channels 12-13) ──
            "interconnect_name": random.choice(["gcpnet-interconnect-primary", "gcpnet-interconnect-secondary"]),
            "circuit_id": f"CIR-{random.randint(100000, 999999)}",
            "interconnect_location": random.choice(["iad-zone1-1", "dfw-zone1-1", "ams-zone1-1"]),
            "circuit_down_sec": random.randint(10, 300),
            "interconnect_bw_gbps": random.choice([10, 100]),
            "failover_status": random.choice(["ACTIVE_ON_BACKUP", "FAILOVER_IN_PROGRESS", "NO_BACKUP"]),
            "cloud_router": random.choice(["gcpnet-router-central1", "gcpnet-router-east1", "gcpnet-router-europe1"]),
            "bgp_peer_ip": f"169.254.{random.randint(0,255)}.{random.randint(1,254)}",
            "bgp_peer_asn": random.choice([16550, 64512, 64513, 65001]),
            "bgp_flap_count": random.randint(5, 30),
            "bgp_flap_window": random.randint(60, 600),
            "bgp_state": random.choice(["IDLE", "ACTIVE", "CONNECT", "OPEN_SENT"]),
            "bgp_advertised_routes": random.randint(0, 50),

            # ── CDN (channels 14-15) ──
            "cdn_backend": random.choice(["gcpnet-cdn-backend-01", "gcpnet-cdn-backend-02", "gcpnet-cdn-backend-03"]),
            "cdn_hit_ratio": round(random.uniform(15.0, 45.0), 1),
            "cdn_hit_sla": 85,
            "cdn_miss_rate": random.randint(500, 5000),
            "cdn_origin_latency_ms": random.randint(200, 2000),
            "cdn_cache_fill_pct": round(random.uniform(30.0, 60.0), 1),
            "cdn_origin_host": random.choice(["origin-central1.gcpnet.internal", "origin-east1.gcpnet.internal"]),
            "cdn_origin_status": random.choice([502, 503, 504, 0]),
            "cdn_origin_failures": random.randint(50, 500),
            "cdn_stale_pct": round(random.uniform(20.0, 80.0), 1),
            "cdn_stale_ttl_sec": random.randint(30, 300),

            # ── Load Balancer (channels 16-17) ──
            "lb_forwarding_rule": random.choice(["gcpnet-fr-https-global", "gcpnet-fr-tcp-regional", "gcpnet-fr-udp-internal"]),
            "lb_backend_service": random.choice(["gcpnet-bs-web", "gcpnet-bs-api", "gcpnet-bs-grpc"]),
            "lb_unhealthy_count": random.randint(2, 6),
            "lb_total_backends": random.randint(6, 12),
            "lb_health_check": random.choice(["hc-http-8080", "hc-https-443", "hc-tcp-3000"]),
            "lb_failed_checks": random.randint(3, 10),
            "ssl_cert_name": random.choice(["gcpnet-managed-cert-01", "gcpnet-managed-cert-02"]),
            "ssl_domain": random.choice(["api.gcpnet.example.com", "cdn.gcpnet.example.com", "*.gcpnet.example.com"]),
            "ssl_days_remaining": random.randint(-5, 3),
            "ssl_managed_status": random.choice(["FAILED_NOT_VISIBLE", "FAILED_CAA_CHECKING", "PROVISIONING"]),
            "ssl_affected_rules": random.randint(2, 8),

            # ── VPN (channels 18-19) ──
            "vpn_tunnel_name": random.choice(["gcpnet-vpn-tunnel-01", "gcpnet-vpn-tunnel-02", "gcpnet-vpn-tunnel-03"]),
            "vpn_gateway_name": random.choice(["gcpnet-vpn-gw-europe1", "gcpnet-vpn-gw-central1"]),
            "vpn_peer_ip": f"203.0.113.{random.randint(1, 254)}",
            "vpn_down_sec": random.randint(10, 300),
            "vpn_ike_version": random.choice(["IKEv2", "IKEv1"]),
            "vpn_last_handshake_sec": random.randint(60, 600),
            "ike_phase": random.choice(["1", "2"]),
            "ike_error": random.choice([
                "NO_PROPOSAL_CHOSEN",
                "AUTHENTICATION_FAILED",
                "INVALID_KE_PAYLOAD",
                "TS_UNACCEPTABLE",
            ]),
            "ike_retry_count": random.randint(3, 10),
            "ike_max_retries": 10,

            # ── Network Intelligence (channel 20) ──
            "ni_test_name": random.choice([
                "test-vpc-to-onprem", "test-central1-to-europe1",
                "test-nat-egress", "test-vpn-connectivity",
            ]),
            "ni_src_ip": f"10.{random.randint(128, 142)}.{random.randint(0, 10)}.{random.randint(1, 254)}",
            "ni_dst_ip": f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
            "ni_protocol": random.choice(["TCP:80", "TCP:443", "ICMP", "UDP:53"]),
            "ni_test_result": random.choice(["UNREACHABLE", "DROPPED", "AMBIGUOUS"]),
            "ni_hops_completed": random.randint(2, 5),
            "ni_hops_total": random.randint(6, 10),
            "ni_blocking_resource": random.choice([
                "firewall-rule/deny-all-ingress",
                "route/default-internet-gateway",
                "vpc-peering/peer-to-shared-vpc",
                "cloud-nat/gcpnet-nat-east1",
            ]),
        }


# Module-level instance for registry discovery
scenario = GCPScenario()
