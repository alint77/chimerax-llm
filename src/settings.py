# vim: set expandtab shiftwidth=4 softtabstop=4:

"""Persistent settings for ChimeraLLM."""

from chimerax.core.settings import Settings


class ChimeraLLMSettings(Settings):
    """API and model preferences (saved to disk)."""

    AUTO_SAVE = {
        "model": "gpt-4o",
        "temperature": 0.2,
        "max_iterations": 10,
        "api_base_url": "",
        "use_opencode": False,
        "opencode_model": "github-copilot/claude-sonnet-4",
    }
    EXPLICIT_SAVE = {
        "api_key": "",
    }

    def __init__(self, session):
        super().__init__(session, "ChimeraLLM", version="1")


def get_settings(session):
    """Return the settings object for this session."""
    s = getattr(session, "_chimerallm_settings", None)
    if not isinstance(s, ChimeraLLMSettings):
        s = ChimeraLLMSettings(session)
        session._chimerallm_settings = s
    return s
