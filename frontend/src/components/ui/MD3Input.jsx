export default function MD3Input({
  label,
  placeholder,
  type = "text",
  icon: Icon,
  value,
  onChange,
  list,
  className = "",
}) {
  return (
    <label className={`block w-full ${className}`}>
      <span className="mb-2 block text-sm font-medium text-[#49454F]">{label}</span>
      <div className="flex items-center rounded-2xl border border-transparent bg-[var(--md-surface-container-low)] px-4 py-3 transition-all duration-300 focus-within:border-[var(--md-primary)] focus-within:bg-white">
        {Icon ? <Icon className="mr-3 h-5 w-5 text-[#49454F]" /> : null}
        <input
          type={type}
          list={list}
          value={value}
          onChange={onChange}
          placeholder={placeholder || label}
          className="w-full border-0 bg-transparent text-[#1C1B1F] outline-none placeholder:text-[#49454F]/70"
        />
      </div>
    </label>
  );
}
