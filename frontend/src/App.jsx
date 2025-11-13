import { BrowserRouter, Routes, Route } from "react-router-dom";
import Gallery from "./pages/Gallery";
import Profile from "./pages/Profile";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ✅ Галерея экспертов — для кнопки "Найти партнёра" */}
        <Route path="/webapp/gallery" element={<Gallery />} />

        {/* ✅ Профиль — для кнопки "Мой профиль" */}
        <Route path="/webapp/profile/:telegram_id" element={<Profile />} />

        {/* ✅ Fallback: любой другой путь → в галерею */}
        <Route path="*" element={<Gallery />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
