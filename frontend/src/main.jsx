import React, { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import {
  createBrowserRouter,
  RouterProvider,
  useLocation,
} from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";

import "./index.css";
import App from "./App.jsx";
import Profile from "./pages/Profile.jsx";

// ==============================
// 🚀 Маршруты
// ==============================
const router = createBrowserRouter(
  [
    { path: "/", element: <App /> },
    { path: "/profile/:telegram_id", element: <Profile /> },
  ],
  {
    basename: "/webapp", // ❗ ОБЯЗАТЕЛЬНО
  }
);

// ==============================
// 🎨 Обёртка с правильным location
// ==============================
function AnimatedRoutes() {
  const location = useLocation(); // 👈 ВАЖНО!

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname} // теперь работает правильно
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
      >
        <RouterProvider router={router} />
      </motion.div>
    </AnimatePresence>
  );
}

// ==============================
// 🔥 Рендер
// ==============================
createRoot(document.getElementById("root")).render(
  <StrictMode>
    <RouterProvider router={router}>
      <AnimatedRoutes />
    </RouterProvider>
  </StrictMode>
);
