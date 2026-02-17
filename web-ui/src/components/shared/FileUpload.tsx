import React, { useCallback, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, File, X, Check } from 'lucide-react';
import { cn, formatFileSize, validateFileExtension } from '@/lib/utils';

interface FileUploadProps {
  accept: string[];
  multiple?: boolean;
  maxSize?: number;
  onFilesSelected: (files: File[]) => void;
  currentFiles?: File[];
  onRemoveFile?: (index: number) => void;
  className?: string;
}

export function FileUpload({
  accept,
  multiple = false,
  maxSize = 10 * 1024 * 1024,
  onFilesSelected,
  currentFiles = [],
  onRemoveFile,
  className,
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateFiles = useCallback(
    (files: FileList | File[]): File[] | null => {
      const fileArray = Array.from(files);

      // Check file count
      if (!multiple && fileArray.length > 1) {
        setError('Only one file is allowed');
        return null;
      }

      // Check file extensions
      for (const file of fileArray) {
        if (!validateFileExtension(file.name, accept)) {
          setError(`Invalid file type. Accepted: ${accept.join(', ')}`);
          return null;
        }

        // Check file size
        if (file.size > maxSize) {
          setError(`File ${file.name} exceeds maximum size of ${formatFileSize(maxSize)}`);
          return null;
        }
      }

      setError(null);
      return fileArray;
    },
    [accept, maxSize, multiple]
  );

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const files = validateFiles(e.dataTransfer.files);
      if (files) {
        onFilesSelected(files);
      }
    },
    [validateFiles, onFilesSelected]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files) {
        const files = validateFiles(e.target.files);
        if (files) {
          onFilesSelected(files);
        }
      }
    },
    [validateFiles, onFilesSelected]
  );

  return (
    <div className={cn('space-y-4', className)}>
      <motion.div
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          'relative border-2 border-dashed rounded-2xl p-12 transition-all cursor-pointer',
          'hover:border-primary-400 hover:bg-primary-50/30',
          isDragging
            ? 'border-primary-500 bg-primary-100/50 scale-[1.02]'
            : 'border-slate-300 bg-slate-50/50'
        )}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        <input
          type="file"
          accept={accept.join(',')}
          multiple={multiple}
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />

        <div className="flex flex-col items-center justify-center text-center space-y-4">
          <motion.div
            animate={{
              y: isDragging ? -10 : 0,
              scale: isDragging ? 1.1 : 1,
            }}
            transition={{ duration: 0.2 }}
            className={cn(
              'p-4 rounded-full',
              isDragging ? 'bg-primary-100' : 'bg-slate-200'
            )}
          >
            <Upload
              className={cn(
                'w-8 h-8',
                isDragging ? 'text-primary-600' : 'text-slate-600'
              )}
            />
          </motion.div>

          <div>
            <p className="text-lg font-medium text-slate-900 mb-1">
              {isDragging ? 'Drop your file here' : 'Drag & drop or click to upload'}
            </p>
            <p className="text-sm text-slate-500">
              Accepted: {accept.join(', ')} • Max {formatFileSize(maxSize)}
            </p>
          </div>
        </div>
      </motion.div>

      {error && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="p-4 bg-red-50 border border-red-200 rounded-xl"
        >
          <p className="text-sm text-red-700">{error}</p>
        </motion.div>
      )}

      {currentFiles.length > 0 && (
        <div className="space-y-2">
          <AnimatePresence>
            {currentFiles.map((file, index) => (
              <motion.div
                key={`${file.name}-${index}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="flex items-center justify-between p-4 bg-white border border-slate-200 rounded-xl shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="p-2 bg-primary-100 rounded-lg">
                    <File className="w-5 h-5 text-primary-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900 truncate">
                      {file.name}
                    </p>
                    <p className="text-xs text-slate-500">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                  <div className="p-1.5 bg-green-100 rounded-full">
                    <Check className="w-4 h-4 text-green-600" />
                  </div>
                </div>

                {onRemoveFile && (
                  <button
                    onClick={() => onRemoveFile(index)}
                    className="ml-3 p-2 hover:bg-red-50 rounded-lg transition-colors group"
                  >
                    <X className="w-4 h-4 text-slate-400 group-hover:text-red-600" />
                  </button>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
