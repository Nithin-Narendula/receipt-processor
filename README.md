"# receipt-processor" 


```markdown
# Receipt Processor Challenge

A RESTful API service that processes receipts and calculates reward points based on predefined rules. Built with Python, Flask, and Docker.

## Features
- **Process Receipts**: Submit receipts via a `POST` endpoint to receive a unique ID.
- **Retrieve Points**: Fetch reward points for a processed receipt using its ID.
- **Validation**: Ensures receipt data integrity (date/time formats, valid prices, etc.).
- **Dockerized**: Ready-to-run containerized setup.

## API Endpoints

### 1. `POST /receipts/process`
- **Request**: Submit a receipt in JSON format.
- **Response**: Returns a unique `id` for the receipt.
- **Example Request**:
  ```json
  {
    "retailer": "Target",
    "purchaseDate": "2022-01-01",
    "purchaseTime": "13:01",
    "items": [
      {"shortDescription": "Mountain Dew 12PK", "price": "6.49"},
      {"shortDescription": "Emils Cheese Pizza", "price": "12.25"}
    ],
    "total": "35.35"
  }
  ```
- **Example Response**:
  ```json
  {"id": "7fb1377b-b223-49d9-a31a-5a02701dd310"}
  ```

### 2. `GET /receipts/{id}/points`
- **Request**: Provide a receipt ID.
- **Response**: Returns the calculated reward points.
- **Example Response**:
  ```json
  {"points": 28}
  ```

## Prerequisites
- Docker ([Installation Guide](https://docs.docker.com/get-docker/))
- Docker Compose (optional)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/receipt-processor-challenge.git
cd receipt-processor-challenge
```

### 2. Run with Docker
```bash
# Build the image
docker build -t receipt-processor .

# Start the container
docker run -p 5000:5000 receipt-processor
```

### 3. Run with Docker Compose
```bash
docker-compose up --build
```

The API will be available at `http://localhost:5000`.

## Testing the API

### Submit a Receipt
```bash
curl -X POST http://localhost:5000/receipts/process \
  -H "Content-Type: application/json" \
  -d '{
    "retailer": "Target",
    "purchaseDate": "2022-01-01",
    "purchaseTime": "13:01",
    "items": [
      {"shortDescription": "Mountain Dew 12PK", "price": "6.49"},
      {"shortDescription": "Emils Cheese Pizza", "price": "12.25"}
    ],
    "total": "35.35"
  }'
```

### Get Points
Replace `{id}` with the ID returned from the `POST` request:
```bash
curl http://localhost:5000/receipts/{id}/points
```

## Points Calculation Rules
Points are awarded based on these rules:
1. **Retailer Name**: 1 point per alphanumeric character.
2. **Round Total**: 50 points if the total is a round dollar amount.
3. **Multiple of 0.25**: 25 points if the total is a multiple of 0.25.
4. **Item Count**: 5 points for every 2 items.
5. **Item Description**: `ceil(price * 0.2)` for items with trimmed descriptions divisible by 3.
6. **Odd Purchase Day**: 6 points if the purchase day is odd.
7. **Purchase Time**: 10 points for purchases between 2:00 PM and 4:00 PM.

## Technologies Used
- Python 3.9
- Flask
- Docker
- JSON Schema Validation

---

**Acknowledgments**: Challenge design by [Fetch Rewards](https://fetch.com/).
```

---


This README provides clear setup instructions, API documentation, and testing examples, making it easy for users (and reviewers) to understand and run this project.
