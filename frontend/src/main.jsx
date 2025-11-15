import React, { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "./index.css";
import Gallery from "./pages/Gallery";
import Profile from "./pages/Profile";
import ErrorBoundary from "./components/ErrorBoundary";

// ==============================
// 🚀 Маршруты
// ==============================
// Важно: basename должен совпадать с base в vite.config.js и <base href> в index.html
const router = createBrowserRouter(
  [
    { 
      path: "/", 
      element: <Gallery />, // Default to gallery
      errorElement: <ErrorBoundary />
    },
    { 
      path: "/gallery", 
      element: <Gallery />,
      errorElement: <ErrorBoundary />
    },
    { 
      path: "/profile/:telegram_id", 
      element: <Profile />,
      errorElement: <ErrorBoundary />
    },
    {
      path: "*", // Catch all unmatched routes - должен быть последним
      element: <ErrorBoundary />
    }
  ],
  {
    basename: "/webapp", // ❗ ОБЯЗАТЕЛЬНО - должен совпадать с base в vite.config.js
    future: {
      v7_startTransition: true,
      v7_relativeSplatPath: true,
    }
  }
);

// ==============================
// 🔥 Рендер с обработкой ошибок
// ==============================
const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Root element not found");
}

const root = createRoot(rootElement);

// Обработка ошибок на уровне приложения
try {
  root.render(
    <StrictMode>
      <RouterProvider 
        router={router}
        fallbackElement={<ErrorBoundary />}
      />
    </StrictMode>
  );
} catch (error) {
  // Если ошибка при рендере, показываем ErrorBoundary напрямую
  console.error("Fatal error during render:", error);
  root.render(<ErrorBoundary />);
}
