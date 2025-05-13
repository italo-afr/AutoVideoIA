# 🎬 Gerador de Vídeos Automatizados com IA

Este projeto automatiza totalmente a criação de vídeos curtos com inteligência artificial, usando um tema fornecido pelo usuário. O sistema gera um roteiro, imagens, narração por voz e monta o vídeo final com zoom suave, fade-in/out e música.

## 🧠 Funcionalidades

- Geração de **roteiros narrativos** com GPT-3.5 ou GPT-4-Turbo (OpenAI)
- Tradução e **refinamento de prompts** para imagem
- Criação de **imagens realistas** com a API do Leonardo.Ai
- Geração de **narração por voz** com ElevenLabs
- Montagem automática do vídeo com imagens + narração
- Exportação do vídeo final em `.mp4` pronto para TikTok, Reels e Shorts
- Sistema de **limpeza opcional** de arquivos anteriores para facilitar novas execuções

## 🧰 Tecnologias Usadas

| Tecnologia     | Finalidade                            |
| -------------- | ------------------------------------- |
| Python         | Lógica principal                      |
| OpenAI API     | Geração de roteiro e tradução         |
| Leonardo.Ai    | Geração de imagens realistas          |
| ElevenLabs API | Narração de voz em alta qualidade     |
| MoviePy        | Montagem do vídeo final               |
| Slugify        | Geração de nomes limpos para arquivos |

## 🗂️ Estrutura de Pastas

```
📁 roteiros/     → Armazena o roteiro gerado
📁 imagens/      → Contém as imagens de cada cena
📁 audios/       → Contém a narração gerada por cena
📁 videos/       → Salva os vídeos finais exportados
```

## ▶️ Como Usar

1. Instale os pacotes necessários:

```bash
pip install -r requirements.txt
```

2. Configure suas **chaves de API**:

   - OpenAI
   - ElevenLabs
   - Leonardo.Ai

3. Execute o script:

```bash
python nome_do_script.py
```

4. Digite um tema quando solicitado, e o sistema cuidará do resto.

5. O vídeo final será salvo em `videos/`.

## 🧹 Limpeza Automática

Ao rodar o script, se houver arquivos antigos de imagens, áudios ou roteiro, você será perguntado se deseja apagá-los antes de começar um novo vídeo.

## 💡 Exemplo de Tema

```
Digite o tema do vídeo: A história de superação de um gato abandonado
```

## 📄 Licença

Este projeto é open-source.
