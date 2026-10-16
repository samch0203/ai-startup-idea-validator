import { NavLink, Outlet } from "react-router-dom";
import { config } from "../config.js";

function Logo() {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" aria-hidden="true">
      <rect width="28" height="28" rx="6" fill="#12233a" />
      <path d="M7 14.5l4.5 4.5L21 9" fill="none" stroke="#fff" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
      <rect x="7" y="22" width="14" height="2.2" rx="1.1" fill="#ffd84d" />
    </svg>
  );
}

export default function Layout() {
  return (
    <>
      <a className="skip" href="#main">
        Skip to content
      </a>
      <header className="site-header">
        <div className="wrap bar">
          <NavLink to="/" className="brand">
            <Logo />
            <span>Idea Validator</span>
          </NavLink>
          <nav className="site-nav" aria-label="Main">
            <NavLink to="/" end>
              Submit idea
            </NavLink>
            <NavLink to="/workspace">Workspace</NavLink>
          </nav>
        </div>
      </header>

      {config.useMock && (
        <div className="notice-bar">
          Demo mode: results are sample data. Set VITE_USE_MOCK=false in .env to use the backend.
        </div>
      )}

      <main id="main" className="wrap main">
        <Outlet />
      </main>

      <footer className="wrap site-footer">
        AI Startup Idea Validator. Reports are decision support, not proof that an idea will succeed.
      </footer>
    </>
  );
}
