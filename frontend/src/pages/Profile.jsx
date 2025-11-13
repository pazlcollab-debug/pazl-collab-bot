import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { motion } from "framer-motion";
import VisionAvatar from "../components/VisionAvatar";
import VisionBackground from "../components/VisionBackground";

export default function Profile() {
  const { telegram_id } = useParams();

  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);
  const [fullUrl, setFullUrl] = useState(null);

  useEffect(() => {
    if (!telegram_id) {
      setError("❌ Telegram ID not found in URL");
      return;
    }

    const url = `${import.meta.env.VITE_API_URL}/api/profile/${telegram_id}`;
    setFullUrl(url);

    fetch(url)
      .then((res) => res.json())
      .then((data) => {
        if (data.error) setError(data.error);
        else setProfile(data);
      })
      .catch((err) => setError(err.message));
  }, [telegram_id]);

  // ❌ Ошибка
  if (error)
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-black text-red-400 font-medium px-6 text-center">
        <VisionBackground />
        <div className="relative z-10">
          <div className="text-xl mb-4">❌ Ошибка загрузки профиля</div>

          <div className="mt-2 text-sm text-gray-300 break-all">
            <b>URL запроса:</b><br />
            {fullUrl}
          </div>

          <div className="mt-4 text-sm text-gray-400">
            <b>Ошибка:</b> {error}
          </div>
        </div>
      </div>
    );

  // ⏳ Загрузка
  if (!profile)
    return (
      <div className="min-h-screen flex items-center justify-center bg-black text-gray-300 font-medium">
        <VisionBackground />
        <div className="relative z-10">⏳ Загрузка профиля...</div>
      </div>
    );

  // 🎉 Готово
  return (
    <motion.div
      className="
        min-h-screen 
        flex flex-col items-center 
        px-6 py-16 
        text-white
        relative
      "
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      {/* Фон VisionOS */}
      <VisionBackground />

      {/* Контент поверх */}
      <div className="relative z-10 flex flex-col items-center w-full max-w-md">

        {/* ⭐ VisionOS Avatar */}
        <VisionAvatar src={profile.photo_url} size={140} />

        {/* ⭐ Имя */}
        <h1 className="text-3xl font-semibold mt-6 mb-2 text-center drop-shadow-sm">
          {profile.name}
        </h1>

        {/* ⭐ Подзаголовок */}
        <p className="text-gray-300 text-sm text-center mb-10 leading-tight">
          {profile.direction || "—"}
          <br />
          <span className="text-xs text-gray-400">{profile.city}</span>
        </p>

        {/* ⭐ VisionOS Glass Card */}
        <motion.div
          className="
            w-full
            bg-white/10
            backdrop-blur-xl
            rounded-3xl
            p-6
            shadow-[0_20px_60px_rgba(0,0,0,0.35)]
            border border-white/10
            space-y-4
            vision-card
          "
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <InfoRow label="🎯 Направление" value={profile.direction} />
          <InfoRow label="💼 Опыт" value={profile.experience} />
          <InfoRow label="📚 Образование" value={profile.education} />
          <InfoRow label="💬 Язык" value={profile.language} />
          <InfoRow label="🧠 Методы" value={profile.methods?.join(", ")} />
          <InfoRow label="💡 Форматы" value={profile.formats?.join(", ")} />
          <InfoRow label="📞 Telegram" value={profile.telegram} />
        </motion.div>

        {/* ⭐ Кнопка */}
        <motion.button
          className="
            mt-10 
            bg-gradient-to-r from-indigo-400 to-blue-500 
            text-white font-semibold 
            py-3 px-10 
            rounded-full 
            shadow-[0_10px_30px_rgba(80,120,255,0.35)]
            hover:shadow-[0_10px_40px_rgba(80,120,255,0.45)]
            transition-all
            text-sm
          "
          onClick={() => alert("Редактирование скоро будет доступно")}
          whileTap={{ scale: 0.97 }}
        >
          ✏️ Редактировать профиль
        </motion.button>

        <p className="text-gray-500 text-xs mt-10 mb-10">PAZL Collab · VisionOS UI</p>
      </div>
    </motion.div>
  );
}

function InfoRow({ label, value }) {
  if (!value) return null;

  return (
    <div className="flex justify-between items-start text-sm gap-4">
      <span className="text-gray-200">{label}</span>
      <span className="text-gray-100 text-right flex-1 break-words">
        {value}
      </span>
    </div>
  );
}
