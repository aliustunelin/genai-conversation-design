# GenAI Conversation Design — Architecture & Explanation

## Proje Ne Yapıyor?

Bu proje, GPT-4o modeli ile OpenRouter API üzerinden **3 turlu bir konuşma** yürütür.
Konuşma boyunca modelin **güçlü yanları** ve **limitasyonları** ortaya konur.
Sonuçta tüm konuşma `.json` olarak export edilir.

---

## Mimari Yapı

```
app.py                                ← Entry point (CLI)
│
├── src/router/conversation_router.py ← Kullanıcı arayüzü, akış kontrolü
│   │
│   └── src/service/conversation_service.py ← İş mantığı, prompt yönetimi, JSON export
│       │
│       ├── src/repository/openrouter_repository.py ← OpenRouter API client (HTTP)
│       │
│       └── src/model/conversation.py ← Pydantic veri modelleri
│
└── src/utils/logger.py               ← Loguru tabanlı loglama
```

---

## Katmanlar ve Neden Kullanıldı

### 1. `model/conversation.py` — Veri Modelleri

**Ne yapar:** Konuşma verilerinin yapısını tanımlar.

**Neden kullanıldı:**
- `Message`: Her mesajı (role, content, timestamp) temsil eder. API'ye gönderilen ve gelen her mesaj bu yapıda tutulur.
- `Conversation`: Tüm konuşmayı tutar. Mesaj listesi + turn sonuçları + metadata.
- `TurnResult`: Her tur sonucunu kaydeder (prompt, response, başarılı mı, notlar).
- `ConversationExport`: JSON export için serialization modeli. `Conversation`'ı temiz bir dict'e dönüştürür.

**Neden Pydantic:** Tip güvenliği, otomatik validasyon, kolay serialization (`.model_dump()`). JSON export için birebir.

---

### 2. `repository/openrouter_repository.py` — API Client

**Ne yapar:** OpenRouter API ile HTTP iletişimi sağlar.

**Neden kullanıldı:**
- Repository pattern ile API erişimini izole ettik. Service katmanı API detaylarını bilmez.
- `httpx.AsyncClient` kullanıyoruz çünkü: async/await desteği, connection pooling, timeout yönetimi.
- `initialize()` / `close()` lifecycle'ı ile client'ı kontrollü açıp kapatıyoruz (resource leak önleme).

**Neden `httpx` ve `requests` değil:** `requests` senkron. Biz async yapıdayız. `httpx` native async destekler.

---

### 3. `service/conversation_service.py` — İş Mantığı

**Ne yapar:** Konuşma akışını yönetir. 3 tur promptu sırayla çalıştırır, sonuçları kaydeder, JSON export eder.

**Neden kullanıldı:**
- **Prompt yönetimi:** 3 turn'ün promptları burada tanımlı. Her biri artan karmaşıklıkta.
- **Turn execution:** Her turda mesajı conversation'a ekler → API'ye gönderir → yanıtı kaydeder.
- **JSON export:** `ConversationExport` modeli ile tüm konuşmayı dosyaya yazar.
- **Metadata:** Assessment bilgileri, strateji açıklaması, hedeflenen model limitasyonu.

**Neden service pattern:** Router'dan iş mantığını ayırır. Test edilebilirlik ve yeniden kullanılabilirlik sağlar.

---

### 4. `router/conversation_router.py` — CLI Arayüzü

**Ne yapar:** Konuşma akışını terminalde görsel olarak sunar.

**Neden kullanıldı:**
- Router, kullanıcı ile etkileşimi yönetir. Service'i çağırır, sonuçları formatlar ve print eder.
- Her tur için: prompt önizleme → bekleme mesajı → yanıt önizleme → durum bilgisi.
- Error handling ve graceful shutdown (KeyboardInterrupt).

**Neden ayrı router:** Sunum katmanını iş mantığından ayırır. İleride FastAPI endpoint'e çevirmek kolay.

---

### 5. `utils/logger.py` — Loglama

**Ne yapar:** Loguru ile yapılandırılmış loglama. Console + dosya çıktısı.

**Neden kullanıldı:**
- Renkli terminal çıktısı (debug kolaylığı).
- Günlük rotasyonlu dosya logları (`src/logs/app.log`).
- Türkiye saat dilimi desteği.

---

### 6. `app.py` — Entry Point

**Ne yapar:** `.env` yükler, router'ı başlatır, `asyncio.run()` ile çalıştırır.

**Neden kullanıldı:** Tek sorumluluk — uygulamayı başlatmak. Tüm mantık alt katmanlarda.

---

## 3-Turn Konuşma Stratejisi

### Turn 1: Balanced Parentheses Checker ✅
- **Zorluk:** Kolay
- **Beklenen sonuç:** Başarılı
- **Neden:** Stack tabanlı klasik problem. GPT-4o bunu %100 doğru yazar.
- **Gösterdiğin yetenek:** Temel bir coding task'i net ve yapılandırılmış şekilde sorabiliyorsun.

### Turn 2: Mathematical Expression Evaluator ✅
- **Zorluk:** Orta-Zor
- **Beklenen sonuç:** Başarılı
- **Neden:** Shunting-Yard algoritması iyi bilinen bir algoritma. GPT-4o bunu da genellikle doğru implemente eder.
- **Gösterdiğin yetenek:** Karmaşıklığı artırırken hala modeli doğru çıktıya yönlendirebiliyorsun.

### Turn 3: Full Regex Engine from Scratch ❌
- **Zorluk:** Çok Zor
- **Beklenen sonuç:** Başarısız
- **Neden modeli kırar:**
  1. **Lookahead + Lookbehind kombinasyonu:** Variable-length lookbehind NFA'da çok zor
  2. **Non-greedy matching:** Full-string match context'inde lazy quantifier'lar hatalı davranır
  3. **Nested groups + alternation + quantifiers:** `((a|b)*c)+` gibi pattern'ler backtracking'i patlatır
  4. **20 test case birden:** Model hepsini aynı anda geçirmeye çalışırken bazılarında çöker
- **Gösterdiğin yetenek:** Modelin sınırlarını biliyorsun. Sofistike bir prompt yazıyorsun ama bilinçli olarak başarısız olacak bir alan seçiyorsun.

---

## Dosya Çıktıları

| Dosya | Açıklama |
|-------|----------|
| `output/conversation.json` | Tüm konuşmanın JSON export'u (mesajlar + turlar + metadata) |
| `docs/architecture.md` | Bu dosya — mimari ve strateji açıklaması |

---

## Çalıştırma

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Çalıştır
python app.py
```

Sonuç `output/conversation.json` dosyasına yazılır.

---

## Kullanılan Teknolojiler

| Teknoloji | Neden |
|-----------|-------|
| `httpx` | Async HTTP client — OpenRouter API çağrıları için |
| `pydantic` | Veri modelleme ve validasyon — JSON export için |
| `loguru` | Yapılandırılmış loglama — debug ve izleme için |
| `python-dotenv` | Environment variable yönetimi — API key güvenliği |
| `asyncio` | Async/await — non-blocking API çağrıları |
