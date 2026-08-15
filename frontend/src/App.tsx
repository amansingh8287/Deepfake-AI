import { NavLink, Route, Routes } from "react-router-dom";
import { ShieldCheckIcon } from "@heroicons/react/24/solid";
import { DashboardPage } from "./pages/DashboardPage";
import { DetectPage } from "./pages/DetectPage";
import { HistoryPage } from "./pages/HistoryPage";
import { AboutPage } from "./pages/AboutPage";

const navItems = [
  { path: "/", label: "Dashboard" },
  { path: "/image", label: "Image Detection" },
  { path: "/video", label: "Video Detection" },
  { path: "/history", label: "History" },
  { path: "/about", label: "About" }
];

export default function App() {
  return (
    <div className="min-h-screen bg-hero-mesh text-white">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-6 md:px-6 xl:flex-row xl:gap-8">
        <aside className="glass mb-6 rounded-[2rem] border border-white/10 p-6 shadow-glass xl:mb-0 xl:w-80 xl:self-start">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-cyan-300/15 p-3 text-cyan-200">
              <ShieldCheckIcon className="h-8 w-8" />
            </div>
            <div>
              <div className="font-display text-2xl">DeepGuard AI</div>
              <div className="text-sm text-slate-400">Deepfake Image & Video Detection</div>
            </div>
          </div>

          <nav className="mt-8 space-y-2">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === "/"}
                className={({ isActive }) =>
                  `block rounded-2xl px-4 py-3 text-sm transition ${
                    isActive ? "bg-cyan-300 text-slate-950" : "text-slate-300 hover:bg-white/5"
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </aside>

        <main className="flex-1 py-2">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/image" element={<DetectPage type="image" />} />
            <Route path="/video" element={<DetectPage type="video" />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/about" element={<AboutPage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

