# 🎵 Spotify Playlist Maker

Este projeto cria automaticamente uma **playlist no Spotify** a partir de um arquivo CSV com duas colunas (`nome`, `banda`).  
Você fornece uma lista de músicas + artistas e o script adiciona tudo em uma playlist na sua conta do Spotify.  

---

## 🚀 Pré-requisitos

- **Conta Spotify** (pode ser gratuita ou premium).  
- **Python 3.9+** instalado.  
- **App do Spotify for Developers** configurado.

---

## ⚙️ Criando seu app no Spotify

1. Vá até o [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).  
2. Clique em **"Create App"**.  
3. Defina um nome e descrição (ex: *Spotify Playlist Maker*).  
4. Em **Redirect URI**, adicione:  
   ```
   http://127.0.0.1:8000/callback
   ```
   ⚠️ Desde **9 de abril de 2025**, novos apps precisam usar exatamente esse formato (`127.0.0.1`, porta `8000`).  
5. Salve as alterações.  
6. Anote o **Client ID** e **Client Secret**. Você vai colocar esses valores dentro do script Python.  
7. Quando for logar pela primeira vez, o Spotify vai pedir autenticação em 2FA:  
   - Você receberá um **e-mail com um código de 6 dígitos**.  
   - Basta inserir esse código para concluir o login.  

---

## 📥 Instalação

Clone o repositório e entre na pasta do projeto. Depois, crie e ative um ambiente virtual Python:

```bash
python3 -m venv spotify
source spotify/bin/activate
```

Instale as dependências:

```bash
pip3 install -r requirements.txt
```

---

## 📝 Estrutura do CSV

O arquivo CSV deve ter exatamente duas colunas: `nome` (música) e `banda` (artista).  

Exemplo (`lista-exemplo.csv`):

```csv
nome,banda
Smells Like Teen Spirit,Nirvana
One,Metallica
Billie Jean,Michael Jackson
```

---

## ▶️ Uso

Execute o script passando o nome da playlist e o caminho para o CSV:

```bash
python3 spotify-playlist-maker.py --playlist "Playlist Teste" --file "lista-exemplo.csv"
```

- O script vai abrir o navegador para login no Spotify.  
- Após autorizar o app, ele criará uma playlist privada com o nome fornecido.  
- Todas as músicas encontradas no CSV serão adicionadas.  

---

## ✅ Resultado esperado

```
🎵 Criando playlist: Playlist Teste
✔ Adicionado: Smells Like Teen Spirit - Nirvana
✔ Adicionado: One - Metallica
✔ Adicionado: Billie Jean - Michael Jackson

✅ Playlist 'Playlist Teste' criada com 3 músicas!
```

---

## 📄 Licença

Este projeto é distribuído sob a licença MIT.  
