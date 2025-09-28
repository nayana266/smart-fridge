import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.services.rekog import RekognitionService, DetectionResult
from app.services.normalize import FoodNormalizer, NormalizedItem
from app.routes.analyze import VisionDetectRequest, VisionDetectResponse

class TestRekognitionService:
    """Test cases for Rekognition service"""
    
    @pytest.fixture
    def mock_rekognition_service(self):
        """Mock Rekognition service for testing"""
        service = RekognitionService()
        service.rekognition = Mock()
        return service
    
    @pytest.fixture
    def sample_rekognition_response(self):
        """Sample Rekognition API response"""
        return {
            'Labels': [
                {
                    'Name': 'Food',
                    'Confidence': 95.5,
                    'Instances': [],
                    'Parents': []
                },
                {
                    'Name': 'Beef',
                    'Confidence': 88.2,
                    'Instances': [],
                    'Parents': [{'Name': 'Food'}]
                },
                {
                    'Name': 'Chicken',
                    'Confidence': 92.1,
                    'Instances': [],
                    'Parents': [{'Name': 'Food'}]
                },
                {
                    'Name': 'Vegetable',
                    'Confidence': 85.0,
                    'Instances': [],
                    'Parents': [{'Name': 'Food'}]
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_detect_labels_with_retry_success(self, mock_rekognition_service, sample_rekognition_response):
        """Test successful label detection with retry"""
        mock_rekognition_service.rekognition.detect_labels.return_value = sample_rekognition_response
        
        result = await mock_rekognition_service._detect_labels_with_retry(
            bucket="test-bucket",
            key="test-image.jpg"
        )
        
        assert len(result) == 4
        assert result[0]['Name'] == 'Food'
        assert result[0]['Confidence'] == 95.5
    
    @pytest.mark.asyncio
    async def test_detect_labels_with_retry_failure(self, mock_rekognition_service):
        """Test label detection with retry on failure"""
        from botocore.exceptions import ClientError
        
        # Mock failure then success
        mock_rekognition_service.rekognition.detect_labels.side_effect = [
            ClientError({'Error': {'Code': 'ThrottlingException'}}, 'DetectLabels'),
            {'Labels': [{'Name': 'Food', 'Confidence': 95.0, 'Instances': [], 'Parents': []}]}
        ]
        
        result = await mock_rekognition_service._detect_labels_with_retry(
            bucket="test-bucket",
            key="test-image.jpg"
        )
        
        assert len(result) == 1
        assert result[0]['Name'] == 'Food'
    
    @pytest.mark.asyncio
    async def test_detect_food_items_multiple_images(self, mock_rekognition_service):
        """Test processing multiple images"""
        # Mock responses for different images
        responses = [
            {'Labels': [{'Name': 'Beef', 'Confidence': 88.2, 'Instances': [], 'Parents': []}]},
            {'Labels': [{'Name': 'Chicken', 'Confidence': 92.1, 'Instances': [], 'Parents': []}]},
            {'Labels': [{'Name': 'Vegetable', 'Confidence': 85.0, 'Instances': [], 'Parents': []}]}
        ]
        
        mock_rekognition_service.rekognition.detect_labels.side_effect = responses
        
        result = await mock_rekognition_service.detect_food_items(
            s3_keys=["image1.jpg", "image2.jpg", "image3.jpg"],
            bucket="test-bucket"
        )
        
        assert len(result) == 3
        names = [item.name for item in result]
        assert 'beef' in names
        assert 'chicken' in names
        assert 'vegetable' in names

class TestFoodNormalizer:
    """Test cases for food normalization"""
    
    @pytest.fixture
    def normalizer(self):
        """Create normalizer with test data"""
        test_aliases = {
            "beef": ["beef", "steak", "ground beef"],
            "chicken": ["chicken", "poultry"],
            "tofu": ["tofu", "bean curd"]
        }
        normalizer = FoodNormalizer()
        normalizer.aliases = test_aliases
        normalizer.canonical_items = list(test_aliases.keys())
        return normalizer
    
    def test_exact_match_normalization(self, normalizer):
        """Test exact match normalization"""
        result = normalizer.normalize_item("beef", 0.9, 1)
        
        assert result is not None
        assert result.canonical_name == "beef"
        assert result.raw_name == "beef"
        assert result.confidence == 0.9
    
    def test_alias_match_normalization(self, normalizer):
        """Test alias match normalization"""
        result = normalizer.normalize_item("steak", 0.85, 2)
        
        assert result is not None
        assert result.canonical_name == "beef"
        assert result.raw_name == "steak"
        assert result.confidence == 0.85
        assert result.count == 2
    
    def test_fuzzy_match_normalization(self, normalizer):
        """Test fuzzy match normalization"""
        # Test with slight variation
        result = normalizer.normalize_item("chikn", 0.8, 1)
        
        assert result is not None
        assert result.canonical_name == "chicken"
        assert result.confidence < 0.8  # Should be adjusted based on fuzzy score
    
    def test_no_match_normalization(self, normalizer):
        """Test when no match is found"""
        result = normalizer.normalize_item("xyz_unknown_food", 0.7, 1)
        
        assert result is None
    
    def test_normalize_items_merge_duplicates(self, normalizer):
        """Test merging duplicate items"""
        raw_items = [
            {'name': 'beef', 'confidence': 0.9, 'count': 1},
            {'name': 'steak', 'confidence': 0.85, 'count': 2},  # Same canonical as beef
            {'name': 'chicken', 'confidence': 0.8, 'count': 1}
        ]
        
        result = normalizer.normalize_items(raw_items)
        
        assert len(result) == 2  # beef and chicken merged
        
        # Find beef item
        beef_item = next(item for item in result if item.canonical_name == "beef")
        assert beef_item.count == 3  # 1 + 2
        assert beef_item.confidence == 0.9  # Higher confidence kept

class TestVisionEndpoint:
    """Test cases for vision detection endpoint"""
    
    @pytest.fixture
    def mock_rekognition_service(self):
        """Mock Rekognition service"""
        service = Mock()
        service.detect_food_items = AsyncMock()
        return service
    
    @pytest.fixture
    def mock_normalizer(self):
        """Mock food normalizer"""
        normalizer = Mock()
        normalizer.normalize_items = Mock()
        return normalizer
    
    @pytest.mark.asyncio
    async def test_vision_detect_success(self, mock_rekognition_service, mock_normalizer):
        """Test successful vision detection"""
        # Mock Rekognition results
        mock_detection_results = [
            DetectionResult(name="beef", count=1, confidence=0.9),
            DetectionResult(name="chicken", count=1, confidence=0.85)
        ]
        mock_rekognition_service.detect_food_items.return_value = mock_detection_results
        
        # Mock normalization results
        mock_normalized_items = [
            NormalizedItem(canonical_name="beef", raw_name="beef", confidence=0.9, count=1),
            NormalizedItem(canonical_name="chicken", raw_name="chicken", confidence=0.85, count=1)
        ]
        mock_normalizer.normalize_items.return_value = mock_normalized_items
        
        # Patch the services
        with patch('app.routes.analyze.rekognition_service', mock_rekognition_service), \
             patch('app.routes.analyze.food_normalizer', mock_normalizer):
            
            from app.routes.analyze import detect_food_items
            
            request = VisionDetectRequest(keys=["image1.jpg", "image2.jpg"])
            response = await detect_food_items(request)
            
            assert len(response.items) == 2
            assert response.processing_stats["images_processed"] == 2
            assert response.processing_stats["normalized_items"] == 2
            assert response.processing_stats["normalization_rate"] == 100.0
    
    def test_vision_detect_request_validation(self):
        """Test request validation"""
        # Valid request
        request = VisionDetectRequest(keys=["image1.jpg", "image2.jpg"])
        assert len(request.keys) == 2
        assert request.bucket == "smart-fridge-images"
        
        # Custom bucket
        request = VisionDetectRequest(keys=["image1.jpg"], bucket="custom-bucket")
        assert request.bucket == "custom-bucket"

# Integration test with real normalization
class TestVisionIntegration:
    """Integration tests with real normalization service"""
    
    def test_real_normalization_examples(self):
        """Test with real food items that should normalize correctly"""
        normalizer = FoodNormalizer()
        
        test_cases = [
            ("ground beef", "beef"),
            ("chicken breast", "chicken"),
            ("bean curd", "tofu"),
            ("dairy milk", "milk"),
            ("cheddar cheese", "cheese"),
            ("white rice", "rice"),
            ("spaghetti noodles", "pasta"),
            ("red onion", "onions"),
            ("baby carrots", "carrots"),
            ("cherry tomatoes", "tomatoes"),
            ("iceberg lettuce", "lettuce"),
            ("fresh spinach", "spinach"),
            ("green bell pepper", "bell peppers"),
            ("button mushrooms", "mushrooms"),
            ("ripe bananas", "bananas"),
            ("red apples", "apples"),
            ("navel oranges", "oranges"),
            ("fresh lemons", "lemons"),
            ("greek yogurt", "yogurt"),
            ("extra virgin olive oil", "olive oil"),
            ("sea salt", "salt"),
            ("black pepper", "pepper"),
            ("garlic cloves", "garlic"),
            ("fresh ginger", "ginger"),
            ("low sodium soy sauce", "soy sauce"),
            ("balsamic vinegar", "vinegar"),
            ("raw honey", "honey"),
            ("granulated sugar", "sugar"),
            ("all purpose flour", "flour"),
            ("red lentils", "lentils"),
            ("black beans", "beans"),
            ("garbanzo beans", "chickpeas"),
            ("white quinoa", "quinoa"),
            ("rolled oats", "oats"),
            ("almonds", "nuts"),
            ("hass avocado", "avocado"),
            ("coconut milk", "coconut"),
            ("dark chocolate", "chocolate")
        ]
        
        for raw_name, expected_canonical in test_cases:
            result = normalizer.normalize_item(raw_name, 0.9, 1)
            assert result is not None, f"Failed to normalize '{raw_name}'"
            assert result.canonical_name == expected_canonical, \
                f"Expected '{expected_canonical}' but got '{result.canonical_name}' for '{raw_name}'"

if __name__ == "__main__":
    pytest.main([__file__])
