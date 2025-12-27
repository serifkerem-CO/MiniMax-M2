"""
MiniMax-M2 Gradio Web UI Şablonu
================================
Tarayıcı tabanlı interaktif web arayüzü.

Gradio, hızlıca demo ve prototip oluşturmak için mükemmel bir kütüphanedir.
Kullanıcılar tarayıcı üzerinden modelle etkileşime geçebilir.

Gereksinimler:
    pip install gradio openai

Kullanım:
    python main.py
    # Tarayıcıda http://localhost:7860 adresine gidin
"""

import os
from typing import Generator

import gradio as gr
from openai import OpenAI

# Yapılandırma
API_BASE_URL = os.getenv("MINIMAX_API_BASE", "http://localhost:8000/v1")
API_KEY = os.getenv("MINIMAX_API_KEY", "your-api-key")
MODEL_NAME = os.getenv("MINIMAX_MODEL", "MiniMax-M2")

# OpenAI istemcisi
client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)


# ============================================================================
# Sohbet Fonksiyonları
# ============================================================================

def chat(message: str, history: list, system_prompt: str, temperature: float, max_tokens: int) -> Generator:
    """Streaming sohbet fonksiyonu."""
    messages = [{"role": "system", "content": system_prompt}]

    # Geçmişi ekle
    for human, assistant in history:
        messages.append({"role": "user", "content": human})
        messages.append({"role": "assistant", "content": assistant})

    messages.append({"role": "user", "content": message})

    # Streaming yanıt
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )

    partial_message = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            partial_message += chunk.choices[0].delta.content
            yield partial_message


def analyze_code(code: str, language: str, analysis_type: str) -> str:
    """Kod analizi fonksiyonu."""
    prompts = {
        "explain": f"Bu {language} kodunu açıkla:\n```{language}\n{code}\n```",
        "review": f"Bu {language} kodunu incele ve iyileştirme önerileri sun:\n```{language}\n{code}\n```",
        "fix": f"Bu {language} kodundaki hataları bul ve düzelt:\n```{language}\n{code}\n```",
        "optimize": f"Bu {language} kodunu optimize et:\n```{language}\n{code}\n```",
    }

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Sen uzman bir kod analistisin."},
            {"role": "user", "content": prompts.get(analysis_type, prompts["explain"])}
        ],
        temperature=0.3,
        max_tokens=2048,
    )

    return response.choices[0].message.content


def generate_code(description: str, language: str) -> str:
    """Kod üretimi fonksiyonu."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": f"Sen uzman bir {language} geliştiricisisin. Temiz, okunabilir kod yaz."},
            {"role": "user", "content": f"Şu özelliklere sahip {language} kodu yaz:\n\n{description}"}
        ],
        temperature=0.3,
        max_tokens=2048,
    )

    return response.choices[0].message.content


def summarize_text(text: str, style: str, length: str) -> str:
    """Metin özetleme fonksiyonu."""
    length_map = {
        "Kısa (1-2 cümle)": "1-2 cümle ile",
        "Orta (1 paragraf)": "1 paragraf ile",
        "Uzun (detaylı)": "detaylı bir şekilde"
    }

    style_map = {
        "Resmi": "resmi ve profesyonel bir dilde",
        "Günlük": "günlük ve anlaşılır bir dilde",
        "Teknik": "teknik ve bilimsel bir dilde",
        "Basit": "basit ve herkesin anlayacağı bir dilde"
    }

    prompt = f"""Aşağıdaki metni {length_map.get(length, '1 paragraf ile')} {style_map.get(style, 'anlaşılır bir dilde')} özetle:

{text}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Sen metin özetleme uzmanısın."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=1024,
    )

    return response.choices[0].message.content


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Çeviri fonksiyonu."""
    prompt = f"{source_lang} dilinden {target_lang} diline çevir:\n\n{text}"

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Sen profesyonel bir çevirmensin."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2048,
    )

    return response.choices[0].message.content


# ============================================================================
# Gradio Arayüzü
# ============================================================================

def create_interface():
    """Gradio arayüzü oluştur."""

    with gr.Blocks(title="MiniMax-M2 Web UI", theme=gr.themes.Soft()) as demo:

        gr.Markdown("""
        # 🤖 MiniMax-M2 Web Arayüzü

        MiniMax-M2 ile etkileşime geçin. Sohbet edin, kod yazın, analiz yapın.
        """)

        with gr.Tabs():

            # ==================== SOHBET SEKMESİ ====================
            with gr.TabItem("💬 Sohbet"):
                with gr.Row():
                    with gr.Column(scale=3):
                        chatbot = gr.Chatbot(
                            label="Sohbet",
                            height=500,
                            show_copy_button=True,
                        )
                        msg = gr.Textbox(
                            label="Mesajınız",
                            placeholder="Bir şey yazın...",
                            lines=2,
                        )
                        with gr.Row():
                            submit_btn = gr.Button("Gönder", variant="primary")
                            clear_btn = gr.Button("Temizle")

                    with gr.Column(scale=1):
                        system_prompt = gr.Textbox(
                            label="Sistem Promptu",
                            value="Sen yardımcı bir asistansın.",
                            lines=3,
                        )
                        temperature = gr.Slider(
                            label="Sıcaklık",
                            minimum=0,
                            maximum=2,
                            value=0.7,
                            step=0.1,
                        )
                        max_tokens = gr.Slider(
                            label="Maks Token",
                            minimum=100,
                            maximum=4096,
                            value=2048,
                            step=100,
                        )

                def respond(message, chat_history, sys_prompt, temp, max_tok):
                    chat_history.append((message, ""))
                    for partial in chat(message, chat_history[:-1], sys_prompt, temp, max_tok):
                        chat_history[-1] = (message, partial)
                        yield "", chat_history

                msg.submit(
                    respond,
                    [msg, chatbot, system_prompt, temperature, max_tokens],
                    [msg, chatbot],
                )
                submit_btn.click(
                    respond,
                    [msg, chatbot, system_prompt, temperature, max_tokens],
                    [msg, chatbot],
                )
                clear_btn.click(lambda: ([], ""), outputs=[chatbot, msg])

            # ==================== KOD ANALİZİ SEKMESİ ====================
            with gr.TabItem("🔍 Kod Analizi"):
                with gr.Row():
                    with gr.Column():
                        code_input = gr.Code(
                            label="Kod",
                            language="python",
                            lines=15,
                        )
                        with gr.Row():
                            code_lang = gr.Dropdown(
                                label="Dil",
                                choices=["python", "javascript", "typescript", "java", "go", "rust", "c++"],
                                value="python",
                            )
                            analysis_type = gr.Dropdown(
                                label="Analiz Türü",
                                choices=["explain", "review", "fix", "optimize"],
                                value="explain",
                            )
                        analyze_btn = gr.Button("Analiz Et", variant="primary")

                    with gr.Column():
                        analysis_output = gr.Markdown(label="Analiz Sonucu")

                analyze_btn.click(
                    analyze_code,
                    [code_input, code_lang, analysis_type],
                    analysis_output,
                )

            # ==================== KOD ÜRETİMİ SEKMESİ ====================
            with gr.TabItem("✨ Kod Üretimi"):
                with gr.Row():
                    with gr.Column():
                        code_desc = gr.Textbox(
                            label="Açıklama",
                            placeholder="Ne tür bir kod istediğinizi açıklayın...",
                            lines=5,
                        )
                        gen_lang = gr.Dropdown(
                            label="Programlama Dili",
                            choices=["python", "javascript", "typescript", "java", "go", "rust", "c++", "sql"],
                            value="python",
                        )
                        generate_btn = gr.Button("Kod Üret", variant="primary")

                    with gr.Column():
                        generated_code = gr.Markdown(label="Üretilen Kod")

                generate_btn.click(
                    generate_code,
                    [code_desc, gen_lang],
                    generated_code,
                )

            # ==================== ÖZETLEME SEKMESİ ====================
            with gr.TabItem("📝 Özetleme"):
                with gr.Row():
                    with gr.Column():
                        summary_input = gr.Textbox(
                            label="Metin",
                            placeholder="Özetlenecek metni girin...",
                            lines=10,
                        )
                        with gr.Row():
                            summary_style = gr.Dropdown(
                                label="Stil",
                                choices=["Resmi", "Günlük", "Teknik", "Basit"],
                                value="Günlük",
                            )
                            summary_length = gr.Dropdown(
                                label="Uzunluk",
                                choices=["Kısa (1-2 cümle)", "Orta (1 paragraf)", "Uzun (detaylı)"],
                                value="Orta (1 paragraf)",
                            )
                        summarize_btn = gr.Button("Özetle", variant="primary")

                    with gr.Column():
                        summary_output = gr.Textbox(
                            label="Özet",
                            lines=10,
                        )

                summarize_btn.click(
                    summarize_text,
                    [summary_input, summary_style, summary_length],
                    summary_output,
                )

            # ==================== ÇEVİRİ SEKMESİ ====================
            with gr.TabItem("🌍 Çeviri"):
                with gr.Row():
                    with gr.Column():
                        translate_input = gr.Textbox(
                            label="Kaynak Metin",
                            placeholder="Çevrilecek metni girin...",
                            lines=8,
                        )
                        with gr.Row():
                            source_lang = gr.Dropdown(
                                label="Kaynak Dil",
                                choices=["Türkçe", "İngilizce", "Almanca", "Fransızca", "İspanyolca", "Japonca", "Çince"],
                                value="Türkçe",
                            )
                            target_lang = gr.Dropdown(
                                label="Hedef Dil",
                                choices=["Türkçe", "İngilizce", "Almanca", "Fransızca", "İspanyolca", "Japonca", "Çince"],
                                value="İngilizce",
                            )
                        translate_btn = gr.Button("Çevir", variant="primary")

                    with gr.Column():
                        translate_output = gr.Textbox(
                            label="Çeviri",
                            lines=8,
                        )

                translate_btn.click(
                    translate_text,
                    [translate_input, source_lang, target_lang],
                    translate_output,
                )

        gr.Markdown("""
        ---
        **MiniMax-M2** ile güçlendirilmiştir | [Dokümantasyon](https://github.com/MiniMaxAI/MiniMax-M2)
        """)

    return demo


# ============================================================================
# Ana Giriş
# ============================================================================

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # True yaparak public link alabilirsiniz
    )
