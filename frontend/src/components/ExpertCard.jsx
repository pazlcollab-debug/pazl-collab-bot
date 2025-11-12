import { motion } from "framer-motion";

function ExpertCard({ expert, onOpen }) {
  return (
    <motion.div
      className="flex flex-col items-center text-center cursor-pointer select-none"
      whileHover={{ scale: 1.06 }}
      transition={{ type: "spring", stiffness: 220, damping: 14 }}
      onClick={() => onOpen(expert)}
    >
      <div
        className="rounded-full overflow-hidden shadow-xl ring-2 ring-transparent hover:ring-indigo-500/70 
                   hover:shadow-indigo-500/40 transition-all duration-300 mb-3"
        style={{ width: "180px", height: "180px" }}
      >
        <img
          src={expert.photo_url || "/default-avatar.jpg"}
          alt={expert.name}
          className="w-full h-full object-cover"
        />
      </div>

      <div className="leading-[1.05] space-y-[2px]">
        <h2 className="text-lg font-semibold text-white">{expert.name || "Без имени"}</h2>
        <p className="text-sm text-gray-400">{expert.direction || "Без направления"}</p>
        {expert.city && <p className="text-xs text-gray-500">{expert.city}</p>}
        <span className="block text-[10px] font-semibold text-blue-400 uppercase tracking-wide">
          {expert.language}
        </span>
      </div>
    </motion.div>
  );
}

export default ExpertCard;
