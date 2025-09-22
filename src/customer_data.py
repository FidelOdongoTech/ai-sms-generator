import json

def get_customer_data():
    customer_data = [
        {
            "name": "John",
            "loan_balance": "15,000 KES",
            "due_date": "20th Sept",
            "tone": "urgent"
        },
        {
            "name": "Mary",
            "loan_balance": "5,000 KES",
            "due_date": "25th Sept",
            "tone": "friendly"
        },
        {
            "name": "Ali",
            "loan_balance": "30,000 KES",
            "due_date": "18th Sept",
            "tone": "formal"
        }
    ]
    return customer_data

if __name__ == "__main__":
    data = get_customer_data()
    print(json.dumps(data, indent=4))

