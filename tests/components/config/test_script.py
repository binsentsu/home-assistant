"""Tests for config/script."""
from asynctest import patch

from homeassistant.bootstrap import async_setup_component
from homeassistant.components import config


async def test_delete_script(hass, hass_client):
    """Test deleting a script."""
    ent_reg = await hass.helpers.entity_registry.async_get_registry()

    assert await async_setup_component(
        hass, "script", {"script": {"one": {"sequence": []}, "two": {"sequence": []}}}
    )

    assert len(ent_reg.entities) == 2

    with patch.object(config, "SECTIONS", ["script"]):
        assert await async_setup_component(hass, "config", {})

    client = await hass_client()

    orig_data = {"one": {}, "two": {}}

    def mock_read(path):
        """Mock reading data."""
        return orig_data

    written = []

    def mock_write(path, data):
        """Mock writing data."""
        written.append(data)

    with patch("homeassistant.components.config._read", mock_read), patch(
        "homeassistant.components.config._write", mock_write
    ), patch("homeassistant.config.async_hass_config_yaml", return_value={}):
        resp = await client.delete("/api/config/script/config/two")

    assert resp.status == 200
    result = await resp.json()
    assert result == {"result": "ok"}

    assert len(written) == 1
    assert written[0] == {"one": {}}

    await hass.async_block_till_done()
    assert len(ent_reg.entities) == 1
