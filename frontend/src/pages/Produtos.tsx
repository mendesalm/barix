import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Plus, Package, Edit, Trash2, AlertTriangle, X } from 'lucide-react';

interface Produto {
  id: number;
  nome: string;
  descricao?: string;
  foto_url?: string;
  data_validade?: string;
  categoria: string;
  preco_custo: number;
  preco_venda: number;
  quantidade_estoque: number;
  ativo: boolean;
}

export function Produtos() {
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [loading, setLoading] = useState(true);

  // Estados dos Modais
  const [isModalNovoOpen, setIsModalNovoOpen] = useState(false);
  const [isModalPerdaOpen, setIsModalPerdaOpen] = useState(false);
  const [produtoSelecionado, setProdutoSelecionado] = useState<Produto | null>(null);

  // Estados do Formulário de Novo Produto
  const [nome, setNome] = useState('');
  const [descricao, setDescricao] = useState('');
  const [fotoUrl, setFotoUrl] = useState('');
  const [dataValidade, setDataValidade] = useState('');
  const [categoria, setCategoria] = useState('');
  const [precoCusto, setPrecoCusto] = useState('');
  const [precoVenda, setPrecoVenda] = useState('');
  const [estoqueInicial, setEstoqueInicial] = useState('');

  // Estados do Formulário de Perda/Quebra
  const [quantidadePerda, setQuantidadePerda] = useState('');
  const [motivoPerda, setMotivoPerda] = useState('');

  useEffect(() => {
    carregarProdutos();
  }, []);

  const carregarProdutos = async () => {
    try {
      const response = await api.get('/produtos/');
      setProdutos(response.data);
    } catch (error) {
      console.error("Erro ao carregar produtos:", error);
    } finally {
      setLoading(false);
    }
  };

  const salvarNovoProduto = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload: any = {
        nome,
        categoria,
        preco_custo: parseFloat(precoCusto),
        preco_venda: parseFloat(precoVenda),
        estoque_inicial: parseInt(estoqueInicial) || 0,
        ativo: true
      };
      
      if (descricao) payload.descricao = descricao;
      if (fotoUrl) payload.foto_url = fotoUrl;
      if (dataValidade) payload.data_validade = new Date(dataValidade).toISOString();

      await api.post('/produtos/', payload);
      setIsModalNovoOpen(false);
      // Limpar form
      setNome(''); setCategoria(''); setPrecoCusto(''); setPrecoVenda(''); setEstoqueInicial('');
      setDescricao(''); setFotoUrl(''); setDataValidade('');
      carregarProdutos();
    } catch (error) {
      alert("Erro ao salvar produto. Verifique os dados.");
      console.error(error);
    }
  };

  const registrarPerda = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!produtoSelecionado) return;
    try {
      await api.post(`/produtos/${produtoSelecionado.id}/perdas`, {
        quantidade: parseInt(quantidadePerda),
        motivo: motivoPerda
      });
      setIsModalPerdaOpen(false);
      setQuantidadePerda(''); setMotivoPerda(''); setProdutoSelecionado(null);
      carregarProdutos();
    } catch (error: any) {
      alert(error.response?.data?.detail || "Erro ao registrar perda.");
    }
  };

  return (
    <div className="space-y-6 relative">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Produtos e Estoque</h1>
          <p className="text-gray-500 mt-1">Gerencie seu catálogo e quantidades disponíveis.</p>
        </div>
        <button 
          onClick={() => setIsModalNovoOpen(true)}
          className="bg-blue-600 text-white px-5 py-2.5 rounded-lg font-medium flex items-center space-x-2 hover:bg-blue-700 transition-colors shadow-sm"
        >
          <Plus size={20} />
          <span>Novo Produto</span>
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500 animate-pulse">Carregando catálogo...</div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200 text-gray-600 text-sm">
                <th className="px-6 py-4 font-semibold">Produto</th>
                <th className="px-6 py-4 font-semibold">Categoria</th>
                <th className="px-6 py-4 font-semibold">Custo</th>
                <th className="px-6 py-4 font-semibold">Preço Venda</th>
                <th className="px-6 py-4 font-semibold">Estoque</th>
                <th className="px-6 py-4 font-semibold text-right">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {produtos.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    <div className="flex flex-col items-center justify-center">
                      <Package size={48} className="text-gray-300 mb-4" />
                      <p className="text-lg font-medium">Nenhum produto cadastrado.</p>
                    </div>
                  </td>
                </tr>
              ) : (
                produtos.map((produto) => (
                  <tr key={produto.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 font-medium text-gray-800 flex items-center space-x-3">
                      {produto.foto_url ? (
                        <img src={produto.foto_url} alt={produto.nome} className="w-10 h-10 rounded-full object-cover shadow-sm border border-gray-200" />
                      ) : (
                        <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 shadow-sm"><Package size={20}/></div>
                      )}
                      <div>
                        <div>{produto.nome}</div>
                        {produto.descricao && <div className="text-xs text-gray-400 font-normal">{produto.descricao}</div>}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-600">
                      <span className="px-2.5 py-1 bg-gray-100 rounded-full text-xs font-medium">{produto.categoria}</span>
                    </td>
                    <td className="px-6 py-4 text-gray-600">R$ {produto.preco_custo.toFixed(2)}</td>
                    <td className="px-6 py-4 font-medium text-blue-600">R$ {produto.preco_venda.toFixed(2)}</td>
                    <td className="px-6 py-4">
                      <div className={`font-semibold ${produto.quantidade_estoque <= 0 ? 'text-red-500' : 'text-green-600'}`}>
                        {produto.quantidade_estoque} un
                      </div>
                      {produto.data_validade && (
                        <div className="text-xs text-gray-400 mt-1">Val: {new Date(produto.data_validade).toLocaleDateString()}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 flex justify-end space-x-4">
                      <button 
                        title="Registrar Quebra/Perda"
                        onClick={() => { setProdutoSelecionado(produto); setIsModalPerdaOpen(true); }}
                        className="text-orange-500 hover:text-orange-700 flex items-center space-x-1 transition-colors"
                      >
                        <AlertTriangle size={18} />
                      </button>
                      <button className="text-gray-400 hover:text-blue-500 transition-colors" title="Editar"><Edit size={18} /></button>
                      <button className="text-gray-400 hover:text-red-500 transition-colors" title="Excluir"><Trash2 size={18} /></button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* Modal Novo Produto */}
      {isModalNovoOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
            <div className="flex justify-between items-center p-6 border-b border-gray-100 shrink-0">
              <h3 className="text-xl font-bold text-gray-800">Cadastrar Produto</h3>
              <button onClick={() => setIsModalNovoOpen(false)} className="text-gray-400 hover:text-gray-600"><X size={24} /></button>
            </div>
            
            <div className="p-6 overflow-y-auto">
              <form id="formNovoProduto" onSubmit={salvarNovoProduto} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nome do Produto</label>
                    <input type="text" required value={nome} onChange={e=>setNome(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Ex: Cerveja Heineken 600ml" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
                    <input type="text" required value={categoria} onChange={e=>setCategoria(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Ex: Bebidas" />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Descrição Breve</label>
                  <input type="text" value={descricao} onChange={e=>setDescricao(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Opcional. Ex: Garrafa de vidro." />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">URL da Foto</label>
                    <input type="url" value={fotoUrl} onChange={e=>setFotoUrl(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" placeholder="https://exemplo.com/foto.jpg" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Data de Validade (Opcional)</label>
                    <input type="date" value={dataValidade} onChange={e=>setDataValidade(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Preço Custo (R$)</label>
                    <input type="number" step="0.01" required value={precoCusto} onChange={e=>setPrecoCusto(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Preço Venda (R$)</label>
                    <input type="number" step="0.01" required value={precoVenda} onChange={e=>setPrecoVenda(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Estoque Inicial</label>
                    <input type="number" required value={estoqueInicial} onChange={e=>setEstoqueInicial(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
                  </div>
                </div>
              </form>
            </div>
            
            <div className="p-6 border-t border-gray-100 flex justify-end space-x-3 shrink-0">
              <button type="button" onClick={() => setIsModalNovoOpen(false)} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg font-medium">Cancelar</button>
              <button type="submit" form="formNovoProduto" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium shadow-sm">Salvar Produto</button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Registrar Perda/Quebra */}
      {isModalPerdaOpen && produtoSelecionado && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-sm overflow-hidden">
            <div className="flex justify-between items-center p-6 border-b border-gray-100 bg-orange-50">
              <h3 className="text-xl font-bold text-orange-800 flex items-center gap-2"><AlertTriangle size={20}/> Registrar Quebra</h3>
              <button onClick={() => setIsModalPerdaOpen(false)} className="text-orange-400 hover:text-orange-600"><X size={24} /></button>
            </div>
            <form onSubmit={registrarPerda} className="p-6 space-y-4">
              <p className="text-sm text-gray-600">Produto: <span className="font-bold text-gray-800">{produtoSelecionado.nome}</span></p>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Quantidade Perdida</label>
                <input type="number" min="1" max={produtoSelecionado.quantidade_estoque} required value={quantidadePerda} onChange={e=>setQuantidadePerda(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 outline-none" placeholder="Ex: 1" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Motivo / Justificativa</label>
                <textarea required value={motivoPerda} onChange={e=>setMotivoPerda(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500 outline-none" placeholder="Ex: Garrafa caiu e quebrou no salão" rows={3}></textarea>
              </div>
              <div className="mt-6 flex justify-end space-x-3">
                <button type="button" onClick={() => setIsModalPerdaOpen(false)} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg font-medium">Cancelar</button>
                <button type="submit" className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 font-medium">Debitar Estoque</button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
