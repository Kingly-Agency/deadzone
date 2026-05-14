import asyncio
from datetime import datetime, timedelta, timezone
from app.runtime.engine import DeadZoneEngine
from app.settings import load_settings
from app.sources.ble import normalize_ble_advertisement

def seed_demo_trace():
    engine = DeadZoneEngine(load_settings())
    trace_id = "demo-trace-1"
    base = datetime.now(timezone.utc)
    
    import random
    rng = random.Random(42)
    
    # Generate 50 devices
    devices = [f"AA:BB:CC:DD:EE:{i:02d}" for i in range(50)]
    
    print("Generating demo trace...")
    for offset_s in range(60):  # 60 seconds of data
        for device in devices:
            if rng.random() > 0.3:  # 70% chance to be seen each second
                rssi = rng.randint(-90, -45)
                engine.store.append(
                    trace_id,
                    normalize_ble_advertisement(
                        raw_identifier=device,
                        rssi=rssi,
                        receiver_id="local-ble-scanner",
                        trace_id=trace_id,
                        salt=engine.config().venue.id,
                        timestamp=base + timedelta(seconds=offset_s),
                    ),
                )
    print(f"Generated demo trace: {trace_id}")

if __name__ == "__main__":
    seed_demo_trace()
