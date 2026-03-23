from fastapi import FastAPI

from personal_jira.routers import attachments, issues, templates, webhooks

app = FastAPI(title="Personal Jira", version="0.1.0")

app.include_router(issues.router)
app.include_router(webhooks.router)
app.include_router(attachments.router)
app.include_router(templates.router)
