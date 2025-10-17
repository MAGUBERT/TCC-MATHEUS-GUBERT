from google import genai

client = genai.Client(api_key="AIzaSyCjCNJbCtv5vI-rJdWr57AZ0FpQE5_nOW0")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain how AI works in a few words",
)

print(response.text)