import React, { useEffect, useRef, useState } from 'react';
import { Html5Qrcode } from 'html5-qrcode';
import { Camera, RefreshCw, X, QrCode, AlertCircle, Barcode } from 'lucide-react';

interface LeitorQrCameraModalProps {
  aberto: boolean;
  aoFechar: () => void;
  aoLerCodigo: (codigo: string) => void;
  titulo?: string;
  subtitulo?: string;
}

export const LeitorQrCameraModal: React.FC<LeitorQrCameraModalProps> = ({
  aberto,
  aoFechar,
  aoLerCodigo,
  titulo = 'Escanear QR Code ou Código de Barras',
  subtitulo = 'Aponte a câmera para o QR Code da embalagem (GS1) ou código de barras'
}) => {
  const [erroCamera, setErroCamera] = useState<string | null>(null);
  const [iniciando, setIniciando] = useState(false);
  const [cameras, setCameras] = useState<{ id: string; label: string }[]>([]);
  const [cameraIdx, setCameraIdx] = useState(0);
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const lidoRef = useRef(false);
  const containerId = 'barix-qr-camera-reader';

  const pararScanner = async () => {
    const scanner = scannerRef.current;
    if (scanner) {
      try {
        if (scanner.isScanning) {
          await scanner.stop();
        }
        scanner.clear();
      } catch {
        // Ignora erro ao parar câmera já desligada
      }
      scannerRef.current = null;
    }
  };

  useEffect(() => {
    if (!aberto) {
      pararScanner();
      return;
    }

    lidoRef.current = false;
    setErroCamera(null);
    setIniciando(true);

    let cancelado = false;

    const iniciar = async () => {
      try {
        await pararScanner();
        if (cancelado) return;

        const elemento = document.getElementById(containerId);
        if (!elemento) return;

        const scanner = new Html5Qrcode(containerId);
        scannerRef.current = scanner;

        let listaCameras: { id: string; label: string }[] = [];
        try {
          listaCameras = await Html5Qrcode.getCameras();
          if (!cancelado && listaCameras.length > 0) {
            setCameras(listaCameras);
          }
        } catch {
          // Segue com facingMode environment
        }

        const config = {
          fps: 15,
          qrbox: { width: 260, height: 260 },
          aspectRatio: 1.0
        };

        const onScan = (decodedText: string) => {
          if (lidoRef.current || !decodedText) return;
          lidoRef.current = true;
          try {
            if (navigator.vibrate) navigator.vibrate(100);
          } catch {
            // Ignora se vibração não suportada
          }
          pararScanner().finally(() => {
            aoLerCodigo(decodedText.trim());
            aoFechar();
          });
        };

        if (listaCameras.length > 0) {
          // Prioriza câmera traseira se for a primeira seleção
          let idxEscolhido = cameraIdx % listaCameras.length;
          if (cameraIdx === 0 && listaCameras.length > 1) {
            const backIdx = listaCameras.findIndex((c) =>
              /back|traseira|rear|environment/i.test(c.label)
            );
            if (backIdx >= 0) idxEscolhido = backIdx;
          }
          await scanner.start(
            listaCameras[idxEscolhido].id,
            config,
            onScan,
            () => {}
          );
        } else {
          await scanner.start(
            { facingMode: 'environment' },
            config,
            onScan,
            () => {}
          );
        }
      } catch (err: any) {
        if (!cancelado) {
          setErroCamera(
            'Não foi possível acessar a câmera. Verifique as permissões do navegador ou dispositivo.'
          );
        }
      } finally {
        if (!cancelado) setIniciando(false);
      }
    };

    const timer = setTimeout(iniciar, 150);

    return () => {
      cancelado = true;
      clearTimeout(timer);
      pararScanner();
    };
  }, [aberto, cameraIdx]);

  if (!aberto) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[100] p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl overflow-hidden border border-gray-100 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-gradient-to-r from-purple-50 to-blue-50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-600 text-white flex items-center justify-center shadow-sm">
              <Camera className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-gray-900">{titulo}</h3>
              <p className="text-[11px] text-gray-500">{subtitulo}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={aoFechar}
            className="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Visor da Câmera */}
        <div className="p-4 space-y-3">
          <div className="relative rounded-2xl overflow-hidden bg-black min-h-[280px] flex items-center justify-center">
            <div id={containerId} className="w-full h-full" />

            {iniciando && !erroCamera && (
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-900/90 text-white gap-3">
                <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
                <span className="text-xs font-semibold uppercase tracking-wider text-purple-200">
                  Iniciando câmera...
                </span>
              </div>
            )}

            {erroCamera && (
              <div className="p-6 text-center space-y-2 text-white">
                <AlertCircle className="w-10 h-10 text-red-400 mx-auto" />
                <p className="text-xs text-red-200 leading-relaxed">{erroCamera}</p>
              </div>
            )}
          </div>

          <div className="flex items-center justify-between gap-2 pt-1">
            <div className="flex items-center gap-1.5 text-xs text-gray-500">
              <QrCode className="w-4 h-4 text-purple-600" />
              <Barcode className="w-4 h-4 text-blue-600" />
              <span>Leitura automática ao centralizar o código</span>
            </div>

            {cameras.length > 1 && (
              <button
                type="button"
                onClick={() => setCameraIdx((prev) => prev + 1)}
                className="px-3 py-1.5 rounded-xl bg-gray-100 hover:bg-gray-200 text-xs font-semibold text-gray-700 flex items-center gap-1.5 transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Alternar Câmera</span>
              </button>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-gray-100 bg-gray-50 flex justify-end">
          <button
            type="button"
            onClick={aoFechar}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-200 bg-white border border-gray-200 transition-colors shadow-xs"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
};

export default LeitorQrCameraModal;
