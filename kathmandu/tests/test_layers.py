"""
🧪 Layer Tests
==============
5 Katman için test ritüelleri
"""

import asyncio
import pytest
from datetime import datetime

# Test edilecek modüller
from kathmandu.layers import (
    ToprakLayer,
    SuLayer,
    AtesLayer,
    HavaLayer,
    EterLayer,
    LayerResult
)
from kathmandu.layers.base import Element, LayerState


class TestToprakLayer:
    """🪨 TOPRAK Katmanı Testleri"""

    @pytest.fixture
    def layer(self):
        return ToprakLayer(num_agents=3)

    @pytest.mark.asyncio
    async def test_layer_creation(self, layer):
        """Katman oluşturma"""
        assert layer.name == "TOPRAK"
        assert layer.element == Element.TOPRAK
        assert layer.code_name == "CHAOS_INGESTION"
        assert len(layer.agents) == 3

    @pytest.mark.asyncio
    async def test_fold_single_source(self, layer):
        """Tek kaynak katlama"""
        result = await layer.process("test_data.pdf")

        assert isinstance(result, LayerResult)
        assert result.layer_name == "TOPRAK"
        assert result.fold_count == 1
        assert layer.state == LayerState.COMPLETE

    @pytest.mark.asyncio
    async def test_fold_multiple_sources(self, layer):
        """Çoklu kaynak katlama"""
        sources = ["file1.pdf", "file2.csv", "api.json"]
        result = await layer.process(
            "batch",
            context={"sources": sources}
        )

        assert result.output_data["total_collected"] == 3

    @pytest.mark.asyncio
    async def test_chaos_index_calculation(self, layer):
        """Kaos indeksi hesaplama"""
        result = await layer.process("normal_text.txt")

        packets = result.output_data.get("packets", [])
        for packet in packets:
            assert 0 <= packet["chaos_index"] <= 1
            assert 0 <= packet["lotus_potential"] <= 1


class TestSuLayer:
    """🌊 SU Katmanı Testleri"""

    @pytest.fixture
    def layer(self):
        return SuLayer()

    @pytest.mark.asyncio
    async def test_layer_creation(self, layer):
        """Katman oluşturma"""
        assert layer.name == "SU"
        assert layer.element == Element.SU
        assert layer.code_name == "PURIFICATION_FLOW"
        assert len(layer.sherpas) == 7

    @pytest.mark.asyncio
    async def test_purification_removes_noise(self, layer):
        """Gürültü temizleme"""
        dirty_data = "Bu   bir   test   metnidir.   Çok   boşluk   var."
        result = await layer.process(dirty_data)

        purified = result.output_data["purified_text"]
        assert "   " not in purified  # Fazla boşluklar temizlendi

    @pytest.mark.asyncio
    async def test_purity_level_assigned(self, layer):
        """Saflık seviyesi ataması"""
        result = await layer.process("clean data")

        purity = result.output_data["purity_level"]
        valid_levels = ["muddy", "cloudy", "clearing", "clear", "crystal", "sacred"]
        assert purity in valid_levels

    @pytest.mark.asyncio
    async def test_sherpa_tracking(self, layer):
        """Şerpa takibi"""
        result = await layer.process("test data")

        sherpas = result.output_data["processing_sherpas"]
        assert len(sherpas) > 0
        assert all(isinstance(s, str) for s in sherpas)


class TestAtesLayer:
    """🔥 ATEŞ Katmanı Testleri"""

    @pytest.fixture
    def layer(self):
        return AtesLayer()

    @pytest.mark.asyncio
    async def test_layer_creation(self, layer):
        """Katman oluşturma"""
        assert layer.name == "ATEŞ"
        assert layer.element == Element.ATES
        assert layer.code_name == "ALCHEMICAL_FORGE"
        assert len(layer.monks) == 7

    @pytest.mark.asyncio
    async def test_voting_produces_consensus(self, layer):
        """Oylama konsensüs üretir"""
        result = await layer.process("test input")

        assert "voting_consensus" in result.output_data
        assert "dissent_ratio" in result.output_data
        assert 0 <= result.output_data["dissent_ratio"] <= 1

    @pytest.mark.asyncio
    async def test_monk_contributions_tracked(self, layer):
        """Rahip katkıları takibi"""
        result = await layer.process("analyze this")

        contributions = result.output_data.get("monk_contributions", {})
        assert len(contributions) > 0

        for monk_name, contribution in contributions.items():
            assert "role" in contribution
            assert "contribution" in contribution

    @pytest.mark.asyncio
    async def test_steel_score_valid(self, layer):
        """Çelik skoru geçerli aralıkta"""
        result = await layer.process("forge this")

        steel_score = result.output_data["steel_score"]
        assert 0 <= steel_score <= 1


class TestHavaLayer:
    """🌬️ HAVA Katmanı Testleri"""

    @pytest.fixture
    def layer(self):
        return HavaLayer()

    @pytest.mark.asyncio
    async def test_layer_creation(self, layer):
        """Katman oluşturma"""
        assert layer.name == "HAVA"
        assert layer.element == Element.HAVA
        assert layer.code_name == "WIND_TRANSMISSION"
        assert layer.altitude == 8848

    @pytest.mark.asyncio
    async def test_prophecies_generated(self, layer):
        """Kehanetler üretildi"""
        result = await layer.process({"forged_wisdom": "test wisdom"})

        prophecies = result.output_data.get("prophecies", [])
        assert len(prophecies) > 0

    @pytest.mark.asyncio
    async def test_prayer_flags_created(self, layer):
        """Dua bayrakları oluşturuldu"""
        result = await layer.process({"forged_wisdom": "test"})

        flags = result.output_data.get("prayer_flags", [])
        assert len(flags) > 0

        for flag in flags:
            assert "color" in flag
            assert "message" in flag
            assert "direction" in flag

    @pytest.mark.asyncio
    async def test_vision_score_valid(self, layer):
        """Vizyon skoru geçerli"""
        result = await layer.process(
            {"forged_wisdom": "vision test", "steel_score": 0.8}
        )

        vision_score = result.output_data["vision_score"]
        assert 0 <= vision_score <= 1


class TestEterLayer:
    """🌌 ETER Katmanı Testleri"""

    @pytest.fixture
    def layer(self):
        return EterLayer()

    @pytest.mark.asyncio
    async def test_layer_creation(self, layer):
        """Katman oluşturma"""
        assert layer.name == "ETER"
        assert layer.element == Element.ETER
        assert layer.code_name == "NIRVANA_SUMMIT"
        assert layer.frequency.value == 963

    @pytest.mark.asyncio
    async def test_crystal_created(self, layer):
        """Kristal oluşturuldu"""
        result = await layer.process({
            "prophecies": ["test prophecy"],
            "vision_score": 0.8
        })

        crystal = result.output_data.get("crystal", {})
        assert "id" in crystal
        assert "essence" in crystal
        assert "frequency" in crystal

    @pytest.mark.asyncio
    async def test_enlightenment_level_assigned(self, layer):
        """Aydınlanma seviyesi atandı"""
        result = await layer.process({
            "prophecies": ["prophecy 1", "prophecy 2"],
            "vision_score": 0.9
        })

        crystal = result.output_data["crystal"]
        valid_levels = [
            "seeker", "initiate", "practitioner",
            "adept", "master", "sage", "buddha"
        ]
        assert crystal["enlightenment"] in valid_levels

    @pytest.mark.asyncio
    async def test_parchment_generated(self, layer):
        """Parşömen oluşturuldu"""
        result = await layer.process({
            "prophecies": ["test"],
            "vision_score": 0.5
        })

        parchment = result.output_data.get("parchment", "")
        assert len(parchment) > 0
        assert "CAZIBE" in parchment

    @pytest.mark.asyncio
    async def test_cazibe_output_complete(self, layer):
        """CAZIBE çıktısı eksiksiz"""
        result = await layer.process({
            "prophecies": ["insight 1"],
            "vision_score": 0.7
        })

        output = result.output_data.get("cazibe_output", {})
        assert "title" in output
        assert "summary" in output
        assert "insights" in output
        assert "recommendations" in output
        assert "n2n_message" in output


class TestLayerIntegration:
    """🔗 Katman Entegrasyon Testleri"""

    @pytest.mark.asyncio
    async def test_layer_chain(self):
        """Katman zinciri testi"""
        toprak = ToprakLayer()
        su = SuLayer()
        ates = AtesLayer()
        hava = HavaLayer()
        eter = EterLayer()

        # Zincir boyunca veri akışı
        r1 = await toprak.process("raw_data.pdf")
        r2 = await su.process(r1.output_data)
        r3 = await ates.process(r2.output_data)
        r4 = await hava.process(r3.output_data)
        r5 = await eter.process(r4.output_data)

        # Son katman kristal üretmeli
        assert "crystal" in r5.output_data
        assert r5.fold_count == 5

    @pytest.mark.asyncio
    async def test_all_layers_have_unique_elements(self):
        """Tüm katmanlar benzersiz elemente sahip"""
        layers = [
            ToprakLayer(),
            SuLayer(),
            AtesLayer(),
            HavaLayer(),
            EterLayer()
        ]

        elements = [layer.element for layer in layers]
        assert len(set(elements)) == 5  # Hepsi benzersiz


# pytest çalıştırma
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
