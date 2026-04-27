# Gestão de Projetos - Base 1 Reconstruída

Esta versão mantém a base aprovada:
- Gantt inicial
- Dashboard de indicadores
- Cadastro de projetos
- Edição de planilha
- Importação e exportação Excel
- Logo/Sidebar GNO
- Engrenagens no cabeçalho
- Prioridade
- Riscos avançados
- Projetos críticos/prioritários

Adicionado sem alterar a estrutura:
- Login profissional
- Controle de usuários
- Permissão por perfil
- Permissão por projeto para usuário visual
- Log de auditoria
- Senha para limpar log
- Correção blindada de datas

## Usuários padrão

Admin:
- usuário: admin
- senha: admin123

Visualização:
- usuário: user
- senha: user123

Senha para limpar log de auditoria:
- limpar123

## Executar

```bash
pip install -r requirements.txt
streamlit run app.py
```


Atualização: adicionada aba explícita 'Editar Planilha' no menu lateral para administrador.


Atualização: adicionada tela 'Atualizar Projeto' para filtrar projeto, editar registros e adicionar novas tarefas/etapas.


Correção: blindado cálculo de Performance/Payback para evitar erro com valores vazios ou NaN.
