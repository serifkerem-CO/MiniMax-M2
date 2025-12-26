"""
MiniMax-M2 LangChain Entegrasyon Şablonu
========================================
LangChain framework'ü ile MiniMax-M2 kullanımı.

LangChain, LLM uygulamaları geliştirmek için güçlü bir framework'tür.
MiniMax-M2, OpenAI uyumlu API'si sayesinde LangChain ile sorunsuz çalışır.

Gereksinimler:
    pip install langchain langchain-openai openai

Kullanım:
    python main.py
"""

import os
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain, ConversationChain
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool, StructuredTool
from pydantic import BaseModel, Field

# Yapılandırma
API_BASE_URL = os.getenv("MINIMAX_API_BASE", "http://localhost:8000/v1")
API_KEY = os.getenv("MINIMAX_API_KEY", "your-api-key-here")
MODEL_NAME = os.getenv("MINIMAX_MODEL", "MiniMax-M2")


# ============================================================================
# LLM Oluşturma
# ============================================================================

def create_llm(
    temperature: float = 0.7,
    max_tokens: int = 2048,
    streaming: bool = False
) -> ChatOpenAI:
    """
    MiniMax-M2 için LangChain ChatOpenAI instance'ı oluştur.

    Args:
        temperature: Yaratıcılık parametresi (0-2)
        max_tokens: Maksimum çıktı token sayısı
        streaming: Streaming yanıt kullan

    Returns:
        ChatOpenAI instance
    """
    return ChatOpenAI(
        model=MODEL_NAME,
        openai_api_key=API_KEY,
        openai_api_base=API_BASE_URL,
        temperature=temperature,
        max_tokens=max_tokens,
        streaming=streaming,
    )


# ============================================================================
# Basit Örnekler
# ============================================================================

def simple_completion():
    """Basit tamamlama örneği."""
    print("\n=== Basit Tamamlama ===")

    llm = create_llm()
    messages = [
        SystemMessage(content="Sen yardımcı bir asistansın."),
        HumanMessage(content="Python'un en önemli 3 özelliği nedir?")
    ]

    response = llm.invoke(messages)
    print(f"Yanıt:\n{response.content}")


def streaming_completion():
    """Streaming yanıt örneği."""
    print("\n=== Streaming Yanıt ===")

    llm = create_llm(streaming=True)
    messages = [HumanMessage(content="Kısa bir hikaye yaz.")]

    print("Yanıt: ", end="")
    for chunk in llm.stream(messages):
        print(chunk.content, end="", flush=True)
    print()


# ============================================================================
# Prompt Templates
# ============================================================================

def prompt_template_example():
    """Prompt şablonu örneği."""
    print("\n=== Prompt Şablonu ===")

    llm = create_llm(temperature=0.3)

    # Basit şablon
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Sen uzman bir {role} olarak cevap ver."),
        ("human", "{question}")
    ])

    # Chain oluştur
    chain = prompt | llm | StrOutputParser()

    # Çalıştır
    result = chain.invoke({
        "role": "Python geliştiricisi",
        "question": "List comprehension nedir?"
    })

    print(f"Yanıt:\n{result}")


def structured_output_example():
    """Yapılandırılmış çıktı örneği."""
    print("\n=== Yapılandırılmış Çıktı (JSON) ===")

    llm = create_llm(temperature=0.1)

    # JSON çıktı için prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Sen bir veri çıkarma asistanısın.
Verilen metinden bilgileri JSON formatında çıkar.
Sadece JSON döndür, başka bir şey yazma."""),
        ("human", "{text}")
    ])

    chain = prompt | llm | StrOutputParser()

    text = """
    Ali Yılmaz, 35 yaşında bir yazılım mühendisi.
    İstanbul'da yaşıyor ve Python, JavaScript biliyor.
    E-postası: ali@example.com
    """

    result = chain.invoke({"text": text})
    print(f"JSON:\n{result}")


# ============================================================================
# Hafıza ve Sohbet
# ============================================================================

def conversation_with_memory():
    """Hafızalı sohbet örneği."""
    print("\n=== Hafızalı Sohbet ===")

    llm = create_llm()

    # Hafıza oluştur
    memory = ConversationBufferMemory(return_messages=True)

    # Sohbet zinciri
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Sen yardımcı ve samimi bir asistansın."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    chain = prompt | llm

    # Sohbet simülasyonu
    conversations = [
        "Merhaba! Benim adım Ahmet.",
        "Python öğrenmek istiyorum. Nereden başlamalıyım?",
        "Adımı hatırlıyor musun?"
    ]

    for user_input in conversations:
        print(f"\n👤 Kullanıcı: {user_input}")

        # Geçmiş mesajları al
        history = memory.load_memory_variables({})

        # Yanıt al
        response = chain.invoke({
            "input": user_input,
            "history": history.get("history", [])
        })

        print(f"🤖 Asistan: {response.content}")

        # Hafızaya kaydet
        memory.save_context(
            {"input": user_input},
            {"output": response.content}
        )


# ============================================================================
# Araçlar ve Agent
# ============================================================================

def calculate(expression: str) -> str:
    """Matematiksel ifadeyi hesapla."""
    try:
        # Güvenli eval (sadece demo için)
        allowed_chars = set("0123456789+-*/.()")
        if all(c in allowed_chars or c.isspace() for c in expression):
            result = eval(expression)
            return f"Sonuç: {result}"
        return "Hata: Geçersiz ifade"
    except Exception as e:
        return f"Hata: {e}"


def get_current_time() -> str:
    """Şu anki zamanı döndür."""
    from datetime import datetime
    now = datetime.now()
    return f"Şu anki zaman: {now.strftime('%Y-%m-%d %H:%M:%S')}"


def search_web(query: str) -> str:
    """Web'de ara (simülasyon)."""
    # Gerçek uygulamada API kullanın
    return f"'{query}' için arama sonuçları: [Simüle edilmiş sonuçlar]"


def agent_example():
    """Agent örneği."""
    print("\n=== Agent ile Araç Kullanımı ===")

    llm = create_llm(temperature=0)

    # Araçları tanımla
    tools = [
        Tool(
            name="hesapla",
            func=calculate,
            description="Matematiksel hesaplamalar yapar. Girdi: matematiksel ifade"
        ),
        Tool(
            name="zaman",
            func=lambda _: get_current_time(),
            description="Şu anki zamanı döndürür. Girdi gerekmez."
        ),
        Tool(
            name="ara",
            func=search_web,
            description="Web'de arama yapar. Girdi: arama sorgusu"
        ),
    ]

    # Agent prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Sen yardımcı bir asistansın.
Verilen araçları kullanarak soruları yanıtla.
Araçları kullanmadan önce düşün ve en uygun aracı seç."""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Agent oluştur
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # Test
    questions = [
        "25 + 17 kaçtır?",
        "Şu an saat kaç?",
    ]

    for q in questions:
        print(f"\n❓ Soru: {q}")
        result = agent_executor.invoke({"input": q})
        print(f"💡 Cevap: {result['output']}")


# ============================================================================
# Zincir Bileşenleri
# ============================================================================

def chain_composition():
    """Zincir bileşimi örneği."""
    print("\n=== Zincir Bileşimi ===")

    llm = create_llm(temperature=0.5)

    # Çoklu adım zinciri
    # 1. Konu özeti
    # 2. Anahtar noktalar
    # 3. Sonuç

    summarize_prompt = ChatPromptTemplate.from_messages([
        ("system", "Verilen metni kısaca özetle."),
        ("human", "{text}")
    ])

    keypoints_prompt = ChatPromptTemplate.from_messages([
        ("system", "Verilen özetten 3 anahtar nokta çıkar. Her birini madde işareti ile listele."),
        ("human", "{summary}")
    ])

    conclusion_prompt = ChatPromptTemplate.from_messages([
        ("system", "Verilen anahtar noktalardan bir sonuç paragrafı yaz."),
        ("human", "{keypoints}")
    ])

    # Zincirleri oluştur
    summarize_chain = summarize_prompt | llm | StrOutputParser()
    keypoints_chain = keypoints_prompt | llm | StrOutputParser()
    conclusion_chain = conclusion_prompt | llm | StrOutputParser()

    # Tam zincir
    full_chain = (
        {"summary": summarize_chain}
        | RunnablePassthrough.assign(keypoints=lambda x: keypoints_chain.invoke({"summary": x["summary"]}))
        | RunnablePassthrough.assign(conclusion=lambda x: conclusion_chain.invoke({"keypoints": x["keypoints"]}))
    )

    # Test metni
    text = """
    Yapay zeka, bilgisayarların insan benzeri zeka sergilemesini sağlayan bir teknoloji alanıdır.
    Makine öğrenmesi, yapay zekanın en önemli alt dallarından biridir ve verilerden öğrenme
    yeteneği sağlar. Derin öğrenme ise, yapay sinir ağları kullanarak karmaşık örüntüleri
    öğrenebilen ileri düzey bir makine öğrenmesi tekniğidir. Bu teknolojiler görüntü tanıma,
    doğal dil işleme ve otonom sistemler gibi birçok alanda kullanılmaktadır.
    """

    result = full_chain.invoke({"text": text})

    print(f"📝 Özet:\n{result['summary']}\n")
    print(f"🔑 Anahtar Noktalar:\n{result['keypoints']}\n")
    print(f"📌 Sonuç:\n{result['conclusion']}")


# ============================================================================
# Ana Fonksiyon
# ============================================================================

def main():
    """Tüm örnekleri çalıştır."""
    print("=" * 60)
    print("MiniMax-M2 LangChain Entegrasyon Demo")
    print("=" * 60)

    examples = [
        ("1", "Basit Tamamlama", simple_completion),
        ("2", "Streaming Yanıt", streaming_completion),
        ("3", "Prompt Şablonu", prompt_template_example),
        ("4", "Yapılandırılmış Çıktı", structured_output_example),
        ("5", "Hafızalı Sohbet", conversation_with_memory),
        ("6", "Zincir Bileşimi", chain_composition),
        ("7", "Agent (Araç Kullanımı)", agent_example),
        ("0", "Tümünü Çalıştır", None),
    ]

    print("\nÖrnekler:")
    for num, name, _ in examples:
        print(f"  {num}. {name}")

    choice = input("\nSeçiminiz (0-7): ").strip()

    if choice == "0":
        for num, name, func in examples[:-1]:
            func()
    else:
        for num, name, func in examples:
            if num == choice and func:
                func()
                break
        else:
            print("Geçersiz seçim!")


if __name__ == "__main__":
    main()
