# rmf_rtls

Web-based rmf realtime location system. This service provides a common coordinate system and agnostic RLTS data format for different vendored RTL-systems.

Vendored RTLS-s can provide or retrieve tags information and map transfromation by interacting the endpoints of RTLS server.

The `rtls_server` persists all tag states and map transformations in a database.

> Still work in progress

## Available REST APIs Endpoints

- `/open-rmf/rtls/map_transformation`
  - POST and GET method
- `/open-rmf/rtls/tag_state`
  - POST and GET method

## Configurations

- IP and port number
- ORM database

## Run it

Installation

Dependencies: 
 - [rmf_api_msgs](https://github.com/open-rmf/rmf_api_msgs)

```bash
pip3 install tortoise-orm fastapi uvicorn
```

Run the server

```bash
ros2 run rmf_rtls rmf_rtls_server
```

- Endpoins: http://0.0.0.0:8085/docs
- *.sqlite3 will be created when server is running.

## WishList

Roadmap:
The location information of rtls tags could enable certain features in RMF core. These features include:

1.  block congested lanes
2.  update tag as "readonly" robot
3.  ...

Others:
 - enable specify operating boundary with `rmf_traffic_editor`, web hook to trigger
