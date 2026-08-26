import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Plus, CreditCard, ShoppingCart, CheckCircle, X, Search } from 'lucide-react';

interface ItemComanda {
  id: number;
  produto_id: number;
  quantidade: number;
  valor_unitario: number;
}

interface Comanda {
  id: number;
  nome_cliente?: string;
  identificador_cartao?: string;
  status: 'ABERTA' | 'FECHADA' | 'CANCELADA';
  data_abertura: string;
  total?: number;
  itens: ItemComanda[];
}

interface Produto {
  id: number;
  nome: string;
  preco_venda: number;
  quantidade_estoque: number;
}

export function Comandas() {
  const [comandas, setComandas] = useState<Comanda[]>([]);
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [loading, setLoading] = useState(true);

  // Estados dos Modais
  const [isModalNovaOpen, setIsModalNovaOpen] = useState(false);
  const [comandaSelecionada, setComandaSelecionada] = useState<Comanda | null>(null);

  // Formulário Nova Comanda
  const [nomeCliente, setNomeCliente] = useState('');
  const [identificadorCartao, setIdentificadorCartao] = useState('');

  // Formulário Adicionar Item
  const [produtoSelecionadoId, setProdutoSelecionadoId] = useState('');
  const [quantidadeItem, setQuantidadeItem] = useState('1');

  useEffect(() => {
    carregarDados();
  }, []);

  const carregarDados = async () => {
    try {
      const [respComandas, respProdutos] = await Promise.all([
        api.get('/comandas/'),
        api.get('/produtos/')
      ]);
      setComandas(respComandas.data);
      setProdutos(respProdutos.data.filter((p: Produto) => p.quantidade_estoque > 0)); // Só mostra produtos em estoque
    } catch (error) {
      console.error("Erro ao carregar dados", error);
    } finally {
      setLoading(false);
    }
  };

  const abrirNovaComanda = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/comandas/', {
        nome_cliente: nomeCliente,
        identificador_cartao: identificadorCartao
      });
      setIsModalNovaOpen(false);
      setNomeCliente(''); setIdentificadorCartao('');
      carregarDados();
    } catch (error: any) {
      alert(error.response?.data?.detail || "Erro ao abrir comanda.");
    }
  };

  const adicionarItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!comandaSelecionada) return;
    try {
      await api.post(`/comandas/${comandaSelecionada.id}/itens`, {
        produto_id: parseInt(produtoSelecionadoId),
        quantidade: parseInt(quantidadeItem)
      });
      
      // Atualizar os dados e focar na comanda atual
      const resp = await api.get(`/comandas/${comandaSelecionada.id}`);
      setComandaSelecionada(resp.data);
      setProdutoSelecionadoId(''); setQuantidadeItem('1');
      carregarDados(); // Atualiza a lista principal de fundo
    } catch (error: any) {
      alert(error.response?.data?.detail || "Erro ao adicionar item.");
    }
  };

  const fecharComanda = async (comanda_id: number) => {
    if (!window.confirm("Deseja fechar esta conta e registrar a receita no financeiro?")) return;
    
    try {
      await api.patch(`/comandas/${comanda_id}/fechar`);
      setComandaSelecionada(null);
      carregarDados();
    } catch (error: any) {
      alert(error.response?.data?.detail || "Erro ao fechar comanda.");
    }
  };

  const getProdutoNome = (id: number) => {
    const prod = produtos.find(p => p.id === id);
    return prod ? prod.nome : `Produto #${id}`;
  };

  return (
    <div className="flex flex-col lg:flex-row h-[calc(100vh-8rem)] lg:h-[calc(100vh-4rem)] gap-6 lg:gap-0">
      
      {/* Coluna Esquerda: Lista de Comandas */}
      <div className="w-full lg:w-1/2 lg:pr-6 flex flex-col border-b lg:border-b-0 lg:border-r border-gray-200 h-1/2 lg:h-full pb-6 lg:pb-0">
        <div className="flex justify-between items-center mb-6 shrink-0">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Comandas</h1>
            <p className="text-gray-500">Mesa e Controle de Pedidos</p>
          </div>
          <button 
            onClick={() => setIsModalNovaOpen(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium flex items-center space-x-2 hover:bg-blue-700 transition-colors shadow-sm"
          >
            <Plus size={20} />
            <span className="hidden sm:inline">Abrir Conta</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto pr-2 space-y-4 pb-10">
          {loading ? (
            <div className="text-center text-gray-400 py-10">Carregando comandas...</div>
          ) : comandas.length === 0 ? (
            <div className="text-center text-gray-400 py-10">Nenhuma comanda encontrada.</div>
          ) : (
            comandas.map(comanda => (
              <div 
                key={comanda.id}
                onClick={() => setComandaSelecionada(comanda)}
                className={`bg-white p-4 rounded-xl shadow-sm border transition-all cursor-pointer hover:shadow-md ${comandaSelecionada?.id === comanda.id ? 'border-blue-500 ring-1 ring-blue-500' : 'border-gray-200'}`}
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center space-x-2">
                    <CreditCard className="text-blue-500" size={20} />
                    <span className="font-bold text-lg text-gray-800">{comanda.identificador_cartao || `Mesa/Cartão #${comanda.id}`}</span>
                  </div>
                  <span className={`px-2.5 py-1 text-xs font-bold rounded-full ${comanda.status === 'ABERTA' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                    {comanda.status}
                  </span>
                </div>
                <div className="flex justify-between items-end">
                  <div className="text-sm text-gray-500">
                    Cliente: {comanda.nome_cliente || 'Não informado'} <br/>
                    Abertura: {new Date(comanda.data_abertura).toLocaleTimeString()}
                  </div>
                  <div className="text-xl font-bold text-gray-800">
                    R$ {(comanda.total || 0).toFixed(2)}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Coluna Direita: Detalhes e PDV */}
      <div className="w-full lg:w-1/2 lg:pl-6 flex flex-col h-1/2 lg:h-full bg-gray-50 rounded-xl p-4 lg:p-6 shadow-inner lg:shadow-none">
        {comandaSelecionada ? (
          <div className="flex flex-col h-full">
            <div className="flex justify-between items-center mb-6 shrink-0 border-b border-gray-200 pb-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-800">Cartão: {comandaSelecionada.identificador_cartao || comandaSelecionada.id}</h2>
                <p className="text-gray-500">Cliente: {comandaSelecionada.nome_cliente || 'N/A'}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Total a Pagar</p>
                <p className="text-3xl font-bold text-blue-600">R$ {(comandaSelecionada.total || 0).toFixed(2)}</p>
              </div>
            </div>

            {comandaSelecionada.status === 'ABERTA' && (
              <form onSubmit={adicionarItem} className="flex space-x-3 mb-6 shrink-0 bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                <div className="flex-1">
                  <select 
                    required
                    value={produtoSelecionadoId} 
                    onChange={e => setProdutoSelecionadoId(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                  >
                    <option value="" disabled>Selecione um Produto...</option>
                    {produtos.map(p => (
                      <option key={p.id} value={p.id}>{p.nome} - R$ {p.preco_venda.toFixed(2)} (Estoque: {p.quantidade_estoque})</option>
                    ))}
                  </select>
                </div>
                <div className="w-24">
                  <input type="number" min="1" required value={quantidadeItem} onChange={e=>setQuantidadeItem(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg outline-none text-center" placeholder="Qtd" />
                </div>
                <button type="submit" className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium flex items-center justify-center transition-colors">
                  <ShoppingCart size={20} />
                </button>
              </form>
            )}

            <div className="flex-1 overflow-y-auto mb-6 bg-white border border-gray-200 rounded-lg shadow-sm">
              <table className="w-full text-left border-collapse text-sm">
                <thead className="bg-gray-50 border-b border-gray-200 sticky top-0">
                  <tr>
                    <th className="px-4 py-3 font-semibold text-gray-600">Qtd</th>
                    <th className="px-4 py-3 font-semibold text-gray-600">Produto</th>
                    <th className="px-4 py-3 font-semibold text-gray-600 text-right">V. Unit</th>
                    <th className="px-4 py-3 font-semibold text-gray-600 text-right">Subtotal</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {comandaSelecionada.itens.length === 0 ? (
                    <tr><td colSpan={4} className="text-center py-8 text-gray-400">Nenhum item consumido ainda.</td></tr>
                  ) : (
                    comandaSelecionada.itens.map((item, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-4 py-3 font-bold text-gray-700">{item.quantidade}x</td>
                        <td className="px-4 py-3 text-gray-800">{getProdutoNome(item.produto_id)}</td>
                        <td className="px-4 py-3 text-right text-gray-500">R$ {item.valor_unitario.toFixed(2)}</td>
                        <td className="px-4 py-3 text-right font-medium text-gray-800">R$ {(item.quantidade * item.valor_unitario).toFixed(2)}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {comandaSelecionada.status === 'ABERTA' ? (
              <button 
                onClick={() => fecharComanda(comandaSelecionada.id)}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-4 rounded-xl font-bold text-lg flex justify-center items-center space-x-2 transition-colors shadow-md shrink-0"
              >
                <CheckCircle size={24} />
                <span>Encerrar Comanda e Cobrar</span>
              </button>
            ) : (
              <div className="w-full bg-gray-200 text-gray-500 py-4 rounded-xl font-bold text-lg flex justify-center items-center text-center shrink-0">
                Comanda Encerrada
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <ClipboardList size={64} className="mb-4 text-gray-300" />
            <p className="text-lg">Selecione uma comanda ao lado</p>
            <p className="text-sm">ou abra uma nova para começar.</p>
          </div>
        )}
      </div>

      {/* Modal Nova Comanda */}
      {isModalNovaOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-sm overflow-hidden">
            <div className="flex justify-between items-center p-6 border-b border-gray-100">
              <h3 className="text-xl font-bold text-gray-800">Abrir Nova Conta</h3>
              <button onClick={() => setIsModalNovaOpen(false)} className="text-gray-400 hover:text-gray-600"><X size={24} /></button>
            </div>
            <form onSubmit={abrirNovaComanda} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Identificador (QR Code / Nº Cartão)</label>
                <input type="text" required value={identificadorCartao} onChange={e=>setIdentificadorCartao(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Ex: MESA-04 ou CARTAO-88" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nome do Cliente (Opcional)</label>
                <input type="text" value={nomeCliente} onChange={e=>setNomeCliente(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Ex: João Silva" />
              </div>
              
              <div className="mt-6 flex justify-end space-x-3">
                <button type="button" onClick={() => setIsModalNovaOpen(false)} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg font-medium">Cancelar</button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium shadow-sm">Abrir</button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
