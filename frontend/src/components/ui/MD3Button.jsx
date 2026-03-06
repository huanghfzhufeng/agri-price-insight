export default function MD3Button({
  children,
  variant = "filled",
  className = "",
  icon,
  onClick,
  type = "button",
}) {
  const baseStyle =
    "relative inline-flex items-center justify-center gap-2 overflow-hidden rounded-full px-6 py-2.5 text-sm font-medium transition-all duration-300 ease-[cubic-bezier(0.2,0,0,1)] active:scale-[0.98]";

  const variants = {
    filled: "bg-[var(--md-primary)] text-[var(--md-on-primary)] shadow-sm hover:shadow-md hover:brightness-95",
    tonal:
      "bg-[var(--md-secondary-container)] text-[var(--md-on-secondary-container)] hover:bg-[var(--md-primary-container)]/70",
    outlined:
      "border border-[var(--md-outline)] bg-transparent text-[var(--md-primary)] hover:bg-[var(--md-primary)]/5",
    text: "bg-transparent px-4 text-[var(--md-primary)] hover:bg-[var(--md-primary)]/8",
  };

  return (
    <button type={type} className={`${baseStyle} ${variants[variant]} ${className}`} onClick={onClick}>
      <span className="pointer-events-none absolute inset-0 bg-black/0 transition-colors duration-200 active:bg-black/10" />
      {icon ? <span className="relative z-10 flex h-4 w-4 items-center justify-center">{icon}</span> : null}
      <span className="relative z-10">{children}</span>
    </button>
  );
}
