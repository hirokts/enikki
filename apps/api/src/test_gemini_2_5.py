"""
Gemini 2.5 Flash Image (Nano Banana) のテストスクリプト
google-genai SDK を使用
"""

import os
from google import genai
from google.genai import types

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "enikki-cloud")
REGION = "us-central1"  # 新しいモデルは us-central1 で利用可能なことが多い

print(f"Creating client for project={PROJECT_ID}, location={REGION}")
client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=REGION
)

def test_gemini_image_generation():
    model_name = "gemini-2.5-flash-image"
    prompt = "A cute illustration of a banana in a crayon style, colorful and cheerful."
    
    print(f"\n--- Testing model: {model_name} ---")
    print(f"Prompt: {prompt}")
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio="1:1",
                ),
            ),
        )
        
        print("Response received!")
        
        for part in response.parts:
            if part.inline_data:
                print(f"Image generated! MIME type: {part.inline_data.mime_type}")
                # 画像を保存
                generated_image = part.as_image()
                filename = "/app/src/test_generated_image.png"
                generated_image.show()  # または generated_image.save(filename)
                print(f"Image saved to: {filename}")
            elif part.text:
                print(f"Text response: {part.text}")
            else:
                print(f"Unknown part type")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini_image_generation()
