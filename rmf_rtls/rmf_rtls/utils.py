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

from dataclasses import dataclass
import numpy as np
import math

###############################################################################

@dataclass
class Tf2D:
    x: float
    y: float
    yaw: float
    scale: float


def tf_matmul(tf1: Tf2D, tf2: Tf2D) -> Tf2D:
    """
    Multiply two 2D transformation matrics, and return the result
    """
    mat1 = np.matrix([
        [math.cos(tf1.yaw), -math.sin(tf1.yaw), tf1.x],
        [math.sin(tf1.yaw), math.cos(tf1.yaw), tf1.y],
        [0, 0, tf1.scale]])
    mat2 = np.matrix([
        [math.cos(tf2.yaw), -math.sin(tf2.yaw), tf2.x],
        [math.sin(tf2.yaw), math.cos(tf2.yaw), tf2.y],
        [0, 0, tf2.scale]])
    r = np.matmul(mat1, mat2)
    yaw = math.atan2(r[1, 0], r[0,0])
    return Tf2D(r[0, 2], r[1, 2], yaw, r[2, 2])
