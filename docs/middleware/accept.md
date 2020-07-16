---
id: accept
sidebar_label: Accept
hide_title: true
---
# Accept

Sets `Content-Type` in request.

## Usage

```py
from hs_formation.middleware import accept

@client
class Google(object):
    base_uri = "https://google.com"
    middleware=[
        accept('application/json')
    ]
    ...
```
