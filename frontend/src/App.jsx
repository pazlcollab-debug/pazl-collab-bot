import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ExpertCard from "./components/ExpertCard";
import "./App.css"; // обязательно подключено!

function App() {
  const [experts, setExperts] = useState([]);
  const [selectedExpert, setSelectedExpert] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/experts")
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

  const getTelegramUrl = (username) => {
    if (!username) return null;
    const clean = username.trim();
    if (clean.startsWith("http")) return clean;
    const name = clean.replace("@", "");
    return `https://t.me/${name}`;
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-start text-white py-16 font-[Manrope] overflow-x-hidden relative bg-animate">
      {/* Заголовок */}
      <motion.h1
        initial={{ opacity: 0, y: -25 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="text-5xl font-extrabold mb-16 tracking-tight bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-500 bg-clip-text text-transparent drop-shadow-md"
      >
        Каталог экспертов
      </motion.h1>

      {/* Сетка карточек */}
      {loading ? (
        <p className="text-gray-400 text-lg">Загрузка данных...</p>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-16 gap-y-40 w-11/12 max-w-6xl place-items-center"
        >
          {experts.map((exp) => (
            <ExpertCard key={exp.id} expert={exp} onOpen={setSelectedExpert} />
          ))}
        </motion.div>
      )}

      {/* Модалка */}
      <AnimatePresence>
        {selectedExpert && (
          <motion.div
            className="fixed inset-0 flex items-center justify-center bg-black/70 backdrop-blur-sm z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedExpert(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 30 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 30 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
              onClick={(e) => e.stopPropagation()}
              className="relative bg-[#111] rounded-3xl p-8 w-[90%] max-w-[380px] shadow-[0_0_40px_rgba(100,100,255,0.3)] border border-gray-800 text-center"
            >
              <button
                onClick={() => setSelectedExpert(null)}
                className="absolute top-3 right-4 text-gray-400 hover:text-white transition-colors text-2xl"
              >
                ✕
              </button>

              <div className="flex flex-col items-center mt-4 space-y-[6px] leading-[1.15]">
                <div
                  className="rounded-full overflow-hidden shadow-lg ring-2 ring-indigo-500/50 mb-4 hover:ring-blue-400/80 transition-all duration-300"
                  style={{ width: "140px", height: "140px" }}
                >
                  <img
                    src={selectedExpert.photo_url || "/default-avatar.jpg"}
                    alt={selectedExpert.name}
                    className="w-full h-full object-cover"
                  />
                </div>

                <h2 className="text-xl font-semibold text-white drop-shadow-sm">
                  {selectedExpert.name}
                </h2>
                <p className="text-sm text-gray-300">{selectedExpert.direction}</p>
                <p className="text-xs text-gray-500">{selectedExpert.city}</p>
                <span className="text-[10px] font-semibold text-blue-400 uppercase tracking-wide">
                  {selectedExpert.language}
                </span>

                {getTelegramUrl(selectedExpert.telegram) ? (
                  <a
                    href={getTelegramUrl(selectedExpert.telegram)}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-4 inline-block bg-gradient-to-r from-blue-500 to-indigo-600 text-white text-sm 
                               font-medium py-2 px-6 rounded-full shadow-md hover:shadow-blue-500/40 hover:scale-105 
                               transition-all duration-300"
                  >
                    Связаться в Telegram
                  </a>
                ) : (
                  <p className="text-xs text-gray-500 mt-3">
                    Telegram не указан или ссылка некорректна
                  </p>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
