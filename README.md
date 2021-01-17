# Raman spectroscopy

This is a project for Raman spectrum recognition.

## Base URL

```json
https://api.sitraman.com/v1
```

## Authentication

Authentication via api key is required for all destructive routes. This includes all `create`, `update`, and `delete` routes.

Authenticate by passing the header `spacex-key` with your api key. Protected routes return `401` without a valid key.

## Pagination + Custom Queries

`/query` routes support pagination, custom queries, and other output controls.

See the pagination + query guide for more details and examples.

## Launch date FAQ's

## Launch date field explanations

## Routes

🔒 = Requires Auth

## Usage

GET string => json.load

POST form-data => `application/json`

```python
import json, requests
data = requests.get('api.sitraman.com/v1/sepctrums').text
data = json.load(data)
x = data['x']
y = data['y']

smoothed = requests.post('api.sitraman.com/v1/processing/smooth', data=data)
```

## Caching

The api makes use of response caching via Redis for all `GET` requests, and `POST` requests on `/query` endpoints.

Standard cache times are as follows:

Cache can be cleared with the following endpoint:

🔒 Clear cache : `DELETE /admin/cache`

## API

### Spectrum

Detailed info about spectrum

-   Get all spectrum : `GET /sepctrums`

-   Get one spectrum: `GET /spectrum/:id`

-   Query spectrum: `GET /spectrum/query`

-   🔒 Create a spectrum: `POST /spectrum`

-   🔒 Update a spectrum: `PUT /spectrum/:id`

-   🔒 Delete a spectrum: `DELETE /spectrum/:id`

```json
{
  "data": {
    "x": [
      -89.568, -86.697, -83.828, -80.96, -78.095, -75.232, -72.37, -69.511, -66.654, -63.798
      ...
    ],
    "y":[
      -1.51, 2.52, 1.51, 5.54, 6.55, 11.58, 6.55, 11.58, 6.55, 13.6
      ...
    ],
    "name": "Trichloromethane",
    "CAS": "67-66-3",
    ...
  }
}
```

### Processing

Detailed info about processing

-   Query processing: `PUT /processing/query/:id`
-   Remove baseline processing: `PUT processing/autbaseline/:id`
-   Smooth processing: `PUT processing/smooth/:id`
-   search_peaks processing: `PUT processing/search_peaks/:id`
-   interpolation processing: `PUT processing/interpolate:id`
-   remove_duplication processing: `PUT processing/rmdup/:id`

### Clasification

Detailed info about clasification

-   compare_unknown_to_known: `PUT /clasification/compare_unknown_to_known/:id`

### terminal

> package

`$pip install -r requirements.txt`

> entry

`export FLASK_APP=app.py`

> reload

`export FLASK_ENV=development`
