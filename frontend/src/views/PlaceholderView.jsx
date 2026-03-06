import { Settings } from "lucide-react";

import MD3Card from "../components/ui/MD3Card";

export default function PlaceholderView({ title, description }) {
  return (
    <div className="page-enter flex min-h-[70vh] items-center justify-center">
      <MD3Card className="max-w-2xl text-center" hoverable={false}>
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-[var(--md-primary-container)] text-[var(--md-on-primary-container)]">
          <Settings size={30} />
        </div>
        <h1 className="mb-3 text-3xl font-medium text-[#1C1B1F]">{title}</h1>
        <p className="leading-7 text-[#49454F]">{description}</p>
      </MD3Card>
    </div>
  );
}
