# API

## `GET /api/health`
Returns service health and active inference mode.

## `POST /api/detect/image`
Accepts multipart form-data with `file`.

## `POST /api/detect/video`
Accepts multipart form-data with `file`.

## `GET /api/history`
Returns summary metrics and persisted scan history.

## `DELETE /api/history/{id}`
Deletes one stored detection item.

## `GET /api/report/{id}`
Generates and downloads a PDF report.

