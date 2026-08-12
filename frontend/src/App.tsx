// import { BrowserRouter, Route, Routes } from "react-router-dom";

// import AppShell from "./components/layout/AppShell";
// import OverviewPage from "./pages/OverviewPage";

// function App() {
//   return (
//     <BrowserRouter>
//       <Routes>
//         <Route element={<AppShell />}>
//           <Route path="/" element={<OverviewPage />} />
//         </Route>
//       </Routes>
//     </BrowserRouter>
//   );
// }

// export default App;



import { Routes, Route } from "react-router-dom";

import AppShell from "./components/layout/AppShell";
import OverviewPage from "./pages/OverviewPage";
import PlaceholderPage from "./pages/PlaceholderPage";
import ProfilePage from "./pages/ProfilePage";
import PreferencesPage from "./pages/PreferencesPage";

function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<OverviewPage />} />

        <Route
          path="/opportunities"
          element={
            <PlaceholderPage
              title="Opportunities"
              description="Discover and manage opportunities that match your career goals."
            />
          }
        />

        <Route
          path="/applications"
          element={
            <PlaceholderPage
              title="Applications"
              description="Track your applications and keep your job search organized."
            />
          }
        />

        <Route
          path="/companies"
          element={
            <PlaceholderPage
              title="Companies"
              description="Manage the companies you're targeting and keep important details in one place."
            />
          }
        />

        <Route
          path="/career-sources"
          element={
            <PlaceholderPage
              title="Career Sources"
              description="Monitor career pages and other sources for new opportunities."
            />
          }
        />

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