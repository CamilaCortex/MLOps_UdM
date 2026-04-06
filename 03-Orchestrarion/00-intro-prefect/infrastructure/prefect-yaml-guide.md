# Prefect YAML Deployment Guide

Simple guide to deploy flows using prefect.yaml configuration file.

## What is prefect.yaml?

A declarative configuration file that defines how your flows are deployed.
Instead of writing Python code for deployments, you define them in YAML.

## Basic Structure

```yaml
deployments:
  - name: my-deployment
    entrypoint: path/to/file.py:flow_function
    schedule:
      cron: "0 * * * *"
    parameters:
      param1: value1
```

## Step 1: Create Your Flow

Create a simple flow file `my_flow.py`:

```python
from prefect import flow, task

@task
def process_data(value: int):
    print(f"Processing: {value}")
    return value * 2

@flow
def my_flow(input_value: int = 10):
    result = process_data(input_value)
    print(f"Result: {result}")
    return result
```

## Step 2: Create prefect.yaml

In the same directory, create `prefect.yaml`:

```yaml
deployments:
  - name: my-deployment
    entrypoint: my_flow.py:my_flow
    schedule:
      cron: "*/5 * * * *"
      timezone: "America/Bogota"
    parameters:
      input_value: 20
```

## Step 3: Deploy

Deploy all deployments defined in the YAML:

```bash
prefect deploy --all
```

Or deploy a specific one:

```bash
prefect deploy -n my-deployment
```

## Step 4: Run

The flow will run automatically based on the schedule.

To run manually:

```bash
prefect deployment run my-flow/my-deployment
```

## Configuration Options

### Schedule with Cron

```yaml
schedule:
  cron: "0 2 * * *"        # Daily at 2 AM
  timezone: "America/Bogota"
```

### Schedule with Interval

```yaml
schedule:
  interval: 3600           # Every hour (in seconds)
  timezone: "America/Bogota"
```

### Parameters

```yaml
parameters:
  year: 2025
  month: 1
  threshold: 0.8
```

### Tags

```yaml
tags:
  - production
  - ml-training
  - daily
```

### Work Pool (requires paid plan)

```yaml
work_pool:
  name: my-work-pool
```

## Complete Example

```yaml
deployments:
  - name: ml-training-daily
    entrypoint: flows/train.py:train_model
    schedule:
      cron: "0 2 * * *"
      timezone: "America/Bogota"
    parameters:
      year: 2025
      month: 1
      n_trials: 20
    tags:
      - production
      - ml
    description: "Daily ML model training"

  - name: ml-training-weekly
    entrypoint: flows/train.py:train_model
    schedule:
      cron: "0 3 * * 0"
      timezone: "America/Bogota"
    parameters:
      year: 2025
      month: 1
      n_trials: 50
    tags:
      - production
      - ml
      - weekly
    description: "Weekly ML model training with more trials"
```

## Useful Commands

```bash
# Deploy all deployments
prefect deploy --all

# Deploy specific deployment
prefect deploy -n my-deployment

# List deployments
prefect deployment ls

# Inspect deployment
prefect deployment inspect my-flow/my-deployment

# Delete deployment
prefect deployment delete my-flow/my-deployment

# Run deployment
prefect deployment run my-flow/my-deployment

# Run with custom parameters
prefect deployment run my-flow/my-deployment --param year=2024
```

## Advantages of prefect.yaml

1. **Declarative**: Configuration as code
2. **Version Control**: Easy to track changes in git
3. **Multiple Deployments**: Define many deployments in one file
4. **Reusable**: Same flow, different schedules/parameters
5. **Simple**: No Python code needed for deployment

## Example: ML Pipeline

File structure:
```
project/
├── prefect.yaml
├── flows/
│   └── ml_pipeline.py
└── src/
    └── model.py
```

`flows/ml_pipeline.py`:
```python
from prefect import flow, task

@task
def load_data(year: int, month: int):
    print(f"Loading data for {year}-{month}")
    return {"samples": 1000}

@task
def train_model(data: dict):
    print(f"Training with {data['samples']} samples")
    return {"rmse": 7.15}

@flow
def ml_pipeline(year: int, month: int):
    data = load_data(year, month)
    result = train_model(data)
    return result
```

`prefect.yaml`:
```yaml
deployments:
  - name: ml-january
    entrypoint: flows/ml_pipeline.py:ml_pipeline
    schedule:
      cron: "0 2 1 * *"
    parameters:
      year: 2025
      month: 1

  - name: ml-february
    entrypoint: flows/ml_pipeline.py:ml_pipeline
    schedule:
      cron: "0 2 1 * *"
    parameters:
      year: 2025
      month: 2
```

Deploy both:
```bash
prefect deploy --all
```

## Troubleshooting

### Deployment not found

Make sure you're in the directory with `prefect.yaml`:

```bash
cd /path/to/your/project
prefect deploy --all
```

### Flow not running

Check that:
1. Deployment was created: `prefect deployment ls`
2. Schedule is correct
3. Flow file path is correct in `entrypoint`

### Syntax errors

Validate YAML syntax:
```bash
python -c "import yaml; yaml.safe_load(open('prefect.yaml'))"
```

## Resources

- [Prefect Deployments Docs](https://docs.prefect.io/concepts/deployments/)
- [prefect.yaml Reference](https://docs.prefect.io/concepts/projects/)
