import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { motion } from "framer-motion";

export default function Profile() {
  const { telegram_id } = useParams();

  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);
  const [fullUrl, setFullUrl] = useState(null); // ⭐ Показываем реальный URL

  useEffect(() => {
    if (!telegram_id) {
      setError("❌ Telegram ID not found in URL");
      return;
    }

    const url = `${import.meta.env.VITE_API_URL}/api/profile/${telegram_id}`;
    setFullUrl(url);

    console.log("📡 Запрос к API:", url);

    fetch(url)
      .then((res) => res.json())
      .then((data) => {
        console.log("📥 Ответ API:", data);
        if (data.error) setError(data.error);
        else setProfile(data);
      })
      .catch((err) => {
        console.error("❌ Fetch error:", err);
        setError(err.message);
      });
  }, [telegram_id]);

  // ❌ Ошибка загрузки
  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-900 to-blue-950 text-red-400 font-medium px-6 text-center">

        <div className="text-xl mb-4">❌ Ошибка загрузки профиля</div>

        <div className="mt-2 text-sm text-gray-300 break-all">
          <b>URL запроса:</b><br />
          {fullUrl}
        </div>

        <div className="mt-4 text-sm text-gray-400">
          <b>Ошибка:</b> {error}
        </div>
      </div>
    );
  }

  // ⏳ Профиль ещё грузится
  if (!profile)
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 to-blue-950 text-gray-300 font-medium">
        ⏳ Загрузка профиля...
      </div>
    );

  // 🎉 Профиль загружен
  return (
    <motion.div
      className="min-h-screen bg-gradient-to-br from-gray-900 to-blue-950 flex flex-col items-center px-4 py-8 text-white"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      {/* Фото */}
      {profile.photo_url ? (
        <motion.img
          src={profile.photo_url}
          alt="Фото эксперта"
          className="w-20 h-20 rounded-full shadow-xl border-2 border-white object-cover mb-3"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.6 }}
        />
      ) : (
        <div className="w-20 h-20 rounded-full bg-gray-600 flex items-center justify-center text-2xl mb-3">
          👤
        </div>
      )}

      {/* Имя */}
      <h1 className="text-xl font-bold mb-1">{profile.name}</h1>
      <p className="text-gray-400 mb-5 text-center text-sm">
        {profile.direction || "—"} · {profile.city || "Не указан город"}
      </p>

      {/* Карточка */}
      <motion.div
        className="bg-white/10 backdrop-blur-md rounded-2xl p-4 w-full max-w-md border border-white/20 shadow-lg space-y-2"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <InfoRow label="🎯 Направление" value={profile.direction} />
        <InfoRow label="💼 Опыт" value={profile.experience} />
        <InfoRow label="📚 Образование" value={profile.education} />
        <InfoRow label="💬 Язык" value={profile.language} />
        <InfoRow label="📞 Telegram" value={profile.telegram} />
        <InfoRow label="🧠 Методы" value={profile.methods?.join(", ")} />
        <InfoRow label="💡 Форматы" value={profile.formats?.join(", ")} />
      </motion.div>

      <motion.button
        className="mt-5 bg-gradient-to-r from-purple-500 to-indigo-500 text-white font-semibold py-2 px-5 rounded-full shadow-md hover:shadow-lg transition-all text-sm"
        onClick={() => alert("Функция редактирования скоро будет доступна.")}
        whileTap={{ scale: 0.97 }}
      >
        ✏️ Редактировать профиль
      </motion.button>

      <p className="text-gray-500 text-xs mt-6">PAZL Collab · Mini App Beta</p>
    </motion.div>
  );
}

function InfoRow({ label, value }) {
  if (!value) return null;
  return (
    <div className="flex justify-between items-start text-sm">
      <span className="text-gray-200">{label}</span>
      <span className="text-gray-100 text-right max-w-[60%]">{value}</span>
    </div>
  );
}
