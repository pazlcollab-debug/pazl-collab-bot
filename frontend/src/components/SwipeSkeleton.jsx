import React from "react";

export default function SwipeSkeleton() {
  return (
    <div className="relative flex flex-col items-center w-full mt-10 select-none">
      <div className="relative w-[92%] max-w-[430px] h-[75vh]">
        <div
          className="
            absolute inset-0 rounded-[32px] overflow-hidden
            bg-white/8 backdrop-blur-2xl border border-white/10
            shadow-[0_25px_80px_rgba(0,0,0,0.4)]
            flex flex-col
          "
        >
          {/* Top image placeholder */}
          <div className="w-full h-[60%] bg-gradient-to-b from-white/10 to-white/5 skeleton-shimmer" />

          {/* Bottom glass panel */}
          <div className="w-full h-[40%] px-6 py-6 flex flex-col justify-between bg-white/5 border-t border-white/10">
            <div className="space-y-3">
              <div className="h-5 w-2/3 rounded-full bg-white/15 skeleton-shimmer" />
              <div className="h-3 w-1/2 rounded-full bg-white/10 skeleton-shimmer" />
              <div className="h-3 w-1/3 rounded-full bg-white/10 skeleton-shimmer" />
              <div className="h-2 w-1/4 rounded-full bg-white/8 skeleton-shimmer" />
            </div>

            <div className="h-11 w-full rounded-full bg-white/12 skeleton-shimmer mt-4" />
          </div>
        </div>
      </div>
    </div>
  );
}
