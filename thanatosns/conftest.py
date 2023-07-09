import pytest
from export.exporters import base_exporter, media_exporter
from pyfakefs.fake_filesystem_unittest import Patcher


# https://github.com/jmcgeheeiv/pyfakefs/issues/458
@pytest.fixture
def fs_patched():
    patcher = Patcher(
        modules_to_reload=[
            base_exporter,
            media_exporter,
        ]
    )
    patcher.setUp()
    yield patcher.fs
    patcher.tearDown()
