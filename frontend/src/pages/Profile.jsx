import { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import VisionAvatar from "../components/VisionAvatar";
import VisionBackground from "../components/VisionBackground";

export default function Profile() {
  const { telegram_id } = useParams();
  const navigate = useNavigate();

  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);
  const [fullUrl, setFullUrl] = useState(null);
  const [currentUserId, setCurrentUserId] = useState(null);
  const [isOwnProfile, setIsOwnProfile] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [partnershipStatus, setPartnershipStatus] = useState(null);
  const [hasRequestedPartnership, setHasRequestedPartnership] = useState(false);

  const handleBack = useCallback(() => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate("/gallery");
    }
  }, [navigate]);

  // Показываем BackButton в Telegram Mini App
  useEffect(() => {
    if (isOwnProfile) {
      window.Telegram?.WebApp?.BackButton?.hide();
      return;
    }

    const backButton = window.Telegram?.WebApp?.BackButton;
    if (!backButton) {
      return;
    }

    backButton.show();
    const handleTelegramBack = () => handleBack();
    backButton.onClick(handleTelegramBack);

    return () => {
      backButton.offClick?.(handleTelegramBack);
      backButton.hide();
    };
    return () => {
      backButton.offClick?.(handleTelegramBack);
      backButton.hide();
    };
  }, [handleBack, isOwnProfile]);

  // ============================
  // Получаем текущего пользователя из Telegram
  // ============================
  useEffect(() => {
    const getCurrentUserId = () => {
      // Ждем немного, если Telegram WebApp еще не загрузился
      // Способ 1: initDataUnsafe (основной)
      if (window.Telegram?.WebApp?.initDataUnsafe?.user?.id) {
        const userId = String(window.Telegram.WebApp.initDataUnsafe.user.id);
        console.log('✅ Got user ID from initDataUnsafe:', userId);
        return userId;
      }
      
      // Способ 2: initData (парсинг строки)
      if (window.Telegram?.WebApp?.initData) {
        try {
          const params = new URLSearchParams(window.Telegram.WebApp.initData);
          const userStr = params.get('user');
          if (userStr) {
            const user = JSON.parse(userStr);
            if (user.id) {
              const userId = String(user.id);
              console.log('✅ Got user ID from initData:', userId);
              return userId;
            }
          }
        } catch (e) {
          console.warn('Failed to parse initData:', e);
        }
      }
      
      // Способ 3: Проверяем, доступен ли Telegram WebApp вообще
      if (window.Telegram?.WebApp) {
        console.warn('⚠️ Telegram WebApp доступен, но user ID не найден');
        console.log('initDataUnsafe:', window.Telegram.WebApp.initDataUnsafe);
        console.log('initData:', window.Telegram.WebApp.initData);
        console.log('version:', window.Telegram.WebApp.version);
      } else {
        console.error('❌ Telegram WebApp API не доступен! Приложение должно быть открыто через Telegram Mini App.');
      }
      
      return "debug-user"; // fallback для тестирования в браузере
    };
    
    if (!telegram_id) {
      setError("❌ Telegram ID not found in URL");
      setIsLoading(false);
      return;
    }

    // Пытаемся получить ID
    let userId = getCurrentUserId();
    setCurrentUserId(userId);

    const own = String(userId) === String(telegram_id);
    setIsOwnProfile(own);

    if (!own && userId !== "debug-user") {
      const partnershipKey = `partnership_${userId}_${telegram_id}`;
      const requested = localStorage.getItem(partnershipKey) === "sent";
      setHasRequestedPartnership(requested);
    }
    
    // Если не получилось сразу, пробуем еще раз через 200ms (для Telegram Mini App)
    if (userId === "debug-user") {
      const retryTimer = setTimeout(() => {
        const retryUserId = getCurrentUserId();
        if (retryUserId !== "debug-user") {
          setCurrentUserId(retryUserId);
          const own = String(retryUserId) === String(telegram_id);
          setIsOwnProfile(own);
          if (!own) {
            const partnershipKey = `partnership_${retryUserId}_${telegram_id}`;
            const requested = localStorage.getItem(partnershipKey) === "sent";
            setHasRequestedPartnership(requested);
          }
        }
      }, 200);

      return () => clearTimeout(retryTimer);
    }
    
    const url =
      `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/profile/${telegram_id}`;
    setFullUrl(url);

    fetch(url)
      .then((r) => r.json())
      .then((data) => {
        if (data.error) setError(data.error);
        else setProfile(data);
        setIsLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setIsLoading(false);
      });
  }, [telegram_id]);

  // ============================
  // Отправка партнерского запроса
  // ============================
  const handlePartnershipRequest = async (e) => {
    console.log('🚀 handlePartnershipRequest CALLED!', {
      currentUserId,
      telegram_id,
      isOwnProfile,
      hasRequestedPartnership,
      partnershipStatus
    });

    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }

    if (!currentUserId || currentUserId === "debug-user") {
      console.error("❌ Missing currentUserId or debug-user detected:", currentUserId);
      const errorMsg = currentUserId === "debug-user" 
        ? "Ошибка: приложение открыто не через Telegram Mini App. Пожалуйста, откройте приложение через бота в Telegram."
        : "Ошибка: не удалось определить ваш ID. Убедитесь, что вы открыли приложение через Telegram.";
      alert(errorMsg);
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.showAlert(errorMsg);
      }
      return;
    }

    if (isOwnProfile) {
      console.log("⚠️ Own profile, skipping");
      return;
    }
    
    if (hasRequestedPartnership) {
      console.log("⚠️ Already requested");
      return;
    }
    
    if (partnershipStatus === "loading") {
      console.log("⚠️ Already loading");
      return;
    }

    const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

    console.log("📤 Sending request to:", `${API_URL}/api/partnership/request`);
    setPartnershipStatus("loading");

    try {
      const response = await fetch(`${API_URL}/api/partnership/request`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          from_user_id: currentUserId,
          to_user_id: telegram_id,
        }),
      });

      console.log("📥 Response status:", response.status);

      const data = await response.json();

      if (!response.ok) {
        console.error("❌ Ошибка запроса:", data);
        setPartnershipStatus("error");
        setTimeout(() => setPartnershipStatus(null), 3000);
        return;
      }

      // Успешно
      console.log("✅ Request successful:", data);
      const partnershipKey = `partnership_${currentUserId}_${telegram_id}`;
      localStorage.setItem(partnershipKey, "sent");

      setPartnershipStatus("sent");
      setHasRequestedPartnership(true);

      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.showAlert("✅ Предложение отправлено!");
      }

    } catch (err) {
      console.error("❌ Network error:", err);
      setPartnershipStatus("error");
      setTimeout(() => setPartnershipStatus(null), 3000);
    }
  };

  // ============================
  // Ошибка загрузки профиля
  // ============================
  if (error)
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-black text-red-400 font-medium px-6 text-center">
        <VisionBackground />
        <div className="relative z-10">
          <div className="text-xl mb-4">❌ Ошибка загрузки профиля</div>

          <div className="mt-2 text-sm text-gray-300 break-all">
            <b>URL запроса:</b>
            <br />
            {fullUrl}
          </div>

          <div className="mt-4 text-sm text-gray-400">
            <b>Ошибка:</b> {error}
          </div>
        </div>
      </div>
    );

  // ============================
  // Загрузка
  // ============================
  if (isLoading || !profile)
    return (
      <div className="min-h-screen flex items-center justify-center bg-black text-gray-300 font-medium">
        <VisionBackground />
        <div className="relative z-10">⏳ Загрузка профиля...</div>
      </div>
    );

  // ============================
  // UI профиля
  // ============================
  return (
    <motion.div
      className="min-h-screen flex flex-col items-center px-6 py-16 text-white relative"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      style={{ pointerEvents: 'auto' }}
    >
      <VisionBackground />

      <div className="relative z-10 flex flex-col items-center w-full max-w-md" style={{ pointerEvents: 'auto' }}>
        {!isOwnProfile && (
          <div className="w-full flex justify-start mb-4">
            <button
              onClick={handleBack}
              className="
                flex items-center gap-2 px-4 py-2
                rounded-full text-sm font-semibold
                bg-white/10 text-white border border-white/20
                hover:bg-white/20 transition-all
              "
            >
              <span>←</span>
              <span>Назад к галерее</span>
            </button>
          </div>
        )}

        <VisionAvatar src={profile.photo_url} size={140} />

        <h1 className="text-3xl font-semibold mt-6 mb-2 text-center drop-shadow-sm">
          {profile.name}
        </h1>

        <p className="text-gray-300 text-sm text-center mb-10 leading-tight">
          {profile.direction || "—"}
          <br />
          <span className="text-xs text-gray-400">{profile.city}</span>
        </p>

        <motion.div
          className="w-full bg-white/10 backdrop-blur-xl rounded-3xl p-6 shadow-[0_20px_60px_rgba(0,0,0,0.35)] border border-white/10 space-y-4 vision-card"
        >
          <InfoRow label="🎯 Направление" value={profile.direction} />
          <InfoRow label="💼 Опыт" value={profile.experience} />
          <InfoRow label="📚 Образование" value={profile.education} />
          <InfoRow label="💬 Язык" value={profile.language} />
          <InfoRow label="🧠 Методы" value={profile.methods?.join(", ")} />
          <InfoRow label="💡 Форматы" value={profile.formats?.join(", ")} />
          <InfoRow label="📞 Telegram" value={profile.telegram} />
        </motion.div>

        {/* КНОПКА партнёрства */}
        {!isOwnProfile && !hasRequestedPartnership && partnershipStatus !== "sent" && (
          <div className="mt-10 w-full max-w-[320px] relative" style={{ zIndex: 1000 }}>
            <button
              type="button"
              onClick={(e) => {
                console.log('🔵🔵🔵 BUTTON CLICKED!');
                if (e) {
                  e.preventDefault();
                  e.stopPropagation();
                }
                handlePartnershipRequest(e);
              }}
              disabled={partnershipStatus === "loading"}
              className="
                w-full
                bg-gradient-to-r from-green-400 via-emerald-500 to-teal-500
                text-white font-semibold py-5 px-12 rounded-full text-base
                transition-all duration-200
                shadow-[0_0_20px_rgba(16,185,129,0.4)]
                hover:shadow-[0_0_30px_rgba(16,185,129,0.6)]
                hover:scale-105 active:scale-95
                disabled:opacity-50 disabled:cursor-not-allowed
                cursor-pointer
                relative
              "
            >
              {partnershipStatus === "loading" ? "⏳ Отправка..." : "🤝 Предложить партнерство"}
            </button>
          </div>
        )}

        {/* Успешно отправлено */}
        {!isOwnProfile && partnershipStatus === "sent" && (
          <div className="mt-10 text-green-300 text-center text-lg">
            ✅ Предложение отправлено!
          </div>
        )}

        {/* Уже отправлено */}
        {!isOwnProfile && hasRequestedPartnership && partnershipStatus !== "sent" && (
          <div className="mt-10 text-gray-300 text-center text-sm">
            📨 Вы уже отправили предложение партнерства
          </div>
        )}

        <p className="text-gray-500 text-xs mt-10 mb-10">
          PAZL Collab · Vision UI
        </p>
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

