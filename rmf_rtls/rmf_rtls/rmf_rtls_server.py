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

# web server
import uvicorn
from fastapi import FastAPI

# ORM interface
import rmf_rtls.database as db
import rmf_rtls.utils as utils

from pydantic import BaseModel, Field, parse_obj_as

app = FastAPI()

tag_state_schema = schemas.rtls_tag_state()
RtlsTagStateModel = rtls_tag_state.RtlsTagState
Transformation2DModel = transformation_2D.Transformation2D


###############################################################################
class RtlsTagStatesResponse(BaseModel):
    success: bool
    response: str = Field(
        ..., description='response msg'
    )
    data: Optional[List[RtlsTagStateModel]] = Field(
        None, description='rtls tag states data if avail'
    )


class Transfromation2DResponse(BaseModel):
    success: bool
    response: str = Field(
        ..., description='response msg'
    )
    data: Optional[Transformation2DModel] = Field(
        None, description='transformation of 2 maps if avail'
    )


###############################################################################

@app.post('/open-rmf/rtls/tag_state')
async def update_tag_state(dest: RtlsTagStateModel):
    """
    Set Tag States
    """
    tag_state_orm = db.RtlsTagState.from_pydantic(dest)
    return await tag_state_orm.save()


@app.get('/open-rmf/rtls/tag_state/',
         response_model=RtlsTagStatesResponse)
async def get_tag_state(
    tag_id: Optional[str] = None,
    asset_type: Optional[str] = None,
    asset_subtype: Optional[str] = None,
):
    """
    Get matching tag states
    """
    # remove all input args Keys that contain None value
    filter_params = {k: v for k, v in locals().items() if v is not None}
    # raw way to convert pk to commmon name: 'id'
    if "tag_id" in filter_params:
        filter_params['id'] = filter_params.pop("tag_id")
    print("filter parasms ::", filter_params)

    tag_states = await db.TtmRtlsTagState.filter(**filter_params)
    return RtlsTagStatesResponse(
        success=True,
        response="Successfully query matching tag states",
        data=[db.RtlsTagState.from_ttm(t) for t in tag_states]
    )


@app.post('/open-rmf/rtls/map_transformation/')
async def update_map_transformation(dest: Transformation2DModel):
    """
    Set map transformation
    """
    # TODO: a check to ensure each: target_map is unique
    tf_2d_orm = db.Transformation2D.from_pydantic(dest)
    return await tf_2d_orm.save()


@app.get('/open-rmf/rtls/map_transformation/',
         response_model=Transfromation2DResponse)
async def get_map_transformation(
    target_map: str,
    ref_map: str
):
    """
    Get map transformation
    """
    tf_2d = await db.TtmTransformation2D.get_or_none(
        id=target_map, ref_map=ref_map)

    # If the input ref and target map is directly avail in db field
    if tf_2d is not None:
        print(f"Return tf_2d query of: {target_map} from {ref_map}")
        tf_data = db.Transformation2D.from_ttm(tf_2d)

        return Transfromation2DResponse(
            success=True,
            response="Successfully query transformation",
            data=tf_data)

    # Need to find the transformation by checking the tf tree
    tf_data = await find_transformation(ref_map, target_map)
    if tf_data is None:
        return Transfromation2DResponse(
            success=False,
            response=f"Transformtion between {target_map} from {ref_map}"
            f" is not avail")

    return Transfromation2DResponse(
        success=True,
        response="Successfully query and calc transformation",
        data=tf_data)


###############################################################################


async def tf_tree_bfs(
    ref_map: str,
    target_map: str
) -> List[db.TtmTransformation2D]:
    """
    Use breadth first search to search for the transformation between 2 maps.
    will return the tf tree from the ref_map to target_map
    """
    # maintain a queue of paths
    tf_tree_queue = [[]]
    queue = []
    queue.append([ref_map])
    # push the first path into the queue
    while queue:
        # get the first path from the queue
        path = queue.pop(0)
        tf_tree = tf_tree_queue.pop(0)
        # get the last node from the path
        node = path[-1]
        if node == target_map:
            # print(" [DEBUG] Found map tf tree path: ", path)  # For debug
            return tf_tree
        # enumerate all adjacent nodes, construct a
        # new path/tree list and push it into the queue
        target_tfs = await db.TtmTransformation2D.filter(ref_map=node)
        for adjacent in target_tfs:
            queue.append(path + [adjacent.id])
            tf_tree_queue.append(tf_tree + [(adjacent)])
    # print(" [DEBUG] no path found")
    return []


async def find_transformation(
    ref_map: str,
    target_map: str
) -> Optional[Transformation2DModel]:
    """
    This function will get the tf_tree of 2 maps, calculate the transformation
    and return the transformation in pydantic model form
    """
    result = await tf_tree_bfs(ref_map, target_map)
    if not result:
        return None

    # Apply 2d transfomation multiplication
    total_tf = None
    for tf in result:
        tf_m = db.Transformation2D.from_ttm(tf)
        if total_tf is None:
            total_tf = utils.Tf2D(tf_m.x, tf_m.y, tf_m.yaw, tf_m.scale)
        else:
            next_tf = utils.Tf2D(tf_m.x, tf_m.y, tf_m.yaw, tf_m.scale)
            total_tf = utils.tf_matmul(total_tf, next_tf)

    return Transformation2DModel(
        target_map=target_map, ref_map=ref_map,
        x=total_tf.x, y=total_tf.y, yaw=total_tf.yaw, scale=total_tf.scale)

###############################################################################


def main(argv=sys.argv):
    print("Init rmf rtls server...")
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--host_address', default="0.0.0.0",
                        type=str, help='host address, default 0.0.0.0')
    parser.add_argument('-p', '--port', default="8085",
                        type=str, help='port number, default 8085')
    parser.add_argument('-db', '--db_url', default="sqlite://db.sqlite3",
                        type=str, help='db url, default sqlite://db.sqlite3')
    args = parser.parse_args(argv[1:])

    # TODO: usage of rmf_traffic_editor graph map?

    print(f" Run RTLS Server... http://{args.host_address}:{args.port}")

    db.setup_database(app, db_url=args.db_url)

    uvicorn.run(app,
                host=args.host_address,
                port=args.port,
                log_level='warning')


###############################################################################
if __name__ == '__main__':
    main(sys.argv)
