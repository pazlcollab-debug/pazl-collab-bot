import { useEffect, useRef } from "react";

export default function VisionBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const dots = [];

    const getDotsCount = () => {
      const area = width * height;
      // ~1 точка на каждые 14k px, но не более 140
      return Math.min(140, Math.max(70, Math.round(area / 14000)));
    };

    const createDots = () => {
      dots.length = 0;
      const DOTS_COUNT = getDotsCount();
      for (let i = 0; i < DOTS_COUNT; i++) {
        dots.push({
          x: Math.random() * width,
          y: Math.random() * height,
          baseSize: 1.4 + Math.random() * 2.2,
          alpha: 0.25 + Math.random() * 0.45,
          dx: (Math.random() - 0.5) * 0.6, // скорость
          dy: (Math.random() - 0.5) * 0.6,
          pulseOffset: Math.random() * Math.PI * 2,
          pulseSpeed: 0.5 + Math.random() * 0.7,
        });
      }
    };

    createDots();

    // ��������� (�������� ��� ��������� ������)
    let parallaxX = 0;
    let parallaxY = 0;

    const handleMove = (e) => {
      const x = e.touches ? e.touches[0].clientX : e.clientX;
      const y = e.touches ? e.touches[0].clientY : e.clientY;

      parallaxX = (x / window.innerWidth - 0.5) * 16;
      parallaxY = (y / window.innerHeight - 0.5) * 16;
    };

    window.addEventListener("mousemove", handleMove);
    window.addEventListener("touchmove", handleMove);

    // ��������
    function render() {
      const time = Date.now() * 0.001;
      ctx.clearRect(0, 0, width, height);

      dots.forEach((dot) => {
        dot.x += dot.dx;
        dot.y += dot.dy;

        if (dot.x < 0) dot.x = width;
        if (dot.x > width) dot.x = 0;
        if (dot.y < 0) dot.y = height;
        if (dot.y > height) dot.y = 0;

        const pulse =
          0.85 + Math.sin(time * dot.pulseSpeed + dot.pulseOffset) * 0.25;
        const size = dot.baseSize * pulse;

        ctx.beginPath();
        ctx.arc(dot.x + parallaxX, dot.y + parallaxY, size, 0, Math.PI * 2);

        const gradient = ctx.createRadialGradient(
          dot.x, dot.y, 0,
          dot.x, dot.y, size * 3
        );

        gradient.addColorStop(0, `rgba(255,255,255,${dot.alpha})`);
        gradient.addColorStop(1, "rgba(255,255,255,0)");

        ctx.fillStyle = gradient;
        ctx.fill();
      });

      requestAnimationFrame(render);
    }

    render();

    // Resize
    const handleResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
      createDots();
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("mousemove", handleMove);
      window.removeEventListener("touchmove", handleMove);
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 w-full h-full pointer-events-none z-[0] opacity-60"
    />
  );
}
