# Mini Pluggable Data Transformer

A lightweight, extensible data transformation system built with Python. This system allows you to apply configurable transformation pipelines to CSV data and get JSON results.

## Contents

- [Feature](#features)
- [Workflow](#workflow)
- [Getting Started](#getting-started)
- [Usage Examples](#usage-examples)
- [Quick Demo](#quick-demo)

## Features

- **Pluggable Transformations**: Easily add, enable, or disable transformations
- **Pipeline Configuration**: Create reusable transformation pipelines
- **Flexible Pipeline Formats**: Define pipelines in JSON, YAML, or using a builder pipeline
- **REST API**: Transform data via a simple API interface
- **Validation**: Comprehensive validation of pipeline configurations
- **Registry Management**: Control which transformations are available
- **AI Pipeline Generation**: Generate transformation pipelines using natural language prompts


## Workflow

The platform follows a simple two-step process:

1. **Upload Your Data**
   - Upload your CSV file through the API
   - The system will return a unique filename for your uploaded file
   - Currently, only CSV files are supported

2. **Transform Your Data**

    You can transform your data in three flexible ways:

   1. **Using AI (Easiest)**
   2. **Using JSON Configuration**
   3. **Using YAML Configuration**

   The transformed data will be returned in JSON format

## Getting Started

### Prerequisites

- Python 3.10+
- conda

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/data-transformer.git
cd data-transformer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the API

Start the FastAPI server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at http://localhost:8000. You can access the interactive API documentation at http://localhost:8000/api/docs.


### Running Tests

```bash
pytest tests/
```

### Running with Docker

1. Copy the environment file:
```bash
cp .env.example .env
```

2. Update the environment variables in `.env` file with your configuration.

3. Build and start the containers:
```bash
docker-compose up --build
```

The API will be available at http://localhost:8000

### Development with Docker

For development, the application will automatically reload when you make changes to the code.

To run tests in Docker:
```bash
docker-compose run api pytest
```

### Docker Commands

- Start the application:
```bash
docker-compose up -d
```

- Stop the application:
```bash
docker-compose down
```

- Run tests:
```bash
docker-compose run api pytest
```

## Usage Examples

### API sample curls

**Upload CSV File**

```bash
curl -X POST "http://localhost:8000/api/files/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/data.csv"
```
**Generate JSON pipeline using AI**
```bash
curl -X POST "http://localhost:8000/api/transformations/pipeline/generate-from-ai" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "your_uploaded_file.csv",
    "prompt": "Filter rows where age is greater than 30, convert names to uppercase, and sort by age in descending order"
  }'
```

**Validate pipeline**
```bash
curl -X POST "http://localhost:8000/api/transformations/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "steps": [
      {
        "transformation": "filter",
        "params": {
          "column": "age",
          "operator": "gt",
          "value": 30
        }
      }
    ]
  }'
```

**Transform Data with JSON pipeline**
```bash
curl -X POST "http://localhost:8000/api/transformations/execute/json" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "your_uploaded_file.csv",
    "pipeline": {
      "steps": [
        {
          "transformation": "filter",
          "params": {
            "column": "age",
            "operator": "gt",
            "value": 30
          }
        },
        {
          "transformation": "uppercase",
          "params": {
            "columns": ["name"]
          }
        }
      ]
    }
  }'
```

**Transform Data using YAML Pipeline**
```bash
curl -X POST "http://localhost:8000/api/transformations/execute/yaml" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "your_uploaded_file.csv",
    "pipeline": "steps:\n  - transformation: filter\n    params:\n      column: status\n      operator: eq\n      value: active\n  - transformation: map_column\n    params:\n      type: rename\n      mapping:\n        first_name: firstName\n        last_name: lastName"
  }'
```

**Get example pipelines**
```bash
curl -X 'GET' "http://localhost:8000/api/transformations/pipeline/examples" \
  -H 'accept: application/json'
```

**Get Registry Configuration**
```bash
curl -X GET "http://localhost:8000/api/transformations/registry/config"
```

**Update Registry Configuration**
```bash
curl -X PUT "http://localhost:8000/api/transformations/registry/config" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "filter": true,
      "uppercase": true,
      "map_column": true,
      "sort": false
    }
  }'
```

### Additional Available Endpoints

The following endpoints are also available but not shown in the curl examples above:

- `GET /api/health` - Check service health status
- `GET /api/transformations` - List all available transformations
- `GET /api/transformations/status` - Get detailed transformation system status
- `DELETE /api/files/{filename}` - Delete an uploaded file


### Available Transformations

The system comes with three built-in transformations:

1. **Filter**: Filter rows based on column conditions
2. **Map Column**: Rename columns or map column values
3. **Uppercase**: Convert string columns to uppercase
4. **Sort**: Sorts the dataset based on a specified column

### Flexible Pipeline Definition Formats

#### JSON Format

```json
{
  "steps": [
    {
      "transformation": "filter",
      "params": {
        "column": "age",
        "operator": "gt",
        "value": 30
      }
    },
    {
      "transformation": "uppercase",
      "params": {
        "columns": ["name"]
      }
    }
  ]
}
```

#### YAML Format

```yaml
steps:
  - transformation: filter
    params:
      column: status
      operator: eq
      value: active
  - transformation: map_column
    params:
      type: rename
      mapping:
        first_name: firstName
        last_name: lastName
```

#### Python Builder API

```python
from app.service.pipeline import PipelineBuilder


pipeline = (
    PipelineBuilder()
    .filter(column="city", operator="contains", value="san")
    .uppercase(columns=["first_name", "last_name"])
    .map_column(mapping={"first_name": "firstName", "last_name": "lastName"})
    .sort(column="age", ascending=False)
    .build()
)

result = pipeline.execute(data)
```

#### Python Dictionary

```python
from src.pipeline import TransformationPipeline

pipeline_dict = {
    "steps": [
        {
            "transformation": "filter",
            "params": {
                "column": "age",
                "operator": "gte",
                "value": 35
            }
        }
    ]
}

pipeline = TransformationPipeline.from_config(pipeline_dict)
result = pipeline.execute(data)
```

#### Text-based pipeline configurage

You can generate transformation pipelines using natural language prompts with AI assistance. The AI will analyze your data's column structure and generate an appropriate pipeline based on your requirements. The generated pipeline will be validated and can be used just like any other pipeline configuration.

##### Validation Rules

The AI performs validation to ensure data integrity and transformation correctness:

1. **Column Validation**
   - Verifies column existence before any transformation
   - Checks column types match transformation requirements
   - Returns error if requested columns don't exist or have invalid types

2. **Transformation Validation**
   - Validates that requested transformations are available and appropriate
   - Ensures transformation parameters match expected types and ranges
   - Returns error if transformation cannot be performed

3. **Error Response Format**
   ```json
   {
     "error": true,
     "message": "Column 'column_name' does not exist or has invalid type"
   }
   ```
   or
   ```json
   {
     "error": true,
     "message": "No appropriate transformation available for the requested operation"
   }
   ```

**Example Prompts**

Here are some examples of natural language prompts you can use:

1. **Basic Filtering and Formatting**:
```python
prompt = "Filter rows where age is greater than 30, convert names to uppercase, and sort by age in descending order"
```

2. **Column Mapping and Renaming**:
```python
prompt = "Rename first_name to firstName and last_name to lastName, then convert all text columns to uppercase"
```

3. **Complex Transformations**:
```python
prompt = "Filter active users, convert their names to uppercase, sort by age in descending order, and rename the status column to user_status"
```

#### Using AI-Generated Pipelines

```python
from app.services.pipeline import TransformationPipeline

pipeline = await TransformationPipeline.from_ai_generated(
    filename="path-to-the-data.csv",
    prompt="Filter rows where age is greater than 30, convert names to uppercase, and sort by age in descending order"
)

result = pipeline.execute(data)
```

**Note**: The AI-generated pipeline feature requires a Groq AI API key

## Transformation Reference

### Filter Transformation

Filters rows based on column conditions.

**Parameters**:
- `column`: Column name to filter on
- `operator`: One of ['eq', 'ne', 'gt', 'lt', 'gte', 'lte', 'contains']
- `value`: Value to compare against

### Map Column Transformation

Renames columns or maps column values.

**Parameters**:
- `type`: Either 'rename' or 'value_map'
- `mapping`: Dictionary of old->new mappings
- `column`: (For value_map only) Column to apply value mapping to

### Uppercase Transformation

Converts string columns to uppercase.

**Parameters**:
- `columns`: List of column names to convert, or 'all' for all string columns

### Sort Transformation

Sorts the dataset based on a specified column.

**Parameters**:
- `column`: The name of the column to sort by.
- `ascending`: A boolean indicating whether to sort in ascending (`true`) or descending (`false`) order.

## Quick Demo

The demo will be using the data in [here](./examples/sample_data.csv)

### Generate pipeline with AI & Transform data

https://github.com/user-attachments/assets/f0e7fe49-af49-4573-9e31-a2ae0fa827af

### Transform data with YAML pipeline format

https://github.com/user-attachments/assets/72a444dc-c0e1-42ab-88dd-981b23048c04

## Extending the System

### Creating a Custom Transformation

1. Create a new class that inherits from `BaseTransformation`
2. Implement the required methods: `transform()` and `validate_params()`
3. Register your transformation with the registry

Example:

```python
from typing import Dict, Any

import pandas as pd

from app.transformations.base import BaseTransformation


class LowercaseTransformation(BaseTransformation):
    def __init__(self):
        super().__init__(
            name="lowercase",
            description="Convert string columns to lowercase"
        )

    def transform(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        result = data.copy()
        columns = params.get('columns', 'all')

        if columns == 'all':
            string_columns = result.select_dtypes(include=['object']).columns
            for col in string_columns:
                result[col] = result[col].astype(str).str.lower()
        else:
            for col in columns:
                if col in result.columns:
                    result[col] = result[col].astype(str).str.lower()

        return result

    def validate_params(self, params: Dict[str, Any]) -> bool:
        if 'columns' not in params:
            return False

        columns = params['columns']
        return columns == 'all' or isinstance(columns, list)

# Register the transformation
from app.dependencies.di_container import registry
registry.register(LowercaseTransformation())
```

## TODO Improvements

### File Handling

- [ ] Implement more file validations (scan for malwares)
- [ ] Add file cleanup mechanism (TTL-based)
- [ ] Add upload progress tracking
- [ ] Store file metadata (size, upload time, user)
- [ ] Add support for other file formats (Excel, JSON)
- [ ] Implement large files processing

### Pipeline Management
- [ ] Add pipeline versioning system
- [ ] Implement pipeline sharing mechanism
- [ ] Implement pipeline performance metrics
- [ ] Enhance pipeline validation rules
- [ ] Create pipeline documentation generator

### AI Integration
- [ ] Implement fallback mechanism for AI service
- [ ] Add caching for common transformations
- [ ] Implement cost optimization for AI calls
- [ ] Optimize prompt engineering
- [ ] Add multiple AI provider support


### Architecture
- [ ] Add monitoring, metrics & tracing
- [ ] Add rate limit
- [ ] Add authentication/authorization system
