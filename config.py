# config.py
SETTINGS = {
    "n_points": 600,
    "contamination": 0.02,
    "random_seed": 42,
    "features": ['bandwidth_mbps', 'latency_ms', 'packet_loss_pct'],
    "thresholds": {
        "bandwidth_multiplier": 1.8,
        "latency_spike": 80,
        "packet_loss_spike": 5.0
    }
}