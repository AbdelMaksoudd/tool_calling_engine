# Project Roadmap & Tasks

## 🚀 High Priority (Current Sprint)
- [ ] Release initial demo (with Gemini provider only)
- [ ] remove `google-genai` library and use litellm for all providers
- [ ] add validation for llm's output before execute

## 📅 Medium Priority (Upcoming)
- [ ] Support nested schema hints via lazy-loaded Pydantic in `ToolManager.register`
- [ ] Implement asynchronous tool execution (`async`/`await`)
- [ ] Enable concurrent multi-agent execution
- [ ] Support API-based tools (execute local user functions via HTTP endpoints / Webhooks)
- [ ] reduce memory usage by replace litellm by httpx

## 💡 Future Ideas / Icebox
- [ ] Autonomous multi-agent workflow for dynamic tool generation (vibe coding)
- [ ] Build an interactive dashboard and UI