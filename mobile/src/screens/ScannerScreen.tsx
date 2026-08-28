import React, { useState, useEffect } from 'react';
import { Text, View, StyleSheet, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { Camera, CameraView } from 'expo-camera';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../../App';
import { api } from '../services/api';
import { X } from 'lucide-react-native';

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'Scanner'>;
};

export function ScannerScreen({ navigation }: Props) {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [scanned, setScanned] = useState(false);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    const getCameraPermissions = async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    };
    getCameraPermissions();
  }, []);

  const handleBarCodeScanned = async ({ type, data }: { type: string; data: string }) => {
    setScanned(true);
    setProcessing(true);
    
    // Assumimos que o QR Code na latinha/geladeira tem o ID do Produto.
    // Exemplo do QR Code: "PRODUTO_ID:3" ou apenas "3"
    const produtoId = parseInt(data.replace(/\D/g, ''), 10);
    
    if (isNaN(produtoId)) {
      Alert.alert("QR Code Inválido", "Este código não pertence a um produto Barix.", [
        { text: "Tentar Novamente", onPress: () => setScanned(false) }
      ]);
      setProcessing(false);
      return;
    }

    try {
      // Chama a rota Honesty Market (Self-Checkout)
      const res = await api.post('/checkout/honesty-market', {
        produto_id: produtoId,
        quantidade: 1
      });
      
      Alert.alert("Sucesso! 🍻", `${res.data.mensagem}\nSaldo restante: R$ ${res.data.recibo.saldo_restante.toFixed(2)}`, [
        { text: "Voltar para Carteira", onPress: () => navigation.replace('Wallet') }
      ]);
    } catch (err: any) {
      Alert.alert("Erro", err.response?.data?.detail || "Falha na comunicação com o Bar.", [
        { text: "OK", onPress: () => setScanned(false) }
      ]);
    } finally {
      setProcessing(false);
    }
  };

  if (hasPermission === null) {
    return <SafeAreaView style={styles.container}><Text style={styles.text}>Solicitando permissão da câmera...</Text></SafeAreaView>;
  }
  if (hasPermission === false) {
    return <SafeAreaView style={styles.container}><Text style={styles.text}>Sem acesso à câmera.</Text></SafeAreaView>;
  }

  return (
    <SafeAreaView style={styles.container}>
      <CameraView
        onBarcodeScanned={scanned ? undefined : handleBarCodeScanned}
        barcodeScannerSettings={{
          barcodeTypes: ["qr", "ean13", "ean8", "pdf417"],
        }}
        style={StyleSheet.absoluteFillObject}
      />
      
      {/* Overlay Escuro com Furo Transparente */}
      <View style={styles.overlay}>
        <View style={styles.topOverlay}>
          <TouchableOpacity style={styles.closeBtn} onPress={() => navigation.goBack()}>
            <X color="#fff" size={24} />
          </TouchableOpacity>
          <Text style={styles.title}>Alinhe o QR Code</Text>
        </View>
        <View style={styles.middleOverlay}>
          <View style={styles.sideOverlay} />
          <View style={styles.focusedArea}>
            <View style={[styles.corner, styles.cornerTL]} />
            <View style={[styles.corner, styles.cornerTR]} />
            <View style={[styles.corner, styles.cornerBL]} />
            <View style={[styles.corner, styles.cornerBR]} />
          </View>
          <View style={styles.sideOverlay} />
        </View>
        <View style={styles.bottomOverlay}>
          {processing && (
            <View style={styles.processingBox}>
              <ActivityIndicator color="#3b82f6" size="large" />
              <Text style={styles.processingText}>Processando compra...</Text>
            </View>
          )}
        </View>
      </View>
    </SafeAreaView>
  );
}

const overlayColor = 'rgba(0,0,0,0.7)';
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  text: { color: '#fff', textAlign: 'center', marginTop: 100 },
  overlay: { ...StyleSheet.absoluteFillObject, justifyContent: 'center', alignItems: 'center' },
  topOverlay: { flex: 1, backgroundColor: overlayColor, width: '100%', alignItems: 'center', paddingTop: 20 },
  bottomOverlay: { flex: 1, backgroundColor: overlayColor, width: '100%', justifyContent: 'center', alignItems: 'center' },
  middleOverlay: { flexDirection: 'row', width: '100%', height: 250 },
  sideOverlay: { flex: 1, backgroundColor: overlayColor },
  focusedArea: { width: 250, height: 250, backgroundColor: 'transparent' },
  closeBtn: { position: 'absolute', top: 20, right: 20, padding: 10 },
  title: { color: '#fff', fontSize: 18, fontWeight: 'bold', marginTop: 40 },
  corner: { position: 'absolute', width: 30, height: 30, borderColor: '#3b82f6', borderWidth: 4 },
  cornerTL: { top: 0, left: 0, borderRightWidth: 0, borderBottomWidth: 0, borderTopLeftRadius: 16 },
  cornerTR: { top: 0, right: 0, borderLeftWidth: 0, borderBottomWidth: 0, borderTopRightRadius: 16 },
  cornerBL: { bottom: 0, left: 0, borderRightWidth: 0, borderTopWidth: 0, borderBottomLeftRadius: 16 },
  cornerBR: { bottom: 0, right: 0, borderLeftWidth: 0, borderTopWidth: 0, borderBottomRightRadius: 16 },
  processingBox: { backgroundColor: 'rgba(255,255,255,0.9)', padding: 20, borderRadius: 16, alignItems: 'center' },
  processingText: { color: '#333', fontWeight: 'bold', marginTop: 10 }
});
