import { Outlet } from "react-router-dom";

import Sidebar from "./Sidebar";
import TopBar from "./TopBar";
import "../../styles/app-shell.css";

function AppShell() {
  return (
    <div className="app-shell">
      <Sidebar />

      <div className="app-main">
        <TopBar />

        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default AppShell;