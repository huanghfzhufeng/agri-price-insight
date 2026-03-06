export default function MD3Card({ children, className = "", hoverable = true }) {
  return (
    <section
      className={[
        "rounded-[24px] border border-white/60 bg-[var(--md-surface-container)] p-6 shadow-sm backdrop-blur-sm",
        hoverable ? "transition-all duration-300 hover:-translate-y-1 hover:shadow-soft" : "",
        className,
      ].join(" ")}
    >
      {children}
    </section>
  );
}
