import { motion } from "framer-motion";
import VisionAvatar from "./VisionAvatar";

function ExpertCard({ expert, onOpen }) {
  return (
    <motion.div
      className="
        flex flex-col items-center text-center cursor-pointer select-none
        bg-white/10 backdrop-blur-xl 
        border border-white/10 
        shadow-[0_20px_50px_rgba(0,0,0,0.35)]
        rounded-3xl p-6 w-[240px]
        vision-card
      "
      whileHover={{ scale: 1.05, y: -5 }}
      transition={{ type: "spring", stiffness: 200, damping: 18 }}
      onClick={() => onOpen(expert)}
    >
      {/* VisionOS Avatar */}
      <div className="mb-5">
        <VisionAvatar src={expert.photo_url} size={120} />
      </div>

      {/* Имя */}
      <h2 className="text-xl font-semibold text-white drop-shadow-sm mb-1">
        {expert.name || "Без имени"}
      </h2>

      {/* Направление */}
      <p className="text-sm text-gray-300 leading-tight">
        {expert.direction || "Без направления"}
      </p>

      {/* Город */}
      {expert.city && (
        <p className="text-xs text-gray-500 mt-1">
          {expert.city}
        </p>
      )}

      {/* Язык */}
      <span className="mt-3 text-[10px] font-semibold text-blue-300 uppercase tracking-wide">
        {expert.language}
      </span>
    </motion.div>
  );
}

export default ExpertCard;
