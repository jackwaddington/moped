from prometheus_client import Counter, Gauge

# Counter: only goes up. Good for "how many times did X happen?"
sync_operations_total = Counter(
    "moped_sync_operations_total",
    "Total number of Google Sheets sync operations",
    ["status"],  # label: "success" or "error"
)

# Gauge: can go up or down. Good for "what is the current value of X?"
entries_synced_last = Gauge(
    "moped_entries_synced_last",
    "Number of entries synced in the last sync operation",
)

km_until_service = Gauge(
    "moped_km_until_service",
    "Kilometers remaining until next service",
    ["service_type"],
)
