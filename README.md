# Machine Vision

Machine Vision is a smart-home security analytics layer built around Frigate-generated person tracking. It does not run a second object detector. Instead, it listens for Frigate events, maintains tracks, applies spatial rules, detects suspicious behavior, and emits structured JSON events for downstream automation.

## What this project does

- ingests person-tracking events over a REST API
- normalizes Frigate payloads into an internal observation model
- tracks people across time and camera events
- detects zone entry and restricted-area activity
- detects line crossings for entrances and exits
- identifies dwell and loitering
- detects tailgating behind an authorized person
- enriches identity with an optional CompreFace adapter
- emits structured `VisionEvent` payloads to a configured REST endpoint

## Architecture

```text
Camera
  │
  ▼
Frigate (YOLO + tracking)
  │
  ▼
REST API: /api/events
  │
  ▼
Machine Vision
  ├─ Frigate normalizer
  ├─ Track manager
  ├─ Zone logic
  ├─ Line-crossing logic
  ├─ Loitering / dwell logic
  ├─ Tailgating logic
  ├─ Identity adapter
  ├─ Incident/context engine
  └─ VisionEvent generation
        │
        ▼
REST API: /api/v1/observations or any configured output URL
```

Important: this service expects Frigate to do the actual person detection and tracking. It is the decision layer, not the ML detector itself.

## Repository layout

```text
.
├── README.md
├── requirements.txt
├── .env
├── .env.example
├── Dockerfile
├── config/
│   ├── cameras.yaml
│   ├── thresholds.yaml
│   └── zones.yaml
├── data/
│   ├── logs/
│   ├── snapshots/
│   └── test_videos/
├── docker/
│   └── docker-compose.yml
├── src/
│   ├── __init__.py
│   ├── demo.py
│   ├── main.py
│   ├── pipeline.py
│   ├── config.py
│   ├── behavior/
│   │   ├── dwell_time.py
│   │   ├── loitering.py
│   │   └── tailgating.py
│   ├── context/
│   │   └── incident_manager.py
│   ├── events/
│   │   ├── event_generator.py
│   │   └── restapi_publisher.py
│   ├── identity/
│   │   └── compreface.py
│   ├── ingestion/
│   │   ├── frigate_listener.py
│   │   └── normalizer.py
│   ├── models/
│   │   ├── identity.py
│   │   ├── incident.py
│   │   ├── track.py
│   │   └── vision_event.py
│   └── spatial/
│       ├── line_crossing.py
│       ├── trajectory.py
│       └── zones.py
├── tests/
│   ├── conftest.py
│   ├── test_events.py
│   ├── test_line_crossing.py
│   ├── test_loitering.py
│   ├── test_tailgating.py
│   ├── test_zones.py
│   └── test_pipeline.py
└── .gitignore
```

## Setup

### 1) Install Python dependencies

```bash
cd /workspaces/machine_vision
python -m pip install -r requirements.txt
```

If your Linux environment is missing OpenCV runtime libraries, install them:

```bash
sudo apt-get update
sudo apt-get install -y libgl1
```

### 2) Copy environment settings

```bash
cp .env.example .env
```

A typical `.env` includes:

```env
RESTAPI_URL=http://localhost:8000
RESTAPI_API_KEY=
FRIGATE_URL=http://localhost:5000
LOITER_THRESHOLD_SECONDS=30
TAILGATE_WINDOW_SECONDS=3
COMPREFACE_URL=http://localhost:8000
COMPREFACE_API_KEY=demo-key
COMPREFACE_MIN_SIMILARITY=0.80
```

## Quick start

### Run the offline demo

This is the fastest way to validate that the system runs end-to-end without a live camera or Frigate instance.

```bash
cd /workspaces/machine_vision
python src/demo.py
```

You can also use the main entry point:

```bash
cd /workspaces/machine_vision
python src/main.py --demo
```

The demo simulates person tracks and emits JSON events such as:

- `person.tracked`
- `person.entered_zone`
- `person.line_crossed`
- `person.tailgating_detected`
- `person.loitering`

### Run the automated tests

```bash
cd /workspaces/machine_vision
pytest -q
```

This project includes behavioral tests for:

- zones
- line crossings
- loitering
- tailgating
- event generation
- end-to-end pipeline behavior

### Start the REST API locally

```bash
cd /workspaces/machine_vision/docker
docker compose up -d
```

Then run the service:

```bash
cd /workspaces/machine_vision
python src/main.py --rest
```

## Configuration

### Cameras and zones

The project uses YAML definitions in `config/`.

Example zone configuration:

```yaml
zones:
  entrance:
    polygon:
      - [100, 100]
      - [700, 100]
      - [700, 500]
      - [100, 500]

  restricted_area:
    polygon:
      - [250, 150]
      - [650, 150]
      - [650, 450]
      - [250, 450]
```

Example entrance line configuration:

```yaml
entrances:
  front_door:
    line:
      - [350, 100]
      - [350, 500]
```

## Frigate integration

Frigate is the expected upstream detector and tracker. This service polls the Frigate REST API and treats those payloads as person observations. In practice, your flow is:

```text
Camera -> Frigate REST API -> Machine Vision -> policy / automation layer
```

The code keeps a clean separation between:

- Frigate-specific payloads
- internal track/state logic
- downstream event schema

This avoids hard coupling to a specific detection stack.

## CompreFace integration

The project includes an adapter for CompreFace in `src/identity/compreface.py`. If the identity service is unavailable, the system falls back gracefully rather than crashing.

## Event model

All emitted alerts are structured as `VisionEvent` objects with fields such as:

- `event_type`
- `camera`
- `track_id`
- `zone`
- `identity`
- `identity_status`
- `confidence`
- `metadata`

These are serialized as JSON and sent to the configured REST output endpoint.

## Notes

- This project is not a webcam app.
- It is not a replacement for Frigate detection.
- It is a security analytics and decision layer built on top of tracking data.

## Verification

The project has been validated in this workspace with:

```bash
pytest -q
```

and the offline demo:

```bash
python src/demo.py
```

Both completed successfully in the current environment.

Example:

```json
{
  "event_id": "...",
  "event_type": "person.tailgating_detected",
  "timestamp": "2024-01-01T10:00:01.400000Z",
  "camera": "front_door",
  "track_id": "42",
  "zone": "entrance",
  "identity": "Rahul",
  "identity_status": "KNOWN",
  "identity_confidence": 0.94,
  "confidence": 0.95,
  "metadata": {
    "authorized_person": "41",
    "time_gap": 1.4,
    "risk": "HIGH"
  }
}
```

## Testing

```bash
cd /workspaces/machine_vision
pytest -q
```

## Docker usage

```bash
cd /workspaces/machine_vision/docker
docker compose up --build
```

This starts the REST API service and can connect to Frigate and CompreFace from other containers on the same Docker network.

## Troubleshooting

- Import errors: ensure the workspace root is on the Python path and the project dependencies are installed.
- OpenCV import failure: install `libgl1` on Linux hosts.
- REST endpoint unavailable: verify `FRIGATE_URL` and `RESTAPI_URL` values and confirm the upstream services are reachable.
- CompreFace unavailable: the adapter intentionally returns `UNKNOWN` instead of crashing the pipeline.
- Malformed Frigate events: the normalizer is defensive and ignores invalid payloads gracefully.

## Important boundary

This framework is intentionally focused on detection and reasoning. It does not decide policy actions. The Policy Agent receives the `VisionEvent` stream and decides whether to alert, lock a door, escalate, or ignore an incident.
