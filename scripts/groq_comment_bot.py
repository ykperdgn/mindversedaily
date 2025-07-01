import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict
from groq_client import generate_content

class GroqCommentBot:
    def __init__(self):
        self.comments_file = "data/comments.json"
        self.ensure_data_directory()

    def ensure_data_directory(self):
        """Veri klasörünü oluştur"""
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.comments_file):
            with open(self.comments_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    def load_comments(self) -> Dict:
        """Mevcut yorumları yükle"""
        try:
            with open(self.comments_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def save_comments(self, comments: Dict):
        """Yorumları kaydet"""
        with open(self.comments_file, 'w', encoding='utf-8') as f:
            json.dump(comments, f, ensure_ascii=False, indent=2)

    def generate_comment_id(self, content: str, author: str) -> str:
        """Yorum için benzersiz ID oluştur"""
        hash_content = f"{content}{author}{datetime.now().isoformat()}"
        return hashlib.md5(hash_content.encode()).hexdigest()[:8]

    def add_comment(self, post_id: str, author: str, content: str, email: str = None) -> str:
        """Yeni yorum ekle"""
        comments = self.load_comments()

        if post_id not in comments:
            comments[post_id] = []

        comment_id = self.generate_comment_id(content, author)

        new_comment = {
            "id": comment_id,
            "author": author,
            "email": email,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "replies": []
        }

        comments[post_id].append(new_comment)
        self.save_comments(comments)

        return comment_id

    def generate_ai_reply(self, post_title: str, post_content: str, comment: str, language: str = "tr") -> str:
        """AI ile akıllı yorum yanıtı oluştur"""

        if language == "tr":
            prompt = f"""
Sen MindVerse Daily'nin akıllı yorum asistanısın. Bilimsel, sağlık ve teknoloji konularında uzman bir editörsün.

Blog Yazısı: "{post_title}"
Yazı İçeriği: "{post_content[:500]}..."
Kullanıcı Yorumu: "{comment}"

Bu yoruma profesyonel, bilgilendirici ve dostane bir yanıt oluştur. Yanıtın:
- Maksimum 200 kelime olsun
- Bilimsel doğrulukta olsun
- Yorumcunun sorularını cevaplasın
- Ek kaynak önerisi içerebilir
- Türkçe olsun
- MindVerse Daily editörü olarak konuş

Yanıt:"""
        else:
            prompt = f"""
You are MindVerse Daily's intelligent comment assistant. You're an expert editor in scientific, health and technology topics.

Blog Post: "{post_title}"
Post Content: "{post_content[:500]}..."
User Comment: "{comment}"

Create a professional, informative and friendly response to this comment. Your response should:
- Be maximum 200 words
- Be scientifically accurate
- Answer the commenter's questions
- Can include additional resource suggestions
- Be in English
- Speak as MindVerse Daily editor

Response:"""

        try:
            return generate_content(prompt)
        except Exception as e:
            if language == "tr":
                return f"Yorumunuz için teşekkürler! Bu konu hakkında daha detaylı araştırma yapıp size dönüş yapacağız."
            else:
                return f"Thank you for your comment! We'll research this topic further and get back to you."

    def add_ai_reply(self, post_id: str, comment_id: str, post_title: str, post_content: str, original_comment: str, language: str = "tr") -> str:
        """AI yanıtı ekle"""
        comments = self.load_comments()

        if post_id not in comments:
            return None

        # Yorumu bul
        for comment in comments[post_id]:
            if comment["id"] == comment_id:
                # AI yanıtı oluştur
                ai_reply = self.generate_ai_reply(post_title, post_content, original_comment, language)

                reply = {
                    "id": self.generate_comment_id(ai_reply, "MindVerse AI"),
                    "author": "MindVerse AI Assistant",
                    "content": ai_reply,
                    "timestamp": datetime.now().isoformat(),
                    "is_ai": True
                }

                comment["replies"].append(reply)
                self.save_comments(comments)
                return reply["id"]

        return None

    def get_comments(self, post_id: str) -> List[Dict]:
        """Belirli bir gönderi için yorumları getir"""
        comments = self.load_comments()
        return comments.get(post_id, [])

    def moderate_comment(self, content: str, language: str = "tr") -> Dict:
        """Yorum moderasyonu (spam, uygunsuz içerik kontrolü)"""

        if language == "tr":
            prompt = f"""
Bu yorumu moderasyon için analiz et:
"{content}"

Aşağıdaki kriterlere göre değerlendir:
1. Spam içerik var mı?
2. Uygunsuz dil var mı?
3. Reklam/link spam var mı?
4. Konuyla alakasız mı?
5. Yapıcı bir yorum mu?

JSON formatında yanıt ver:
{{
  "approved": true/false,
  "reason": "Ret sebebi veya onay notu",
  "confidence": 0.0-1.0
}}"""
        else:
            prompt = f"""
Analyze this comment for moderation:
"{content}"

Evaluate based on these criteria:
1. Contains spam?
2. Inappropriate language?
3. Advertisement/link spam?
4. Off-topic?
5. Constructive comment?

Respond in JSON format:
{{
  "approved": true/false,
  "reason": "Rejection reason or approval note",
  "confidence": 0.0-1.0
}}"""

        try:
            moderation_result = generate_content(prompt)
            # JSON parse etmeye çalış
            return json.loads(moderation_result)
        except:
            # Hata durumunda güvenli tarafta kal
            return {
                "approved": True,
                "reason": "Moderasyon sistemi şu anda kullanılamıyor",
                "confidence": 0.5
            }

# CLI kullanımı için
if __name__ == "__main__":
    import sys

    bot = GroqCommentBot()

    if len(sys.argv) < 2:
        print("Kullanım: python groq_comment_bot.py [test|add|reply|list]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "test":
        # Test yorumu
        test_reply = bot.generate_ai_reply(
            "Stresin Sağlığa Etkileri",
            "Stres, modern yaşamın en büyük sorunlarından biri haline geldi...",
            "Stresin kalp sağlığına etkileri neler? Yoga gerçekten faydalı mı?",
            "tr"
        )
        print("AI Test Yanıtı:")
        print(test_reply)

    elif command == "add":
        # Test yorumu ekle
        comment_id = bot.add_comment(
            "health/stress-effects",
            "Test Kullanıcı",
            "Bu makale çok faydalıydı, teşekkürler!"
        )
        print(f"Yorum eklendi: {comment_id}")

    elif command == "list":
        # Yorumları listele
        if len(sys.argv) > 2:
            post_id = sys.argv[2]
            comments = bot.get_comments(post_id)
            print(f"{post_id} için yorumlar:")
            for comment in comments:
                print(f"- {comment['author']}: {comment['content'][:50]}...")
        else:
            print("Post ID gerekli: python groq_comment_bot.py list POST_ID")
