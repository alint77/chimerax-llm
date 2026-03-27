# vim: set expandtab shiftwidth=4 softtabstop=4:

"""Command-line interface: `chimerallm`"""

from chimerax.core.commands import CmdDesc, register as register_command, RestOfLine


def register(logger):
    register_command(
        "chimerallm",
        CmdDesc(
            optional=[("prompt", RestOfLine)],
            synopsis="Show ChimeraLLM tool; optional prompt text is queued when the tool is open",
        ),
        chimerallm,
        logger=logger,
    )


def chimerallm(session, prompt=None):
    from chimerax.ui.cmd import ui_tool_show

    if not session.ui.is_gui:
        session.logger.error("chimerallm requires the ChimeraX graphical interface.")
        return

    ti = ui_tool_show(session, "ChimeraLLM")
    if prompt and hasattr(ti, "submit_prompt"):
        ti.submit_prompt(prompt.strip())
