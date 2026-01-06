## MLX Dağıtım Kılavuzu

[**MiniMax-M2**](https://huggingface.co/MiniMaxAI/MiniMax-M2) modelini **MLX** framework'ü ile Mac'inizde yerel olarak çalıştırın, sunun ve ince ayar yapın. Bu kılavuz sizi hızlıca başlatır.

> **Gereksinimler**
> - Apple Silicon Mac (M3 Ultra veya üstü)
> - **En az 256GB birleşik bellek (RAM)**


**Kurulum**

`mlx-lm` paketini pip ile kurun:

```bash
pip install mlx-lm
```

**Komut Satırı (CLI)**

Terminalden doğrudan metin oluşturun:

```bash
mlx_lm.generate \
  --model mlx-community/MiniMax-M2-4bit \
  --prompt "Everest Dağı ne kadar yüksek?"
```

> Yanıt uzunluğunu kontrol etmek için `--max-tokens 256`, yaratıcılık için `--temp 0.7` ekleyin.

**Python Script Örneği**

`mlx-lm`'i kendi Python scriptlerinizde kullanın:

```python
from mlx_lm import load, generate

# Quantize edilmiş modeli yükle
model, tokenizer = load("mlx-community/MiniMax-M2-4bit")

prompt = "Merhaba, nasılsın?"

# Varsa sohbet şablonunu uygula (sohbet modelleri için önerilir)
if tokenizer.chat_template is not None:
    messages = [{"role": "user", "content": prompt}]
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

# Yanıt oluştur
response = generate(
    model,
    tokenizer,
    prompt=prompt,
    max_tokens=256,
    temp=0.7,
    verbose=True
)

print(response)
```

**İpuçları**
- **Model varyantları**: `MiniMax-M2-4bit`, `6bit`, `8bit` veya `bfloat16` sürümleri için [Hugging Face](https://huggingface.co/collections/mlx-community/minimax-m2) sayfasını kontrol edin.
- **İnce ayar**: Verimli parametre-etkin ince ayar (PEFT) için `mlx-lm.lora` kullanın.

**Kaynaklar**
- GitHub: [https://github.com/ml-explore/mlx-lm](https://github.com/ml-explore/mlx-lm)
- Modeller: [https://huggingface.co/mlx-community](https://huggingface.co/mlx-community)
