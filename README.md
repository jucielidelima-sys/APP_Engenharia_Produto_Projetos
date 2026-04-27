# Gestão de Projetos - Login Profissional + Auditoria

Usuários padrão:
- admin / admin123: administrador
- user / user123: somente visualização

Recursos:
- Login corporativo
- Cadastro de usuários pelo administrador
- Troca de senha
- Bloqueio de cadastro/edição/importação para usuário visual
- Permissão por projeto para usuários visuais
- Log de auditoria: quem alterou, o que alterou e quando
- Página Auditoria para consulta e exportação CSV

## Ações registradas na auditoria

- Login
- Logout
- Cadastro de projeto
- Edição de planilha
- Importação de Excel
- Criação de usuário
- Alteração de usuário
- Troca de senha
- Limpeza do log

## Executar

```bash
pip install -r requirements.txt
streamlit run app.py
```


Senha padrão para limpar auditoria: limpar123
