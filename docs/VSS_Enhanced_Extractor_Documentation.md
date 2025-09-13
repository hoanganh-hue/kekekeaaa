# VSS Enhanced Fields Extraction Engine - Documentation

## Tổng quan

Enhanced Fields Extraction Engine là hệ thống trích xuất dữ liệu nâng cao cho VSS (Vietnam Social Security), được thiết kế để trích xuất 5 trường dữ liệu enhanced với độ chính xác cao và khả năng xử lý multiple HTML structures.

## Tính năng chính

### 1. Enhanced Fields Extraction
- **Số điện thoại** (`so_dien_thoai`)
- **Thu nhập** (`thu_nhap`) 
- **Ngân hàng** (`ngan_hang`)
- **Mã hộ gia đình** (`ma_ho_gia_dinh`)
- **Thông tin thành viên** (`thong_tin_thanh_vien`)

### 2. Multiple Extraction Strategies
- **CSS Selectors**: Sử dụng CSS selectors để target các elements cụ thể
- **Regex Patterns**: Pattern matching mạnh mẽ cho text extraction
- **Context Search**: Tìm kiếm dựa trên context keywords
- **XPath Simulation**: Mô phỏng XPath functionality với BeautifulSoup
- **Fallback Patterns**: Backup patterns khi main methods thất bại

### 3. HTML Structure Support
- **Table-based**: Traditional VSS table structures
- **Div-based**: Modern responsive layouts
- **Form-based**: Form inputs và select elements
- **JSON-embedded**: Embedded JSON data trong HTML
- **Mixed structures**: Combination của multiple formats

### 4. Advanced Data Normalization
- **Phone numbers**: Vietnam phone format standardization
- **Income**: Currency parsing và amount extraction
- **Bank names**: Bank code mapping và full name resolution
- **Household codes**: Format validation và standardization
- **Member info**: Structured parsing of family member data

### 5. Quality Scoring System
- **Confidence scores**: 0.0 - 1.0 confidence rating
- **Quality levels**: EXCELLENT, GOOD, MODERATE, POOR, FAILED
- **Method tracking**: Which extraction method was used
- **Validation metrics**: Error counting và consistency checking

### 6. Cross-validation
- **Input data comparison**: So sánh extracted data với input data
- **Consistency checking**: Field-level consistency validation
- **Error detection**: Identify inconsistencies và anomalies

## Cách sử dụng

### Basic Usage

```python
from src.vss_enhanced_extractor import VSS_EnhancedExtractor

# Initialize extractor
extractor = VSS_EnhancedExtractor()

# Extract fields từ HTML response
html_content = """
<table>
    <tr><td>Điện thoại</td><td>0912345678</td></tr>
    <tr><td>Thu nhập</td><td>25,000,000 VND</td></tr>
    <tr><td>Ngân hàng</td><td>VCB</td></tr>
    <tr><td>Mã hộ gia đình</td><td>HGD123456789</td></tr>
</table>
"""

# Extract với optional input data cho cross-validation
input_data = {
    'phone': '0912345678',
    'expected_income': 25000000
}

result = extractor.extract_enhanced_fields(html_content, input_data)

# Access results
extracted_fields = result['extracted_fields']
quality_metrics = result['quality_metrics']
summary = result['extraction_summary']
```

### Analyzing Results

```python
# Check overall success
if summary['status'] == 'excellent':
    print(f"Extraction successful! Success rate: {summary['success_rate']:.1%}")

# Check individual fields
for field_name, extraction_result in extracted_fields.items():
    print(f"{field_name}:")
    print(f"  Value: {extraction_result.extracted_value}")
    print(f"  Confidence: {extraction_result.confidence_score:.2f}")
    print(f"  Quality: {extraction_result.quality_level.value}")
    print(f"  Method: {extraction_result.extraction_method}")
    
    if extraction_result.validation_errors:
        print(f"  Validation errors: {len(extraction_result.validation_errors)}")
```

## Architecture

### ExtractionResult Class
```python
@dataclass
class ExtractionResult:
    field_name: str
    extracted_value: Any
    confidence_score: float
    quality_level: ExtractionQuality
    extraction_method: str
    fallback_used: bool = False
    validation_errors: List[str] = field(default_factory=list)
    normalization_applied: List[str] = field(default_factory=list)
```

### FieldPattern Class
```python
@dataclass
class FieldPattern:
    css_selectors: List[str]
    xpath_selectors: List[str]
    regex_patterns: List[str]
    context_keywords: List[str]
    validation_rules: List[str]
    normalization_functions: List[str]
    fallback_patterns: List[str]
```

## Pattern Definitions

### Số điện thoại
- **CSS Selectors**: `'td:contains("Điện thoại") + td'`, `'span[class*="phone"]'`
- **Regex Patterns**: `r'(?:0|\+84|84)[1-9][0-9]{7,9}'`
- **Normalization**: Remove formatting, convert +84 to 0 prefix
- **Validation**: Vietnam phone format validation

### Thu nhập
- **CSS Selectors**: `'td:contains("Thu nhập") + td'`, `'span[class*="salary"]'`
- **Regex Patterns**: `r'([0-9,.]+)\s*(?:VND|đồng)'`
- **Normalization**: Parse currency, convert to number
- **Validation**: Reasonable income range check

### Ngân hàng
- **CSS Selectors**: `'td:contains("Ngân hàng") + td'`, `'select[name*="bank"] option[selected]'`
- **Regex Patterns**: Bank codes (`ACB`, `VCB`, etc.)
- **Normalization**: Map codes to full bank names
- **Validation**: Check against known banks list

### Mã hộ gia đình
- **CSS Selectors**: `'td:contains("Mã hộ") + td'`, `'[data-field="household_code"]'`
- **Regex Patterns**: `r'(?:Mã\s*hộ)[:\s]*([A-Z0-9]{8,15})'`
- **Normalization**: Uppercase, remove spaces
- **Validation**: Alphanumeric format validation

### Thông tin thành viên
- **CSS Selectors**: `'table:contains("Thành viên") tbody tr'`
- **Regex Patterns**: Relationship patterns (`Con`, `Vợ`, `Chồng`)
- **Normalization**: Parse structured member data
- **Validation**: Ensure name và relationship fields

## Quality Metrics

### Confidence Score Calculation
```python
confidence = base_confidence * method_weight - error_penalty
```

- **Base confidence**: Initial confidence từ extraction method
- **Method weight**: CSS (1.0), Regex (0.9), Context (0.8), Fallback (0.5)
- **Error penalty**: 0.1 per validation error

### Quality Levels
- **EXCELLENT** (≥0.9): High confidence, no errors
- **GOOD** (≥0.7): Good confidence, minimal errors
- **MODERATE** (≥0.5): Acceptable confidence, some errors
- **POOR** (>0.0): Low confidence, many errors
- **FAILED** (0.0): No extraction possible

### Cross-validation Scoring
- **Field consistency**: Compare extracted vs input values
- **Similarity calculation**: Percentage match for numeric values
- **Overall consistency**: Average của tất cả field consistencies

## Error Handling

### Validation Errors
- **Format errors**: Incorrect data format
- **Range errors**: Values outside expected ranges
- **Consistency errors**: Mismatches với input data

### Fallback Mechanisms
1. **Primary extraction** fails → Try secondary patterns
2. **All patterns** fail → Use fallback patterns
3. **Complete failure** → Return ExtractionResult với error info

## Testing

### Comprehensive Test Suite
```bash
cd /workspace
python test_enhanced_extractor.py
```

### Test Coverage
- **5 HTML structure types**: Table, Div, Form, Mixed, Minimal
- **All extraction methods**: CSS, Regex, Context, XPath, Fallback
- **Cross-validation scenarios**: With và without input data
- **Error conditions**: Invalid HTML, missing data

### Performance Metrics
- **Success rate**: Percentage of successful field extractions
- **Quality distribution**: Count của each quality level
- **Method effectiveness**: Which methods work best per structure type

## Integration với VSS System

### Usage trong VSS Workflow
```python
# Trong VSS data collection pipeline
html_response = vss_client.lookup_citizen(cccd)
input_data = get_original_input_data(cccd)

extractor = VSS_EnhancedExtractor()
enhanced_data = extractor.extract_enhanced_fields(html_response, input_data)

# Merge với existing data
final_data = merge_with_basic_data(basic_data, enhanced_data)
save_to_database(final_data)
```

### Configuration Options
```python
# Customize extraction patterns
extractor.field_patterns['so_dien_thoai'].css_selectors.append('custom-selector')

# Adjust quality weights
extractor.quality_weights['validation_score'] = 0.4

# Add custom normalization
extractor.normalization_maps['banks']['CUSTOM'] = 'Custom Bank Name'
```

## Performance Considerations

### Optimization Tips
1. **Order patterns** by likelihood of success
2. **Use specific selectors** trước generic ones
3. **Cache normalization** maps for repeated use
4. **Limit regex complexity** để avoid performance issues

### Memory Usage
- **BeautifulSoup parsing**: Memory scales với HTML size
- **Pattern matching**: Minimal memory overhead
- **Result storage**: Linear với number of extracted fields

## Future Enhancements

### Planned Features
1. **Machine Learning**: Use ML models for pattern recognition
2. **Dynamic patterns**: Auto-generate patterns từ training data
3. **Performance optimization**: Async processing, caching
4. **Extended validation**: More sophisticated cross-validation rules
5. **Custom extractors**: Plugin system cho custom field types

### Extensibility
- **New field types**: Add patterns for additional fields
- **Custom validators**: Implement domain-specific validation
- **Alternative parsers**: Support cho other HTML parsing libraries
- **Output formats**: Export results trong different formats

## Support & Maintenance

### Troubleshooting
1. **Low confidence scores**: Check pattern matching effectiveness
2. **Validation errors**: Review normalization logic
3. **Performance issues**: Profile HTML parsing bottlenecks
4. **Integration problems**: Verify input data format compatibility

### Monitoring
- Track success rates over time
- Monitor quality score distributions
- Identify patterns that need improvement
- Log extraction failures for analysis

---

**Version**: 2.0  
**Last Updated**: 2025-09-13  
**Contact**: MiniMax Agent Development Team
