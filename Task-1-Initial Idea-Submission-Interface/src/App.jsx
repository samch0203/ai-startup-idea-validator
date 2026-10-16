import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import SubmitIdeaPage from "./pages/SubmitIdeaPage.jsx";
import WorkspacePage from "./pages/WorkspacePage.jsx";
import IdeaDetailPage from "./pages/IdeaDetailPage.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<SubmitIdeaPage />} />
        <Route path="/workspace" element={<WorkspacePage />} />
        <Route path="/workspace/:id" element={<IdeaDetailPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
