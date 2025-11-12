import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import "./index.css";
import App from "./App.jsx";
import Profile from "./pages/Profile.jsx";

// --- Контейнер с анимацией страниц ---
function AnimatedRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
      >
        <RouterProvider router={router} location={location} />
      </motion.div>
    </AnimatePresence>
  );
}

// --- маршруты ---
const router = createBrowserRouter([
  { path: "/", element: <App /> },
  { path: "/profile/:telegram_id", element: <Profile /> },
]);

// --- рендер ---
createRoot(document.getElementById("root")).render(
  <StrictMode>
    <AnimatedRoutes />
  </StrictMode>
);
