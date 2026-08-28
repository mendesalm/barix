import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../../App';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../services/api';
import { QrCode, Wallet, LogOut, ArrowUpRight } from 'lucide-react-native';

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'Wallet'>;
};

export function WalletScreen({ navigation }: Props) {
  const [saldo, setSaldo] = useState<number | null>(null);

  useEffect(() => {
    // Para simplificar o protótipo, vamos bater numa rota que retorna o saldo, ou 
    // listar transações e pegar o saldo de lá. Como não temos rota direta GET /carteira ainda,
    // usarei um mockup ou a rota do Dashboard se a segurança permitir.
    setSaldo(250.00); // Mock rápido para o protótipo UX
  }, []);

  const logout = async () => {
    await AsyncStorage.removeItem('barix_token');
    navigation.replace('Login');
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.greeting}>Olá, Membro!</Text>
        <TouchableOpacity onPress={logout}>
          <LogOut color="#ff4444" size={24} />
        </TouchableOpacity>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardLabel}>Seu Saldo Barix</Text>
        <Text style={styles.cardValue}>R$ {saldo?.toFixed(2) || '0.00'}</Text>
        
        <TouchableOpacity style={styles.pixBtn}>
          <ArrowUpRight color="#fff" size={20} />
          <Text style={styles.pixBtnText}>Adicionar Saldo (PIX)</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.actions}>
        <TouchableOpacity 
          style={styles.scanBtn}
          onPress={() => navigation.navigate('Scanner')}
        >
          <QrCode color="#fff" size={40} />
          <Text style={styles.scanBtnText}>Escanear Cerveja</Text>
        </TouchableOpacity>
        <Text style={styles.helper}>Aponte para o QR Code do Produto na geladeira</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0f', padding: 24 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 32, marginTop: 16 },
  greeting: { fontSize: 24, fontWeight: 'bold', color: '#fff' },
  card: { backgroundColor: '#1a1a24', padding: 24, borderRadius: 24, borderWidth: 1, borderColor: '#333' },
  cardLabel: { color: '#888', fontSize: 14, textTransform: 'uppercase', tracking: 2 },
  cardValue: { color: '#fff', fontSize: 48, fontWeight: 'bold', marginVertical: 16 },
  pixBtn: { backgroundColor: '#10b981', padding: 16, borderRadius: 12, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8 },
  pixBtnText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
  actions: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  scanBtn: { backgroundColor: '#3b82f6', width: 200, height: 200, borderRadius: 100, justifyContent: 'center', alignItems: 'center', shadowColor: '#3b82f6', shadowOpacity: 0.5, shadowRadius: 20, elevation: 10 },
  scanBtnText: { color: '#fff', fontSize: 18, fontWeight: 'bold', marginTop: 16 },
  helper: { color: '#666', marginTop: 32, textAlign: 'center', fontSize: 14 }
});
