import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  motion,
  AnimatePresence,
  useMotionValue,
  useTransform,
} from "framer-motion";

function Profile() {
  const { telegram_id } = useParams();
  const navigate = useNavigate();
  const [experts, setExperts] = useState([]);
  const [index, setIndex] = useState(0);
  const [loading, setLoading] = useState(true);

  // Загружаем всех экспертов
  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/experts?limit=50")
      .then((res) => res.json())
      .then((data) => {
        const list = data.experts || [];
        setExperts(list);
        const idx = list.findIndex(
          (e) => e.telegram === telegram_id || e.id === telegram_id
        );
        setIndex(idx >= 0 ? idx : 0);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Ошибка загрузки:", err);
        setLoading(false);
      });
  }, [telegram_id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-400 bg-gray-950">
        Загрузка профиля...
      </div>
    );
  }

  const expert = experts[index];
  if (!expert) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-gray-400 bg-gray-950 space-y-4">
        <p>❌ Профиль не найден</p>
        <button
          onClick={() => navigate(-1)}
          className="px-5 py-2 rounded-full bg-gray-800 hover:bg-gray-700 text-white transition"
        >
          ← Назад
        </button>
      </div>
    );
  }

  // Перелистывание
  const handleSwipe = (direction) => {
    if (direction === "left" && index < experts.length - 1) {
      setIndex(index + 1);
    } else if (direction === "right" && index > 0) {
      setIndex(index - 1);
    }
  };

  // Motion эффекты
  const x = useMotionValue(0);

  // Свечение
  const glow = useTransform(
    x,
    [-150, 0, 150],
    [
      "0 0 40px rgba(59,130,246,0.25)", // слева
      "0 0 0px rgba(0,0,0,0)", // центр
      "0 0 40px rgba(147,51,234,0.3)", // справа
    ]
  );

  // Динамический градиентный блик
  const gloss = useTransform(
    x,
    [-150, 0, 150],
    [
      "linear-gradient(120deg, rgba(59,130,246,0.2) 0%, rgba(255,255,255,0) 70%)",
      "linear-gradient(120deg, rgba(255,255,255,0.05) 30%, rgba(255,255,255,0.02) 70%)",
      "linear-gradient(240deg, rgba(147,51,234,0.2) 0%, rgba(255,255,255,0) 70%)",
    ]
  );

  const variants = {
    enter: (direction) => ({
      x: direction > 0 ? 200 : -200,
      opacity: 0,
    }),
    center: { x: 0, opacity: 1 },
    exit: (direction) => ({
      x: direction < 0 ? 200 : -200,
      opacity: 0,
    }),
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-950 flex flex-col items-center justify-center text-white px-4 relative overflow-hidden">
      {/* Кнопка Назад */}
      <button
        onClick={() => navigate(-1)}
        className="absolute top-6 left-6 bg-gray-800/70 hover:bg-gray-700/90 text-white px-4 py-2 rounded-full shadow-md transition-all duration-300 z-10"
      >
        ← Назад
      </button>

      {/* Контейнер карточек */}
      <div className="w-full max-w-sm h-[520px] flex items-center justify-center relative">
        <AnimatePresence custom={index}>
          <motion.div
            key={expert.id}
            custom={index}
            variants={variants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{
              x: { type: "spring", stiffness: 300, damping: 30 },
              opacity: { duration: 0.2 },
            }}
            drag="x"
            dragConstraints={{ left: 0, right: 0 }}
            dragElastic={0.6}
            style={{
              x,
              boxShadow: glow,
              backgroundImage: gloss,
              backgroundBlendMode: "screen",
            }}
            onDragEnd={(e, { offset, velocity }) => {
              const swipe =
                Math.abs(offset.x) > 100 && Math.abs(velocity.x) > 100;
              if (swipe) handleSwipe(offset.x < 0 ? "left" : "right");
            }}
            className="absolute bg-gray-800/40 p-6 rounded-3xl shadow-2xl w-full border border-gray-700 text-center backdrop-blur-md transition-all duration-300"
          >
            {/* Фото */}
            <motion.div
              animate={{ scale: [1, 1.03, 1] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
              className="w-32 h-32 rounded-full overflow-hidden mx-auto mb-4 ring-2 ring-blue-500/50 shadow-lg"
            >
              <img
                src={expert.photo_url || "/default-avatar.jpg"}
                alt={expert.name}
                className="w-full h-full object-cover"
              />
            </motion.div>

            {/* Имя и направление */}
            <h1 className="text-2xl font-semibold">{expert.name}</h1>
            <p className="text-blue-400 text-sm mt-1">
              {expert.direction || "Без направления"}
            </p>

            {/* Остальная информация */}
            <div className="mt-4 space-y-1 text-sm text-gray-300">
              <p>🌍 {expert.city || "Город не указан"}</p>
              <p>💬 {expert.language?.toUpperCase() || "RU"}</p>
            </div>

            {/* Telegram-кнопка */}
            {expert.telegram && (
              <a
                href={`https://t.me/${expert.telegram.replace("@", "")}`}
                target="_blank"
                rel="noreferrer"
                className="mt-6 inline-block bg-gradient-to-r from-blue-500 to-indigo-600 text-white py-2 px-6 rounded-full shadow-md hover:shadow-blue-500/40 hover:scale-105 transition-transform duration-300"
              >
                Связаться в Telegram
              </a>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Индикатор карточек */}
      <div className="mt-6 flex space-x-2">
        {experts.slice(0, 6).map((_, i) => (
          <div
            key={i}
            className={`w-2 h-2 rounded-full transition-all ${
              i === index ? "bg-blue-400 w-3" : "bg-gray-600"
            }`}
          />
        ))}
      </div>
    </div>
  );
}

export default Profile;
