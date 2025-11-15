import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import VisionBackground from "../components/VisionBackground";
import SwipeCards from "../components/SwipeCards";
import SwipeSkeleton from "../components/SwipeSkeleton";
import "../App.css";

export default function Gallery() {
  const [experts, setExperts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetch(`${API_URL}/api/experts`)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        if (data && Array.isArray(data.experts)) {
          setExperts(data.experts);
        } else {
          console.error("Invalid API response:", data);
          setExperts([]);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Ошибка загрузки:", err);
        let errorMessage = err.message;
        
        // Улучшенная обработка ошибок
        if (err.message.includes("Failed to fetch") || err.message.includes("NetworkError")) {
          errorMessage = "Не удалось подключиться к серверу. Проверьте подключение к интернету.";
        } else if (err.message.includes("429")) {
          errorMessage = "Слишком много запросов. Попробуйте позже.";
        } else if (err.message.includes("500")) {
          errorMessage = "Ошибка на сервере. Попробуйте позже.";
        }
        
        setError(errorMessage);
        setExperts([]);
        setLoading(false);
      });
  }, [API_URL]);

  return (
    <div className="relative min-h-screen flex flex-col items-center text-white font-[Manrope] overflow-hidden">
      <VisionBackground />

      <div className="relative z-[2] w-full flex flex-col items-center pt-16">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-4xl sm:text-5xl font-extrabold mb-10 tracking-tight
                     bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-500
                     bg-clip-text text-transparent drop-shadow-md"
        >
          Галерея экспертов
        </motion.h1>

        {loading ? (
          <SwipeSkeleton />
        ) : error ? (
          <div className="text-center mt-10 max-w-md px-6">
            <div className="text-6xl mb-4">⚠️</div>
            <h2 className="text-xl font-semibold text-red-400 mb-2">
              Ошибка загрузки
            </h2>
            <p className="text-gray-400 text-sm mb-6">
              {error.includes("Failed to fetch") || error.includes("NetworkError")
                ? "Не удалось подключиться к серверу. Проверьте подключение к интернету."
                : error.includes("404")
                ? "Сервер не найден. Попробуйте позже."
                : error.includes("500")
                ? "Ошибка на сервере. Попробуйте позже."
                : `Произошла ошибка: ${error}`}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="
                py-2 px-6 rounded-full text-sm font-semibold text-white
                bg-gradient-to-r from-indigo-400 to-blue-500
                shadow-[0_10px_35px_rgba(80,120,255,0.35)]
                hover:shadow-[0_10px_45px_rgba(80,120,255,0.55)]
                active:scale-95 transition-all
              "
            >
              🔄 Попробовать снова
            </button>
          </div>
        ) : experts.length === 0 ? (
          <div className="text-center mt-10 max-w-md px-6">
            <div className="text-6xl mb-4">🔍</div>
            <h2 className="text-xl font-semibold text-gray-300 mb-2">
              Нет доступных экспертов
            </h2>
            <p className="text-gray-400 text-sm">
              В данный момент в галерее нет анкет экспертов. Попробуйте позже.
            </p>
          </div>
        ) : (
          <SwipeCards experts={experts} />
        )}
      </div>
    </div>
  );
}
