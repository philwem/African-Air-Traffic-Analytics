"""
Unit tests for data ingestion components
"""

from geospatial_filter import GeospatialFilter, EnhancedGeospatialFilter
from config import Config, GeoBoundingBox
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import json

# Import modules to test
import sys
sys.path.insert(0, '..')


class TestGeoBoundingBox:
    """Test geospatial bounding box"""

    def test_west_africa_contains_lagos(self):
        bbox = GeoBoundingBox()
        # Lagos, Nigeria coordinates
        assert bbox.contains(6.5244, 3.3792) is True

    def test_west_africa_contains_accra(self):
        bbox = GeoBoundingBox()
        # Accra, Ghana coordinates
        assert bbox.contains(5.6037, -0.1870) is True

    def test_west_africa_excludes_london(self):
        bbox = GeoBoundingBox()
        # London, UK coordinates (outside West Africa)
        assert bbox.contains(51.5074, -0.1278) is False

    def test_west_africa_excludes_johannesburg(self):
        bbox = GeoBoundingBox()
        # Johannesburg, South Africa (too far south)
        assert bbox.contains(-26.2041, 28.0473) is False

    def test_edge_cases(self):
        bbox = GeoBoundingBox()
        # Test exact boundaries
        assert bbox.contains(4.0, -17.0) is True
        assert bbox.contains(20.0, 15.0) is True
        # Just outside boundaries
        assert bbox.contains(3.9, -17.0) is False
        assert bbox.contains(20.1, 15.0) is False


class TestGeospatialFilter:
    """Test geospatial filtering logic"""

    @pytest.fixture
    def filter_instance(self):
        return GeospatialFilter()

    def test_filter_valid_position_in_bounds(self, filter_instance):
        position = {
            'hex': 'ABC123',
            'lat': 6.5244,
            'lon': 3.3792,
            'alt_baro': 35000
        }

        result = filter_instance.filter_position(position)

        assert result is not None
        assert result['hex'] == 'ABC123'
        assert 'filtered_at' in result
        assert result['region'] == 'west_africa'

    def test_filter_position_out_of_bounds(self, filter_instance):
        position = {
            'hex': 'XYZ789',
            'lat': 51.5074,  # London
            'lon': -0.1278,
            'alt_baro': 35000
        }

        result = filter_instance.filter_position(position)

        assert result is None
        assert filter_instance.filtered_count == 1

    def test_filter_position_missing_coordinates(self, filter_instance):
        position = {
            'hex': 'ABC123',
            'alt_baro': 35000
            # Missing lat/lon
        }

        result = filter_instance.filter_position(position)

        assert result is None
        assert filter_instance.filtered_count == 1

    def test_filter_position_invalid_coordinates(self, filter_instance):
        position = {
            'hex': 'ABC123',
            'lat': 'invalid',
            'lon': 'invalid',
            'alt_baro': 35000
        }

        result = filter_instance.filter_position(position)

        assert result is None

    def test_filter_batch(self, filter_instance):
        positions = [
            {'hex': 'A1', 'lat': 6.5244, 'lon': 3.3792},  # Lagos - IN
            {'hex': 'A2', 'lat': 51.5074, 'lon': -0.1278},  # London - OUT
            {'hex': 'A3', 'lat': 5.6037, 'lon': -0.1870},  # Accra - IN
            {'hex': 'A4', 'lat': -26.2041, 'lon': 28.0473},  # Joburg - OUT
        ]

        filtered = filter_instance.filter_batch(positions)

        assert len(filtered) == 2
        assert filtered[0]['hex'] == 'A1'
        assert filtered[1]['hex'] == 'A3'

    def test_statistics_tracking(self, filter_instance):
        positions = [
            {'hex': 'A1', 'lat': 6.5244, 'lon': 3.3792},  # IN
            {'hex': 'A2', 'lat': 51.5074, 'lon': -0.1278},  # OUT
        ]

        filter_instance.filter_batch(positions)

        assert filter_instance.total_count == 2
        assert filter_instance.passed_count == 1
        assert filter_instance.filtered_count == 1


class TestEnhancedGeospatialFilter:
    """Test enhanced filter with airport detection"""

    @pytest.fixture
    def enhanced_filter(self):
        return EnhancedGeospatialFilter()

    def test_find_nearest_airport_lagos(self, enhanced_filter):
        # Position very close to Lagos airport
        nearest = enhanced_filter.find_nearest_airport(
            6.5774, 3.3212, max_distance_km=5)

        assert nearest == 'LOS'

    def test_find_nearest_airport_accra(self, enhanced_filter):
        # Position very close to Accra airport
        nearest = enhanced_filter.find_nearest_airport(
            5.6052, -0.1667, max_distance_km=5)

        assert nearest == 'ACC'

    def test_find_nearest_airport_none_nearby(self, enhanced_filter):
        # Position far from any airport
        nearest = enhanced_filter.find_nearest_airport(
            10.0, 5.0, max_distance_km=50)

        assert nearest is None

    def test_enrich_position_with_airport(self, enhanced_filter):
        position = {
            'hex': 'ABC123',
            'lat': 6.5774,
            'lon': 3.3212,
            'alt_baro': 1000  # Low altitude, likely near airport
        }

        enriched = enhanced_filter.enrich_position(position)

        assert 'nearest_airport' in enriched
        assert enriched['nearest_airport'] == 'LOS'
        assert enriched['airport_name'] == 'Lagos Murtala Muhammed'
        assert enriched['country'] == 'Nigeria'


class TestStreamIngestion:
    """Test streaming ingestion components"""

    @patch('streaming_ingestion.KafkaProducer')
    @patch('streaming_ingestion.requests.Session')
    def test_fetch_positions_success(self, mock_session, mock_producer):
        from streaming_ingestion import ADSBStreamIngester

        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'aircraft': [
                {'hex': 'ABC123', 'lat': 6.5, 'lon': 3.3, 'alt_baro': 35000}
            ]
        }
        mock_session.return_value.get.return_value = mock_response

        ingester = ADSBStreamIngester()
        positions = ingester.fetch_positions()

        assert positions is not None
        assert len(positions) == 1
        assert positions[0]['hex'] == 'ABC123'

    @patch('streaming_ingestion.KafkaProducer')
    @patch('streaming_ingestion.requests.Session')
    def test_fetch_positions_api_error(self, mock_session, mock_producer):
        from streaming_ingestion import ADSBStreamIngester
        import requests

        # Mock API error
        mock_session.return_value.get.side_effect = requests.exceptions.RequestException(
            "API Error")

        ingester = ADSBStreamIngester()
        positions = ingester.fetch_positions()

        assert positions is None
        assert ingester.error_count == 1


class TestBatchIngestion:
    """Test batch ingestion components"""

    @patch('batch_ingestion.requests.Session')
    def test_fetch_aircraft_metadata_success(self, mock_session):
        from ingestion.batch.adsbdb_metadata_ingestion import ADSBDBMetadataIngester

        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'icao': 'ABC123',
            'registration': 'N12345',
            'model': 'Boeing 737',
            'operator': 'Test Airlines'
        }
        mock_response.raise_for_status = Mock()
        mock_session.return_value.get.return_value = mock_response

        ingester = ADSBDBMetadataIngester()
        metadata = ingester.fetch_aircraft_metadata('ABC123')

        assert metadata is not None
        assert metadata['icao'] == 'ABC123'
        assert metadata['registration'] == 'N12345'
        assert 'metadata_fetched_at' in metadata

    @patch('batch_ingestion.requests.Session')
    def test_fetch_aircraft_metadata_not_found(self, mock_session):
        from ingestion.batch.adsbdb_metadata_ingestion import ADSBDBMetadataIngester
        import requests

        # Mock 404 response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_response.status_code = 404
        mock_session.return_value.get.return_value = mock_response

        ingester = ADSBDBMetadataIngester()
        metadata = ingester.fetch_aircraft_metadata('NOTFOUND')

        assert metadata is None


class TestConfiguration:
    """Test configuration management"""

    def test_config_initialization(self):
        config = Config()

        assert config.geo_bbox is not None
        assert config.adsb is not None
        assert config.kafka is not None
        assert config.storage is not None

    def test_kafka_topics_configured(self):
        config = Config()

        assert config.kafka.raw_topic == "adsb.raw.positions"
        assert config.kafka.filtered_topic == "adsb.bronze.positions"
        assert config.kafka.metadata_topic == "adsb.bronze.metadata"

    def test_storage_paths_configured(self):
        config = Config()

        assert config.storage.bronze_path is not None
        assert config.storage.format == "parquet"
        assert config.storage.partition_by == ["year", "month", "day", "hour"]


# Integration tests (require running services)
@pytest.mark.integration
class TestIntegration:
    """Integration tests - require running Kafka"""

    @pytest.mark.skip(reason="Requires running Kafka instance")
    def test_kafka_producer_connection(self):
        from kafka import KafkaProducer
        from config import config

        producer = KafkaProducer(
            bootstrap_servers=config.kafka.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        # Send test message
        future = producer.send(config.kafka.raw_topic, {'test': 'message'})
        record_metadata = future.get(timeout=10)

        assert record_metadata is not None
        producer.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
