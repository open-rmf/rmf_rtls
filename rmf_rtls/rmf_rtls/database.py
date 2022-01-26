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


from fastapi import FastAPI
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

# for tortoise class elements
from tortoise import fields
from tortoise.models import Model

from rmf_api_msgs.models import rtls_tag_state, transformation_2D

PydanticRtlsTagState = rtls_tag_state.RtlsTagState
PydanticTransformation2D = transformation_2D.Transformation2D

###############################################################################


class JsonMixin(Model):
    id = fields.CharField(255, pk=True, source_field="id")
    data = fields.JSONField()


# Note: target_map is unique, thus is set as id - pk
class TtmTransformation2D(JsonMixin):
    ref_map = fields.CharField(255, null=True, index=True)


# Note: tag_id is set as id (pk)
class TtmRtlsTagState(JsonMixin):
    asset_type = fields.CharField(255, null=True, index=True)
    asset_subtype = fields.CharField(255, null=True, index=True)


###############################################################################

class RtlsTagState(PydanticRtlsTagState):
    @staticmethod
    def from_ttm(tortoise: TtmRtlsTagState) -> "RtlsTagState":
        return RtlsTagState(**tortoise.data)

    @staticmethod
    def from_pydantic(pydantic: PydanticTransformation2D) -> "RtlsTagState":
        return RtlsTagState(**pydantic.dict())

    async def save(self) -> None:
        print("save tag: ", self.tag_id)
        return await TtmRtlsTagState.update_or_create(
            {
                "data": self.json(),
                "asset_type": self.asset_type.asset_type,
                "asset_subtype": self.asset_type.asset_subtype
            },
            id=self.tag_id)


###############################################################################

# Create a transformation tree from rmf_map
class Transformation2D(PydanticTransformation2D):
    @staticmethod
    def from_ttm(tortoise: TtmTransformation2D) -> "Transformation2D":
        return Transformation2D(**tortoise.data)

    @staticmethod
    def from_pydantic(pydantic: PydanticTransformation2D) -> "Transformation2D":
        return Transformation2D(**pydantic.dict())

    async def save(self) -> None:
        return await TtmTransformation2D.update_or_create(
            {
                "data": self.dict(),
                "ref_map": self.ref_map,
            },
            id=self.target_map)


###############################################################################

def setup_database(app: FastAPI, db_url: str):
    register_tortoise(
        app,
        db_url=db_url,
        modules={"models": ["rmf_rtls.database"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )
