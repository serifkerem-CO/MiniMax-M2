"""
🧪 DataStupa Tests
==================
Ana orkestratör testleri
"""

import asyncio
import pytest
from datetime import datetime

from kathmandu.stupa import DataStupa, enlighten, StupaState


class TestDataStupa:
    """🛕 DataStupa Testleri"""

    @pytest.fixture
    def stupa(self):
        return DataStupa(enable_logging=False)

    @pytest.mark.asyncio
    async def test_stupa_creation(self, stupa):
        """Stupa oluşturma"""
        assert stupa.state == StupaState.DORMANT
        assert len(stupa.layers) == 5
        assert len(stupa.layer_order) == 5

    @pytest.mark.asyncio
    async def test_full_process(self, stupa):
        """Tam işleme döngüsü"""
        journey = await stupa.process("test data")

        assert journey.journey_id.startswith("JOURNEY_")
        assert journey.state == StupaState.ENLIGHTENED
        assert len(journey.layers_traversed) == 5
        assert journey.duration_seconds > 0

    @pytest.mark.asyncio
    async def test_partial_process(self, stupa):
        """Kısmi işleme (belirli katmanlar)"""
        journey = await stupa.process(
            "test",
            start_layer="SU",
            end_layer="ATEŞ"
        )

        assert journey.layers_traversed == ["SU", "ATEŞ"]

    @pytest.mark.asyncio
    async def test_process_with_context(self, stupa):
        """Bağlamla işleme"""
        context = {
            "client": "TEST_CLIENT",
            "priority": "high"
        }
        journey = await stupa.process("data", context=context)

        assert journey.state == StupaState.ENLIGHTENED

    @pytest.mark.asyncio
    async def test_journey_tracking(self, stupa):
        """Yolculuk takibi"""
        j1 = await stupa.process("data1")
        j2 = await stupa.process("data2")

        assert len(stupa.journeys) == 2
        assert stupa.get_journey(j1.journey_id) is not None
        assert stupa.get_journey(j2.journey_id) is not None

    @pytest.mark.asyncio
    async def test_quick_process(self, stupa):
        """Hızlı işleme"""
        result = await stupa.quick_process("quick test")

        assert "journey_id" in result
        assert "duration" in result

    @pytest.mark.asyncio
    async def test_batch_process(self, stupa):
        """Toplu işleme"""
        data_list = ["item1", "item2", "item3"]
        journeys = await stupa.process_batch(data_list, parallel=True)

        assert len(journeys) == 3
        assert all(j.state == StupaState.ENLIGHTENED for j in journeys)

    @pytest.mark.asyncio
    async def test_meditation(self, stupa):
        """Meditasyon"""
        await stupa.meditate(duration_seconds=0.1)
        assert stupa.state == StupaState.MEDITATION

    @pytest.mark.asyncio
    async def test_reset(self, stupa):
        """Sıfırlama"""
        await stupa.process("data")
        assert len(stupa.journeys) > 0

        stupa.reset()
        assert len(stupa.journeys) == 0
        assert stupa.state == StupaState.DORMANT

    @pytest.mark.asyncio
    async def test_layer_stats(self, stupa):
        """Katman istatistikleri"""
        await stupa.process("data")

        for layer_name in stupa.layer_order:
            stats = stupa.get_layer_stats(layer_name)
            assert "name" in stats
            assert "element" in stats
            assert "state" in stats

    @pytest.mark.asyncio
    async def test_stupa_stats(self, stupa):
        """Stupa istatistikleri"""
        await stupa.process("data1")
        await stupa.process("data2")

        stats = stupa.get_stupa_stats()

        assert stats["total_journeys"] == 2
        assert stats["successful_journeys"] == 2
        assert "layers" in stats
        assert "monk_council" in stats
        assert "prayer_wheels" in stats

    @pytest.mark.asyncio
    async def test_final_output_has_crystal(self, stupa):
        """Son çıktı kristal içerir"""
        journey = await stupa.process("test for crystal")

        assert journey.final_output is not None
        assert "crystal" in journey.final_output

        crystal = journey.final_output["crystal"]
        assert "id" in crystal
        assert "essence" in crystal
        assert "frequency" in crystal

    @pytest.mark.asyncio
    async def test_final_output_has_parchment(self, stupa):
        """Son çıktı parşömen içerir"""
        journey = await stupa.process("test for parchment")

        assert journey.final_output is not None
        assert "parchment" in journey.final_output
        assert len(journey.final_output["parchment"]) > 0


class TestEnlightenFunction:
    """⚡ Hızlı Aydınlanma Fonksiyonu Testleri"""

    @pytest.mark.asyncio
    async def test_enlighten_basic(self):
        """Temel aydınlanma"""
        result = await enlighten("test question")

        assert "journey_id" in result
        assert "duration" in result

    @pytest.mark.asyncio
    async def test_enlighten_returns_insights(self):
        """Aydınlanma içgörü döndürür"""
        result = await enlighten("analyze market")

        if "insights" in result:
            assert isinstance(result["insights"], list)


class TestStupaObservers:
    """👁️ Gözlemci Testleri"""

    @pytest.mark.asyncio
    async def test_observer_called(self):
        """Gözlemci çağrılır"""
        messages = []

        def observer(msg):
            messages.append(msg)

        stupa = DataStupa(enable_logging=False)
        stupa.add_observer(observer)

        await stupa.process("test")

        # Gözlemci mesaj aldı
        assert len(messages) > 0


# pytest çalıştırma
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
