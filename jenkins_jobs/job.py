# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from dataclasses import dataclass

from .root_base import RootBase, NonTemplateRootMixin, TemplateRootMixin, Group
from .defaults import split_contents_params, job_contents_keys


@dataclass
class JobBase(RootBase):
    project_type: str
    folder: str

    @classmethod
    def from_dict(cls, config, roots, expander, data):
        keep_descriptions = config.yamlparser["keep_descriptions"]
        d = {**data}
        name = d.pop("name")
        id = d.pop("id", None)
        description = d.pop("description", None)
        defaults = d.pop("defaults", "global")
        project_type = d.pop("project-type", None)
        folder = d.pop("folder", None)
        contents, params = split_contents_params(d, job_contents_keys)
        return cls(
            roots.defaults,
            expander,
            keep_descriptions,
            id,
            name,
            description,
            defaults,
            params,
            contents,
            project_type,
            folder,
        )

    def _as_dict(self):
        data = {
            "name": self._full_name,
            **self.contents,
        }
        if self.project_type:
            data["project-type"] = self.project_type
        return data

    @property
    def _full_name(self):
        if self.folder:
            return f"{self.folder}/{self.name}"
        else:
            return self.name


class Job(JobBase, NonTemplateRootMixin):
    @classmethod
    def add(cls, config, roots, expander, param_expander, data):
        job = cls.from_dict(config, roots, expander, data)
        roots.assign(roots.jobs, job.id, job, "job")


class JobTemplate(JobBase, TemplateRootMixin):
    @classmethod
    def add(cls, config, roots, expander, params_expander, data):
        template = cls.from_dict(config, roots, params_expander, data)
        roots.assign(roots.job_templates, template.id, template, "job template")


@dataclass
class JobGroup(Group):
    _jobs: dict
    _job_templates: dict

    @classmethod
    def add(cls, config, roots, expander, params_expander, data):
        d = {**data}
        name = d.pop("name")
        job_specs = [
            cls._spec_from_dict(item, error_context=f"Job group {name}")
            for item in d.pop("jobs", [])
        ]
        group = cls(
            name,
            job_specs,
            d,
            roots.jobs,
            roots.job_templates,
        )
        roots.assign(roots.job_groups, group.name, group, "job group")

    def __str__(self):
        return f"Job group {self.name}"

    @property
    def _root_dicts(self):
        return [self._jobs, self._job_templates]
