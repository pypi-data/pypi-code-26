import os

from publisher import settings


class ProcedureFileManager(object):

    def __init__(self, procedure):
        self._procedure_code = procedure.code
        self._ensure_structure_exists()

        self.phase_files = [PhaseFileManager(p, self._procedure_code) for p in procedure.phases]

    def _ensure_structure_exists(self):
        for d in [self.base_directory, self.asset_directory, self.build_asset_directory, self.more_info_directory,
                  self.overview_directory, self.devices_directory, self.eula_directory, self.csv_directory]:
            if not os.path.exists(d):
                os.makedirs(d)

    @property
    def base_directory(self):
        return os.path.join(settings.PROCEDURE_CHECKOUT_DIRECTORY, self._procedure_code)

    @property
    def procedure_file(self):
        return os.path.join(self.base_directory, 'procedure.yml')

    @property
    def asset_directory(self):
        return os.path.join(self.base_directory, 'assets')

    @property
    def build_asset_directory(self):
        return os.path.join(self.base_directory, 'build_assets')

    @property
    def more_info_directory(self):
        return os.path.join(self.build_asset_directory, 'moreInfo')

    @property
    def overview_directory(self):
        return os.path.join(self.build_asset_directory, 'overview')

    @property
    def devices_directory(self):
        return os.path.join(self.build_asset_directory, 'devices')

    @property
    def eula_directory(self):
        return os.path.join(self.build_asset_directory, 'eula')

    @property
    def csv_directory(self):
        return os.path.join(self.build_asset_directory, 'csv')


class PhaseFileManager(object):

    def __init__(self, phase, procedure_code):
        self._procedure_code = procedure_code
        self.phase_code = phase.code

        self._ensure_structure_exists()

    def _ensure_structure_exists(self):
        for d in [self.base_directory, self.asset_directory, self.translation_directory]:
            if not os.path.exists(d):
                os.makedirs(d)

    @property
    def base_directory(self):
        return os.path.join(self.procedure_directory, self.phase_code)

    @property
    def procedure_directory(self):
        return os.path.join(settings.PROCEDURE_CHECKOUT_DIRECTORY, self._procedure_code)

    @property
    def phase_file(self):
        return os.path.join(self.base_directory, 'phase.yml')

    @property
    def asset_directory(self):
        return os.path.join(self.base_directory, 'assets')

    @property
    def translation_directory(self):
        return os.path.join(self.base_directory, 'translations')
