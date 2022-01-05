# Copyright 2022 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import sys
import argparse

from typing import Optional, List

import json
from jsonschema import validate

# rmf api deps
from rmf_api_msgs import schemas
from rmf_api_msgs.models import rtls_tag_state, transformation_2D
# import rmf_adapter as adpt
# import rmf_adapter.vehicletraits as traits

# web server
import uvicorn
from fastapi import FastAPI

from pydantic import BaseModel

# ORM
import rmf_rtls.database as db

app = FastAPI()

tag_state_schema = schemas.rtls_tag_state()
RtlsTagStateModel = rtls_tag_state.RtlsTagState
Transformation2DModel = transformation_2D.Transformation2D

###############################################################################


class rmf_rtls:
    def __init__(self):
        # TODO: impl of rmf_feature_lib
        pass

    # Set Tag State
    @app.post('/open-rmf/rtls/tag_state')
    async def update_tag_state(dest: RtlsTagStateModel):
        tag_state_orm = db.RtlsTagState.from_pydantic(dest)
        return await tag_state_orm.save()

    # Get Matching Tag States
    @app.get('/open-rmf/rtls/tag_state/',
             response_model=List[RtlsTagStateModel])
    async def get_tag_state(
        tag_id: Optional[str] = None,
        asset_type: Optional[str] = None,
        asset_subtype: Optional[str] = None,
    ):
        # TODO: return array or more
        tag_states = await db.TtmRtlsTagState.get_or_none(
            id=tag_id,
            asset_type=asset_type,
            asset_subtype=asset_subtype
        )
        if tag_states is None:
            return None
        return [db.RtlsTagState.from_ttm(tag_states)]

    # Set Map Transformation
    @app.post('/open-rmf/rtls/map_transformation/')
    async def update_map_transformation(dest: Transformation2DModel):
        tf_2d_orm = db.Transformation2D.from_pydantic(dest)
        return await tf_2d_orm.save()

    # Get Map Transformation
    @app.get('/open-rmf/rtls/map_transformation/',
             response_model=Transformation2DModel)
    async def get_map_transformation(
        target_map: str,
        ref_map: str = None  # TODO: will need to construct a tf tree
    ):
        tf_2d = await db.TtmTransformation2D.get_or_none(id=target_map)
        if tf_2d is None:
            return None
        print(f"Return tf_2d query of: {id}")
        return db.Transformation2D.from_ttm(tf_2d)


###############################################################################


def main(argv=sys.argv):
    print("Init rmf rtls server...")
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--host_address', default="0.0.0.0",
                        type=str, help='host address, default 0.0.0.0')
    parser.add_argument('-p', '--port', default="8080",
                        type=str, help='port number, default 8080')
    args = parser.parse_args(argv[1:])

    print(" Run RTLS Server...")

    db.setup_database(app)

    uvicorn.run(app,
                host=args.host_address,
                port=args.port,
                log_level='warning')


###############################################################################
if __name__ == '__main__':
    main(sys.argv)