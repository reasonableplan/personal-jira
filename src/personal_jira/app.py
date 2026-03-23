from fastapi import FastAPI


def create_app() -> FastAPI:
    """Create and configure the FastAPI application with all routers."""
    from personal_jira.routers import issues, attachments, templates, webhooks
    from personal_jira.routers import comments, sprints, hierarchy, delete_issue, ws

    app = FastAPI(title="Personal Jira", version="0.1.0")

    app.include_router(issues.router)
    app.include_router(attachments.router)
    app.include_router(templates.router)
    app.include_router(webhooks.router)
    app.include_router(comments.router)
    app.include_router(sprints.router)
    app.include_router(hierarchy.router)
    app.include_router(delete_issue.router)

    # WebSocket router (optional - may not be present)
    try:
        app.include_router(ws.router)
    except Exception:
        pass

    # API v1 routers
    try:
        from personal_jira.api.v1.endpoints import dependencies as dep_ep
        app.include_router(dep_ep.router)
    except Exception:
        pass

    try:
        from personal_jira.api import labels as labels_ep
        app.include_router(labels_ep.router)
    except Exception:
        pass

    try:
        from personal_jira.api.v1.endpoints import context_bundle as cb_ep
        app.include_router(cb_ep.router)
    except Exception:
        pass

    return app
