import React from "react";

export default function VisionAvatar({ src, size = 120 }) {
  return (
    <div
      className="
        relative
        flex items-center justify-center
        rounded-full
        overflow-hidden
        shadow-[0px_20px_40px_rgba(0,0,0,0.35)]
        backdrop-blur-xl
        ring-1 ring-white/20
        after:absolute after:inset-0
        after:rounded-full
        after:bg-gradient-to-br after:from-white/15 after:to-white/5
        after:pointer-events-none
      "
      style={{
        width: size,
        height: size,
      }}
    >
      {/* внутреннее м€гкое свечение (VisionOS glow ring) */}
      <div
        className="
          absolute inset-[-12%]
          rounded-full
          blur-2xl
          opacity-40
          bg-gradient-to-br
          from-white/30 to-indigo-300/30
        "
      />

      {/* ‘ото */}
      <img
        src={src || "/default-avatar.jpg"}
        alt="avatar"
        className="relative z-10 w-full h-full object-cover rounded-full"
      />

      {/* верхний м€гкий блик Ч как стекло VisionOS */}
      <div
        className="
          absolute inset-0 rounded-full
          bg-gradient-to-b from-white/40 to-transparent
          opacity-20 pointer-events-none
        "
      />

      {/* нижний внутренний блик */}
      <div
        className="
          absolute bottom-0 h-1/3 w-full
          bg-gradient-to-t from-black/30 to-transparent
          opacity-40 pointer-events-none
        "
      />
    </div>
  );
}
