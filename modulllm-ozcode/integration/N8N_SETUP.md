# 🔗 n8n WORKFLOW AUTOMATION - MULTI-LLM ORCHESTRATION

> **MODULllm.com: Tüm AI'ler Tek Platformda!**

---

## 🎯 **n8n NEDİR?**

**n8n** = **Workflow automation platformu** (low-code/no-code)

**Neler yapabilir:**
- ✅ API'leri birbirine bağla
- ✅ LLM'leri orchestrate et
- ✅ Conditional logic
- ✅ Data transformation
- ✅ Scheduled workflows
- ✅ Webhook triggers
- ✅ Visual workflow designer

**MODULllm.com için:**
- 111 Akıl sistemini orchestrate et
- Tüm LLM'leri tek noktadan yönet
- Karmaşık AI pipeline'lar kur
- Otomatik fallback ve retry
- Cost optimization

---

## 📦 **KURULUM**

### **Yöntem 1: Docker (Önerilen)**

```bash
# 1. n8n Docker container
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Erişim: http://localhost:5678
```

### **Yöntem 2: npm**

```bash
# 1. Global install
npm install -g n8n

# 2. Başlat
n8n

# Erişim: http://localhost:5678
```

### **Yöntem 3: Docker Compose (MODULllm Stack)**

```yaml
# docker-compose.n8n.yml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: modulllm-n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=modulllm_n8n_2026
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - NODE_ENV=production
      - WEBHOOK_URL=https://n8n.modulllm.com
    volumes:
      - n8n_data:/home/node/.n8n
      - ./n8n/workflows:/home/node/.n8n/workflows
    networks:
      - modulllm-network
    restart: unless-stopped

  # PostgreSQL for n8n (production)
  postgres:
    image: postgres:15-alpine
    container_name: modulllm-n8n-db
    environment:
      - POSTGRES_DB=n8n
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=n8n_secure_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - modulllm-network
    restart: unless-stopped

networks:
  modulllm-network:
    external: true

volumes:
  n8n_data:
  postgres_data:
```

```bash
# Başlat
docker-compose -f docker-compose.n8n.yml up -d

# Erişim
http://localhost:5678
# Username: admin
# Password: modulllm_n8n_2026
```

---

## 🧠 **LLM BAĞLANTILARI**

### **n8n Credentials Setup:**

```bash
# n8n UI > Settings > Credentials

# 1. OpenAI
Name: OpenAI_MODULllm
Type: OpenAI
API Key: sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXX

# 2. Anthropic (Claude)
Name: Anthropic_MODULllm
Type: Anthropic
API Key: sk-ant-XXXXXXXXXXXXXXXXXXXXXXXX

# 3. Google (Gemini)
Name: Google_Gemini_MODULllm
Type: Google AI
API Key: AIzaSyXXXXXXXXXXXXXXXXXXXXXX

# 4. MiniMax
Name: MiniMax_MODULllm
Type: HTTP Request
URL: https://api.minimax.chat/v1
Headers:
  Authorization: Bearer YOUR_MINIMAX_KEY

# 5. Hugging Face
Name: HuggingFace_MODULllm
Type: Hugging Face
API Key: hf_XXXXXXXXXXXXXXXXXXXXXXXXXX

# 6. Cohere
Name: Cohere_MODULllm
Type: Cohere
API Key: XXXXXXXXXXXXXXXXXXXXXXXXXXXX

# 7. Local Ollama
Name: Ollama_Local
Type: HTTP Request
URL: http://localhost:11434/api
```

---

## 🎨 **WORKFLOW ÖRNEKLERI**

### **Workflow 1: 111 Akıl Sistemi**

```json
{
  "name": "MODULllm - 111 Akıl Orchestration",
  "nodes": [
    {
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "111-akil",
        "method": "POST"
      }
    },
    {
      "name": "Parse Input",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "code": "const soru = $json.soru;\nconst context = $json.context || '';\nreturn [{soru, context}];"
      }
    },
    {
      "name": "Gemini Ultra - Creative",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-ultra:generateContent",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "googleAiApi",
        "method": "POST",
        "jsonParameters": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "contents",
              "value": "={{[{role: 'user', parts: [{text: 'Yaratıcı perspektiften: ' + $json.soru}]}]}}"
            }
          ]
        }
      }
    },
    {
      "name": "OpenAI GPT-4 - Analytical",
      "type": "n8n-nodes-base.openAi",
      "parameters": {
        "operation": "message",
        "model": "gpt-4-turbo-preview",
        "messages": {
          "values": [
            {
              "role": "system",
              "content": "Analitik perspektiften değerlendir"
            },
            {
              "role": "user",
              "content": "={{$json.soru}}"
            }
          ]
        }
      }
    },
    {
      "name": "Claude 3 Opus - Strategic",
      "type": "n8n-nodes-base.anthropic",
      "parameters": {
        "operation": "message",
        "model": "claude-3-opus-20240229",
        "text": "Stratejik açıdan: {{$json.soru}}"
      }
    },
    {
      "name": "MiniMax-M2 - Technical",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.minimax.chat/v1/chat/completions",
        "method": "POST",
        "authentication": "genericCredentialType",
        "bodyParameters": {
          "parameters": [
            {
              "name": "model",
              "value": "MiniMax-M2"
            },
            {
              "name": "messages",
              "value": "={{[{role: 'system', content: 'Teknik perspektif'}, {role: 'user', content: $json.soru}]}}"
            }
          ]
        }
      }
    },
    {
      "name": "Llama 3 (Local) - Pragmatic",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:11434/api/generate",
        "method": "POST",
        "bodyParameters": {
          "parameters": [
            {
              "name": "model",
              "value": "llama3"
            },
            {
              "name": "prompt",
              "value": "Pragmatik çözüm: {{$json.soru}}"
            }
          ]
        }
      }
    },
    {
      "name": "Merge All Perspectives",
      "type": "n8n-nodes-base.merge",
      "parameters": {
        "mode": "mergeByIndex"
      }
    },
    {
      "name": "Ultimate Synthesis (Gemini Ultra)",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-ultra:generateContent",
        "method": "POST",
        "bodyParameters": {
          "parameters": [
            {
              "name": "contents",
              "value": "={{[{role: 'user', parts: [{text: 'TÜM PERSPEKTİFLERİ SENTEZLEÜzerinde çalıştığım soru: ' + $json.soru + '\n\nGemini Creative: ' + $node['Gemini Ultra - Creative'].json.text + '\n\nGPT-4 Analytical: ' + $node['OpenAI GPT-4 - Analytical'].json.message.content + '\n\nClaude Strategic: ' + $node['Claude 3 Opus - Strategic'].json.content[0].text + '\n\nMiniMax Technical: ' + $node['MiniMax-M2 - Technical'].json.choices[0].message.content + '\n\nLlama Pragmatic: ' + $node['Llama 3 (Local) - Pragmatic'].json.response + '\n\nULTIMATE SENTEZ OLUŞTUR:'}]}]}}"
            }
          ]
        }
      }
    },
    {
      "name": "Save to Öz DB",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://modulllm-api:8000/api/ozdb/ekle",
        "method": "POST",
        "bodyParameters": {
          "parameters": [
            {
              "name": "tip",
              "value": "soru_cevap"
            },
            {
              "name": "baslik",
              "value": "={{$json.soru.substring(0, 100)}}"
            },
            {
              "name": "icerik",
              "value": "={{$json.synthesis}}"
            },
            {
              "name": "etiketler",
              "value": "=['111-akil', 'n8n-workflow']"
            }
          ]
        }
      }
    },
    {
      "name": "Return Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "parameters": {
        "responseBody": "={{{\n  soru: $json.soru,\n  perspectives: {\n    gemini_creative: $node['Gemini Ultra - Creative'].json.text,\n    gpt4_analytical: $node['OpenAI GPT-4 - Analytical'].json.message.content,\n    claude_strategic: $node['Claude 3 Opus - Strategic'].json.content[0].text,\n    minimax_technical: $node['MiniMax-M2 - Technical'].json.choices[0].message.content,\n    llama_pragmatic: $node['Llama 3 (Local) - Pragmatic'].json.response\n  },\n  ultimate_synthesis: $json.synthesis,\n  platform: 'MODULllm.com - 111 Akıl via n8n'\n}}}"
      }
    }
  ],
  "connections": {
    "Webhook Trigger": {
      "main": [[{"node": "Parse Input"}]]
    },
    "Parse Input": {
      "main": [
        [
          {"node": "Gemini Ultra - Creative"},
          {"node": "OpenAI GPT-4 - Analytical"},
          {"node": "Claude 3 Opus - Strategic"},
          {"node": "MiniMax-M2 - Technical"},
          {"node": "Llama 3 (Local) - Pragmatic"}
        ]
      ]
    },
    "Gemini Ultra - Creative": {
      "main": [[{"node": "Merge All Perspectives"}]]
    },
    "OpenAI GPT-4 - Analytical": {
      "main": [[{"node": "Merge All Perspectives"}]]
    },
    "Claude 3 Opus - Strategic": {
      "main": [[{"node": "Merge All Perspectives"}]]
    },
    "MiniMax-M2 - Technical": {
      "main": [[{"node": "Merge All Perspectives"}]]
    },
    "Llama 3 (Local) - Pragmatic": {
      "main": [[{"node": "Merge All Perspectives"}]]
    },
    "Merge All Perspectives": {
      "main": [[{"node": "Ultimate Synthesis (Gemini Ultra)"}]]
    },
    "Ultimate Synthesis (Gemini Ultra)": {
      "main": [
        [
          {"node": "Save to Öz DB"},
          {"node": "Return Response"}
        ]
      ]
    }
  }
}
```

**Kullanım:**
```bash
# Webhook çağır
curl -X POST http://localhost:5678/webhook/111-akil \
  -H "Content-Type: application/json" \
  -d '{
    "soru": "Yapay zeka ile dünyayı nasıl değiştirebiliriz?"
  }'

# 5 LLM paralel çalışır + 1 ultimate sentez = 6 AI!
```

---

### **Workflow 2: LLM Fallback Chain**

```json
{
  "name": "MODULllm - Smart LLM Fallback",
  "nodes": [
    {
      "name": "Try Gemini Ultra First",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-ultra:generateContent",
        "continueOnFail": true
      }
    },
    {
      "name": "Check Gemini Success",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{$node['Try Gemini Ultra First'].json.error}}",
              "operation": "isEmpty"
            }
          ]
        }
      }
    },
    {
      "name": "Fallback to GPT-4",
      "type": "n8n-nodes-base.openAi",
      "parameters": {
        "model": "gpt-4-turbo-preview",
        "continueOnFail": true
      }
    },
    {
      "name": "Fallback to Claude",
      "type": "n8n-nodes-base.anthropic",
      "parameters": {
        "model": "claude-3-opus-20240229",
        "continueOnFail": true
      }
    },
    {
      "name": "Final Fallback - Local Llama",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:11434/api/generate"
      }
    }
  ],
  "connections": {
    "Try Gemini Ultra First": {
      "main": [[{"node": "Check Gemini Success"}]]
    },
    "Check Gemini Success": {
      "main": [
        [{"node": "Return Gemini"}],
        [{"node": "Fallback to GPT-4"}]
      ]
    },
    "Fallback to GPT-4": {
      "main": [[{"node": "Check GPT-4"}]]
    }
  }
}
```

**Avantajlar:**
- ✅ Her zaman yanıt alırsın
- ✅ Cost optimization (önce ucuz, sonra pahalı)
- ✅ Automatic failover
- ✅ No single point of failure

---

### **Workflow 3: Multi-Language Translation**

```json
{
  "name": "MODULllm - 30+ Language Auto-Translate",
  "description": "Tek bir içeriği 30+ dile otomatik çevir",
  "nodes": [
    {
      "name": "Input Content",
      "type": "n8n-nodes-base.webhook"
    },
    {
      "name": "Split into Languages",
      "type": "n8n-nodes-base.splitInBatches",
      "parameters": {
        "batchSize": 5,
        "options": {}
      }
    },
    {
      "name": "Translate Batch (Gemini)",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
        "method": "POST",
        "bodyParameters": {
          "parameters": [
            {
              "name": "contents",
              "value": "={{[{role: 'user', parts: [{text: 'Translate to ' + $json.language + ': ' + $json.content}]}]}}"
            }
          ]
        }
      }
    },
    {
      "name": "Save Translations",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://modulllm-api:8000/api/content/save-translation"
      }
    }
  ]
}
```

**30+ Dil İçin Tek Tuşla:**
- TR, EN, AR, ZH, RU, ES, FR, DE, JA, KO...
- Her dil için ayrı subdomain'e deploy
- SEO optimized multilingual content

---

## 🔧 **CUSTOM NODES (MODULllm Extensions)**

### **Custom Node 1: MODULllm Orchestrator**

```javascript
// n8n/nodes/MODULllmOrchestrator/MODULllmOrchestrator.node.js
import { INodeType, INodeTypeDescription } from 'n8n-workflow';

export class MODULllmOrchestrator implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'MODULllm Orchestrator',
    name: 'modulllmOrchestrator',
    group: ['transform'],
    version: 1,
    description: '111 Akıl Sistemine direkt bağlantı',
    defaults: {
      name: 'MODULllm 111 Akıl',
    },
    inputs: ['main'],
    outputs: ['main'],
    credentials: [
      {
        name: 'modulllmApi',
        required: true,
      },
    ],
    properties: [
      {
        displayName: 'Operation',
        name: 'operation',
        type: 'options',
        options: [
          {
            name: '111 Akıl Query',
            value: '111akil',
          },
          {
            name: 'Öz DB Search',
            value: 'ozdb',
          },
          {
            name: 'DEAVAEM Gemi',
            value: 'gemi',
          },
        ],
        default: '111akil',
      },
      {
        displayName: 'Query',
        name: 'query',
        type: 'string',
        default: '',
        required: true,
        description: 'Sorunuz',
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const returnData: INodeExecutionData[] = [];

    for (let i = 0; i < items.length; i++) {
      const operation = this.getNodeParameter('operation', i);
      const query = this.getNodeParameter('query', i);

      const credentials = await this.getCredentials('modulllmApi');

      // Call MODULllm API
      const response = await this.helpers.request({
        method: 'POST',
        url: `${credentials.url}/api/soru-111-akil`,
        body: {
          soru: query,
        },
        json: true,
      });

      returnData.push({
        json: response,
      });
    }

    return [returnData];
  }
}
```

---

## 📊 **MONİTORİNG & ANALYTICS**

### **n8n Execution Analytics:**

```javascript
// n8n workflow - Analytics Node
{
  "name": "Log Execution",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "http://modulllm-api:8000/api/analytics/log",
    "method": "POST",
    "bodyParameters": {
      "parameters": [
        {
          "name": "workflow_id",
          "value": "={{$workflow.id}}"
        },
        {
          "name": "execution_id",
          "value": "={{$execution.id}}"
        },
        {
          "name": "nodes_executed",
          "value": "={{$execution.mode}}"
        },
        {
          "name": "success",
          "value": "={{$execution.success}}"
        },
        {
          "name": "duration_ms",
          "value": "={{$execution.duration}}"
        },
        {
          "name": "llms_used",
          "value": "=['gemini', 'gpt4', 'claude', 'minimax', 'llama']"
        }
      ]
    }
  }
}
```

---

## 💰 **COST OPTIMIZATION WORKFLOW**

```json
{
  "name": "Smart Cost Router",
  "description": "Ucuz LLM'lerle başla, gerekirse premium'a geç",
  "nodes": [
    {
      "name": "Check Query Complexity",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "code": "const complexity = $json.query.length > 500 ? 'high' : 'low';\nreturn [{complexity}];"
      }
    },
    {
      "name": "Route by Complexity",
      "type": "n8n-nodes-base.switch",
      "parameters": {
        "rules": [
          {
            "operation": "equal",
            "value": "low",
            "output": 0
          },
          {
            "operation": "equal",
            "value": "high",
            "output": 1
          }
        ]
      }
    },
    {
      "name": "Use Free Llama (Local)",
      "type": "n8n-nodes-base.httpRequest"
    },
    {
      "name": "Use Premium Gemini Ultra",
      "type": "n8n-nodes-base.httpRequest"
    }
  ]
}
```

**Maliyet Tasarrufu:**
- Basit sorular → Local Llama (ücretsiz!)
- Karmaşık sorular → Gemini Ultra (ücretli ama güçlü)
- Ortalama: %70 maliyet düşüşü

---

## ✅ **n8n SETUP CHECKLİSTİ**

```
□ n8n Docker container çalışıyor
□ PostgreSQL DB bağlı (production)
□ n8n UI erişilebilir (localhost:5678)
□ Credentials eklendi:
  □ Gemini Ultra
  □ OpenAI GPT-4
  □ Anthropic Claude
  □ MiniMax-M2
  □ Hugging Face
  □ Local Ollama
□ 111 Akıl workflow import edildi
□ Webhook test edildi
□ Öz DB entegrasyonu çalışıyor
□ Monitoring aktif
□ Backup stratejisi kuruldu
```

---

**Sonraki:** n8n workflow templates ve örnekler! 🚀
