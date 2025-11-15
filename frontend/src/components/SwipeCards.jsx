import { useState } from "react";
import { motion, AnimatePresence, useMotionValue, useTransform } from "framer-motion";
import { useNavigate } from "react-router-dom";
import VisionAvatar from "./VisionAvatar";

export default function SwipeCards({ experts }) {
  const [index, setIndex] = useState(0);
  const [exitDirection, setExitDirection] = useState(0);
  const navigate = useNavigate();

  // ✅ Safety check
  if (!experts || experts.length === 0) {
    return (
      <div className="text-gray-400 text-lg mt-10">
        Нет доступных экспертов
      </div>
    );
  }

  // Карточки-кандидаты
  const current = experts[index];
  const next = experts[(index + 1) % experts.length];

  // ⭐ Предзагрузка следующего фото
  if (next?.photo_url) {
    const prefetchImg = new Image();
    prefetchImg.src = next.photo_url;
  }

  // Порог свайпа
  const swipeConfidenceThreshold = 100;

  const handleSwipe = (_, info) => {
    const swipe = info.offset.x;
    const velocity = info.velocity.x;

    // Учитываем скорость свайпа
    if (Math.abs(swipe) > swipeConfidenceThreshold || Math.abs(velocity) > 500) {
      setExitDirection(swipe > 0 ? 1 : -1);
      setIndex((prev) => (prev + 1) % experts.length);
    }
  };

  const goToProfile = (e) => {
    // Предотвращаем всплытие события
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    
    if (current?.telegram_id) {
      console.log('Navigating to profile:', current.telegram_id);
      navigate(`/profile/${current.telegram_id}`);
    } else {
      console.error('No telegram_id found for expert:', current);
    }
  };

  return (
    <div className="relative flex flex-col items-center w-full mt-6 select-none">
      {/* Индикатор свайпа */}
      <SwipeIndicator />

      {/* Z-stack карточек */}
      <div className="relative w-[92%] max-w-[430px] h-[75vh]">
        {/* Следующая карточка (depth) */}
        <motion.div
          className="
            absolute inset-0 rounded-[32px]
            bg-white/5 backdrop-blur-xl border border-white/5
            shadow-[0_20px_40px_rgba(0,0,0,0.25)]
            flex flex-col items-center justify-center
          "
          initial={{ scale: 0.92, y: 20, opacity: 0.4 }}
          animate={{ scale: 0.95, y: 10, opacity: 0.6 }}
          transition={{ duration: 0.3 }}
        >
          {next && (
            <div className="scale-75 opacity-50">
              <VisionAvatar src={next.photo_url} size={180} />
            </div>
          )}
        </motion.div>

        {/* Текущая карточка */}
        <AnimatePresence initial={false} mode="wait">
          <Card
            key={current.telegram_id}
            expert={current}
            onSwipe={handleSwipe}
            onProfileClick={goToProfile}
            exitDirection={exitDirection}
          />
        </AnimatePresence>
      </div>

      {/* Индикатор прогресса */}
      <div className="flex gap-2 mt-6">
        {experts.map((_, i) => (
          <motion.div
            key={i}
            className={`h-1.5 rounded-full ${
              i === index ? "bg-blue-400 w-8" : "bg-white/20 w-1.5"
            }`}
            initial={false}
            animate={{
              width: i === index ? 32 : 6,
              opacity: i === index ? 1 : 0.3,
            }}
            transition={{ duration: 0.3 }}
          />
        ))}
      </div>
    </div>
  );
}

// Компонент карточки с улучшенными свайпами
function Card({ expert, onSwipe, onProfileClick, exitDirection }) {
  const x = useMotionValue(0);
  const rotate = useTransform(x, [-300, 300], [-15, 15]);
  const opacity = useTransform(x, [-300, -100, 0, 100, 300], [0, 1, 1, 1, 0]);

  return (
    <motion.div
      className="
        absolute inset-0 flex flex-col items-center justify-center rounded-[32px] overflow-hidden
        shadow-[0_25px_80px_rgba(0,0,0,0.4)]
        bg-white/10 backdrop-blur-2xl border border-white/10
        cursor-grab active:cursor-grabbing
      "
      style={{ x, rotate, opacity }}
      drag="x"
      dragConstraints={{ left: -300, right: 300 }}
      dragElastic={0.2}
      onDragEnd={onSwipe}
      initial={{ opacity: 0, scale: 0.9, y: 50, rotate: 0 }}
      animate={{ opacity: 1, scale: 1, y: 0, rotate: 0 }}
      exit={{
        opacity: 0,
        scale: 0.8,
        x: exitDirection * 400,
        rotate: exitDirection * 20,
        transition: { duration: 0.4, ease: "easeInOut" },
      }}
      transition={{
        type: "spring",
        stiffness: 200,
        damping: 25,
      }}
      whileDrag={{ scale: 1.05, zIndex: 10 }}
    >
      {/* Фоновый градиент */}
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/20 via-purple-500/10 to-blue-500/20" />
      
      {/* Круглый аватар в центре */}
      <motion.div
        className="relative z-10 mb-6"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
      >
        <VisionAvatar src={expert.photo_url} size={200} />
      </motion.div>

      {/* Информация */}
      <div className="relative z-10 flex flex-col items-center px-8 pb-8 text-center pointer-events-none">
        <motion.h2
          className="text-3xl font-bold mb-2 drop-shadow-lg"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          {expert.name}
        </motion.h2>

        <motion.p
          className="text-lg text-gray-300 mb-1 font-medium"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.35 }}
        >
          {expert.direction}
        </motion.p>

        {expert.city && (
          <motion.p
            className="text-sm text-gray-400 mb-3"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            📍 {expert.city}
          </motion.p>
        )}

        <motion.span
          className="text-xs font-semibold uppercase tracking-wider text-blue-300 mb-6 px-3 py-1.5 rounded-full bg-blue-500/20 border border-blue-400/30"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.45 }}
        >
          {expert.language}
        </motion.span>

        <motion.button
          className="
            w-full max-w-[280px] py-4 rounded-full text-base font-semibold text-white
            bg-gradient-to-r from-indigo-400 via-blue-500 to-purple-500
            shadow-[0_10px_35px_rgba(80,120,255,0.4)]
            hover:shadow-[0_15px_45px_rgba(80,120,255,0.6)]
            active:scale-95 transition-all
            relative overflow-hidden
            z-20
            cursor-pointer
            pointer-events-auto
          "
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('Button clicked, calling onProfileClick');
            onProfileClick(e);
          }}
          onMouseDown={(e) => {
            // Останавливаем drag при нажатии на кнопку
            e.stopPropagation();
          }}
          onTouchStart={(e) => {
            // Останавливаем drag на мобильных устройствах
            e.stopPropagation();
          }}
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.5 }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <span className="relative z-10 pointer-events-none">Подробнее</span>
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent pointer-events-none"
            initial={{ x: "-100%" }}
            whileHover={{ x: "100%" }}
            transition={{ duration: 0.6 }}
          />
        </motion.button>
      </div>

      {/* Индикаторы направления свайпа */}
      <SwipeHints x={x} />
    </motion.div>
  );
}

// Индикатор направления свайпа
function SwipeHints({ x }) {
  const leftOpacity = useTransform(x, [-100, -50, 0], [0, 0.5, 0]);
  const rightOpacity = useTransform(x, [0, 50, 100], [0, 0.5, 0]);

  return (
    <>
      <motion.div
        className="absolute left-6 top-1/2 -translate-y-1/2 text-4xl pointer-events-none"
        style={{ opacity: leftOpacity }}
      >
        👈
      </motion.div>
      <motion.div
        className="absolute right-6 top-1/2 -translate-y-1/2 text-4xl pointer-events-none"
        style={{ opacity: rightOpacity }}
      >
        👉
      </motion.div>
    </>
  );
}

// Индикатор свайпа вверху
function SwipeIndicator() {
  return (
    <motion.div
      className="text-xs text-gray-400 mb-4 flex items-center gap-2"
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
    >
      <span>Свайпните влево или вправо</span>
      <motion.span
        animate={{ x: [0, 5, 0, -5, 0] }}
        transition={{ duration: 1.5, repeat: Infinity }}
      >
        ↔️
      </motion.span>
    </motion.div>
  );
}
