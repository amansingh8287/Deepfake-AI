import { useDropzone } from "react-dropzone";
import clsx from "clsx";

interface UploadZoneProps {
  accept: Record<string, string[]>;
  label: string;
  helper: string;
  onFileSelected: (file: File) => void;
}

export function UploadZone({ accept, label, helper, onFileSelected }: UploadZoneProps) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    multiple: false,
    accept,
    onDrop: (files) => {
      if (files[0]) {
        onFileSelected(files[0]);
      }
    }
  });

  return (
    <div
      {...getRootProps()}
      className={clsx(
        "glass cursor-pointer rounded-3xl border border-dashed p-8 text-center transition",
        isDragActive ? "border-glow bg-cyan-400/10" : "border-white/15 hover:border-white/30"
      )}
    >
      <input {...getInputProps()} />
      <p className="font-display text-2xl text-white">{label}</p>
      <p className="mt-3 text-sm text-slate-400">{helper}</p>
    </div>
  );
}

