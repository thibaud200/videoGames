// components/SafeImage.tsx
"use client";

import { useState, useEffect } from 'react';
import Image, { type ImageProps } from 'next/image';

// On étend les props de l'image Next.js pour y ajouter notre fallback
interface SafeImageProps extends ImageProps {
  fallbackSrc: string;
}

const SafeImage = (props: SafeImageProps) => {
  const { src, fallbackSrc, alt, ...rest } = props;
  const [imgSrc, setImgSrc] = useState(src);

  // Si la source principale (props.src) change, on met à jour l'état
  useEffect(() => {
    setImgSrc(src);
  }, [src]);

  return (
    <Image
      {...rest}
      alt={alt} // alt est obligatoire pour l'accessibilité
      src={imgSrc}
      onError={() => {
        // En cas d'erreur (image cassée), on utilise l'image de secours
        setImgSrc(fallbackSrc);
      }}
    />
  );
};

export default SafeImage;