from flask import (
    g
)

from .schemas import (
    user_schema, answer_schema, question_schema
)

from jsonschema import validate, ValidationError

def validate_user(user_data):
  """
  Validates user data against the defined in src.schemas.user_schema

  Args:
      user_data: A dictionary containing user information.

  Returns:
      None if the data is valid, otherwise raises a ValidationError with details.
  """
  try:
    validate(user_data, user_schema)
  except ValidationError as e:
        raise ValidationError(f"Error: Invalid user data: {e}")

def validate_question(question_data):
  """
  Validates question data against the defined in src.schemas.question_schema

  Args:
      question_data: A dictionary containing question information.

  Returns:
      None if the data is valid, otherwise raises a ValidationError with details.
  """
  try:
    validate(question_data, question_schema)
  except ValidationError as e:
        raise ValidationError(f"Error: Invalid question data: {e}")


def validate_answer(answer_data):
  """
  Validates answer data against the defined in src.schemas.question_schema

  Args:
      answer_data: A dictionary containing answer information.

  Returns:
      None if the data is valid, otherwise raises a ValidationError with details.
  """
  try:
    validate(answer_data, answer_schema)
  except ValidationError as e:
        raise ValidationError(f"Error: Invalid answer data: {e}")

if __name__ == "__main__":
    # Example usage
    user_data = {
      # "name": "John Doe",
      # "_id": "1234567890abcdef1234567890",  # Invalid format
      "email": "john.doe@example.com",
      "password_hash": "$2b$12$hH538J91Yv7yG12t0Q.0PO..."  # Hashed password
    }

    try:
      validate_user(user_data)
      print("User data is valid!")
    except ValidationError as e:
      print("Error:", e)
