/**
 * UploadZone component: drag-and-drop or click-to-upload for PDF/DOCX files.
 * Shows file name and size after selection, with a loading state during upload.
 */

import { useCallback, useRef, useState } from 'react'

interface UploadZoneProps {
  onUpload: (file: File) => Promise<void>
  isLoading?: boolean
}

const ACCEPTED_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]
const MAX_SIZE_MB = 10

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function UploadZone({ onUpload, isLoading = false }: UploadZoneProps) {
  const [dragging, setDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const validate = (file: File): string | null => {
    if (!ACCEPTED_TYPES.includes(file.type)) {
      return 'Only PDF and DOCX files are supported.'
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      return `File is too large. Maximum size is ${MAX_SIZE_MB} MB.`
    }
    return null
  }

  const handleFile = useCallback(
    async (file: File) => {
      const validationError = validate(file)
      if (validationError) {
        setError(validationError)
        setSelectedFile(null)
        return
      }
      setError(null)
      setSelectedFile(file)
      await onUpload(file)
    },
    [onUpload],
  )

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      setDragging(false)
      const file = e.dataTransfer.files[0]
      if (file) handleFile(file)
    },
    [handleFile],
  )

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  return (
    <div className="w-full">
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => !isLoading && inputRef.current?.click()}
        className={`
          relative border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all
          ${dragging ? 'border-brand-500 bg-brand-50' : 'border-gray-300 hover:border-brand-400 bg-gray-50 hover:bg-gray-100'}
          ${isLoading ? 'cursor-not-allowed opacity-70' : ''}
        `}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={handleInputChange}
          disabled={isLoading}
        />

        {isLoading ? (
          <div className="flex flex-col items-center gap-3">
            <div className="animate-spin text-4xl">⏳</div>
            <p className="text-gray-600 font-medium">Uploading and analysing…</p>
            <p className="text-sm text-gray-400">This may take 30–60 seconds</p>
          </div>
        ) : selectedFile ? (
          <div className="flex flex-col items-center gap-2">
            <span className="text-4xl">📄</span>
            <p className="font-semibold text-gray-800">{selectedFile.name}</p>
            <p className="text-sm text-gray-500">{formatBytes(selectedFile.size)}</p>
            <p className="text-xs text-gray-400 mt-1">Click or drag to replace</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <span className="text-5xl">☁️</span>
            <div>
              <p className="text-gray-700 font-semibold text-lg">
                Drop your contract here
              </p>
              <p className="text-gray-500 text-sm mt-1">
                or <span className="text-brand-500 underline">click to browse</span>
              </p>
            </div>
            <p className="text-xs text-gray-400">PDF or DOCX · Max {MAX_SIZE_MB} MB</p>
          </div>
        )}
      </div>

      {error && (
        <p className="mt-2 text-sm text-red-600 flex items-center gap-1.5">
          <span>⚠</span> {error}
        </p>
      )}
    </div>
  )
}
