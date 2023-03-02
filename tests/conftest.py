import pytest

from rocks import index

@pytest.fixture(autouse=True, scope='session')
def ensure_index_exists(request):
    # Work around https://github.com/pytest-dev/pytest/issues/2704 to avoid capturing output:
    with request.config.pluginmanager.getplugin('capturemanager').global_and_fixture_disabled():
        index._ensure_index_exists()
