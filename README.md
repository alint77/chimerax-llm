# chimerax-llm

ChimeraX bundle that turns natural language into ChimeraX commands using an LLM agent. Supports any OpenAI-compatible API (OpenRouter, OpenAI, etc.) or GitHub Copilot directly (included with your Copilot subscription).

## Screenshot

![ChimeraX with ChimeraLLM: structure viewport and chat panel with a multi-step prompt](docs/images/chimerallm-screenshot.png)

**ChimeraLLM** (dock on the right) shows the chat log, running commands, and a **multi-line prompt** (use **Enter** for a new line; **Ctrl+Enter** or **Send** to submit). The 3D view shows the structure after the agent executes your instructions (here: PDB 1a6m, surfaces, hydrophobicity coloring, and cross-section).

## Prerequisites

- **ChimeraX** 1.1 or newer (graphical interface; does not run in `--nogui` mode).
- **Git** (to clone), or download the source as a ZIP.

**For API mode (default):**
- An **API key** for an OpenAI-compatible service.
- The bundle declares a dependency on the Python **`openai`** package; ChimeraX should install it automatically. If you see import errors, run `devel pip install openai` from the ChimeraX command line and restart.

**For GitHub Copilot mode:**
- A **GitHub Copilot** subscription (Free, Pro, Pro+, Business, or Enterprise).
- No external tools needed — authentication is handled directly in the plugin.

## Install from source

1. Clone the repository:

   ```bash
   git clone https://github.com/AminN77/chimerax-llm.git
   cd chimerax-llm
   ```

2. Start **ChimeraX** and open the **Command Line**.

3. Install the bundle:

   ```text
   devel install /full/path/to/chimerax-llm
   ```

   For development (pick up Python edits after restart without reinstalling):

   ```text
   devel install /full/path/to/chimerax-llm user true editable true
   ```

4. **Restart ChimeraX**.

## Configuration

Open the **ChimeraLLM** tool, click **Settings**, and use the **OpenAI-compatible API** or **GitHub Copilot** tab. The active tab is the backend used for chat (you can switch anytime and save).

### Tab: OpenAI-compatible API

| Setting | Description |
|---|---|
| **API endpoint URL** | Leave empty for OpenRouter (`https://openrouter.ai/api/v1`), or enter any OpenAI-compatible base URL |
| **API key** | Your API key for the chosen endpoint |
| **Model** | Model identifier (default: `gpt-4o`). Use **Refresh models** to load IDs from the provider (`GET /v1/models`) using the URL and key above; models also load on open when a key is saved |
| **Temperature** | Sampling temperature, 0.0 - 2.0 (default: 0.2) |
| **Refresh models** | Fetches the model list from the API and fills the dropdown |

### Tab: GitHub Copilot

This calls the Copilot API directly with native tool calling — no API key or separate billing beyond Copilot. Each user prompt costs exactly **one premium request** regardless of how many tool-calling rounds the agent takes (follow-up rounds use `x-initiator: agent` and are not billed as premium, matching [opencode](https://github.com/sst/opencode)).

| Setting | Description |
|---|---|
| **Model** | Pick from the dropdown or type a model ID. Use **Refresh models** to reload IDs from the public model registry (after signing in, refresh again if needed) |
| **Sign in with GitHub…** | GitHub device flow (one-time setup) |

Typical registry entries include GPT-4o, GPT-4.1, GPT-5-mini, Claude Sonnet 4.x, Gemini 2.5 Pro, and o4-mini; availability depends on your Copilot plan.

### Shared options (below the tabs)

| Setting | Description |
|---|---|
| **Write ChimeraLLM messages to the ChimeraX log** | When enabled (default), ChimeraLLM writes lines such as LLM requests and settings notices to the ChimeraX log. Turn off to keep the log quiet |
| **Max tool rounds per message** | Maximum tool-calling rounds per user message (default: 10) |

While the assistant is working, a **rotating indicator** and status text appear above the prompt area.

## GitHub Copilot setup

1. Open **ChimeraLLM Settings** in ChimeraX.
2. Open the **GitHub Copilot** tab.
3. Click **Sign in with GitHub…**.
4. A dialog shows a URL and a one-time code — open the URL in your browser and enter the code.
5. When authorized, **Status** shows **Signed in to GitHub**. Use **Refresh models** if needed, pick a model, and click **OK**.

If you've previously authenticated with [opencode](https://github.com/anomalyco/opencode), the plugin can reuse that token (see `~/.local/share/opencode/auth.json` when applicable).

## Usage

- **Menu:** Tools > **ChimeraLLM**
- **Command line:**

  ```text
  chimerallm
  ```

  With an inline prompt:

  ```text
  chimerallm fetch 1ubq and color it by secondary structure
  ```

Type natural language in the **prompt area** at the bottom of the panel. It supports **multiple lines**; press **Enter** for a new line and **Ctrl+Enter** (or **Send**) to submit. The agent runs ChimeraX commands, can read session state, and streams the assistant reply in the chat while tool calls and command output appear as they run. Use **Cancel** to stop a long request.

## Updating

After `git pull`, run `devel install` again with the same path and options, then restart ChimeraX.

## Architecture

See [architecture.md](architecture.md) for a detailed overview of the codebase, threading model, and backend design.

## More information

- ChimeraX `devel install` options: [Command: devel](https://rbvi.ucsf.edu/chimerax/docs/user/commands/devel.html)
- Bundle development overview: [Building and distributing bundles](https://www.cgl.ucsf.edu/chimerax/docs/devel/writing_bundles.html)
