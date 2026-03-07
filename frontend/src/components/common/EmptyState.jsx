import MD3Card from "../ui/MD3Card";

export default function EmptyState({ title, description, className = "" }) {
  return (
    <MD3Card className={`border border-dashed border-[var(--md-outline)]/30 bg-white/40 ${className}`} hoverable={false}>
      <div className="py-8 text-center">
        <p className="text-lg font-medium text-[#1C1B1F]">{title}</p>
        <p className="mt-2 text-sm text-[#49454F]">{description}</p>
      </div>
    </MD3Card>
  );
}
