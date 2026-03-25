import { NavLink, Outlet } from "react-router-dom";
import { cn } from "@/lib/utils";
import { LayoutDashboard, FolderKanban, Tags } from "lucide-react";

const NAV_ITEMS = [
  { to: "/board", label: "Board", icon: LayoutDashboard },
  { to: "/epics", label: "Epics", icon: FolderKanban },
  { to: "/settings/labels", label: "Labels", icon: Tags },
] as const;

export function AppLayout() {
  return (
    <div className="flex h-screen">
      <aside className="w-60 border-r bg-muted/40 flex flex-col">
        <div className="p-4 font-semibold text-lg border-b">Personal Jira</div>
        <nav className="flex-1 p-2 space-y-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors",
                  isActive ? "bg-accent text-accent-foreground" : "hover:bg-accent/50",
                )
              }
            >
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
