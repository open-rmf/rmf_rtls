# rmf_rtls

rmf realtime location system. This server provides a common coordinate system for multiple vendored RTLS-s.
Systems can provide or retrieve tags information and map transfromation by interacting the endpoints of RTLS server.
The `rtls_server` persists all tagstates and transformation informaiton in a databad, and can scale horizontally.

> Still work in progress

Roadmap:
The location information of rtls tags could enable certain features in RMF core. These features include:

1.  block congested lanes
2.  update tag as "readonly" robot
3.  ...

## Available APIs Endpoints

- `/open-rmf/rtls/map_transformation`
  - POST and GET method
- `/open-rmf/rtls/tag_state`
  - POST and GET method

## Configurations

- IP and port number
- ORM database

## Run it

Installation

```bash
pip3 install tortoise-orm fastapi uvicorn
```

Run the server

```bash
ros2 run rmf_rtls rmf_rtls_server
```

- Endpoins: http://0.0.0.0:8080/docs
- *.sqlite3 will be created when server is running.
