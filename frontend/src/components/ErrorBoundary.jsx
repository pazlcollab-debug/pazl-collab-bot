import React from 'react';
import { useRouteError, useNavigate, useLocation } from 'react-router-dom';
import VisionBackground from './VisionBackground';

export default function ErrorBoundary() {
  let error;
  let navigate;
  let location;
  
  try {
    error = useRouteError();
    navigate = useNavigate();
    location = useLocation();
  } catch (e) {
    // Если хуки не работают, значит роутер не инициализирован
    console.error("Router not initialized:", e);
  }

  let errorMessage = 'Произошла непредвиденная ошибка';
  let errorDetails = '';
  let statusCode = null;

  // Обработка разных типов ошибок
  if (error?.status === 404 || error?.statusText === 'Not Found' || error?.status === 404) {
    statusCode = 404;
    errorMessage = 'Страница не найдена';
    errorDetails = 'Запрашиваемая страница не существует. Попробуйте вернуться в галерею.';
  } else if (error?.status) {
    statusCode = error.status;
    errorMessage = `Ошибка ${error.status}`;
    errorDetails = error.statusText || error.message || '';
  } else if (error?.message) {
    errorMessage = error.message;
    errorDetails = error.stack || '';
  } else if (typeof error === 'string') {
    errorMessage = error;
  } else if (!error && !navigate) {
    // Если роутер не инициализирован
    errorMessage = 'Ошибка инициализации приложения';
    errorDetails = 'Не удалось загрузить приложение. Попробуйте обновить страницу.';
  }

  const handleGoToGallery = () => {
    if (navigate) {
      navigate('/gallery');
    } else {
      window.location.href = '/webapp/gallery';
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-black text-white font-[Manrope] px-6 text-center relative">
      <VisionBackground />
      
      <div className="relative z-10 max-w-md">
        <div className="text-6xl mb-6">⚠️</div>
        
        <h1 className="text-2xl font-bold mb-4 text-red-400">
          {errorMessage}
        </h1>
        
        {errorDetails && (
          <p className="text-gray-400 text-sm mb-6 break-all">
            {errorDetails}
          </p>
        )}

        <div className="space-y-3">
          <button
            onClick={handleGoToGallery}
            className="
              w-full py-3 px-6 rounded-full text-sm font-semibold text-white
              bg-gradient-to-r from-indigo-400 to-blue-500
              shadow-[0_10px_35px_rgba(80,120,255,0.35)]
              hover:shadow-[0_10px_45px_rgba(80,120,255,0.55)]
              active:scale-95 transition-all
            "
          >
            🏠 Вернуться в галерею
          </button>

          <button
            onClick={() => window.location.reload()}
            className="
              w-full py-3 px-6 rounded-full text-sm font-semibold text-white
              bg-white/10 backdrop-blur-xl border border-white/20
              hover:bg-white/20 active:scale-95 transition-all
            "
          >
            🔄 Обновить страницу
          </button>
        </div>

        {process.env.NODE_ENV === 'development' && error?.stack && (
          <details className="mt-6 text-left">
            <summary className="text-gray-500 text-xs cursor-pointer mb-2">
              Детали ошибки (только для разработки)
            </summary>
            <pre className="text-xs text-gray-600 bg-black/50 p-4 rounded overflow-auto max-h-40">
              {error.stack}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
}

