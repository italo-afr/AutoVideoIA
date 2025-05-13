# === IMPORTAÇÕES ===
import os
import re
import time
import openai
import requests
import shutil
import sys
from slugify import slugify
from moviepy.editor import *
from elevenlabs.client import ElevenLabs
import moviepy.video.fx.all as vfx

# === CONFIGURAÇÕES ===
client = openai.OpenAI(api_key="Sua-Chave-API")
client_eleven = ElevenLabs(api_key="Sua-Chave-API")
leonardo_api_key = "Sua-Chave-API"
VOZ_ID = "ID-Voz-ElevenLab"

# === PASTAS ===
os.makedirs("roteiros", exist_ok=True)
os.makedirs("imagens", exist_ok=True)
os.makedirs("audios", exist_ok=True)
os.makedirs("videos", exist_ok=True)

# === FUNÇÃO: CONFIRMAR LIMPEZA DE ARQUIVOS ANTIGOS ===
def confirmar_limpeza():
    arquivos_existentes = (
        any(os.listdir("roteiros")) or
        any(os.listdir("imagens")) or
        any(os.listdir("audios"))
    )

    if arquivos_existentes:
        resposta = input("⚠️ Existem arquivos antigos. Deseja apagá-los antes de gerar o novo vídeo? (s/n): ").lower()
        if resposta == "s":
            print("🧹 Limpando arquivos antigos...")
            shutil.rmtree("roteiros")
            shutil.rmtree("imagens")
            shutil.rmtree("audios")
            os.makedirs("roteiros", exist_ok=True)
            os.makedirs("imagens", exist_ok=True)
            os.makedirs("audios", exist_ok=True)
        else:
            print("Mantendo arquivos antigos.")

# === GERA ROTEIRO ===
def gerar_roteiro(prompt_base):
    print("Gerando roteiro com IA...")
    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt_base}]
    )
    texto = resposta.choices[0].message.content
    with open("roteiros/roteiro.txt", "w", encoding="utf-8") as f:
        f.write(texto)
    return texto

# === EXTRAI CENAS E PROMPTS ===
def extrair_cenas_e_prompts(texto):
    cenas = []
    padrao = r"Cena\s+\d+:\s*(.*?)📸 Prompt imagem:\s*(.+?)(?:\n\n|\Z)"
    matches = re.findall(padrao, texto, re.DOTALL | re.IGNORECASE)

    for descricao, prompt in matches:
        descricao = descricao.strip().replace("\n", " ")
        prompt = prompt.strip()
        cenas.append((descricao, prompt))

    return cenas

# === GERA IMAGEM COM LEONARDO.AI ===
def gerar_imagem(prompt, index):
    print(f"Gerando imagem {index + 1}...")
    url = "https://cloud.leonardo.ai/api/rest/v1/generations"
    headers = {
        "Authorization": f"Bearer {leonardo_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "negative_prompt": "blurry, deformed, extra limbs, fused paws, bad anatomy, distorted face, poor lighting, low detail",
        "height": 1024,
        "width": 576,
        "num_images": 1,
        "guidance_scale": 7,
        "modelId": "1e60896f-3c26-4296-8ecc-53e2afecc132",
        "init_strength": 0.0,
        "num_inference_steps": 30
    }
    response = requests.post(url, json=data, headers=headers)
    try:
        generation_id = response.json()['sdGenerationJob']['generationId']
    except KeyError:
        print(f"Erro ao gerar imagem {index}: {response.text}")
        return

    status_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
    while True:
        time.sleep(5)
        status_resp = requests.get(status_url, headers=headers)
        gen_data = status_resp.json()
        if gen_data['generations_by_pk'] and gen_data['generations_by_pk']['status'] == 'COMPLETE':
            image_url = gen_data['generations_by_pk']['generated_images'][0]['url']
            image_data = requests.get(image_url).content
            with open(f"imagens/cena{index}.png", "wb") as f:
                f.write(image_data)
            break
        print(f"Aguardando imagem {index + 1}...")

# === GERA AUDIO POR CENA ===
def gerar_audio_cena(texto, index):
    print(f"Gerando áudio da cena {index + 1}...")
    resposta = client_eleven.text_to_speech.convert(
        voice_id=VOZ_ID,
        model_id="eleven_multilingual_v2",
        text=texto
    )
    caminho = f"audios/cena{index}.mp3"
    with open(caminho, "wb") as f:
        for chunk in resposta:
            f.write(chunk)

    if os.path.getsize(caminho) < 1000:
        print(f"Áudio da cena {index} está vazio ou corrompido. Removendo...")
        os.remove(caminho)

# === TRADUZIR PROMPT ===
def traduzir_para_ingles(texto):
    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": (
                "Traduza o texto abaixo para o inglês e reescreva como um prompt fotográfico visual, "
                "com foco em realismo e composição natural. Seja descritivo, direto e objetivo. "
                "Evite frases longas e adjetivos vagos."
            )},
            {"role": "user", "content": texto}
        ]
    )
    return resposta.choices[0].message.content.strip()

# === CRIA VÍDEO FINAL ===
def criar_video(tema, cenas):
    print("Montando vídeo final...")
    clips = []

    for i, (descricao, _) in enumerate(cenas):
        imagem = f"imagens/cena{i}.png"
        audio = f"audios/cena{i}.mp3"
        if not os.path.exists(imagem) or not os.path.exists(audio):
            continue

        narração = AudioFileClip(audio)
        clip = (ImageClip(imagem)
            .set_duration(narração.duration)
            .set_audio(narração)
            .fx(vfx.resize, height=1024)
            .resize(lambda t: 1 + 0.01 * t)
            .fx(vfx.fadein, 0.5)
            .fx(vfx.fadeout, 0.5))
        clips.append(clip)

    if not clips:
        print("Nenhum clip para montar o vídeo.")
        return

    video_final = concatenate_videoclips(clips, method="compose", padding=-0.5)
    nome_video = slugify(tema)
    video_final.write_videofile(f"videos/{nome_video}.mp4", fps=24)

# === EXECUÇÃO PRINCIPAL ===
if __name__ == "__main__":
    confirmar_limpeza()
    tema = input("Digite o tema do vídeo: ")
    print(f"🔹 Tema selecionado: {tema}")

    prompt_roteiro = f"""
    Crie um roteiro com 5 cenas sobre "{tema}".
    Cada cena deve conter exatamente:

    1. Uma descrição narrativa de curta e envolvente de até 5s cada cena.
    2. Um prompt de imagem separado, sempre na linha seguinte à descrição, com o emoji 📸, assim:
    📸 Prompt imagem:
    "texto para gerar imagem"

    As cenas devem ser numeradas: Cena 1:, Cena 2:, etc.
    """

    if os.path.exists("roteiros/roteiro.txt"):
        print("Roteiro já existente. Pulando geração...")
        with open("roteiros/roteiro.txt", "r", encoding="utf-8") as f:
            texto = f.read()
    else:
        texto = gerar_roteiro(prompt_roteiro)

    cenas = extrair_cenas_e_prompts(texto)

    if not cenas:
        print("Nenhuma cena foi extraída do roteiro. Verifique o formato.")
        with open("debug_roteiro.txt", "w", encoding="utf-8") as f:
            f.write(texto)
        sys.exit(1)

    for i, (descricao, prompt) in enumerate(cenas):
        caminho_img = f"imagens/cena{i}.png"
        caminho_audio = f"audios/cena{i}.mp3"

        if not os.path.exists(caminho_img):
            prompt_traduzido = traduzir_para_ingles(prompt)
            gerar_imagem(prompt_traduzido, i)
        else:
            print(f"Imagem {i+1} já existente. Pulando...")

        if not os.path.exists(caminho_audio):
            gerar_audio_cena(descricao, i)
        else:
            print(f"Áudio da cena {i+1} já existente. Pulando...")

    criar_video(tema, cenas)
