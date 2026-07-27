# Pipeline ETL de Extração de Dados de Jogos (API CheapShark )

Este projeto consiste em um script automatizado em Python, construído com as bibliotecas `requests` e `pandas`. Ele foi projetado para consumir de forma iterativa os dados da API pública da CheapShark, extrair informações de ofertas de jogos em diversas lojas virtuais e gerar um relatório limpo no Excel para análises posteriores.

A arquitetura foi pensada para ser facilmente integrada a orquestradores de dados (como o Dagster), utilizando gerenciamento absoluto de caminhos e rotinas seguras de sobrescrita.

(O projeto será aprimorado com o tempo...)

---

## Funcionalidades

O script executa um fluxo de Extração, Transformação e Carga (ETL):

* **Conexão e Requisição de API:** Identifica e consome dinamicamente os endpoints da CheapShark API para mapeamento relacional de lojas (`/stores`) e extração de ofertas (`/deals`).
* **Bypass de Restrições (User-Agent):** Implementação de cabeçalhos HTTP customizados (`headers`) para simular requisições de navegador, evitando bloqueios de segurança (Erro HTTP 400).
* **Paginação Automatizada:** Executa um fluxo para processar dezenas de páginas da API, respeitando os limites de taxa de requisição com pausas estratégicas predefinidas.
* **Transformação e Limpeza de Dados (Transform):**
  * Tratamento de formatos de tempo, convertendo *Unix Timestamps* brutos para o formato legível `YYYY-MM-DD`.
  * Cruzamento relacional inteligente entre os IDs numéricos das lojas e seus respectivos nomes reais.
  * Seleção, tipagem e estruturação apenas das variáveis relevantes (Preço Normal, Preço com Desconto, Notas do Metacritic, etc.).
* **Gestão Dinâmica de Diretórios:** Utilização da biblioteca nativa `pathlib` para resolução de caminhos absolutos. Isso garante a criação autônoma da pasta de destino (`data`) e a execução impecável do script independentemente do diretório de trabalho (CWD) do terminal.
* **Geração de Base de Dados (Load):** Consolidação dos dados limpos em um `DataFrame` do Pandas e exportação automatizada para um arquivo final `.xlsx`, sem indexação residual.
* **Rotina de Sobrescrita e Limpeza:** 
  * Verifica previamente a existência de arquivos de extrações anteriores.
  * Realiza a deleção segura (`unlink`) do arquivo antigo antes de gravar a nova base de dados, garantindo que o diretório não acumule lixo eletrônico e o arquivo consumido seja sempre a versão mais atual.
* **Monitoramento e Rastreabilidade:** Implementação de uma esteira de logs (via biblioteca `logging` customizada), fornecendo visibilidade em tempo real sobre o status do pipeline, sucessos de paginação e captura de exceções de rede.
