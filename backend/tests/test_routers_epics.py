from app.routers.epics import router


class TestRouterConfig:
    def test_prefix(self) -> None:
        assert router.prefix == "/api/epics"

    def test_tags(self) -> None:
        assert "epics" in router.tags


class TestRouterRoutes:
    def _route_methods(self) -> dict[str, set[str]]:
        result: dict[str, set[str]] = {}
        for route in router.routes:
            path = getattr(route, "path", None)
            methods = getattr(route, "methods", set())
            if path:
                result.setdefault(path, set()).update(methods)
        return result

    def test_post_root(self) -> None:
        routes = self._route_methods()
        assert "POST" in routes["/"]

    def test_get_root(self) -> None:
        routes = self._route_methods()
        assert "GET" in routes["/"]

    def test_get_detail(self) -> None:
        routes = self._route_methods()
        assert "GET" in routes["/{epic_id}"]

    def test_patch_detail(self) -> None:
        routes = self._route_methods()
        assert "PATCH" in routes["/{epic_id}"]

    def test_delete_detail(self) -> None:
        routes = self._route_methods()
        assert "DELETE" in routes["/{epic_id}"]

    def test_total_route_count(self) -> None:
        paths = [getattr(r, "path", None) for r in router.routes]
        real_paths = [p for p in paths if p is not None]
        assert len(real_paths) == 5


class TestEndpointStatusCodes:
    def _find_route(self, path: str, method: str):
        for route in router.routes:
            route_path = getattr(route, "path", None)
            methods = getattr(route, "methods", set())
            if route_path == path and method in methods:
                return route
        return None

    def test_create_returns_201(self) -> None:
        route = self._find_route("/", "POST")
        assert route is not None
        assert route.status_code == 201  # type: ignore[union-attr]

    def test_delete_returns_204(self) -> None:
        route = self._find_route("/{epic_id}", "DELETE")
        assert route is not None
        assert route.status_code == 204  # type: ignore[union-attr]
