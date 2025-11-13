import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import VisionBackground from "../components/VisionBackground";
import SwipeCards from "../components/SwipeCards";
import SwipeSkeleton from "../components/SwipeSkeleton";
import "../App.css";

export default function Gallery() {
  const [experts, setExperts] = useState([]);
  const [loading, setLoading] = useState(true);

  const API_URL = import.meta.env.VITE_API_URL;

  useEffect(() => {
    fetch(`${API_URL}/api/experts`)
      .then((res) => res.json())
      .then((data) => {
        setExperts(data.experts || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Ошибка загрузки:", err);
        setLoading(false);
      });
  }, []);

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
          Каталог экспертов
        </motion.h1>

        {loading ? (
          <SwipeSkeleton />
        ) : experts.length === 0 ? (
          <p className="text-gray-400 text-lg mt-10">
            Нет доступных экспертов
          </p>
        ) : (
          <SwipeCards experts={experts} />
        )}
      </div>
    </div>
  );
}
