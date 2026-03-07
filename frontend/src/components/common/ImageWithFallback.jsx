import { useEffect, useState } from "react";

const FALLBACK_IMAGE = "/images/products/default-product.svg";

export default function ImageWithFallback({ src, alt, className = "", ...props }) {
  const [currentSrc, setCurrentSrc] = useState(src || FALLBACK_IMAGE);

  useEffect(() => {
    setCurrentSrc(src || FALLBACK_IMAGE);
  }, [src]);

  return (
    <img
      src={currentSrc}
      alt={alt}
      className={className}
      onError={() => setCurrentSrc(FALLBACK_IMAGE)}
      {...props}
    />
  );
}
