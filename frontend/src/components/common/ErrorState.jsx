import MD3Button from "../ui/MD3Button";
import MD3Card from "../ui/MD3Card";

export default function ErrorState({ title = "加载失败", message, actionLabel = "重试", onRetry, className = "" }) {
  return (
    <MD3Card className={`border border-[var(--md-error)]/20 bg-[var(--md-error-container)] ${className}`} hoverable={false}>
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="font-medium text-[var(--md-error)]">{title}</p>
          <p className="mt-1 text-sm text-[var(--md-error)]/90">{message}</p>
        </div>
        {onRetry ? (
          <MD3Button variant="outlined" className="border-[var(--md-error)] text-[var(--md-error)]" onClick={onRetry}>
            {actionLabel}
          </MD3Button>
        ) : null}
      </div>
    </MD3Card>
  );
}
