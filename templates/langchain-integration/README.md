# MiniMax-M2 LangChain Entegrasyon Şablonu

LangChain framework'ü ile MiniMax-M2 kullanımı.

MiniMax-M2, OpenAI uyumlu API'si sayesinde LangChain ile sorunsuz çalışır.

## Hızlı Başlangıç

1. Bağımlılıkları yükle:
```bash
pip install -r requirements.txt
```

2. Ortam değişkenlerini ayarla:
```bash
export MINIMAX_API_BASE="http://localhost:8000/v1"
export MINIMAX_API_KEY="your-api-key"
```

3. Çalıştır:
```bash
python main.py
```

## Özellikler

- **ChatOpenAI Entegrasyonu**: Standart LangChain arayüzü
- **Prompt Şablonları**: Dinamik prompt oluşturma
- **Hafıza Yönetimi**: Sohbet geçmişi takibi
- **Zincir Bileşimi**: Çoklu adım işlemler
- **Agent Desteği**: Araç kullanımı
- **Streaming**: Gerçek zamanlı yanıtlar

## Kullanım Örnekleri

### Basit Kullanım
```python
from main import create_llm
from langchain_core.messages import HumanMessage

llm = create_llm()
response = llm.invoke([HumanMessage(content="Merhaba!")])
print(response.content)
```

### Prompt Şablonu
```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "Sen {role} olarak cevap ver."),
    ("human", "{question}")
])

chain = prompt | llm
result = chain.invoke({"role": "öğretmen", "question": "AI nedir?"})
```

### Hafızalı Sohbet
```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(return_messages=True)
# ... sohbet döngüsü
```

### Zincir Bileşimi
```python
from langchain_core.output_parsers import StrOutputParser

chain = prompt | llm | StrOutputParser()
result = chain.invoke({"input": "..."})
```

## Demo İçerikleri

| Demo | Açıklama |
|------|----------|
| Basit Tamamlama | Temel mesaj-yanıt |
| Streaming | Gerçek zamanlı token akışı |
| Prompt Şablonu | Dinamik prompt oluşturma |
| Yapılandırılmış Çıktı | JSON formatında çıktı |
| Hafızalı Sohbet | Sohbet geçmişi ile konuşma |
| Zincir Bileşimi | Çoklu adım işleme |
| Agent | Araç kullanımı ile görev tamamlama |

## LangChain Avantajları

1. **Modülerlik**: Bileşenleri kolayca değiştirin
2. **Standartlaştırma**: Tutarlı API arayüzü
3. **Ekosistem**: Geniş araç ve entegrasyon desteği
4. **Bellek**: Konuşma geçmişi yönetimi
5. **Agent**: Otonom görev tamamlama
