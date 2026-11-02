# Copyright (c) 2025 Franka Robotics GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import yaml


def load_yaml(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def load_overrides(overrides_file):
    """Load a top-level overrides file, or return an empty mapping if unset."""
    if not overrides_file:
        return {}
    return load_yaml(overrides_file) or {}


def resolve_bool_override(overrides, key, launch_value, default):
    """Resolve a boolean with CLI > overrides file > built-in precedence."""
    value = launch_value if launch_value != '' else overrides.get(key, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in {'true', 'false'}:
        return value.lower() == 'true'
    raise ValueError(f"{key} must be true or false, got {value!r}")


def merge_overrides(base, overrides_file, key):
    """Shallow-merge overrides_file[key] onto a copy of base.

    No-op if overrides_file is unset or missing, so callers stay runnable
    without a top-level overrides file present.

    For standard arms with gripper_type set, an absent or 'auto' frame is
    derived from the gripper. Explicit frame names are preserved.
    """
    if not overrides_file or not os.path.exists(overrides_file):
        return base
    overrides = load_yaml(overrides_file) or {}
    merged = dict(base)
    merged.update(overrides.get(key, {}))
    # Keep robot bringup, IK, and teleop on the frame provided by the gripper.
    # Explicit tool frames take precedence over automatic selection.
    if key in {'franka_left', 'franka_right'} and 'gripper_type' in merged:
        gripper_type = merged['gripper_type']
        no_gripper = gripper_type is None or str(gripper_type).lower() == 'none'
        if no_gripper:
            # Xacro mappings require strings, including for YAML null values.
            merged['gripper_type'] = 'none'
        if merged.get('end_effector_frame', 'auto') == 'auto':
            suffix = 'fr3_link8' if no_gripper else 'grasp_point'
            merged['end_effector_frame'] = f'{key}_{suffix}'
    return merged
