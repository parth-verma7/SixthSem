user_schema = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "User Object Schema",
  "description": "Schema for validating user objects",
  "required": [
    "name",
    "email",
    "password"
  ],
  "properties": {
    "name": {
      "type": "string",
      "description": "User's name"
    },
    "_id": {
      "type": "string",
      "description": "User's MongoDB _id field",
      "pattern": "^[0-9a-fA-F]{24}$"  # Validate MongoDB ObjectID format
    },
    "email": {
      "type": "string",
      "format": "email",
      "description": "User's email address"
    },
    "password": {
      "type": "string",
      "description": "User's hashed password"
    }
  }
}

question_schema = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Question Object Schema",
  "description": "Schema for validating question objects",
  "required": ["title"],
  "properties": {
    "title": {
      "type": "string",
      "description": "The title of the question"
    },
    "description": {
      "type": "string",
      "description": "Optional description of the question"
    },
    "topics": {
      "type": "array",
      "description": "An array of strings representing the question's topics",
      "items": {
        "type": "string"
      },
      "minItems": 1  # Ensure at least one topic is present
    }
  }
}

answer_schema = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Answer Object Schema",
  "description": "Schema for validating answer objects",
  "required": ["text", "questionId", "userId"],
  "properties": {
    "text": {
      "type": "string",
      "description": "The content of the answer"
    },
    "questionId": {
      "type": "string",
      "description": "MongoDB _id of the question the answer belongs to",
      "pattern": "^[0-9a-fA-F]{24}$"  # Validate MongoDB ObjectID format
    },
    "userId": {
      "type": "string",
      "description": "MongoDB _id of the user who submitted the answer",
      "pattern": "^[0-9a-fA-F]{24}$"  # Validate MongoDB ObjectID format
    }
  }
}
