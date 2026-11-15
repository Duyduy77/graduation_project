# WordSpeak ten-sound MVP

Current app: http://127.0.0.1:8013/demo

Open OPEN_WORDSPEAK.url from the project root. If offline, run START_WORDSPEAK.cmd.

Full guide: [Ten-sound MVP](../docs/TEN_SOUND_MVP.md).

Handoff and validation: [MVP handoff](../docs/MVP_HANDOFF.md).

Earlier three-sound prototype ports 8011/8012 are obsolete.

## Integration with the backend

This branch adds the local `/demo` workflow. `/demo/analyze` returns provisional
sound categories and a null score; it does not return the backend's `Assessment`
schema. The old fabricated-score `/assess` stub now returns HTTP 501, and this
development MVP does not implement `/transcribe`. The backend's Talk/assessment
integration therefore still needs real transcription and validated scoring.
Its existing unavailable-service handling should be retained.

The shared OpenAPI contract preserves the backend endpoints, JWT definitions and
Assessment schema from current main while documenting the demo and retired stub.
Dataset preparation scripts are included; recordings, model weights, local
environment packages, runtime tokens and generated reports remain local.
