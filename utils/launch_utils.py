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


def merge_overrides(base, overrides_file, key):
    """Shallow-merge overrides_file[key] onto a copy of base.

    No-op if overrides_file is unset or missing, so callers stay runnable
    without a top-level overrides file present.
    """
    if not overrides_file or not os.path.exists(overrides_file):
        return base
    overrides = load_yaml(overrides_file) or {}
    merged = dict(base)
    merged.update(overrides.get(key, {}))
    return merged
