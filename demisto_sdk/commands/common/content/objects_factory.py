import re
from typing import Union

from demisto_sdk.commands.common.constants import (CANVAS, CLASSIFIER,
                                                   CLASSIFIERS_DIR, CONNECTION,
                                                   CONNECTIONS_DIR, DASHBOARD,
                                                   DASHBOARDS_DIR,
                                                   DOC_FILES_DIR,
                                                   DOCUMENTATION_DIR,
                                                   INCIDENT_FIELDS_DIR,
                                                   INCIDENT_TYPE,
                                                   INCIDENT_TYPES_DIR,
                                                   INDICATOR_TYPE, INTEGRATION,
                                                   INTEGRATIONS_DIR, LAYOUT,
                                                   LAYOUT_CONTAINER,
                                                   LAYOUTS_DIR,
                                                   OLD_INDICATOR_TYPE,
                                                   PLAYBOOK, PLAYBOOKS_DIR,
                                                   RELEASE_NOTES_DIR, REPORT,
                                                   REPORTS_DIR, SCRIPT,
                                                   SCRIPTS_DIR,
                                                   TEST_PLAYBOOKS_DIR,
                                                   TOOLS_DIR, WIDGET,
                                                   WIDGETS_DIR, FileType)
from demisto_sdk.commands.common.content.objects.content_objects import \
    Documentation
from demisto_sdk.commands.common.content.objects.pack_objects import (
    AgentTool, ChangeLog, Classifier, Connection, Dashboard, DocFile,
    IncidentField, IncidentType, IndicatorField, IndicatorType, Integration,
    Layout, LayoutsContainer, OldIndicatorType, PackIgnore, PackMetaData,
    Playbook, Readme, ReleaseNote, Report, Script, SecretIgnore, Widget)
from demisto_sdk.commands.common.tools import find_type
from wcmatch.pathlib import Path

type_conversion_by_FileType = {
    FileType.CLASSIFIER: Classifier,
    FileType.LAYOUT: Layout,
    FileType.REPORT: Report,
    FileType.PLAYBOOK: Playbook,
    FileType.DASHBOARD: Dashboard,
    FileType.SCRIPT: Script,
    FileType.WIDGET: Widget,
    FileType.MAPPER: Classifier,
    FileType.REPUTATION: IndicatorType,
    FileType.INTEGRATION: Integration,
    FileType.INCIDENT_FIELD: IncidentField,
    FileType.INCIDENT_TYPE: IncidentType,
    FileType.TEST_SCRIPT: Script,
    FileType.TEST_PLAYBOOK: Playbook,
    FileType.BETA_INTEGRATION: Integration,
    FileType.CHANGELOG: ChangeLog,
    FileType.CONNECTION: Connection,
    FileType.DESCRIPTION: '',
    FileType.IMAGE: DocFile,
    FileType.INDICATOR_FIELD: IndicatorField,
    FileType.JAVSCRIPT_FILE: '',
    FileType.OLD_CLASSIFIER: Classifier,
    FileType.POWERSHELL_FILE: '',
    FileType.PYTHON_FILE: '',
    FileType.README: Readme,
    FileType.RELEASE_NOTES: ReleaseNote,
}

type_conversion_by_prefix = {
    INTEGRATION: Integration,
    SCRIPT: Script,
    PLAYBOOK: Playbook,
    CLASSIFIER: Classifier,
    CONNECTION: Connection,
    REPORT: Report,
    DASHBOARD: Dashboard,
    LAYOUT: Layout,
    LAYOUT_CONTAINER: LayoutsContainer,
    WIDGET: Widget,
    CANVAS: Connection,
    INDICATOR_TYPE: IndicatorType,
    INCIDENT_TYPE: IncidentType,
}

type_conversion_by_dir = {
    INTEGRATIONS_DIR: Integration,
    SCRIPTS_DIR: Script,
    PLAYBOOKS_DIR: Playbook,
    TEST_PLAYBOOKS_DIR: Playbook,
    INCIDENT_FIELDS_DIR: IncidentField,
    INCIDENT_TYPES_DIR: IncidentType,
    CLASSIFIERS_DIR: Classifier,
    CONNECTIONS_DIR: Connection,
    REPORTS_DIR: Report,
    DASHBOARDS_DIR: Dashboard,
    LAYOUTS_DIR: Layout,
    WIDGETS_DIR: Widget,
    TOOLS_DIR: AgentTool,
    RELEASE_NOTES_DIR: ReleaseNote,
    DOC_FILES_DIR: DocFile,
    DOCUMENTATION_DIR: Documentation,
}

type_conversion_by_file_name = {
    'pack_metadata.json': PackMetaData,
    '.secrets-ignore': SecretIgnore,
    '.pack-ignore': PackIgnore,
    f'{OLD_INDICATOR_TYPE}.json': OldIndicatorType,
}

type_conversion_by_regex = {
    r'.*_CHANGELOG.md': ChangeLog,
    r'.*README.md': Readme,
    r'\d+_\d+_\d+.md': ReleaseNote,
}


class ContentObjectFactory:
    @staticmethod
    def _find_type_by_prefix(file_name: str):
        object_type = None
        prefix_match = re.search(pattern=r'^([a-z]+)-.+', string=file_name)
        if prefix_match:
            object_type = type_conversion_by_prefix.get(prefix_match.group(1))
        elif type_conversion_by_file_name.get(file_name):
            object_type = type_conversion_by_file_name.get(file_name)
        else:
            for pattern, obj_type in type_conversion_by_regex.items():
                if re.search(pattern=pattern, string=file_name):
                    object_type = obj_type

        return object_type

    @staticmethod
    def _find_type_by_dir(path: Union[Path, str]):
        path_parts = Path(path).parts
        for part in [-3, -2]:
            object_type = type_conversion_by_dir.get(path_parts[part])
            if object_type:
                break

        return object_type

    @staticmethod
    def from_path(path: Union[Path, str]):
        path = Path(path)
        object_type = None
        if path.suffix in ['.yaml', '.json', '.yml'] or path.name.startswith('.'):
            object_type = ContentObjectFactory._find_type_by_prefix(file_name=path.name)
        if not object_type:
            file_type = find_type(str(path))
            object_type = type_conversion_by_FileType.get(file_type)
        if not object_type:
            object_type = ContentObjectFactory._find_type_by_dir(path=path)

        return object_type(path)