"""Fanatics Collectibles scenario — enterprise infrastructure and network operations."""

from __future__ import annotations

import random
from typing import Any

from scenarios.base import BaseScenario, CountdownConfig, UITheme



class FanaticsScenario(BaseScenario):
    """Enterprise infrastructure and network operations for Fanatics Collectibles."""

    # ── Identity ──────────────────────────────────────────────────────

    @property
    def scenario_id(self) -> str:
        return "fanatics"

    @property
    def scenario_name(self) -> str:
        return "Fanatics Collectibles"

    @property
    def scenario_description(self) -> str:
        return (
            "Enterprise infrastructure and network operations for vertically integrated "
            "trading cards and memorabilia. Recently migrated 100% out of physical DCs to "
            "50% AWS / 50% Azure with GCP edge."
        )

    @property
    def namespace(self) -> str:
        return "fanatics"

    # ── Services ──────────────────────────────────────────────────────

    @property
    def services(self) -> dict[str, dict[str, Any]]:
        return {
            "card-printing-system": {
                "cloud_provider": "aws",
                "cloud_region": "us-east-1",
                "cloud_platform": "aws_ec2",
                "cloud_availability_zone": "us-east-1a",
                "subsystem": "manufacturing",
                "language": "java",
            },
            "digital-marketplace": {
                "cloud_provider": "aws",
                "cloud_region": "us-east-1",
                "cloud_platform": "aws_ec2",
                "cloud_availability_zone": "us-east-1b",
                "subsystem": "commerce",
                "language": "python",
            },
            "auction-engine": {
                "cloud_provider": "aws",
                "cloud_region": "us-east-1",
                "cloud_platform": "aws_ec2",
                "cloud_availability_zone": "us-east-1c",
                "subsystem": "commerce",
                "language": "go",
            },
            "packaging-fulfillment": {
                "cloud_provider": "gcp",
                "cloud_region": "us-central1",
                "cloud_platform": "gcp_compute_engine",
                "cloud_availability_zone": "us-central1-a",
                "subsystem": "logistics",
                "language": "python",
            },
            "wifi-controller": {
                "cloud_provider": "gcp",
                "cloud_region": "us-central1",
                "cloud_platform": "gcp_compute_engine",
                "cloud_availability_zone": "us-central1-b",
                "subsystem": "network_access",
                "language": "cpp",
                "generates_traces": False,
            },
            "cloud-inventory-scanner": {
                "cloud_provider": "gcp",
                "cloud_region": "us-central1",
                "cloud_platform": "gcp_compute_engine",
                "cloud_availability_zone": "us-central1-a",
                "subsystem": "cloud_ops",
                "language": "python",
            },
            "network-controller": {
                "cloud_provider": "azure",
                "cloud_region": "eastus",
                "cloud_platform": "azure_vm",
                "cloud_availability_zone": "eastus-1",
                "subsystem": "network_core",
                "language": "go",
                "generates_traces": False,
            },
            "firewall-gateway": {
                "cloud_provider": "azure",
                "cloud_region": "eastus",
                "cloud_platform": "azure_vm",
                "cloud_availability_zone": "eastus-2",
                "subsystem": "security",
                "language": "rust",
                "generates_traces": False,
            },
            "dns-dhcp-service": {
                "cloud_provider": "azure",
                "cloud_region": "eastus",
                "cloud_platform": "azure_vm",
                "cloud_availability_zone": "eastus-1",
                "subsystem": "network_services",
                "language": "java",
                "generates_traces": False,
            },
        }

    # ── Channel Registry ──────────────────────────────────────────────

    @property
    def channel_registry(self) -> dict[int, dict[str, Any]]:
        return {
            1: {
                "name": "MAC Address Flapping",
                "subsystem": "network_core",
                "vehicle_section": "switching_fabric",
                "error_type": "MACFlapException",
                "sensor_type": "mac_table",
                "affected_services": ["network-controller", "dns-dhcp-service"],
                "cascade_services": ["firewall-gateway", "wifi-controller"],
                "description": "MAC address table instability causing port flapping on the switching fabric",
                "error_message": (
                    "MAC flap detected: address {mac_address} flapping between "
                    "ports {interface_src} and {interface_dst} on VLAN {vlan_id}, "
                    "{flap_count} moves in {flap_window}s"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "network_core/mac_manager.py", line 412, in process_mac_notification\n'
                    "    entry = self._cam_table.lookup(mac_addr, vlan)\n"
                    '  File "network_core/mac_manager.py", line 378, in _detect_flapping\n'
                    "    if move_count > self.FLAP_THRESHOLD:\n"
                    '  File "network_core/mac_manager.py", line 385, in _detect_flapping\n'
                    '    raise MACFlapException(f"MAC {mac_addr} flapping on VLAN {vlan}: {move_count} moves")\n'
                    "MACFlapException: MAC {mac_address} flapping between {interface_src} and {interface_dst} on VLAN {vlan_id}"
                ),
            },
            2: {
                "name": "Spanning Tree Topology Change",
                "subsystem": "network_core",
                "vehicle_section": "switching_fabric",
                "error_type": "STPTopologyChangeException",
                "sensor_type": "stp_state",
                "affected_services": ["network-controller", "firewall-gateway"],
                "cascade_services": ["dns-dhcp-service", "wifi-controller"],
                "description": "Rapid spanning tree topology changes destabilizing Layer 2 forwarding",
                "error_message": (
                    "STP topology change storm: VLAN {vlan_id} instance {stp_instance} received "
                    "{tc_count} TCN BPDUs in {tc_window}s from bridge {bridge_id} via {interface}"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "network_core/stp_engine.py", line 267, in process_bpdu\n'
                    "    self._handle_topology_change(vlan, instance, bpdu)\n"
                    '  File "network_core/stp_engine.py", line 234, in _handle_topology_change\n'
                    "    if tc_count > self.TC_STORM_THRESHOLD:\n"
                    '  File "network_core/stp_engine.py", line 241, in _handle_topology_change\n'
                    '    raise STPTopologyChangeException(f"TC storm on VLAN {vlan}: {tc_count} TCNs in {window}s")\n'
                    "STPTopologyChangeException: TC storm on VLAN {vlan_id}, {tc_count} TCNs from bridge {bridge_id}"
                ),
            },
            3: {
                "name": "BGP Peer Flapping",
                "subsystem": "network_core",
                "vehicle_section": "routing_engine",
                "error_type": "BGPPeerFlapException",
                "sensor_type": "bgp_session",
                "affected_services": ["network-controller", "firewall-gateway"],
                "cascade_services": ["dns-dhcp-service", "cloud-inventory-scanner"],
                "description": "BGP peering session repeatedly transitioning between Established and Idle states",
                "error_message": (
                    "BGP peer flapping: neighbor {bgp_peer_ip} AS {bgp_peer_as} "
                    "transitioned {bgp_flap_count} times in {bgp_flap_window}s, "
                    "last state {bgp_last_state}, notification: {bgp_notification}"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "network_core/bgp_fsm.py", line 523, in handle_state_change\n'
                    "    self._check_flap_dampening(neighbor, new_state)\n"
                    '  File "network_core/bgp_fsm.py", line 489, in _check_flap_dampening\n'
                    "    penalty = self._calculate_penalty(flap_count, window)\n"
                    '  File "network_core/bgp_fsm.py", line 502, in _check_flap_dampening\n'
                    '    raise BGPPeerFlapException(f"Peer {neighbor} flapping: {flap_count} transitions, penalty {penalty}")\n'
                    "BGPPeerFlapException: Peer {bgp_peer_ip} AS{bgp_peer_as} flap count {bgp_flap_count} exceeds dampening threshold"
                ),
            },
            4: {
                "name": "Firewall Session Table Exhaustion",
                "subsystem": "security",
                "vehicle_section": "perimeter_defense",
                "error_type": "SessionExhaustionException",
                "sensor_type": "session_table",
                "affected_services": ["firewall-gateway", "network-controller"],
                "cascade_services": ["digital-marketplace", "auction-engine"],
                "description": "Firewall session table approaching maximum capacity, new connections being dropped",
                "error_message": (
                    "Session table exhaustion: {session_count}/{session_max} sessions "
                    "({session_util_pct}% utilization), {session_drops} new connections dropped "
                    "in zone {fw_zone}, top source {top_source_ip}"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "security/session_manager.py", line 345, in allocate_session\n'
                    "    if self._table.size() >= self._max_sessions:\n"
                    '  File "security/session_manager.py", line 351, in allocate_session\n'
                    "    self._drop_counter.increment(zone)\n"
                    '  File "security/session_manager.py", line 358, in allocate_session\n'
                    '    raise SessionExhaustionException(f"Session table full: {current}/{max_s}, zone {zone}")\n'
                    "SessionExhaustionException: Session table at {session_util_pct}% capacity, dropping connections in {fw_zone}"
                ),
            },
            5: {
                "name": "Firewall CPU Overload",
                "subsystem": "security",
                "vehicle_section": "perimeter_defense",
                "error_type": "FirewallCPUException",
                "sensor_type": "cpu_utilization",
                "affected_services": ["firewall-gateway", "network-controller"],
                "cascade_services": ["dns-dhcp-service", "digital-marketplace"],
                "description": "Firewall data plane CPU exceeding safe operating threshold",
                "error_message": (
                    "Firewall CPU overload: data plane {fw_dp_cpu_pct}% (threshold {fw_cpu_threshold}%), "
                    "management plane {fw_mgmt_cpu_pct}%, "
                    "packet buffer utilization {fw_buffer_pct}%, "
                    "active policy rules {fw_policy_count}"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "security/health_monitor.py", line 278, in check_cpu_utilization\n'
                    "    dp_cpu = self._read_dp_cpu_stats()\n"
                    '  File "security/health_monitor.py", line 256, in _read_dp_cpu_stats\n'
                    "    if dp_cpu > self.CPU_CRITICAL_THRESHOLD:\n"
                    '  File "security/health_monitor.py", line 263, in _read_dp_cpu_stats\n'
                    '    raise FirewallCPUException(f"Data plane CPU at {dp_cpu}%, threshold {threshold}%")\n'
                    "FirewallCPUException: Data plane CPU {fw_dp_cpu_pct}% exceeds threshold {fw_cpu_threshold}%"
                ),
            },
            6: {
                "name": "SSL Decryption Certificate Expiry",
                "subsystem": "security",
                "vehicle_section": "ssl_inspection",
                "error_type": "CertExpiryException",
                "sensor_type": "certificate",
                "affected_services": ["firewall-gateway", "dns-dhcp-service"],
                "cascade_services": ["digital-marketplace", "auction-engine"],
                "description": "SSL decryption forward proxy certificate expiring or expired, breaking TLS inspection",
                "error_message": (
                    "SSL certificate expiry: certificate '{cert_cn}' (serial {cert_serial}) "
                    "expires in {cert_days_remaining} days, used by {cert_profile} decryption profile, "
                    "affecting {cert_affected_rules} policy rules"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "security/cert_manager.py", line 189, in validate_certificates\n'
                    "    days_remaining = (cert.not_after - datetime.utcnow()).days\n"
                    '  File "security/cert_manager.py", line 195, in validate_certificates\n'
                    "    if days_remaining <= self.EXPIRY_WARNING_DAYS:\n"
                    '  File "security/cert_manager.py", line 201, in validate_certificates\n'
                    '    raise CertExpiryException(f"Certificate {cn} expires in {days_remaining}d")\n'
                    "CertExpiryException: Certificate '{cert_cn}' serial {cert_serial} expiring in {cert_days_remaining} days"
                ),
            },
            7: {
                "name": "WiFi AP Disconnect Storm",
                "subsystem": "network_access",
                "vehicle_section": "wireless_lan",
                "error_type": "APDisconnectException",
                "sensor_type": "ap_status",
                "affected_services": ["wifi-controller", "network-controller"],
                "cascade_services": ["packaging-fulfillment", "card-printing-system"],
                "description": "Multiple wireless access points simultaneously losing connectivity to the controller",
                "error_message": (
                    "AP disconnect storm: {ap_disconnect_count} APs lost connectivity in {ap_disconnect_window}s, "
                    "affected APs include {ap_name} (site {ap_site}), "
                    "last CAPWAP heartbeat {ap_last_heartbeat}s ago"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "network_access/wlc_manager.py", line 334, in monitor_ap_health\n'
                    "    heartbeat_age = time.time() - ap.last_heartbeat\n"
                    '  File "network_access/wlc_manager.py", line 341, in monitor_ap_health\n'
                    "    if heartbeat_age > self.HEARTBEAT_TIMEOUT:\n"
                    '  File "network_access/wlc_manager.py", line 348, in monitor_ap_health\n'
                    '    raise APDisconnectException(f"AP {ap_name} heartbeat timeout after {heartbeat_age}s")\n'
                    "APDisconnectException: {ap_disconnect_count} APs disconnected, including {ap_name} at site {ap_site}"
                ),
            },
            8: {
                "name": "WiFi Channel Interference",
                "subsystem": "network_access",
                "vehicle_section": "wireless_lan",
                "error_type": "ChannelInterferenceException",
                "sensor_type": "rf_spectrum",
                "affected_services": ["wifi-controller", "network-controller"],
                "cascade_services": ["packaging-fulfillment"],
                "description": "Co-channel and adjacent-channel interference degrading wireless performance",
                "error_message": (
                    "Channel interference: AP {ap_name} on channel {channel_number} "
                    "detecting {interference_pct}% co-channel interference, "
                    "noise floor {noise_floor_dbm}dBm, "
                    "client retransmit rate {retransmit_pct}%, "
                    "neighboring AP count {neighbor_ap_count}"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "network_access/rf_manager.py", line 223, in analyze_spectrum\n'
                    "    interference = self._measure_cci(ap, channel)\n"
                    '  File "network_access/rf_manager.py", line 198, in _measure_cci\n'
                    "    if interference_pct > self.CCI_THRESHOLD:\n"
                    '  File "network_access/rf_manager.py", line 205, in _measure_cci\n'
                    '    raise ChannelInterferenceException(f"CCI {interference_pct}% on ch{channel} at {ap_name}")\n'
                    "ChannelInterferenceException: {interference_pct}% co-channel interference on channel {channel_number} at {ap_name}"
                ),
            },
            9: {
                "name": "Client Authentication Storm",
                "subsystem": "network_access",
                "vehicle_section": "wireless_auth",
                "error_type": "AuthStormException",
                "sensor_type": "radius_auth",
                "affected_services": ["wifi-controller", "dns-dhcp-service"],
                "cascade_services": ["network-controller"],
                "description": "RADIUS authentication requests spiking beyond server capacity",
                "error_message": (
                    "Authentication storm: {auth_requests_per_sec} RADIUS requests/sec "
                    "(threshold {auth_threshold}/s), "
                    "{auth_failures} failures, {auth_timeouts} timeouts, "
                    "NAS {radius_nas_ip}, server {radius_server}"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "network_access/radius_handler.py", line 289, in process_auth_request\n'
                    "    rate = self._auth_rate_counter.get_rate()\n"
                    '  File "network_access/radius_handler.py", line 267, in process_auth_request\n'
                    "    if rate > self.AUTH_STORM_THRESHOLD:\n"
                    '  File "network_access/radius_handler.py", line 274, in process_auth_request\n'
                    '    raise AuthStormException(f"Auth rate {rate}/s exceeds threshold {threshold}/s")\n'
                    "AuthStormException: {auth_requests_per_sec} auth/s from NAS {radius_nas_ip}, {auth_failures} failures"
                ),
            },
            10: {
                "name": "DNS Resolution Failure Over VPN",
                "subsystem": "network_services",
                "vehicle_section": "name_resolution",
                "error_type": "DNSResolutionException",
                "sensor_type": "dns_query",
                "affected_services": ["dns-dhcp-service", "network-controller"],
                "cascade_services": ["digital-marketplace", "auction-engine", "cloud-inventory-scanner"],
                "description": "DNS queries traversing VPN tunnel failing to resolve internal records",
                "error_message": (
                    "DNS resolution failure: query '{dns_query_name}' type {dns_query_type} "
                    "via VPN tunnel {vpn_tunnel_name} returned {dns_rcode}, "
                    "upstream forwarder {dns_forwarder_ip} unreachable, "
                    "fallback forwarder {dns_fallback_ip} timeout after {dns_timeout_ms}ms"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "network_services/dns_resolver.py", line 312, in resolve_query\n'
                    "    response = self._forward_via_vpn(query, tunnel)\n"
                    '  File "network_services/dns_resolver.py", line 289, in _forward_via_vpn\n'
                    "    raise socket.timeout(f'Forwarder {forwarder} timeout after {timeout}ms')\n"
                    '  File "network_services/dns_resolver.py", line 296, in _forward_via_vpn\n'
                    '    raise DNSResolutionException(f"Cannot resolve {qname} ({qtype}) via {tunnel}")\n'
                    "DNSResolutionException: Failed to resolve '{dns_query_name}' ({dns_query_type}) via tunnel {vpn_tunnel_name}"
                ),
            },
            11: {
                "name": "DHCP Lease Storm",
                "subsystem": "network_services",
                "vehicle_section": "address_management",
                "error_type": "DHCPLeaseStormException",
                "sensor_type": "dhcp_lease",
                "affected_services": ["dns-dhcp-service", "network-controller"],
                "cascade_services": ["wifi-controller", "packaging-fulfillment"],
                "description": "DHCP scope exhaustion from excessive DISCOVER/REQUEST rate",
                "error_message": (
                    "DHCP lease storm: scope {dhcp_scope} at {dhcp_util_pct}% utilization "
                    "({dhcp_active_leases}/{dhcp_total_leases} leases), "
                    "{dhcp_discover_rate} DISCOVER/s, {dhcp_nak_count} NAKs sent, "
                    "rogue DHCP detected from {dhcp_rogue_ip}"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "network_services/dhcp_server.py", line 234, in handle_discover\n'
                    "    lease = self._pool.allocate(scope, mac_addr)\n"
                    '  File "network_services/dhcp_server.py", line 212, in _pool_allocate\n'
                    "    if pool.utilization() > self.STORM_THRESHOLD:\n"
                    '  File "network_services/dhcp_server.py", line 219, in _pool_allocate\n'
                    '    raise DHCPLeaseStormException(f"Scope {scope} at {util}%, discover rate {rate}/s")\n'
                    "DHCPLeaseStormException: Scope {dhcp_scope} exhaustion at {dhcp_util_pct}%, {dhcp_discover_rate} DISCOVER/s"
                ),
            },
            12: {
                "name": "Auction Bid Latency Spike",
                "subsystem": "commerce",
                "vehicle_section": "bidding_platform",
                "error_type": "BidLatencyException",
                "sensor_type": "bid_processing",
                "affected_services": ["auction-engine", "digital-marketplace"],
                "cascade_services": ["network-controller", "firewall-gateway"],
                "description": "Real-time bid processing latency exceeding SLA thresholds",
                "error_message": (
                    "Bid latency spike: auction {auction_id} bid {bid_id} "
                    "processing latency {bid_latency_ms}ms (SLA {bid_sla_ms}ms), "
                    "queue depth {bid_queue_depth}, "
                    "websocket broadcast delay {ws_delay_ms}ms, "
                    "affected bidders {affected_bidders}"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "commerce/bid_processor.py", line 289, in process_bid\n'
                    "    elapsed = time.monotonic() - start\n"
                    '  File "commerce/bid_processor.py", line 295, in process_bid\n'
                    "    if elapsed_ms > self.BID_SLA_MS:\n"
                    '  File "commerce/bid_processor.py", line 301, in process_bid\n'
                    '    raise BidLatencyException(f"Bid {bid_id} took {elapsed_ms}ms, SLA {sla}ms")\n'
                    "BidLatencyException: Bid {bid_id} on auction {auction_id} latency {bid_latency_ms}ms exceeds SLA {bid_sla_ms}ms"
                ),
            },
            13: {
                "name": "Payment Processing Timeout",
                "subsystem": "commerce",
                "vehicle_section": "payment_system",
                "error_type": "PaymentTimeoutException",
                "sensor_type": "payment_gateway",
                "affected_services": ["digital-marketplace", "auction-engine"],
                "cascade_services": ["firewall-gateway"],
                "description": "Payment gateway requests timing out, affecting checkout and auction settlements",
                "error_message": (
                    "Payment timeout: order {order_id} payment via {payment_provider} "
                    "timed out after {payment_timeout_ms}ms, "
                    "gateway response code {gateway_response_code}, "
                    "retry {payment_retry_count}/{payment_max_retries}, "
                    "amount ${payment_amount}"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "commerce/payment_handler.py", line 178, in process_payment\n'
                    "    response = self._gateway.charge(order_id, amount, provider)\n"
                    '  File "commerce/payment_handler.py", line 156, in _gateway_charge\n'
                    "    raise requests.exceptions.ReadTimeout(f'Gateway timeout after {timeout}ms')\n"
                    '  File "commerce/payment_handler.py", line 163, in _gateway_charge\n'
                    '    raise PaymentTimeoutException(f"Payment for order {order_id} timed out via {provider}")\n'
                    "PaymentTimeoutException: Order {order_id} payment via {payment_provider} timeout after {payment_timeout_ms}ms"
                ),
            },
            14: {
                "name": "Product Catalog Sync Failure",
                "subsystem": "commerce",
                "vehicle_section": "catalog_system",
                "error_type": "CatalogSyncException",
                "sensor_type": "catalog_sync",
                "affected_services": ["digital-marketplace", "card-printing-system"],
                "cascade_services": ["auction-engine"],
                "description": "Product catalog replication between marketplace and printing system failing",
                "error_message": (
                    "Catalog sync failure: {catalog_sync_failed} of {catalog_sync_total} records "
                    "failed to sync from {catalog_source} to {catalog_destination}, "
                    "last successful sync {catalog_last_sync_min}m ago, "
                    "error: {catalog_error_detail}"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "commerce/catalog_replicator.py", line 267, in sync_catalog\n'
                    "    result = self._replicate_batch(source, dest, batch)\n"
                    '  File "commerce/catalog_replicator.py", line 245, in _replicate_batch\n'
                    "    if result.failed_count > 0:\n"
                    '  File "commerce/catalog_replicator.py", line 251, in _replicate_batch\n'
                    '    raise CatalogSyncException(f"Sync failed: {failed}/{total} records from {source} to {dest}")\n'
                    "CatalogSyncException: {catalog_sync_failed}/{catalog_sync_total} records failed syncing {catalog_source} -> {catalog_destination}"
                ),
            },
            15: {
                "name": "Print Queue Overflow",
                "subsystem": "manufacturing",
                "vehicle_section": "production_line",
                "error_type": "PrintQueueOverflowException",
                "sensor_type": "print_queue",
                "affected_services": ["card-printing-system", "packaging-fulfillment"],
                "cascade_services": ["digital-marketplace"],
                "description": "Print job queue exceeding buffer capacity, new jobs being rejected",
                "error_message": (
                    "Print queue overflow: queue depth {print_queue_depth}/{print_queue_max} "
                    "({print_queue_pct}% full), "
                    "job {print_job_id} rejected, "
                    "oldest pending job {print_oldest_job_min}m old, "
                    "printer {printer_name} status {printer_status}"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "manufacturing/print_scheduler.py", line 312, in enqueue_job\n'
                    "    if self._queue.size() >= self._max_depth:\n"
                    '  File "manufacturing/print_scheduler.py", line 318, in enqueue_job\n'
                    "    self._rejected_counter.increment()\n"
                    '  File "manufacturing/print_scheduler.py", line 324, in enqueue_job\n'
                    '    raise PrintQueueOverflowException(f"Queue full: {depth}/{max_d}, job {job_id} rejected")\n'
                    "PrintQueueOverflowException: Queue at {print_queue_pct}%, job {print_job_id} rejected, printer {printer_name} {printer_status}"
                ),
            },
            16: {
                "name": "Quality Control Rejection Spike",
                "subsystem": "manufacturing",
                "vehicle_section": "quality_assurance",
                "error_type": "QCRejectionException",
                "sensor_type": "qc_inspection",
                "affected_services": ["card-printing-system", "packaging-fulfillment"],
                "cascade_services": ["digital-marketplace", "auction-engine"],
                "description": "Automated quality inspection system rejecting cards above acceptable defect rate",
                "error_message": (
                    "QC rejection spike: {qc_reject_count}/{qc_inspected_count} cards rejected "
                    "({qc_reject_pct}% defect rate, threshold {qc_threshold_pct}%), "
                    "primary defect: {qc_defect_type}, "
                    "batch {qc_batch_id}, line {qc_line_number}"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "manufacturing/qc_inspector.py", line 234, in inspect_batch\n'
                    "    defect_rate = rejected / inspected * 100\n"
                    '  File "manufacturing/qc_inspector.py", line 240, in inspect_batch\n'
                    "    if defect_rate > self.DEFECT_THRESHOLD:\n"
                    '  File "manufacturing/qc_inspector.py", line 246, in inspect_batch\n'
                    '    raise QCRejectionException(f"Defect rate {{defect_rate:.1f}}% on batch {{batch_id}}")\n'
                    "QCRejectionException: Batch {qc_batch_id} defect rate {qc_reject_pct}% exceeds {qc_threshold_pct}% threshold on line {qc_line_number}"
                ),
            },
            17: {
                "name": "Fulfillment Label Printer Failure",
                "subsystem": "logistics",
                "vehicle_section": "shipping_bay",
                "error_type": "LabelPrinterException",
                "sensor_type": "label_printer",
                "affected_services": ["packaging-fulfillment", "card-printing-system"],
                "cascade_services": ["digital-marketplace"],
                "description": "Shipping label printers going offline or producing unreadable labels",
                "error_message": (
                    "Label printer failure: printer {label_printer_id} status {label_printer_status}, "
                    "error code {label_error_code}, "
                    "{label_failed_count} labels failed in last {label_window_min}m, "
                    "carrier {label_carrier}, "
                    "queue backed up to {label_queue_depth} shipments"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "logistics/label_manager.py", line 198, in print_label\n'
                    "    result = self._printer.send_zpl(label_data)\n"
                    '  File "logistics/label_manager.py", line 176, in _printer_send_zpl\n'
                    "    if result.status != 'OK':\n"
                    '  File "logistics/label_manager.py", line 183, in _printer_send_zpl\n'
                    '    raise LabelPrinterException(f"Printer {printer_id} error: {error_code}")\n'
                    "LabelPrinterException: Printer {label_printer_id} {label_printer_status}, error {label_error_code}, {label_failed_count} failures"
                ),
            },
            18: {
                "name": "Warehouse Scanner Desync",
                "subsystem": "logistics",
                "vehicle_section": "inventory_system",
                "error_type": "ScannerDesyncException",
                "sensor_type": "barcode_scanner",
                "affected_services": ["packaging-fulfillment", "cloud-inventory-scanner"],
                "cascade_services": ["digital-marketplace", "card-printing-system"],
                "description": "Barcode scanners losing synchronization with inventory management system",
                "error_message": (
                    "Scanner desync: scanner {scanner_id} in zone {scanner_zone} "
                    "last sync {scanner_last_sync_sec}s ago (max {scanner_sync_max_sec}s), "
                    "{scanner_missed_scans} missed scans, "
                    "inventory delta {inventory_delta} items, "
                    "firmware v{scanner_firmware}"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "logistics/scanner_manager.py", line 267, in check_sync_status\n'
                    "    age = time.time() - scanner.last_sync_ts\n"
                    '  File "logistics/scanner_manager.py", line 273, in check_sync_status\n'
                    "    if age > self.MAX_SYNC_AGE:\n"
                    '  File "logistics/scanner_manager.py", line 279, in check_sync_status\n'
                    '    raise ScannerDesyncException(f"Scanner {scanner_id} desync: {age}s since last sync")\n'
                    "ScannerDesyncException: Scanner {scanner_id} zone {scanner_zone} desync, {scanner_missed_scans} missed scans"
                ),
            },
            19: {
                "name": "Orphaned Cloud Resource Alert",
                "subsystem": "cloud_ops",
                "vehicle_section": "asset_management",
                "error_type": "OrphanedResourceException",
                "sensor_type": "cloud_asset",
                "affected_services": ["cloud-inventory-scanner", "network-controller"],
                "cascade_services": ["firewall-gateway"],
                "description": "Cloud resources detected without owner tags or associated workloads",
                "error_message": (
                    "Orphaned resource: {cloud_resource_type} '{cloud_resource_id}' "
                    "in {cloud_resource_provider}/{cloud_resource_region}, "
                    "no owner tag, running for {cloud_resource_age_days} days, "
                    "estimated cost ${cloud_resource_cost_daily}/day, "
                    "security group {cloud_resource_sg}"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "cloud_ops/asset_scanner.py", line 345, in scan_resources\n'
                    "    owner = self._resolve_owner(resource)\n"
                    '  File "cloud_ops/asset_scanner.py", line 323, in _resolve_owner\n'
                    "    if not resource.tags.get('owner') and not resource.tags.get('team'):\n"
                    '  File "cloud_ops/asset_scanner.py", line 329, in _resolve_owner\n'
                    '    raise OrphanedResourceException(f"Resource {resource_id} has no owner tag")\n'
                    "OrphanedResourceException: {cloud_resource_type} '{cloud_resource_id}' in {cloud_resource_provider}/{cloud_resource_region} unowned for {cloud_resource_age_days} days"
                ),
            },
            20: {
                "name": "Cross-Cloud VPN Tunnel Flapping",
                "subsystem": "cloud_ops",
                "vehicle_section": "vpn_connectivity",
                "error_type": "VPNTunnelFlapException",
                "sensor_type": "vpn_tunnel",
                "affected_services": ["cloud-inventory-scanner", "network-controller"],
                "cascade_services": ["dns-dhcp-service", "firewall-gateway"],
                "description": "Site-to-site VPN tunnels between cloud providers repeatedly going up and down",
                "error_message": (
                    "VPN tunnel flapping: tunnel {vpn_tunnel_name} ({vpn_src_cloud} -> {vpn_dst_cloud}) "
                    "{vpn_flap_count} state changes in {vpn_flap_window}s, "
                    "current state {vpn_current_state}, "
                    "IKE phase {vpn_ike_phase} {vpn_ike_status}, "
                    "last DPD {vpn_last_dpd_sec}s ago"
                ),
                "stack_trace": (
                    "Traceback (most recent call last):\n"
                    '  File "cloud_ops/vpn_monitor.py", line 289, in check_tunnel_health\n'
                    "    flap_count = self._count_state_changes(tunnel, window)\n"
                    '  File "cloud_ops/vpn_monitor.py", line 267, in _count_state_changes\n'
                    "    if flap_count > self.FLAP_THRESHOLD:\n"
                    '  File "cloud_ops/vpn_monitor.py", line 274, in _count_state_changes\n'
                    '    raise VPNTunnelFlapException(f"Tunnel {name} flapped {flap_count} times in {window}s")\n'
                    "VPNTunnelFlapException: Tunnel {vpn_tunnel_name} ({vpn_src_cloud}->{vpn_dst_cloud}) flapped {vpn_flap_count} times"
                ),
            },
        }

    # ── Topology ──────────────────────────────────────────────────────

    @property
    def service_topology(self) -> dict[str, list[tuple[str, str, str]]]:
        return {
            "network-controller": [
                ("firewall-gateway", "/api/v1/firewall/sessions", "GET"),
                ("firewall-gateway", "/api/v1/firewall/policy-push", "POST"),
                ("dns-dhcp-service", "/api/v1/dns/zone-status", "GET"),
                ("dns-dhcp-service", "/api/v1/dhcp/scope-status", "GET"),
                ("wifi-controller", "/api/v1/wifi/ap-status", "GET"),
            ],
            "firewall-gateway": [
                ("dns-dhcp-service", "/api/v1/dns/resolve", "POST"),
                ("network-controller", "/api/v1/network/route-table", "GET"),
            ],
            "digital-marketplace": [
                ("auction-engine", "/api/v1/auction/active-listings", "GET"),
                ("auction-engine", "/api/v1/auction/place-bid", "POST"),
                ("card-printing-system", "/api/v1/printing/order-status", "GET"),
                ("card-printing-system", "/api/v1/printing/submit-job", "POST"),
                ("packaging-fulfillment", "/api/v1/fulfillment/ship-order", "POST"),
            ],
            "auction-engine": [
                ("digital-marketplace", "/api/v1/marketplace/listing-update", "POST"),
                ("digital-marketplace", "/api/v1/marketplace/payment-settle", "POST"),
            ],
            "card-printing-system": [
                ("packaging-fulfillment", "/api/v1/fulfillment/queue-package", "POST"),
                ("digital-marketplace", "/api/v1/marketplace/inventory-update", "POST"),
            ],
            "packaging-fulfillment": [
                ("cloud-inventory-scanner", "/api/v1/inventory/reconcile", "POST"),
                ("digital-marketplace", "/api/v1/marketplace/shipment-notify", "POST"),
            ],
            "cloud-inventory-scanner": [
                ("network-controller", "/api/v1/network/vpn-health", "GET"),
                ("firewall-gateway", "/api/v1/firewall/sg-audit", "GET"),
            ],
            "wifi-controller": [
                ("dns-dhcp-service", "/api/v1/dhcp/client-lease", "GET"),
                ("network-controller", "/api/v1/network/vlan-map", "GET"),
            ],
            "dns-dhcp-service": [
                ("network-controller", "/api/v1/network/interface-status", "GET"),
            ],
        }

    @property
    def entry_endpoints(self) -> dict[str, list[tuple[str, str]]]:
        return {
            "network-controller": [
                ("/api/v1/network/health", "GET"),
                ("/api/v1/network/topology", "GET"),
                ("/api/v1/network/config-push", "POST"),
            ],
            "firewall-gateway": [
                ("/api/v1/firewall/status", "GET"),
                ("/api/v1/firewall/threat-log", "GET"),
            ],
            "dns-dhcp-service": [
                ("/api/v1/dns/query", "POST"),
                ("/api/v1/dhcp/lease-report", "GET"),
                ("/api/v1/dns/health", "GET"),
            ],
            "digital-marketplace": [
                ("/api/v1/marketplace/browse", "GET"),
                ("/api/v1/marketplace/checkout", "POST"),
                ("/api/v1/marketplace/search", "GET"),
            ],
            "auction-engine": [
                ("/api/v1/auction/live", "GET"),
                ("/api/v1/auction/bid", "POST"),
            ],
            "card-printing-system": [
                ("/api/v1/printing/queue-status", "GET"),
                ("/api/v1/printing/submit", "POST"),
            ],
            "packaging-fulfillment": [
                ("/api/v1/fulfillment/status", "GET"),
                ("/api/v1/fulfillment/ship", "POST"),
            ],
            "wifi-controller": [
                ("/api/v1/wifi/dashboard", "GET"),
            ],
            "cloud-inventory-scanner": [
                ("/api/v1/inventory/scan", "POST"),
                ("/api/v1/inventory/compliance", "GET"),
            ],
        }

    @property
    def db_operations(self) -> dict[str, list[tuple[str, str, str]]]:
        return {
            "digital-marketplace": [
                ("SELECT", "products", "SELECT id, name, price, stock FROM products WHERE category = ? AND status = 'active' ORDER BY listed_at DESC LIMIT 50"),
                ("INSERT", "orders", "INSERT INTO orders (user_id, product_id, quantity, total, status, created_at) VALUES (?, ?, ?, ?, 'pending', NOW())"),
                ("UPDATE", "inventory", "UPDATE inventory SET quantity = quantity - ? WHERE sku = ? AND quantity >= ?"),
            ],
            "auction-engine": [
                ("SELECT", "auctions", "SELECT id, current_bid, bid_count, end_time FROM auctions WHERE status = 'active' AND end_time > NOW()"),
                ("INSERT", "bids", "INSERT INTO bids (auction_id, bidder_id, amount, placed_at) VALUES (?, ?, ?, NOW())"),
                ("UPDATE", "auctions", "UPDATE auctions SET current_bid = ?, bid_count = bid_count + 1, last_bid_at = NOW() WHERE id = ? AND current_bid < ?"),
            ],
            "card-printing-system": [
                ("SELECT", "print_jobs", "SELECT job_id, card_design_id, quantity, priority, status FROM print_jobs WHERE status IN ('queued', 'printing') ORDER BY priority DESC"),
                ("UPDATE", "print_jobs", "UPDATE print_jobs SET status = ?, completed_at = NOW() WHERE job_id = ?"),
            ],
            "packaging-fulfillment": [
                ("SELECT", "shipments", "SELECT order_id, tracking_number, carrier, status FROM shipments WHERE created_at > NOW() - INTERVAL 24 HOUR AND status = 'pending'"),
                ("INSERT", "shipments", "INSERT INTO shipments (order_id, tracking_number, carrier, weight_oz, status) VALUES (?, ?, ?, ?, 'label_printed')"),
            ],
            "dns-dhcp-service": [
                ("SELECT", "dns_records", "SELECT fqdn, record_type, ttl, value FROM dns_records WHERE zone = ? AND record_type = ?"),
                ("SELECT", "dhcp_leases", "SELECT mac_addr, ip_addr, lease_start, lease_end, hostname FROM dhcp_leases WHERE scope = ? AND lease_end > NOW()"),
            ],
            "cloud-inventory-scanner": [
                ("SELECT", "cloud_resources", "SELECT resource_id, resource_type, provider, region, owner_tag, created_at FROM cloud_resources WHERE owner_tag IS NULL AND created_at < NOW() - INTERVAL 7 DAY"),
            ],
        }

    # ── Infrastructure ────────────────────────────────────────────────

    @property
    def hosts(self) -> list[dict[str, Any]]:
        return [
            {
                "host.name": "fanatics-aws-host-01",
                "host.id": "i-0f2a3b4c5d6e78901",
                "host.arch": "amd64",
                "host.type": "m5.xlarge",
                "host.image.id": "ami-0fedcba987654321",
                "host.cpu.model.name": "Intel(R) Xeon(R) Platinum 8175M CPU @ 2.50GHz",
                "host.cpu.vendor.id": "GenuineIntel",
                "host.cpu.family": "6",
                "host.cpu.model.id": "85",
                "host.cpu.stepping": "4",
                "host.cpu.cache.l2.size": 1048576,
                "host.ip": ["10.10.1.50", "172.16.1.10"],
                "host.mac": ["0a:2b:3c:4d:5e:6f", "0a:2b:3c:4d:5e:70"],
                "os.type": "linux",
                "os.description": "Amazon Linux 2023.6.20250115",
                "cloud.provider": "aws",
                "cloud.platform": "aws_ec2",
                "cloud.region": "us-east-1",
                "cloud.availability_zone": "us-east-1a",
                "cloud.account.id": "987654321012",
                "cloud.instance.id": "i-0f2a3b4c5d6e78901",
                "cpu_count": 4,
                "memory_total_bytes": 16 * 1024 * 1024 * 1024,
                "disk_total_bytes": 200 * 1024 * 1024 * 1024,
            },
            {
                "host.name": "fanatics-gcp-host-01",
                "host.id": "7823456789012345678",
                "host.arch": "amd64",
                "host.type": "e2-standard-4",
                "host.image.id": "projects/debian-cloud/global/images/debian-12-bookworm-v20250115",
                "host.cpu.model.name": "Intel(R) Xeon(R) CPU @ 2.20GHz",
                "host.cpu.vendor.id": "GenuineIntel",
                "host.cpu.family": "6",
                "host.cpu.model.id": "85",
                "host.cpu.stepping": "7",
                "host.cpu.cache.l2.size": 1048576,
                "host.ip": ["10.128.1.20", "10.128.1.21"],
                "host.mac": ["42:01:0a:80:01:14", "42:01:0a:80:01:15"],
                "os.type": "linux",
                "os.description": "Debian GNU/Linux 12 (bookworm)",
                "cloud.provider": "gcp",
                "cloud.platform": "gcp_compute_engine",
                "cloud.region": "us-central1",
                "cloud.availability_zone": "us-central1-a",
                "cloud.account.id": "fanatics-infra-prod",
                "cloud.instance.id": "7823456789012345678",
                "cpu_count": 4,
                "memory_total_bytes": 16 * 1024 * 1024 * 1024,
                "disk_total_bytes": 100 * 1024 * 1024 * 1024,
            },
            {
                "host.name": "fanatics-azure-host-01",
                "host.id": "/subscriptions/fab-012/resourceGroups/fanatics-rg/providers/Microsoft.Compute/virtualMachines/fanatics-vm-01",
                "host.arch": "amd64",
                "host.type": "Standard_D4s_v3",
                "host.image.id": "Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest",
                "host.cpu.model.name": "Intel(R) Xeon(R) Platinum 8370C CPU @ 2.80GHz",
                "host.cpu.vendor.id": "GenuineIntel",
                "host.cpu.family": "6",
                "host.cpu.model.id": "106",
                "host.cpu.stepping": "6",
                "host.cpu.cache.l2.size": 1310720,
                "host.ip": ["10.2.0.10", "10.2.0.11"],
                "host.mac": ["00:0d:3a:7e:8f:9a", "00:0d:3a:7e:8f:9b"],
                "os.type": "linux",
                "os.description": "Ubuntu 22.04.5 LTS",
                "cloud.provider": "azure",
                "cloud.platform": "azure_vm",
                "cloud.region": "eastus",
                "cloud.availability_zone": "eastus-1",
                "cloud.account.id": "fab-012-345-678",
                "cloud.instance.id": "fanatics-vm-01",
                "cpu_count": 4,
                "memory_total_bytes": 16 * 1024 * 1024 * 1024,
                "disk_total_bytes": 128 * 1024 * 1024 * 1024,
            },
        ]

    @property
    def k8s_clusters(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "fanatics-eks-cluster",
                "provider": "aws",
                "platform": "aws_eks",
                "region": "us-east-1",
                "zones": ["us-east-1a", "us-east-1b", "us-east-1c"],
                "os_description": "Amazon Linux 2",
                "services": ["card-printing-system", "digital-marketplace", "auction-engine"],
            },
            {
                "name": "fanatics-gke-cluster",
                "provider": "gcp",
                "platform": "gcp_gke",
                "region": "us-central1",
                "zones": ["us-central1-a", "us-central1-b", "us-central1-c"],
                "os_description": "Container-Optimized OS",
                "services": ["packaging-fulfillment", "wifi-controller", "cloud-inventory-scanner"],
            },
            {
                "name": "fanatics-aks-cluster",
                "provider": "azure",
                "platform": "azure_aks",
                "region": "eastus",
                "zones": ["eastus-1", "eastus-2", "eastus-3"],
                "os_description": "Ubuntu 22.04 LTS",
                "services": ["network-controller", "firewall-gateway", "dns-dhcp-service"],
            },
        ]

    # ── Theme ─────────────────────────────────────────────────────────

    @property
    def theme(self) -> UITheme:
        return UITheme(
            bg_primary="#0d1117",
            bg_secondary="#161b22",
            bg_tertiary="#21262d",
            accent_primary="#58a6ff",
            accent_secondary="#3fb950",
            text_primary="#e6edf3",
            text_secondary="#8b949e",
            text_accent="#58a6ff",
            status_nominal="#3fb950",
            status_warning="#d29922",
            status_critical="#f85149",
            status_info="#58a6ff",
            font_family="'Inter', system-ui, sans-serif",
            grid_background=True,
            dashboard_title="Network Operations Center (NOC)",
            chaos_title="Incident Simulator",
            landing_title="Fanatics Infrastructure Operations",
        )

    @property
    def countdown_config(self) -> CountdownConfig:
        return CountdownConfig(enabled=False)

    # ── Agent Config ──────────────────────────────────────────────────

    @property
    def agent_config(self) -> dict[str, Any]:
        return {
            "id": "fanatics-infra-analyst",
            "name": "Infrastructure & Network Analyst",
            "assessment_tool_name": "platform_load_assessment",
            "system_prompt": (
                "You are the Fanatics Infrastructure & Network Analyst, an expert AI assistant "
                "for enterprise network and infrastructure operations. You help NOC engineers "
                "investigate incidents, analyze telemetry data, and provide root cause analysis "
                "for fault conditions across 9 infrastructure services spanning AWS, GCP, and Azure. "
                "You have deep expertise in Cisco IOS-XE/NX-OS switching and routing, "
                "Palo Alto PAN-OS firewall management, Juniper Mist wireless LAN controllers, "
                "Infoblox DDI (DNS/DHCP/IPAM), AWS VPC networking, Azure Virtual Network, "
                "and GCP VPC. You understand BGP peering, spanning tree protocol, "
                "802.1X/RADIUS authentication, SSL inspection, and cross-cloud VPN tunneling."
            ),
        }

    @property
    def assessment_tool_config(self) -> dict[str, Any]:
        return {
            "id": "platform_load_assessment",
            "description": (
                "Comprehensive platform load assessment. Evaluates all "
                "infrastructure services against event-day readiness criteria. "
                "Returns data for load evaluation across networking, DNS, "
                "VPN, firewall, and cloud infrastructure systems. "
                "Log message field: body.text (never use 'body' alone)."
            ),
        }

    @property
    def knowledge_base_docs(self) -> list[dict[str, Any]]:
        return []  # Populated by deployer from channel_registry

    # ── Service Classes ───────────────────────────────────────────────

    def get_service_classes(self) -> list[type]:
        from scenarios.fanatics.services.card_printing import CardPrintingSystemService
        from scenarios.fanatics.services.digital_marketplace import DigitalMarketplaceService
        from scenarios.fanatics.services.auction_engine import AuctionEngineService
        from scenarios.fanatics.services.packaging_fulfillment import PackagingFulfillmentService
        from scenarios.fanatics.services.wifi_controller import WifiControllerService
        from scenarios.fanatics.services.cloud_inventory_scanner import CloudInventoryScannerService
        from scenarios.fanatics.services.network_controller import NetworkControllerService
        from scenarios.fanatics.services.firewall_gateway import FirewallGatewayService
        from scenarios.fanatics.services.dns_dhcp_service import DnsDhcpService

        return [
            CardPrintingSystemService,
            DigitalMarketplaceService,
            AuctionEngineService,
            PackagingFulfillmentService,
            WifiControllerService,
            CloudInventoryScannerService,
            NetworkControllerService,
            FirewallGatewayService,
            DnsDhcpService,
        ]

    # ── Fault Parameters ──────────────────────────────────────────────

    def get_fault_params(self, channel: int) -> dict[str, Any]:
        return {
            # ── Network core (channels 1-3) ──
            "mac_address": f"{random.randint(0,255):02x}:{random.randint(0,255):02x}:{random.randint(0,255):02x}:{random.randint(0,255):02x}:{random.randint(0,255):02x}:{random.randint(0,255):02x}",
            "interface_src": random.choice(["Gi0/0/1", "Gi0/0/2", "Gi0/0/3", "Te1/0/1", "Te1/0/2"]),
            "interface_dst": random.choice(["Gi0/0/4", "Gi0/0/5", "Te1/0/3", "Te1/0/4"]),
            "interface": random.choice(["Gi0/0/1", "Gi0/0/2", "Te1/0/1", "Te1/0/2", "Po1"]),
            "vlan_id": random.choice([100, 200, 300, 400, 500, 1000]),
            "flap_count": random.randint(10, 50),
            "flap_window": random.randint(5, 30),
            "stp_instance": random.randint(0, 15),
            "tc_count": random.randint(15, 80),
            "tc_window": random.randint(10, 60),
            "bridge_id": f"8000.{random.randint(0,255):02x}{random.randint(0,255):02x}.{random.randint(0,255):02x}{random.randint(0,255):02x}.{random.randint(0,255):02x}{random.randint(0,255):02x}",
            "bgp_peer_ip": f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
            "bgp_peer_as": random.choice([64512, 64513, 64514, 65001, 65002, 65100]),
            "bgp_flap_count": random.randint(5, 25),
            "bgp_flap_window": random.randint(30, 300),
            "bgp_last_state": random.choice(["Idle", "Active", "OpenSent", "OpenConfirm"]),
            "bgp_notification": random.choice([
                "Hold Timer Expired (code 4/0)",
                "Cease/Admin Reset (code 6/4)",
                "UPDATE Message Error (code 3/1)",
                "FSM Error (code 5/0)",
            ]),

            # ── Security (channels 4-6) ──
            "session_count": random.randint(58000, 63500),
            "session_max": 64000,
            "session_util_pct": round(random.uniform(90.0, 99.5), 1),
            "session_drops": random.randint(50, 500),
            "fw_zone": random.choice(["TRUST", "UNTRUST", "DMZ"]),
            "top_source_ip": f"10.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
            "fw_dp_cpu_pct": round(random.uniform(85.0, 99.0), 1),
            "fw_mgmt_cpu_pct": round(random.uniform(60.0, 90.0), 1),
            "fw_cpu_threshold": 80,
            "fw_buffer_pct": round(random.uniform(75.0, 98.0), 1),
            "fw_policy_count": random.randint(800, 2500),
            "cert_cn": random.choice([
                "*.fanatics.internal", "forward-proxy.fanatics.com",
                "ssl-inspect.collectibles.prod", "tls-decrypt.warehouse.local",
            ]),
            "cert_serial": f"{random.randint(100000,999999):X}",
            "cert_days_remaining": random.randint(-5, 3),
            "cert_profile": random.choice(["ssl-forward-proxy", "ssl-inbound-inspection", "tls-decrypt-all"]),
            "cert_affected_rules": random.randint(15, 80),

            # ── Network access (channels 7-9) ──
            "ap_name": random.choice([
                "AP-WAREHOUSE-01", "AP-WAREHOUSE-02", "AP-PRINT-FLOOR-01",
                "AP-OFFICE-01", "AP-SHIPPING-01", "AP-DOCK-01",
            ]),
            "ap_site": random.choice(["warehouse-east", "print-facility", "office-hq", "shipping-dock"]),
            "ap_disconnect_count": random.randint(5, 20),
            "ap_disconnect_window": random.randint(10, 60),
            "ap_last_heartbeat": random.randint(30, 300),
            "channel_number": random.choice([1, 6, 11, 36, 40, 44, 48, 149, 153, 157, 161]),
            "interference_pct": round(random.uniform(25.0, 75.0), 1),
            "noise_floor_dbm": round(random.uniform(-80.0, -60.0), 1),
            "retransmit_pct": round(random.uniform(10.0, 40.0), 1),
            "neighbor_ap_count": random.randint(5, 20),
            "auth_requests_per_sec": random.randint(200, 1000),
            "auth_threshold": 100,
            "auth_failures": random.randint(50, 300),
            "auth_timeouts": random.randint(20, 150),
            "radius_nas_ip": f"10.1.{random.randint(1,10)}.{random.randint(1,254)}",
            "radius_server": random.choice(["radius-01.fanatics.internal", "radius-02.fanatics.internal"]),

            # ── Network services (channels 10-11) ──
            "dns_query_name": random.choice([
                "marketplace.fanatics.internal", "auction-api.collectibles.prod",
                "card-printer-01.warehouse.local", "inventory.cloud-ops.internal",
            ]),
            "dns_query_type": random.choice(["A", "AAAA", "CNAME", "SRV"]),
            "vpn_tunnel_name": random.choice(["aws-to-azure-01", "aws-to-gcp-01", "gcp-to-azure-01"]),
            "dns_rcode": random.choice(["SERVFAIL", "REFUSED", "NXDOMAIN"]),
            "dns_forwarder_ip": random.choice(["10.0.0.53", "10.1.0.53", "168.63.129.16"]),
            "dns_fallback_ip": random.choice(["10.0.1.53", "10.2.0.53"]),
            "dns_timeout_ms": random.randint(3000, 10000),
            "dhcp_scope": random.choice(["10.1.0.0/24", "10.2.0.0/24", "172.16.0.0/22", "192.168.1.0/24"]),
            "dhcp_util_pct": round(random.uniform(92.0, 100.0), 1),
            "dhcp_active_leases": random.randint(235, 254),
            "dhcp_total_leases": 254,
            "dhcp_discover_rate": random.randint(50, 300),
            "dhcp_nak_count": random.randint(10, 100),
            "dhcp_rogue_ip": f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",

            # ── Commerce (channels 12-14) ──
            "auction_id": f"AUC-{random.randint(100000,999999)}",
            "bid_id": f"BID-{random.randint(1000000,9999999)}",
            "bid_latency_ms": random.randint(500, 5000),
            "bid_sla_ms": 200,
            "bid_queue_depth": random.randint(100, 2000),
            "ws_delay_ms": random.randint(200, 3000),
            "affected_bidders": random.randint(10, 500),
            "order_id": f"ORD-{random.randint(100000,999999)}",
            "payment_provider": random.choice(["Stripe", "PayPal", "Adyen", "Braintree"]),
            "payment_timeout_ms": random.randint(5000, 30000),
            "gateway_response_code": random.choice(["504", "408", "429", "503"]),
            "payment_retry_count": random.randint(1, 3),
            "payment_max_retries": 3,
            "payment_amount": round(random.uniform(9.99, 4999.99), 2),
            "catalog_sync_failed": random.randint(50, 500),
            "catalog_sync_total": random.randint(1000, 5000),
            "catalog_source": random.choice(["card-printing-system", "product-master"]),
            "catalog_destination": random.choice(["digital-marketplace", "auction-engine"]),
            "catalog_last_sync_min": random.randint(30, 360),
            "catalog_error_detail": random.choice([
                "connection reset by peer",
                "schema version mismatch",
                "primary key conflict on sku column",
                "timeout waiting for lock on products table",
            ]),

            # ── Manufacturing (channels 15-16) ──
            "print_queue_depth": random.randint(450, 500),
            "print_queue_max": 500,
            "print_queue_pct": round(random.uniform(90.0, 100.0), 1),
            "print_job_id": f"PJ-{random.randint(10000,99999)}",
            "print_oldest_job_min": random.randint(30, 480),
            "printer_name": random.choice(["HP-Indigo-7K-01", "HP-Indigo-7K-02", "Koenig-Bauer-01", "Heidelberg-XL-01"]),
            "printer_status": random.choice(["PAPER_JAM", "INK_LOW", "OFFLINE", "HEAD_CLOG"]),
            "qc_reject_count": random.randint(20, 150),
            "qc_inspected_count": random.randint(500, 2000),
            "qc_reject_pct": round(random.uniform(5.0, 25.0), 1),
            "qc_threshold_pct": 2.0,
            "qc_defect_type": random.choice([
                "color_registration_shift", "die_cut_misalignment",
                "foil_stamp_incomplete", "surface_scratch", "centering_off",
            ]),
            "qc_batch_id": f"BATCH-{random.randint(1000,9999)}",
            "qc_line_number": random.choice(["LINE-A", "LINE-B", "LINE-C"]),

            # ── Logistics (channels 17-18) ──
            "label_printer_id": random.choice(["ZBR-SHIP-01", "ZBR-SHIP-02", "ZBR-DOCK-01"]),
            "label_printer_status": random.choice(["OFFLINE", "PAPER_OUT", "HEAD_ERROR", "RIBBON_EMPTY"]),
            "label_error_code": random.choice(["E1001", "E2003", "E3005", "E4002"]),
            "label_failed_count": random.randint(10, 100),
            "label_window_min": random.randint(5, 30),
            "label_carrier": random.choice(["UPS", "FedEx", "USPS", "DHL"]),
            "label_queue_depth": random.randint(50, 500),
            "scanner_id": random.choice(["SCN-WH-01", "SCN-WH-02", "SCN-WH-03", "SCN-DOCK-01"]),
            "scanner_zone": random.choice(["receiving", "storage-A", "storage-B", "packing", "shipping"]),
            "scanner_last_sync_sec": random.randint(120, 600),
            "scanner_sync_max_sec": 60,
            "scanner_missed_scans": random.randint(20, 200),
            "inventory_delta": random.randint(5, 50),
            "scanner_firmware": random.choice(["3.2.1", "3.1.8", "3.0.5"]),

            # ── Cloud ops (channels 19-20) ──
            "cloud_resource_type": random.choice(["EC2 Instance", "Azure VM", "GCE Instance", "EBS Volume", "Managed Disk", "S3 Bucket"]),
            "cloud_resource_id": f"res-{random.randint(10000,99999)}",
            "cloud_resource_provider": random.choice(["aws", "azure", "gcp"]),
            "cloud_resource_region": random.choice(["us-east-1", "eastus", "us-central1"]),
            "cloud_resource_age_days": random.randint(14, 180),
            "cloud_resource_cost_daily": round(random.uniform(2.50, 85.00), 2),
            "cloud_resource_sg": random.choice(["sg-0abc1234", "nsg-fanatics-default", "fw-rule-legacy"]),
            "vpn_src_cloud": random.choice(["aws", "gcp"]),
            "vpn_dst_cloud": random.choice(["azure", "gcp"]),
            "vpn_flap_count": random.randint(5, 30),
            "vpn_flap_window": random.randint(60, 600),
            "vpn_current_state": random.choice(["DOWN", "NEGOTIATING", "REKEYING"]),
            "vpn_ike_phase": random.choice(["1", "2"]),
            "vpn_ike_status": random.choice(["FAILED", "TIMEOUT", "SA_EXPIRED"]),
            "vpn_last_dpd_sec": random.randint(30, 300),
        }


# Module-level instance for registry discovery
scenario = FanaticsScenario()
