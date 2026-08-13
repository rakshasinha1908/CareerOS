import { NavLink } from "react-router-dom";
import {
  LayoutGrid,
  Briefcase,
  FileText,
  Building2,
  Users,
  Folder,
  CircleUserRound,
  SlidersHorizontal,
  Settings,
  Plus,
} from "lucide-react";
import "../../styles/sidebar.css";

const mainNavigation = [
  { label: "Overview", path: "/", icon: LayoutGrid },
  { label: "Opportunities", path: "/opportunities", icon: Briefcase },
  { label: "Applications", path: "/applications", icon: FileText },
  { label: "Companies", path: "/companies", icon: Building2 },
  { label: "Contacts", path: "/contacts", icon: Users },
  { label: "Documents", path: "/documents", icon: Folder },
];

const secondaryNavigation = [
  { label: "Profile", path: "/profile", icon: CircleUserRound },
  { label: "Preferences", path: "/preferences", icon: SlidersHorizontal },
  { label: "Settings", path: "/settings", icon: Settings },
];

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">
          <LayoutGrid size={18} strokeWidth={2.25} />
        </div>

        <div>
          <div className="brand-name">CareerOS</div>
          <div className="brand-subtitle">Professional Hub</div>
        </div>
      </div>

      <button className="add-opportunity" type="button">
        <Plus size={18} strokeWidth={2.5} />
        Add Opportunity
      </button>

      <nav className="sidebar-nav">
        <div className="nav-group">
          {mainNavigation.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/"}
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <item.icon className="nav-icon" size={18} strokeWidth={2} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>

        <div className="nav-divider" />

        <div className="nav-group">
          {secondaryNavigation.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <item.icon className="nav-icon" size={18} strokeWidth={2} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </aside>
  );
}

export default Sidebar;