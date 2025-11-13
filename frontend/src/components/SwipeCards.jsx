import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";

export default function SwipeCards({ experts }) {
  const [index, setIndex] = useState(0);
  const navigate = useNavigate();

  // Карточки-кандидаты
  const current = experts[index];
  const next = experts[(index + 1) % experts.length];

  // ⭐ Предзагрузка следующего фото
  if (next?.photo_url) {
    const prefetchImg = new Image();
    prefetchImg.src = next.photo_url;
  }

  // Порог свайпа
  const swipeConfidenceThreshold = 120;

  const handleSwipe = (_, info) => {
    const swipe = info.offset.x;

    if (Math.abs(swipe) > swipeConfidenceThreshold) {
      setIndex((prev) => (prev + 1) % experts.length);
    }
  };

  const goToProfile = () => {
    navigate(`/webapp/profile/${current.telegram_id}`);
  };

  return (
    <div className="relative flex flex-col items-center w-full mt-10 select-none">

      {/* Z-stack карточек */}
      <div className="relative w-[92%] max-w-[430px] h-[75vh]">

        {/* Следующая карточка (depth) */}
        <div
          className="
            absolute inset-0 rounded-[32px]
            bg-white/5 backdrop-blur-xl border border-white/5
            shadow-[0_20px_40px_rgba(0,0,0,0.25)]
            scale-[0.92] translate-y-5
          "
        >
          {next && (
            <img
              src={next.photo_url}
              alt=""
              loading="lazy"
              draggable="false"
              className="w-full h-[60%] object-cover rounded-t-[32px] opacity-40 fade-in-image"
            />
          )}
        </div>

        {/* Текущая карточка */}
        <AnimatePresence initial={false}>
          <motion.div
            key={current.telegram_id}
            className="
              absolute inset-0 flex flex-col rounded-[32px] overflow-hidden
              shadow-[0_25px_80px_rgba(0,0,0,0.4)]
              bg-white/10 backdrop-blur-2xl border border-white/10
            "
            drag="x"
            dragConstraints={{ left: 0, right: 0 }}
            dragElastic={0.25}
            onDragEnd={handleSwipe}
            initial={{ opacity: 0, scale: 0.95, y: 40 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{
              opacity: 0,
              scale: 0.9,
              x: 300,
              transition: { duration: 0.35 },
            }}
            transition={{
              type: "spring",
              stiffness: 180,
              damping: 22,
            }}
          >
            {/* Фото */}
           <div className="w-full h-[60%] overflow-hidden relative">
  
  {/* ⭐ fade-in */}
  <img
    src={current.photo_url}
    alt={current.name}
    draggable="false"
    className="w-full h-full object-cover fade-in-image"
  />

  <div className="absolute inset-0 bg-gradient-to-b from-white/20 to-transparent opacity-30" />
  <div className="absolute bottom-0 h-1/3 w-full bg-gradient-to-t from-black/30 to-transparent" />
</div>



            {/* Нижняя стеклянная панель */}
            <div className="flex flex-col justify-between w-full h-[40%] px-6 py-6">
              <div className="space-y-1">
                <h2 className="text-2xl font-semibold drop-shadow-sm">
                  {current.name}
                </h2>
                <p className="text-sm text-gray-300">{current.direction}</p>
                <p className="text-xs text-gray-400">{current.city}</p>
                <span className="text-[10px] font-semibold uppercase tracking-wide text-blue-300">
                  {current.language}
                </span>
              </div>

              <button
                className="
                  w-full mt-4 py-3 rounded-full text-sm font-semibold text-white
                  bg-gradient-to-r from-indigo-400 to-blue-500
                  shadow-[0_10px_35px_rgba(80,120,255,0.35)]
                  hover:shadow-[0_10px_45px_rgba(80,120,255,0.55)]
                  active:scale-95 transition-all
                "
                onClick={goToProfile}
              >
                Подробнее
              </button>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
