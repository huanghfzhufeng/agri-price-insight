export default function MD3Badge({
  children,
  color = "primary",
  active = false,
  onClick,
  className = "",
}) {
  const colors = {
    primary: "bg-[var(--md-primary-container)] text-[var(--md-on-primary-container)]",
    error: "bg-[var(--md-error-container)] text-[var(--md-error)]",
    success: "bg-[var(--md-success-container)] text-[var(--md-success)]",
    neutral: "bg-white/70 text-[#49454F]",
  };

  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        "rounded-full px-3 py-1 text-xs font-medium transition-all duration-300",
        colors[color],
        active ? "ring-2 ring-[var(--md-primary)] ring-offset-2 ring-offset-[var(--md-background)]" : "",
        onClick ? "cursor-pointer hover:-translate-y-0.5" : "cursor-default",
        className,
      ].join(" ")}
    >
      {children}
    </button>
  );
}
