# eva_snapshot_hosted

## Introduction
EVA Visualization API is a Python-Django based API for generating visualizations of EVA, an AI virtual assistant that serves as a front desk operative in hotels. This innovative tool visualizes the conversational interactions of EVA, offering insights into its operational effectiveness and guest engagement.

## Features
- **Conversational AI Visualization**: Dynamic representations of EVA's interactions with guests.
- **Secure Authentication**: Access restricted to authorized users, ensuring data security.
- **Customizable Visual Output**: Allows users to request specific site visualization.
- **High-Performance Backend**: Built on Django for efficient and scalable request handling.

## Getting Started

### Prerequisites
- Python 3.x
- Django 3.x

### Installation
1. Clone the repository:
```git clone [repository URL]```
2. install dependencies:
```pip install -r requirements.txt```

### Usage
1. Start the Django server:
```python manage.py runserver```
2. Access the API endpoints:
- Authentication: `http://localhost:8000/auth`
- Visualization: `http://localhost:8000/eva-snapshot?{parameters}`

#### Example
http://127.0.0.1:8000/eva-snapshot?account_id=ACCOUNT-d9a69212&project_id=Westin-multi-variant-usp&group_id=MCODW&region=US&customer_email=jordan.prescott@fourteenip.com

## Support
For any inquiries or support, please contact Jordan Prescott at Jordan.Prescott@fourteenip.com or via our alternate email aisupport@fourteenip.com.
