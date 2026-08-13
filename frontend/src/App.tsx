import { Routes, Route } from "react-router-dom";

import AppShell from "./components/layout/AppShell";
import OverviewPage from "./pages/OverviewPage";
import PlaceholderPage from "./pages/PlaceholderPage";
import ProfilePage from "./pages/ProfilePage";
import PreferencesPage from "./pages/PreferencesPage";
import CompaniesPage from "./pages/CompaniesPage";
import CareerSourcesPage from "./pages/CareerSourcesPage";
import OpportunitiesPage from "./pages/OpportunitiesPage";

function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<OverviewPage />} />

        <Route path="/opportunities" element={<OpportunitiesPage />} />

        <Route
          path="/applications"
          element={
            <PlaceholderPage
              title="Applications"
              description="Track your applications and keep your job search organized."
            />
          }
        />

        <Route path="/companies" element={<CompaniesPage />} />

        <Route path="/career-sources" element={<CareerSourcesPage />} />

        <Route
          path="/contacts"
          element={
            <PlaceholderPage
              title="Contacts"
              description="Keep track of recruiters, hiring managers, referrals, and professional connections."
            />
          }
        />

        <Route
          path="/documents"
          element={
            <PlaceholderPage
              title="Documents"
              description="Keep your resumes, cover letters, and other career documents organized."
            />
          }
        />

        <Route path="/profile" element={<ProfilePage />} />

        <Route path="/preferences" element={<PreferencesPage />} />

        <Route
          path="/settings"
          element={
            <PlaceholderPage
              title="Settings"
              description="Manage your CareerOS application settings."
            />
          }
        />
      </Route>
    </Routes>
  );
}

export default App;