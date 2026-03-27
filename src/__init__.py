# vim: set expandtab shiftwidth=4 softtabstop=4:

"""ChimeraLLM: natural language LLM agent for ChimeraX."""

from chimerax.core.toolshed import BundleAPI


class _ChimeraLLMBundleAPI(BundleAPI):
    api_version = 1

    @staticmethod
    def start_tool(session, bi, ti):
        if ti.name == "ChimeraLLM":
            from chimerallm.tool import ChimeraLLMTool

            return ChimeraLLMTool(session, ti.name)
        raise ValueError(f"Unknown tool {ti.name!r}")

    @staticmethod
    def register_command(bi, ci, logger):
        if ci.name == "chimerallm":
            from chimerallm.cmd import register as register_cmd

            register_cmd(logger)

    @staticmethod
    def get_class(name):
        if name == "ChimeraLLMTool":
            from chimerallm.tool import ChimeraLLMTool

            return ChimeraLLMTool
        return None


bundle_api = _ChimeraLLMBundleAPI()
