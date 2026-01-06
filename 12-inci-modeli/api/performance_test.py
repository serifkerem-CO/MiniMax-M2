"""
Performance Testing for 12. İnci Modeli
Load testing with Locust

Installation:
    pip install locust

Run:
    locust -f performance_test.py --host=http://localhost:8000

Open browser:
    http://localhost:8089
"""

from locust import HttpUser, task, between, events
import random
import json

# ============================================
# Test Data
# ============================================

# Turkish test messages
TR_TEST_MESSAGES = [
    "Bugün harika bir gün geçirdim, çok mutluyum!",
    "Çok üzgünüm, bugün kötü bir gün",
    "Bu duruma çok sinirlendim, yeter artık!",
    "Endişeliyim, ne yapacağımı bilmiyorum",
    "Vay canına, bunu hiç beklemiyordum!",
    "Seni çok seviyorum, teşekkürler",
    "Bu çok ilginç, nasıl çalışıyor acaba?",
    "Çok huzurluyum, her şey harika",
    "Başarabilirim, kendime güveniyorum!",
    "Keşke yapmasa, pişmanım",
    "Çok heyecanlıyım, harika bir şey olacak!",
    "Merhaba nasılsın?"
]

# English test messages
EN_TEST_MESSAGES = [
    "I'm so happy today!",
    "I feel sad and lonely",
    "I'm really angry about this",
    "I'm worried and anxious",
    "Wow, this is amazing!",
    "I love you so much",
    "This is very interesting",
    "I feel peaceful and calm",
    "I'm confident I can do this",
    "I regret doing that",
    "I'm so excited!",
    "Hello how are you?"
]

# ============================================
# Locust User Classes
# ============================================

class EmotionAnalysisUser(HttpUser):
    """
    User performing emotion analysis requests
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    @task(10)  # Weight: 10 (most common task)
    def analyze_emotion_tr(self):
        """Analyze Turkish text"""
        message = random.choice(TR_TEST_MESSAGES)

        with self.client.post(
            "/api/v1/emotion/analyze",
            json={"text": message, "language": "tr"},
            catch_response=True,
            name="Emotion Analysis (TR)"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "emotions" in data and len(data["emotions"]) > 0:
                    response.success()
                else:
                    response.failure("No emotions detected")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(5)  # Weight: 5
    def analyze_emotion_en(self):
        """Analyze English text"""
        message = random.choice(EN_TEST_MESSAGES)

        with self.client.post(
            "/api/v1/emotion/analyze",
            json={"text": message, "language": "en"},
            catch_response=True,
            name="Emotion Analysis (EN)"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(3)  # Weight: 3
    def chat_endpoint(self):
        """Test chat endpoint"""
        message = random.choice(TR_TEST_MESSAGES)

        with self.client.post(
            "/api/v1/chat",
            json={"text": message},
            catch_response=True,
            name="Chat"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(2)  # Weight: 2
    def get_emotions_list(self):
        """Get emotions list"""
        with self.client.get(
            "/api/v1/emotions/list",
            catch_response=True,
            name="Get Emotions List"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("total") == 12:
                    response.success()
                else:
                    response.failure("Invalid emotion count")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)  # Weight: 1
    def health_check(self):
        """Health check"""
        with self.client.get(
            "/health",
            catch_response=True,
            name="Health Check"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"HTTP {response.status_code}")


class HeavyLoadUser(HttpUser):
    """
    User generating heavy load for stress testing
    """
    wait_time = between(0.1, 0.5)  # Very fast requests

    @task
    def rapid_analysis(self):
        """Rapid-fire emotion analysis"""
        message = random.choice(TR_TEST_MESSAGES + EN_TEST_MESSAGES)

        self.client.post(
            "/api/v1/emotion/analyze",
            json={"text": message, "language": random.choice(["tr", "en"])},
            name="Heavy Load Analysis"
        )


# ============================================
# Custom Metrics
# ============================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    print("\n" + "="*60)
    print("🚀 Starting 12. İnci Modeli Performance Test")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    print("\n" + "="*60)
    print("✅ Performance Test Completed")
    print("="*60)

    stats = environment.stats.total

    print(f"\nTotal Requests: {stats.num_requests}")
    print(f"Total Failures: {stats.num_failures}")
    print(f"Avg Response Time: {stats.avg_response_time:.2f}ms")
    print(f"Min Response Time: {stats.min_response_time:.2f}ms")
    print(f"Max Response Time: {stats.max_response_time:.2f}ms")
    print(f"Requests/sec: {stats.total_rps:.2f}")
    print(f"Failure Rate: {stats.fail_ratio*100:.2f}%")
    print()


# ============================================
# Custom Load Shapes (Optional)
# ============================================

from locust import LoadTestShape

class StepLoadShape(LoadTestShape):
    """
    Step load shape - gradually increase users
    """
    step_time = 30  # seconds
    step_load = 10  # users per step
    spawn_rate = 5  # users per second
    time_limit = 300  # 5 minutes total

    def tick(self):
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None

        current_step = run_time // self.step_time
        return (current_step * self.step_load, self.spawn_rate)


class SpikeLoadShape(LoadTestShape):
    """
    Spike load - sudden traffic spikes
    """
    def tick(self):
        run_time = self.get_run_time()

        if run_time < 60:
            user_count = 10
        elif run_time < 120:
            user_count = 100  # Spike!
        elif run_time < 180:
            user_count = 10  # Back to normal
        elif run_time < 240:
            user_count = 200  # Bigger spike!
        elif run_time < 300:
            user_count = 10  # Back to normal
        else:
            return None

        return (user_count, 10)


# ============================================
# Run Instructions
# ============================================

"""
# Basic Run
locust -f performance_test.py --host=http://localhost:8000

# Headless Mode (no web UI)
locust -f performance_test.py --host=http://localhost:8000 \
    --users 100 --spawn-rate 10 --run-time 5m --headless

# With step load shape
locust -f performance_test.py --host=http://localhost:8000 \
    --users 100 --spawn-rate 5 --headless --load-shape StepLoadShape

# Distributed load testing (multiple workers)
# Master:
locust -f performance_test.py --host=http://localhost:8000 --master

# Workers (run in separate terminals):
locust -f performance_test.py --host=http://localhost:8000 --worker

# Export results
locust -f performance_test.py --host=http://localhost:8000 \
    --users 100 --spawn-rate 10 --run-time 5m --headless \
    --html=report.html --csv=results
"""
