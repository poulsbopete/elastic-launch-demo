# Thermal Calibration Drift — Root Cause Analysis Guide

## Overview

Thermal Calibration Drift (Channel 1) occurs when engine bay thermal sensors report calibration values that deviate beyond the acceptable threshold of 2.5K from the baseline reference. This anomaly is detected by the `ThermalCalibrationException` error type on `thermal` sensors in the `engine_bay` vehicle section.

## Error Signature

- **Error Type**: `ThermalCalibrationException`
- **Sensor Type**: `thermal`
- **Vehicle Section**: `engine_bay`
- **Affected Services**: fuel-system (AWS us-east-1), sensor-validator (Azure eastus)
- **Cascade Services**: mission-control (AWS us-east-1), range-safety (Azure eastus)

## Subsystem Context

The propulsion subsystem thermal sensors in the engine bay continuously measure temperatures at critical points around the main engine and fuel injectors. Calibration baselines are established during pre-launch sensor checkout and stored in the calibration store. The sensor-validator service (running on Azure) periodically verifies that live readings remain within calibration tolerance.

## Common Root Causes

### 1. Environmental Thermal Gradient
**Probability**: High
**Description**: Rapid ambient temperature changes at the launch pad (e.g., sun exposure transition, weather front) cause the physical sensor housing to expand or contract, shifting the calibration reference point.
**Diagnostic Steps**:
- Check weather station data (Channel 15) for temperature changes in the past 30 minutes
- Compare multiple thermal sensors in the engine bay for correlated drift patterns
- Verify if the drift is unidirectional (all sensors drifting the same way) or random

### 2. Calibration Epoch Stale
**Probability**: Medium
**Description**: The calibration baseline was generated too long ago and no longer reflects current sensor characteristics. This is especially common when launch is delayed.
**Diagnostic Steps**:
- Check calibration epoch (Channel 18) for the affected sensor
- Verify time delta between calibration epoch and current time
- Look for `CalibrationEpochException` events that may indicate a broader calibration staleness issue

### 3. Sensor Hardware Degradation
**Probability**: Low
**Description**: Physical degradation of the thermocouple or RTD element, typically due to vibration exposure during transport or handling.
**Diagnostic Steps**:
- Check if the drift is isolated to a single sensor or multiple sensors
- Review vibration data (Channel 11) for unusual mechanical stress events
- Compare affected sensor readings against redundant sensors in the same zone

### 4. Cross-Cloud Latency Artifact
**Probability**: Low
**Description**: When the telemetry relay between AWS (where fuel-system runs) and Azure (where sensor-validator runs) experiences high latency (Channel 12), calibration comparisons may use stale baseline values.
**Diagnostic Steps**:
- Check relay latency metrics for the AWS-Azure path
- Look for `RelayLatencyException` events in the same time window
- Verify if the calibration drift resolves when relay latency normalizes

## Remediation Procedures

### Immediate Actions
1. **Verify with redundant sensors**: Compare the drifting sensor against at least two independent sensors in the same engine bay zone. If redundant sensors agree, the anomaly is confirmed.
2. **Check calibration age**: If calibration epoch is more than 24 hours old, initiate a fresh calibration cycle.
3. **Monitor trend**: Determine if the drift is increasing, stable, or recovering. Increasing drift at rate > 0.5K/minute warrants escalation.

### Corrective Actions
1. **Reset pipeline**: Use the `reset_pipeline` remediation action to reset the processing pipeline and re-establish calibration baselines against the known reference temperature.
2. **Update calibration epoch**: After recalibration, verify the new epoch is recorded correctly.
3. **Validate cross-cloud path**: Confirm sensor-validator is receiving timely data from the fuel-system service.

### Escalation Criteria
- Drift exceeds 5.0K: Escalate to launch director
- Multiple sensors drifting simultaneously: Potential systemic issue, request hold
- Drift correlating with fuel pressure anomalies (Channel 2): Potential engine pre-ignition thermal event, immediate hold

## Historical Precedents

### NOVA-5 T-45:00 Thermal Drift Event
During the NOVA-5 countdown, thermal sensors in zone B of the engine bay reported calibration drift of 4.2K. Root cause was determined to be solar heating of the sensor housing after the mobile service tower was retracted. Resolution: sensors were recalibrated with adjusted baseline accounting for solar load. Countdown resumed after 8-minute hold.

### NOVA-6 Calibration Store Corruption
A software bug in the calibration store caused incorrect baseline values to be loaded for thermal sensors after a service restart. All engine bay sensors showed simultaneous drift of exactly 3.1K. Resolution: calibration store was flushed and reloaded from the pre-launch reference dataset.

## Related Channels
- Channel 2: Fuel Pressure Anomaly (propulsion subsystem correlation)
- Channel 3: Oxidizer Flow Rate Deviation (engine bay thermal dependency)
- Channel 12: Cross-Cloud Relay Latency (data freshness dependency)
- Channel 18: Calibration Epoch Mismatch (calibration infrastructure)
