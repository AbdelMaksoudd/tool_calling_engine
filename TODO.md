# Project Roadmap & Tasks

## ✅ Completed (Recent Achievements)
- [x] Release initial demo (with Gemini provider only)
- [x] add validation for llm's output before execute (Implemented dynamic models via Pydantic `create_model` to validate data before function execution).
- [x] Extract and handle all function type hints dynamically using the `typing` module.
- [x] Parse and extract docstrings and parameter descriptions across all styles using `docstring_parser`.
- [x] remove `google-genai` library and use `litellm` for all providers

## 🚀 High Priority (Current Sprint)
- [ ] Implement asynchronous tool execution (`async`/`await`)
- [ ] Support API-based tools (execute local user functions via HTTP endpoints / Webhooks)

## 📅 Medium Priority (Upcoming)
- [ ] Support nested schema hints via lazy-loaded Pydantic in `ToolManager.register`
- [ ] Enable concurrent multi-agent execution
- [ ] reduce memory usage by replace litellm by httpx

## 💡 Future Ideas / Icebox
- [ ] Autonomous multi-agent workflow for dynamic tool generation (vibe coding)
- [ ] Build an interactive dashboard and UI