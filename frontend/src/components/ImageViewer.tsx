import React, { useState } from 'react';
import { Download, Maximize2, X } from 'lucide-react';

interface ImageViewerProps {
  src: string;
  alt: string;
}

export function ImageViewer({ src, alt }: ImageViewerProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleDownload = async () => {
    try {
      const response = await fetch(src);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `visualization-${Date.now()}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading image:', error);
    }
  };

  return (
    <div className="relative group">
      <img 
        src={src} 
        alt={alt} 
        className="max-w-full rounded-lg shadow-lg"
      />
      
      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <div className="flex gap-2 bg-white/90 backdrop-blur-sm rounded-lg p-1 shadow-lg">
          <button
            onClick={handleDownload}
            className="p-1.5 hover:bg-gray-100 rounded-md transition-colors"
            title="Download image"
          >
            <Download className="w-4 h-4 text-gray-700" />
          </button>
          <button
            onClick={() => setIsExpanded(true)}
            className="p-1.5 hover:bg-gray-100 rounded-md transition-colors"
            title="Expand image"
          >
            <Maximize2 className="w-4 h-4 text-gray-700" />
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="relative max-w-[90vw] max-h-[90vh]">
            <button
              onClick={() => setIsExpanded(false)}
              className="absolute -top-4 -right-4 p-2 bg-white rounded-full shadow-lg hover:bg-gray-100 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
            <img 
              src={src} 
              alt={alt} 
              className="max-w-full max-h-[90vh] object-contain rounded-lg"
            />
          </div>
        </div>
      )}
    </div>
  );
}